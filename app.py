import os
import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ID della cartella Google Drive dove salvare i file (sostituisci con il tuo Folder ID)
FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"

# Funzione per autenticarsi con Google Drive
def authenticate_drive():
    # Creazione delle credenziali dai segreti di Streamlit
    creds = Credentials.from_service_account_info(st.secrets["gdrive_service_account"])
    service = build("drive", "v3", credentials=creds)
    return service

# Funzione per caricare un file su Google Drive
def upload_to_drive(service, file_name, file_path, folder_id):
    # Metadati del file
    file_metadata = {"name": file_name, "parents": [folder_id]}
    # Caricamento del file
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    return file.get("id")

# Titolo dell'app Streamlit
st.title("Carica file audio su Google Drive")

# Autenticazione con Google Drive
service = authenticate_drive()

# Caricamento file da parte dell'utente
uploaded_file = st.file_uploader("Carica un file audio", type=["mp3", "wav", "ogg"])

if uploaded_file:
    st.write(f"File caricato: {uploaded_file.name}")

    # Salva temporaneamente il file localmente
    temp_file_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Carica il file su Google Drive
    with st.spinner("Caricamento su Google Drive in corso..."):
        file_id = upload_to_drive(service, uploaded_file.name, temp_file_path, FOLDER_ID)
        st.success(f"File caricato su Google Drive con successo! ID del file: {file_id}")

    # Rimuovi il file locale temporaneo
    os.remove(temp_file_path)
