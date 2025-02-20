import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive,get_gsheet_connection
from audio_recorder2 import get_audio_recorder_html
from settings_folder import settings_folder
import requests
import ffmpeg 
import tempfile
from datetime import datetime
import time
import pandas as pd
from streamlit_javascript import st_javascript

js_code="""
  <!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Registrazione Audio con Trascrizione</title>
    <style>
        .custom-button {
            background-color: white;
            color: #34637D;
            border: 1px solid #34637D;
            border-radius: 8px;
            padding: 8px 16px;
            font-size: 14px;
            font-family: Arial, sans-serif;
            cursor: pointer;
            transition: all 0.1s ease-in-out;
            display: inline-block;
            text-decoration: none;
        }

        .custom-button:hover {
            border:1px solid #FBB614;
            color:#FBB614;
        }

        .custom-button:disabled {
            color: #adb5bd;
            border-color: #dee2e6;
            cursor: not-allowed;
        }

        #transcription {
            margin-top: 20px;
            height: 150px; /* Imposta un'altezza fissa */
            overflow-y: auto; /* Abilita lo scroll verticale */
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            background-color: white;
            font-size: 16px;
            font-family: Arial, sans-serif;
            color: #34637D;
            min-height: 50px;
        }
    </style>
</head>
<body>
<canvas id="waveCanvas" width="600" height="200" style="border:1px solid #ccc; margin-bottom: 20px;"></canvas>
<div style="margin-bottom: 20px;">
    <button class="custom-button" id="startBtn">Avvia registrazione</button>
    <button class="custom-button" id="pauseBtn" disabled>Pausa</button>
    <button class="custom-button" id="resumeBtn" disabled>Riprendi</button>
    <button class="custom-button" id="stopBtn" disabled>Ferma registrazione</button>
    <br><br>
    <textarea id="transcription" placeholder="La trascrizione apparirà qui..."></textarea>
    <br>
    <button id="saveBtn">Salva Trascrizione</button>
    <a id="downloadLink" style="display:none; margin-top: 20px;">Download Audio</a>
</div>
<audio id="audioPlayback" controls style="display: none; margin-top: 20px;"></audio>

<script>
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resumeBtn = document.getElementById('resumeBtn');
    const stopBtn = document.getElementById('stopBtn');
    const audioPlayback = document.getElementById('audioPlayback');
    const downloadLink = document.getElementById('downloadLink');
    const waveCanvas = document.getElementById('waveCanvas');
    const canvasCtx = waveCanvas.getContext('2d');
    const transcriptionDiv = document.getElementById('transcription');

    let mediaRecorder;
    let audioChunks = [];
    let stream;
    let audioContext;
    let analyser;
    let dataArray;
    let animationId;
    let recognition;
    let finalTranscript = ""; // Buffer per il testo definitivo

    function drawWaveform() {
        analyser.getByteTimeDomainData(dataArray);
        canvasCtx.fillStyle = 'white';
        canvasCtx.fillRect(0, 0, waveCanvas.width, waveCanvas.height);
        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'blue';
        canvasCtx.beginPath();

        const sliceWidth = waveCanvas.width / analyser.fftSize;
        let x = 0;

        for (let i = 0; i < analyser.fftSize; i++) {
            const v = dataArray[i] / 128.0;
            const y = (v * waveCanvas.height) / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(waveCanvas.width, waveCanvas.height / 2);
        canvasCtx.stroke();

        animationId = requestAnimationFrame(drawWaveform);
    }

    function startTranscription() {
        if (!('webkitSpeechRecognition' in window)) {
            transcriptionDiv.textContent = "Il riconoscimento vocale non è supportato su questo browser.";
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'it-IT';

        recognition.onresult = (event) => {
            let interimTranscript = "";

            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    // Se la trascrizione è definitiva, la aggiungiamo al buffer
                    finalTranscript += event.results[i][0].transcript + " ";
                } else {
                    // Se la trascrizione è provvisoria, la mostriamo senza cancellare il buffer
                    interimTranscript += event.results[i][0].transcript + " ";
                }
            }
            let textArea = document.getElementById('transcription');
            textArea.value = finalTranscript + interimTranscript;
        };

        recognition.onerror = (event) => {
            console.error("Errore nel riconoscimento vocale: ", event.error);
        };

        recognition.start();
    }

        document.getElementById('saveBtn').addEventListener('click', () => {
            let transcript = document.getElementById('transcription').value;
            localStorage.setItem("transcription", transcript);
        });

    function startTranscription2() {
        if (!('webkitSpeechRecognition' in window)) {
            transcriptionDiv.textContent = "Il riconoscimento vocale non è supportato su questo browser.";
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'it-IT';

        recognition.onresult = (event) => {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript + " ";
            }
            transcriptionDiv.textContent = transcript;
        };

        recognition.onerror = (event) => {
            console.error("Errore nel riconoscimento vocale: ", event.error);
        };

        recognition.start();
    }

    startBtn.addEventListener('click', async () => {
        audioChunks = [];
        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        source.connect(analyser);
        analyser.fftSize = 2048;
        dataArray = new Uint8Array(analyser.fftSize);

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioURL = URL.createObjectURL(audioBlob);

            // Mostra l'audio nel player
            audioPlayback.src = audioURL;
            audioPlayback.style.display = 'block';

            // Imposta il link per il download
            downloadLink.href = audioURL;
            downloadLink.download = "recording.wav";
            downloadLink.style.display = 'block';
            downloadLink.textContent = "Download Audio";

            cancelAnimationFrame(animationId);
            recognition.stop(); // Ferma la trascrizione alla fine della registrazione
        };

        mediaRecorder.start();
        drawWaveform();
        startTranscription(); // Avvia la trascrizione

        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
    });

    pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.pause();
            recognition.stop();
            pauseBtn.disabled = true;
            resumeBtn.disabled = false;
            cancelAnimationFrame(animationId);
        }
    });

    resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
            mediaRecorder.resume();
            startTranscription();
            resumeBtn.disabled = true;
            pauseBtn.disabled = false;
            drawWaveform();
        }
    });

    stopBtn.addEventListener('click', () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            stream.getTracks().forEach((track) => track.stop());
            recognition.stop();

            startBtn.disabled = false;
            pauseBtn.disabled = true;
            resumeBtn.disabled = true;
            stopBtn.disabled = true;
        }
    });
</script>
</body>
</html>

  """


