import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Configurare PyDrive
def authenticate_pydrive():
    gauth = GoogleAuth(settings_file="settings.yaml")
    gauth.LocalWebserverAuth()
    return GoogleDrive(gauth)

# Autenticazione PyDrive
drive = authenticate_pydrive()

# Specificare la cartella Drive dove salvare i file
FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"

st.title("Carica e salva file audio su Google Drive")

uploaded_file = st.file_uploader("Carica un file audio", type=["mp3", "wav", "ogg"])

if uploaded_file:
    st.write(f"Caricato: {uploaded_file.name}")
    
    # Salva il file localmente (opzionale)
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Carica su Google Drive
    with st.spinner("Caricamento su Google Drive..."):
        file_drive = drive.CreateFile({"title": uploaded_file.name, "parents": [{"id": FOLDER_ID}]})
        file_drive.SetContentFile(uploaded_file.name)
        file_drive.Upload()
        st.success(f"File caricato su Google Drive con successo: {uploaded_file.name}")

        # Rimuovi il file locale (opzionale)
        os.remove(uploaded_file.name)
