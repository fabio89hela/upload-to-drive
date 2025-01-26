import streamlit as st
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import tempfile
import os
import ffmpeg
from upload_handler import authenticate_drive, upload_to_drive

# Configurazione di Streamlit
st.set_page_config(page_title="Registrazione Audio con Streamlit", layout="centered")
st.title("Registrazione Audio con Streamlit")

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


# Funzione per convertire un file in formato OGG
def convert_to_ogg(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(
            output_path,
            acodec="libopus",  # Codec per OGG
            audio_bitrate="128k",
            format="ogg"
        ).run(overwrite_output=True)
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione in OGG: {e.stderr.decode()}")
        return False
    return True


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
