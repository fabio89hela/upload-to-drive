import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
import requests
import ffmpeg 
import tempfile

# Configura la pagina
st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
)

# ID della cartella Google Drive dove salvare i file (sostituisci con il tuo Folder ID)
FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link

# Layout della pagina
st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=200)

# Titolo dell'app Streamlit
st.title("Carica un file già registrato")

# Pulsante per registrare un nuovo audio
if st.button("Registra un nuovo audio"):
    st.components.v1.html(get_audio_recorder_html(), height=500)

# Pulsante per caricare un file audio locale
uploaded_file = st.file_uploader("Carica un file audio salvato in locale", type=["ogg", "mp3", "wav"])
if uploaded_file:
    temp_path = f"./{uploaded_file.name}"
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"File caricato correttamente: {uploaded_file.name}")


# Funzione per convertire il file audio in formato .ogg
def convert_to_ogg(input_data, output_file_name):
    try:
        input_stream = ffmpeg.input("pipe:0")  # Leggi dati da stdin
        output_stream = ffmpeg.output(
            input_stream,
            "pipe:1",
            vn=None,  # Nessun video
            map_metadata=-1,  # Rimuovi metadati
            ac=1,  # Mono
            c="libopus",  # Codec audio
            b="12k",  # Bitrate
            application="voip",  # Ottimizzazione per voce
            f="ogg"  # Formato di output
        ).global_args("-y")  # Sovrascrivi l'output

        # Esegui ffmpeg con input e output in memoria
        out, _ = ffmpeg.run(output_stream, input=input_data, capture_stdout=True, capture_stderr=True)
        return io.BytesIO(out)  # Ritorna un buffer di BytesIO
    except ffmpeg.Error as e:
        st.error("Errore durante la conversione con FFmpeg.")
        st.error(f"FFmpeg stderr: {e.stderr.decode()}")
        raise RuntimeError(f"Errore durante la conversione con FFmpeg: {e.stderr.decode()}")

# Funzione per inviare una lista di file a n8n e ricevere le trascrizioni
def get_transcriptions_from_n8n(file_id):
    payload = {"file_id": file_id}
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        transcription = response.json().get("text", "Errore: nessuna trascrizione ricevuta.")
    else:
        transcription=(f"Errore: {response.status_code} - {response.text}")
    return transcription

# Autenticazione con Google Drive
service = authenticate_drive()

# Caricamento file da parte dell'utente
uploaded_file = st.file_uploader("Carica un file audio", type=["mp3", "wav"])

