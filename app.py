import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
from audio_recorder import get_audio_recorder_html
import requests
import ffmpeg 
import tempfile

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
    # Endpoint personalizzato per ricevere i file audio
    if "upload-audio" not in st.session_state:
        from flask import Flask, request, jsonify

        app = Flask(__name__)

        @app.route('/upload-audio', methods=['POST'])
        def upload_audio():
            if 'file' not in request.files:
                return jsonify({'error': 'No file part in the request'}), 400

            audio_file = request.files['file']
            if audio_file.filename == '':
                return jsonify({'error': 'No file selected for uploading'}), 400

            # Salva il file in una directory temporanea
            temp_path = os.path.join(tempfile.gettempdir(), audio_file.filename)
            audio_file.save(temp_path)

            return jsonify({'status': 'success', 'file_path': temp_path}), 200

        st.session_state["upload-audio"] = app

    # Interfaccia per registrare l'audio
    st.components.v1.html(get_audio_recorder_html(), height=400)

    # Mostra il file registrato
    audio_file_path = st.query_params.get("audio_file_path", [None])[0]

    if audio_file_path:
        st.success(f"File audio salvato: {audio_file_path}")
        st.audio(audio_file_path, format="audio/wav")
    else:
        st.warning("Nessun file audio registrato trovato.")
    
    st.warning("Dopo la registrazione, premi STOP e aspetta che il file venga salvato.")
    if st.button("Carica file registrato su Google Drive"):
        response = st.query_params.get("audio_file_path", [None])[0]
        if response:
            input_path = response

            # Percorso per il file convertito
            with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
                output_path = temp_ogg_file.name

            # Conversione in OGG
            if convert_to_ogg(input_path, output_path):
                # Carica su Google Drive
                file_id = authenticate_and_upload("recorded_audio.ogg", output_path)
                st.success(f"File caricato su Google Drive con ID: {file_id}")
            else:
                st.error("Impossibile completare la conversione.")
        else:
            st.error("Nessun file registrato trovato.")

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