if "avvio" not in st.session_state:
    st.session_state["avvio"]=True
if "selezione1" not in st.session_state:
    st.session_state["selezione1"]=0
if "selezione2" not in st.session_state:
    st.session_state["selezione2"]=0
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"]=None
if "ricomincia" not in st.session_state:
    st.session_state["ricomincia"]=False
if "file_upload_ids" not in st.session_state:
    st.session_state["file_upload_ids"] = []
if "transcription" not in st.session_state:
    st.session_state["transcription"]=""
if "transcription_saved" not in st.session_state:
    st.session_state["transcription_saved"] = False
if "transcription_text" not in st.session_state:
    st.session_state["transcription_text"]=""

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link
c,FOLDER_ID,domanda1,domanda2=settings_folder("Ematologia")
domande=[domanda1,domanda2]

def convert_mp3_to_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, format="wav").run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione MP3 -> WAV: {e.stderr.decode()}")
        return False

# Autenticazione Google Drive
def authenticate_and_upload(file_name, file_path):
    service = authenticate_drive()
    # Carica il file su Google Drive
    file_id = upload_to_drive(service, file_name, file_path, FOLDER_ID)
    return file_id

# Funzione per convertire il file audio in formato .ogg
def convert_to_ogg(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(
            output_path,
            acodec="libopus",  # Codec per OGG
            audio_bitrate="192k",
            format="ogg"
        ).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione in OGG: {e.stderr.decode()}")
        return False

# Funzione per inviare una lista di file a n8n e ricevere le trascrizioni
def get_transcriptions_from_n8n(file_id,nome,cartella):
    payload = {"file_id": file_id}
    payload["file_name"]=nome
    payload["folder"]=cartella
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        transcription = response.json().get("text", "Errore: nessuna trascrizione ricevuta.")
    else:
        transcription=(f"Errore: {response.status_code} - {response.text}")
    return transcription

# Configura la pagina
st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
)