if uploaded_file:
    #st.write(f"File caricato: {uploaded_file.name}")

    # Leggi i dati dal file caricato
    input_data = uploaded_file.read()
    output_file_name = uploaded_file.name.replace(".mp3", ".ogg").replace(".wav", ".ogg")

    # Converti il file in formato .ogg
    with st.spinner("Conversione in corso..."):
        converted_audio = convert_to_ogg(input_data, output_file_name)
        st.success(f"File convertito con successo in formato .ogg!")
    # Salva il file convertito su disco temporaneo per caricarlo su Google Drive
    temp_path = f"/tmp/{output_file_name}"
    st.success(f"{temp_path}")
    with open(temp_path, "wb") as temp_file:
        temp_file.write(converted_audio.getbuffer())
        st.success(f"Dimensione file: {os.path.getsize(temp_path) / (1024 * 1024)}")

    # Carica il file convertito su Google Drive
    if 1<0:
        service = authenticate_drive()
        with st.spinner("Caricamento su Google Drive in corso..."):
            file_ids = upload_to_drive(service, output_file_name, temp_path, FOLDER_ID)
            st.success(f"File caricato con successo su Google Drive! IDs del file: {file_ids}")
    
        # Pulsante per avviare la trascrizione
        if file_ids:
            transcriptions=[]
            # Itera su ciascun ID del file
            with st.spinner("Esecuzione della trascrizione..."):
                for file_id in file_ids:
                    st.success(f"trascrivendo {file_id}")
                    transcription=get_transcriptions_from_n8n(file_id)
                    transcriptions.append(transcription)
        else:
            st.error("Inserisci almeno un ID file per procedere.")
        combined_transcription = "\n".join(transcriptions)
        st.write(combined_transcription)
        st.text_area("Trascrizione combinata:", combined_transcription, height=600)
    else:
        # Inserisci il codice HTML + JavaScript
        st.components.v1.html(
    """
    <canvas id="waveCanvas" width="600" height="200" style="border:1px solid #ccc; margin-bottom: 20px;"></canvas>
    <div style="margin-bottom: 20px;">
      <button id="startBtn">Start Recording</button>
      <button id="pauseBtn" disabled>Pause</button>
      <button id="resumeBtn" disabled>Resume</button>
      <button id="stopBtn" disabled>Stop</button>
    </div>
    <audio id="audioPlayback" controls style="display: none; margin-top: 20px;"></audio>

    <script src="https://unpkg.com/wavesurfer.js"></script>
    <script>
      const startBtn = document.getElementById('startBtn');
      const pauseBtn = document.getElementById('pauseBtn');
      const resumeBtn = document.getElementById('resumeBtn');
      const stopBtn = document.getElementById('stopBtn');
      const audioPlayback = document.getElementById('audioPlayback');
      const waveCanvas = document.getElementById('waveCanvas');
      const canvasCtx = waveCanvas.getContext('2d');

      let mediaRecorder;
      let audioChunks = [];
      let stream;
      let audioContext;
      let analyser;
      let dataArray;
      let animationId;

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
      // Crea il Blob audio
      const audioBlob = new Blob(audioChunks, { type: 'audio/ogg; codecs=opus' });

      // Crea un URL per l'audio registrato (per il player)
      const audioURL = URL.createObjectURL(audioBlob);

      // Mostra l'audio nel player
      audioPlayback.src = audioURL;
      audioPlayback.style.display = 'block';

      // Invia il file audio al backend
      const formData = new FormData();
      formData.append('file', audioBlob, 'recording.ogg');

      fetch('/audio-upload', {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('File audio inviato con successo:', data);
        })
        .catch((error) => {
          console.error('Errore durante l\'invio del file audio:', error);
        });

      // Ferma il rendering dell'onda
      cancelAnimationFrame(animationId);
    };
        mediaRecorder.start();
        drawWaveform();
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        stopBtn.disabled = false;
      });

      pauseBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
          mediaRecorder.pause();
          pauseBtn.disabled = true;
          resumeBtn.disabled = false;
          cancelAnimationFrame(animationId);
        }
      });

      resumeBtn.addEventListener('click', () => {
        if (mediaRecorder && mediaRecorder.state === 'paused') {
          mediaRecorder.resume();
          resumeBtn.disabled = true;
          pauseBtn.disabled = false;
          drawWaveform();
        }
      });

      stopBtn.addEventListener('click', () => {
        if (mediaRecorder) {
          mediaRecorder.stop();
          stream.getTracks().forEach((track) => track.stop());
          startBtn.disabled = false;
          pauseBtn.disabled = true;
          resumeBtn.disabled = true;
          stopBtn.disabled = true;
        }
      });
    </script>
    """,
    height=500,
)
        
    # Salva temporaneamente il file localmente
    #temp_file_path = os.path.join(os.getcwd(), uploaded_file.name)
    #with open(temp_file_path, "wb") as f:
    #    f.write(uploaded_file.getbuffer())
    #    input_path = f.name
    
    # Carica il file su Google Drive
    #with st.spinner("Caricamento su Google Drive in corso..."):
    #    file_id = upload_to_drive(service, uploaded_file.name, temp_file_path, FOLDER_ID)
    #    st.success(f"File caricato su Google Drive con successo! ID del file: {file_id}")
        
    # Trascrivi il file tramite n8n
    #with st.spinner("Trascrizione in corso tramite n8n..."):
    #    transcription = get_transcription_from_n8n(temp_file_path)
    #    st.text_area("Trascrizione", transcription, height=300)

        # Rimuovi il file locale temporaneo
        #os.remove(temp_path)
