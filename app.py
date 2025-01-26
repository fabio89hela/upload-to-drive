import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
import requests
import ffmpeg 
import tempfile
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link

# Autenticazione Google Drive
def authenticate_and_upload(file_name, file_path):
    FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"  # Cambia con l'ID della tua cartella Drive
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
            audio_bitrate="128k",
            format="ogg"
        ).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione in OGG: {e.stderr.decode()}")
        return False

# Funzione per inviare una lista di file a n8n e ricevere le trascrizioni
def get_transcriptions_from_n8n(file_id):
    payload = {"file_id": file_id}
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        transcription = response.json().get("text", "Errore: nessuna trascrizione ricevuta.")
    else:
        transcription=(f"Errore: {response.status_code} - {response.text}")
    return transcription

# Variabili globali per gestire la registrazione
is_recording = threading.Event()
audio_frames = []
samplerate = 44100


# Funzione per avviare la registrazione
def start_recording():
    global audio_frames
    audio_frames = []  # Reset delle tracce audio

    def callback(indata, frames, time, status):
        """Callback chiamato durante la registrazione."""
        if is_recording.is_set():
            audio_frames.append(indata.copy())

    # Configura lo stream audio
    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, dtype='float32'):
        while is_recording.is_set():  # Mantieni attivo lo stream finché `is_recording` è True
            sd.sleep(100)


# Funzione per fermare la registrazione
def stop_recording():
    is_recording.clear()  # Ferma la registrazione
    # Concatena tutti i frame in un unico array
    audio_data = np.concatenate(audio_frames, axis=0)
    return audio_data, samplerate  

# Configura la pagina
st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
)

# Layout della pagina
st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=200)

# Titolo dell'app Streamlit
st.title("Carica un file già registrato")

# Layout dell'interfaccia Streamlit
if st.button("Avvia Registrazione"):
    st.info("Registrazione in corso... premi Stop per fermare.")
    is_recording.set()
    threading.Thread(target=start_recording).start()  # Avvia la registrazione in un thread separato

if st.button("Stop"):
    if is_recording.is_set():  # Verifica che la registrazione sia in corso
        st.info("Fermando la registrazione...")
        audio_data, samplerate = stop_recording()

        # Salva il file WAV temporaneamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
            wav_path = temp_wav_file.name
            write(wav_path, samplerate, (audio_data * 32767).astype(np.int16))  # Salva come WAV

        # Percorso per il file convertito
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            ogg_path = temp_ogg_file.name

        # Conversione in OGG
        st.info("Convertendo il file in formato OGG...")
        if convert_to_ogg(wav_path, ogg_path):
            st.success("Conversione completata.")
            # Carica su Google Drive
            FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"  # Cambia con l'ID della tua cartella Drive
            service = authenticate_drive(st.secrets["gdrive_service_account"])
            file_id = upload_to_drive(service, "recorded_audio.ogg", ogg_path, FOLDER_ID)
            st.success(f"File caricato su Google Drive con ID: {file_id}")
        else:
            st.error("Errore durante la conversione.")

        # Pulizia dei file temporanei
        os.remove(wav_path)
        os.remove(ogg_path)
    else:
        st.warning("La registrazione non è attualmente in corso.")


# Scelta modalità: Caricamento o Registrazione
mode = st.radio("Scegli un'opzione:", ["Carica un file audio", "Registra un nuovo audio"])

if mode == "Carica un file audio":
    # Caricamento di un file audio locale
    uploaded_file = st.file_uploader("Carica un file audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            input_path = temp_file.name

        # Percorso per il file convertito
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            output_path = temp_ogg_file.name

        # Conversione in OGG
        st.info("Salvataggio file...")
        if convert_to_ogg(input_path, output_path):
            # Carica su Google Drive
            file_id = authenticate_and_upload("converted_audio.ogg", output_path)
            st.success(f"File caricato su Google Drive con ID: {file_id}")
        else:
            st.error("Impossibile completare la conversione in ogg.")

elif mode == "Registra un nuovo audio":
    if st.button("Avvia Registrazione"):
        st.info("Registrazione in corso... premi Stop per fermare.")
        recording_thread = threading.Thread(target=start_recording)
        recording_thread.start()

    if st.button("Stop"):
        st.info("Fermando la registrazione...")
        recorded_audio, samplerate = stop_recording()

        # Salva il file WAV temporaneamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
            wav_path = temp_wav_file.name
            write(wav_path, samplerate, (recorded_audio * 32767).astype(np.int16))  # Salva come WAV

        # Percorso per il file convertito
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            ogg_path = temp_ogg_file.name     

        # Conversione in OGG
        st.info("Convertendo il file in formato OGG...")
        if convert_to_ogg(wav_path, ogg_path):
            # Carica su Google Drive
            file_id = authenticate_and_upload("converted_audio.ogg", output_path)
            st.success(f"File caricato su Google Drive con ID: {file_id}")
        else:
            st.error("Impossibile completare la conversione in ogg.")

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