# Layout della pagina
st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=200)

# Titolo dell'app Streamlit
st.title("Carica un file già registrato")

col1,col2,col3=st.columns(3)

with col3:
    # Scelta modalità: Caricamento o Registrazione
    mode = st.radio("Scegli un'opzione:", ["Carica un file audio", "Registra un nuovo audio"],index=st.session_state["selezione1"],disabled=st.session_state["ricomincia"])
    if mode=="Registra un nuovo audio":
        st.session_state["selezione1"]=1
    else:
        st.session_state["selezione1"]=0
with col2:
    cartella=st.radio("Tema di riferimento:",["Ematologia","Emofilia","Oncoematologia"],index=st.session_state["selezione2"],disabled=st.session_state["ricomincia"])
    if cartella=="Emofilia":
        st.session_state["selezione2"]=1
    elif cartella=="Oncoematologia":
        st.session_state["selezione2"]=2
    else:
        st.session_state["selezione2"]=0
    c,FOLDER_ID,domanda1,domanda2=settings_folder(cartella)
    domande=[domanda1,domanda2]
with col1:
    gc = get_gsheet_connection()
    SHEET_ID = "1WmImKIOs20FjqSBUHgQkr5tltEWlxHJosCEOEZMI_HQ"  
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1
    data_fo = worksheet.get_all_values()
    df = pd.DataFrame(data_fo[1:], columns=data_fo[0])
    regional=df.loc[df["Specializzazione"] == c, "Label"].tolist()
    nome=df["Abbreviazione"].tolist()
    if st.button("Riavvia",disabled=not(st.session_state["ricomincia"])):
        st.session_state["ricomincia"]=False
        st.session_state["transcription"]=""
        st.session_state["uploaded_file"]=None
        st.session_state["avvio"]=True
        st.session_state["selezione1"]=0
        st.rerun()

if mode == "Carica un file audio":
    file_ids=[]
    # Scelta farmacista e data
    regional_list=regional+["Altro"]
    fo_lungo=st.selectbox("Nome del farmacista intervistato",regional_list,index=len(regional_list)-2)
    if fo_lungo=="Altro":
        fo_lungo=st.text_input("Specificare")
        ruolo=st.text_input("Ruolo")
        if st.button("Aggiungi farmacista"):
            if fo_lungo and ruolo:
                worksheet.append_row([fo_lungo, ruolo,c])  
                st.rerun()
            else:
                st.error("Inserisci tutti i campi!")
    else:
        fo=df.loc[df["Label"] == fo_lungo, "Abbreviazione"].tolist()
        fo=fo[0]
        data_valore=st.date_input("Data dell'intervista", value="today",format="DD/MM/YYYY")
        now = datetime.now()
        data=data_valore.strftime("%Y-%m-%d")+"_"+now.strftime("%H-%M-%S")
        # Caricamento di un file audio locale
        st.session_state["uploaded_file"] = st.file_uploader("Carica un file audio (WAV o MP3)", type=["wav","mp3"])
        if st.session_state["uploaded_file"]:
            if st.session_state["ricomincia"]==False:
                st.session_state["ricomincia"]=True
                st.session_state["uploaded_file"]=None
                st.session_state["avvio"]=True
                st.rerun()
            with st.spinner("Caricando..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{st.session_state["uploaded_file"].name.split('.')[-1]}") as temp_file:
                    temp_file.write(st.session_state["uploaded_file"].getbuffer())
                    input_path = temp_file.name

                # Percorso per il file convertito
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
                    output_path = temp_ogg_file.name
        
                # Conversione in OGG
                if convert_to_ogg(input_path, output_path):
                    # Carica su Google Drive
                    temp_name_personalised=c+"_"+data+"_"+fo+".ogg"
                    if st.button("Salva su Drive"):
                        file_ids = authenticate_and_upload(temp_name_personalised, output_path)
                        st.session_state["file_upload_ids"]=file_ids
                        st.success("File caricato su Drive")
                        st.session_state["avvio"]=False
                if st.button("Trascrivi il file caricato",disabled=st.session_state["avvio"]):
                        file_ids=st.session_state["file_upload_ids"]
                        if file_ids:
                            transcriptions=[]
                            # Itera su ciascun ID del file
                            for file_id in file_ids:
                                transcription=get_transcriptions_from_n8n(file_id,c+"_"+data+"_"+fo+".txt",FOLDER_ID)
                                transcriptions.append(transcription)
                        else:
                            st.error("Inserisci almeno un ID file per procedere.")       
                        combined_transcription = "\n".join(transcriptions)
                        st.session_state["transcription"] = combined_transcription
                        st.session_state["transcription_saved"] = False
        if st.session_state["transcription"]:
            with st.form(key="save_transcription_form"):
                    st.subheader("Trascrizione:")
                    transcription_content = st.text_area("Puoi modificare la trascrizione prima di salvarla:", st.session_state["transcription"], height=300)
                    submit_button = st.form_submit_button("Salva la trascrizione su Google Drive")
                    if submit_button and not st.session_state["transcription_saved"]:
                        if transcription_content != st.session_state["transcription"]:
                            st.session_state["transcription"]=transcription_content
                        # Salva il contenuto temporaneamente come file di testo
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_text_file:
                            temp_text_file.write(transcription_content.encode('utf-8'))
                            temp_text_file_path = temp_text_file.name
                        # Carica il file su Google Drive
                        file_name = f"Trascrizione_{temp_name_personalised}.txt"
                        try:
                            file_id = authenticate_and_upload(file_name, temp_text_file_path)
                            st.success(f"Salvataggio completato")
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio su Google Drive: {e}")

