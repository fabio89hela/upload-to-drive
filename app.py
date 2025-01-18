import json
import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Funzione per autenticare PyDrive2
def authenticate_pydrive():
    # Crea una copia delle credenziali dai segreti di Streamlit
    creds = dict(st.secrets["gdrive_service_account"])

    # Assicurati che la chiave privata sia formattata correttamente
    creds["private_key"] = creds["private_key"].replace("\\n", "\n")

    # Scrivi il file delle credenziali client_secrets.json
    with open("client_secrets.json", "w") as f:
        json.dump(creds, f)

    # Configura PyDrive2 utilizzando settings.yaml
    gauth = GoogleAuth(settings_file="settings.yaml")
    gauth.LocalWebserverAuth()  # Avvia l'autenticazione
    return GoogleDrive(gauth)

# Autenticazione PyDrive
drive = authenticate_pydrive()

# ID della cartella Google Drive dove salvare i file (da sostituire con il tuo Folder ID)
FOLDER_ID = "INSERISCI_LA_TUA_FOLDER_ID"

# Titolo dell'app Streamlit
st.title("Carica e salva file audio su Google Drive")

# Caricamento del file da parte dell'utente
uploaded_file = st.file_uploader("Carica un file audio", type=["mp3", "wav", "ogg"])

if uploaded_file:
    st.write(f"File caricato: {uploaded_file.name}")
    
    # Salva temporaneamente il file caricato
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Carica il file su Google Drive
    with st.spinner("Caricamento su Google Drive in corso..."):
        file_drive = drive.CreateFile({"title": uploaded_file.name, "parents": [{"id": FOLDER_ID}]})
        file_drive.SetContentFile(uploaded_file.name)
        file_drive.Upload()
        st.success(f"File caricato con successo su Google Drive: {uploaded_file.name}")

        # Rimuovi il file locale
        os.remove(uploaded_file.name)

# Mostra i file esistenti nella cartella su Google Drive (opzionale)
if st.button("Mostra file salvati su Google Drive"):
    file_list = drive.ListFile({"q": f"'{FOLDER_ID}' in parents and trashed=false"}).GetList()
    if file_list:
        st.write("File nella cartella Google Drive:")
        for file in file_list:
            st.write(f"{file['title']} - ID: {file['id']}")
    else:
        st.write("Nessun file trovato nella cartella.")
