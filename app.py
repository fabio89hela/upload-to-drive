import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json

# Configurazione e autenticazione PyDrive
def authenticate_pydrive():
    # Crea una copia del dizionario dei segreti
    creds = dict(st.secrets["gdrive_service_account"])

    # Assicurati che la chiave privata sia formattata correttamente
    creds["private_key"] = creds["private_key"].replace("\\n", "\n")

    # Scrivi le credenziali in un file temporaneo
    with open("client_secrets.json", "w") as f:
        json.dump(creds, f)

    # Configura PyDrive con il file temporaneo
    from pydrive2.auth import GoogleAuth
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile("client_secrets.json")
    gauth.LocalWebserverAuth()
    from pydrive2.drive import GoogleDrive
    return GoogleDrive(gauth)

# Autenticazione PyDrive
drive = authenticate_pydrive()

# Specifica la cartella Drive dove salvare i file (sostituisci con il tuo Folder ID)
FOLDER_ID = "INSERISCI_LA_TUA_FOLDER_ID"

# Titolo dell'app
st.title("Carica e salva file audio su Google Drive")

# Caricamento file da parte dell'utente
uploaded_file = st.file_uploader("Carica un file audio", type=["mp3", "wav", "ogg"])

if uploaded_file:
    st.write(f"Caricato: {uploaded_file.name}")
    
    # Salva temporaneamente il file caricato
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Carica il file su Google Drive
    with st.spinner("Caricamento su Google Drive..."):
        file_drive = drive.CreateFile({"title": uploaded_file.name, "parents": [{"id": FOLDER_ID}]})
        file_drive.SetContentFile(uploaded_file.name)
        file_drive.Upload()
        st.success(f"File caricato su Google Drive con successo: {uploaded_file.name}")

        # Rimuovi il file locale
        os.remove(uploaded_file.name)