elif mode == "Registra un nuovo audio":
    if st.session_state["ricomincia"]==False:
        st.session_state["ricomincia"]=True
        st.session_state["uploaded_file"]=None
        st.session_state["avvio"]=True
        st.rerun()

    with st.expander("Sezione 1"):
        st.markdown(domanda1)
        st.components.v1.html(js_code, height=300,scrolling=True)
        transcription_text = st_javascript(js_code)
        
        st.write(transcription_text)
        if transcription_text and transcription_text != st.session_state["transcription_text"]:
            st.session_state["transcription_text"] = transcription_text
        st.text_area("Testo trascritto", st.session_state["transcription_text"], height=200)
    #with st.expander("Sezione 2"):
    #    st.markdown(domanda2)
    #    st.components.v1.html(get_audio_recorder_html(), height=500)

elif mode=="Trascrivi": 
    # Elenca i file nella cartella
    if os.path.exists("https://drive.google.com/drive/folders/"+FOLDER_ID):
        audio_files = [f for f in os.listdir(FOLDER_ID) if f.endswith(('.ogg'))]
        if audio_files:
            st.title("File caricati")
            selected_file = st.selectbox("Seleziona un file audio", audio_files)

            # Mostra il nome del file selezionato
            st.write(f"Hai selezionato: {selected_file}")

            # Riproduci l'audio selezionato
            file_path = os.path.join(FOLDER_ID, selected_file)
            with open(file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/wav" if selected_file.endswith(".wav") else "audio/mp3")
        else:
            st.warning("Nessun file audio trovato nella cartella.")
    else:
        st.error(f"La cartella {FOLDER_ID} non esiste. Creala e aggiungi file audio.")   
        # Pulsante per avviare la trascrizione
        if 1<0:#file_ids:
            transcriptions=[]
            # Itera su ciascun ID del file
            with st.spinner("Esecuzione della trascrizione..."):
                for file_id in file_ids:
                    st.success(f"trascrivendo {file_id}")
                    transcription=get_transcriptions_from_n8n(file_id,"",FOLDER_ID)
                    transcriptions.append(transcription)
        else:
            st.error("Inserisci almeno un ID file per procedere.")
