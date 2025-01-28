from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st
import os 
import io
import json
import requests
import ffmpeg 
import tempfile


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
        st.write("controllo dimensione ok")
        # Crea una directory temporanea per i segmenti
        with tempfile.TemporaryDirectory() as temp_dir:
            segment_prefix = file_name.rsplit('.', 1)[0]  # Nome base senza estensione
            segment_pattern = os.path.join(temp_dir, f"{segment_prefix}_%03d.ogg")
            # Usa ffmpeg per dividere il file in segmenti più piccoli
            segment_duration =600 #int((max_size_mb * 1024 * 1024) / (file_size_mb / 60))  # Durata stimata in secondi
            try:
                st.write(file_path)
                ffmpeg.input(file_path).output(
                    segment_pattern, f="segment", segment_time=segment_duration, c="copy"
                ).run(overwrite_output=True)
            except ffmpeg.Error as e:
                raise RuntimeError(f"Errore durante la suddivisione del file: {e.stderr.decode()}")
                st.error(f"{e.stderr.decode()}")
            # Carica ogni segmento su Google Drive
            st.write(os.listdir(temp_dir))
            for segment_file in sorted(os.listdir(temp_dir)):
                st.write(segment_file)
                if segment_file.startswith(segment_prefix) and segment_file.endswith(".ogg"):
                    segment_path = os.path.join(temp_dir, segment_file)
                    segment_metadata = {"name": segment_file, "parents": [folder_id]}
                    segment_media = MediaFileUpload(segment_path, resumable=True)
                    file = service.files().create(body=segment_metadata, media_body=segment_media, fields="id").execute()
                    uploaded_file_ids.append(file.get("id"))
                else:
                    st.write("siamo qui")
    else:
        # Carica il file intero se non supera il limite
        file_metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        uploaded_file_ids.append(file.get("id"))
    return uploaded_file_ids
