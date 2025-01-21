import os 
import io
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import ffmpeg 
import tempfile

# ID della cartella Google Drive dove salvare i file (sostituisci con il tuo Folder ID)
FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"

N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione"

# Funzione per autenticarsi con Google Drive
def authenticate_drive():
    # Creazione delle credenziali dai segreti di Streamlit
    creds = Credentials.from_service_account_info(st.secrets["gdrive_service_account"])
    service = build("drive", "v3", credentials=creds)
    return service

def upload_to_drive(service, file_name, file_path, folder_id, max_size_mb=20):
    # Controlla la dimensione del file
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Converti byte in MB
    # Lista degli ID dei file caricati
    uploaded_file_ids = []
    if file_size_mb > max_size_mb:
        # Crea una directory temporanea per i segmenti
        with tempfile.TemporaryDirectory() as temp_dir:
            segment_prefix = file_name.rsplit('.', 1)[0]  # Nome base senza estensione
            segment_pattern = os.path.join(temp_dir, f"{segment_prefix}_%03d.ogg")
            # Usa ffmpeg per dividere il file in segmenti più piccoli
            segment_duration =600 #int((max_size_mb * 1024 * 1024) / (file_size_mb / 60))  # Durata stimata in secondi
            try:
                ffmpeg.input(file_path).output(
                    segment_pattern, f="segment", segment_time=segment_duration, c="copy"
                ).run(overwrite_output=True)
            except ffmpeg.Error as e:
                raise RuntimeError(f"Errore durante la suddivisione del file: {e.stderr.decode()}")
            # Carica ogni segmento su Google Drive
            for segment_file in sorted(os.listdir(temp_dir)):
                if segment_file.startswith(segment_prefix) and segment_file.endswith(".ogg"):
                    segment_path = os.path.join(temp_dir, segment_file)
                    segment_metadata = {"name": segment_file, "parents": [folder_id]}
                    segment_media = MediaFileUpload(segment_path, resumable=True)
                    file = service.files().create(body=segment_metadata, media_body=segment_media, fields="id").execute()
                    uploaded_file_ids.append(file.get("id"))
    else:
        # Carica il file intero se non supera il limite
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        uploaded_file_ids.append(file.get("id"))
    return uploaded_file_ids

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
        transcription="Errore"#: {response.status_code} - {response.text}")
    return transcription
    
# Titolo dell'app Streamlit
st.title("Carica file audio su Google Drive")

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
    if 1>0:
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
