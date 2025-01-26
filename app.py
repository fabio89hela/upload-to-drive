import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
from audio_recorder import get_audio_recorder_html
import requests
import ffmpeg 
import tempfile
import base64
import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
import wave

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
    """
    Converte un file audio in formato OGG.
    Args:
        input_path (str): Percorso del file di input.
        output_path (str): Percorso per il file convertito.
    Returns:
        bool: True se la conversione ha successo, False in caso contrario.
    """
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

# Variabili globali
duration = st.slider("Durata della registrazione (in secondi):", min_value=1, max_value=60, value=5)
sample_rate = 44100  # Frequenza di campionamento (44.1 kHz)

# Funzione per registrare l'audio
def record_audio(duration, sample_rate):
    """
    Registra audio per una durata specificata e restituisce i dati audio e il sample rate.
    """
    st.info("Registrazione in corso...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float64")
    sd.wait()  # Aspetta che la registrazione finisca
    st.success("Registrazione completata!")
    return audio_data

# Funzione per salvare l'audio in un file WAV temporaneo
def save_audio(audio_data, sample_rate):
    """
    Salva i dati audio in un file WAV temporaneo.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_file.name, "w") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 byte per campione
        wf.setframerate(sample_rate)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
    return temp_file.name

# Funzione per disegnare l'onda audio
def plot_waveform(audio_data, sample_rate):
    """
    Disegna l'onda audio usando matplotlib.
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    time = np.linspace(0, len(audio_data) / sample_rate, num=len(audio_data))
    ax.plot(time, audio_data, color="blue")
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Ampiezza")
    ax.set_title("Onda Audio")
    st.pyplot(fig)
    
# Configura la pagina
st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
)

# Layout della pagina
st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=200)

# Titolo dell'app Streamlit
st.title("Carica un file già registrato")

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
    audio_data = record_audio(duration, sample_rate)
    audio_data = audio_data.flatten()  # Trasforma in array 1D
    plot_waveform(audio_data, sample_rate)  # Mostra l'onda audio

    # Salva l'audio in un file temporaneo
    temp_wav_path = save_audio(audio_data, sample_rate)
    st.audio(temp_wav_path, format="audio/wav")

    # Conversione in OGG
    st.info("Convertendo in formato OGG...")
    temp_ogg_path = temp_wav_path.replace(".wav", ".ogg")
    os.system(f"ffmpeg -i {temp_wav_path} -c:a libopus {temp_ogg_path}")
    st.success("Conversione completata!")

    # Mostra il file convertito
    with open(temp_ogg_path, "rb") as f:
        st.download_button("Scarica il file audio in formato OGG", f, file_name="registrazione.ogg")
            
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
