import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive
from audio_recorder import get_audio_recorder_html
from settings_folder import settings_folder
import requests
import ffmpeg 
import tempfile
from datetime import datetime

if "file_uploaded" not in st.session_state:
    st.session_state["file_uploaded"] = []
if "transcription" not in st.session_state:
    st.session_state["transcription"]=""
if "transcription_saved" not in st.session_state:
    st.session_state["transcription_saved"] = False

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link
c,FOLDER_ID,regional,nome,domanda1,domanda2=settings_folder("Ematologia")

def convert_mp3_to_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, format="wav").run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione MP3 -> WAV: {e.stderr.decode()}")
        return False

# Autenticazione Google Drive
def authenticate_and_upload(file_name, file_path):
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
    payload["prompt"]="Trascrivi la riunione e fanne una sintesi"
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

col1,col2=st.columns(2)

with col2:
    # Scelta modalità: Caricamento o Registrazione
    mode = st.radio("Scegli un'opzione:", ["Carica un file audio", "Registra un nuovo audio"])
with col1:
    cartella=st.radio("Tema di riferimento:",["Ematologia","Emofilia","Oncoematologia"])
    c,FOLDER_ID,regional,nome,domanda1,domanda2=settings_folder(cartella)

if mode == "Carica un file audio":
    # Scelta farmacista e data
    fo_lungo=st.selectbox("Nome del farmacista intervistato",regional)
    fo=nome[fo_lungo]
    #fo=st.text_input("Indica il nome del farmacista intervistato", value="")
    data_valore=st.date_input("Data dell'intervista", value="today",format="DD/MM/YYYY")
    now = datetime.now()
    data=data_valore.strftime("%Y-%m-%d")+"_"+now.strftime("%H-%M-%S")
    
    # Caricamento di un file audio locale
    uploaded_file = st.file_uploader("Carica un file audio (MP3, WAV)", type=["mp3", "wav"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            input_path = temp_file.name

        # Percorso per il file convertito
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
            output_path = temp_ogg_file.name

        if convert_mp3_to_wav(input_path, output_path):
            a=1
            #st.success("Conversione completata con successo!")
        
        # Conversione in OGG
        if convert_to_ogg(input_path, output_path):
            # Carica su Google Drive
            temp_name_personalised=c+"_"+data+"_"+fo+".ogg"
            if not st.session_state["file_uploaded"]:
                file_ids = authenticate_and_upload(temp_name_personalised, output_path)
                st.session_state["file_uploaded"]=file_ids
            st.success(f"File caricato su Google Drive")
            if st.button("Trascrivi il file caricato"):
                file_ids=st.session_state["file_uploaded"]
                if file_ids:
                    transcriptions=[]
                    # Itera su ciascun ID del file
                    with st.spinner("Esecuzione della trascrizione..."):
                        for file_id in file_ids:
                            transcription=get_transcriptions_from_n8n(file_id)
                            transcriptions.append(transcription)
                else:
                    st.error("Inserisci almeno un ID file per procedere.")       
                combined_transcription = "\n".join(transcriptions)
                st.session_state["transcription"] = combined_transcription
                st.session_state["transcription_saved"] = False
                with st.form(key="save_transcription_form"):
                    submit_button = st.form_submit_button("Salva la trascrizione su Google Drive")
                    if submit_button and not st.session_state["transcription_saved"]:
                        transcription_content = st.session_state["transcription"]
                        transcription_content = st.text_area("Trascrizione:", transcription_content, height=600)
                        # Salva il contenuto temporaneamente come file di testo
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_text_file:
                            temp_text_file.write(transcription_content.encode('utf-8'))
                            temp_text_file_path = temp_text_file.name
                        # Carica il file su Google Drive
                        file_name = f"Trascrizione_{temp_name_personalised}.txt"
                        try:
                            file_id = authenticate_and_upload(file_name, temp_text_file_path)
                            st.success(f"File della trascrizione salvato correttamente su Google Drive con ID: {file_id}")
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio su Google Drive: {e}")
        else:
            st.error("Impossibile completare la conversione in ogg.")

elif mode == "Registra un nuovo audio":
    with st.expander("Sezione 1"):
        st.markdown(domanda1)
        st.components.v1.html(get_audio_recorder_html(), height=500)
    with st.expander("Sezione 2"):
        st.markdown(domanda2)
        st.components.v1.html(get_audio_recorder_html(), height=500)

elif mode=="Trascrivi": 
    # Elenca i file nella cartella
    if os.path.exists("https://drive.google.com/drive/folders/"+FOLDER_ID):
        audio_files = [f for f in os.listdir(FOLDER_ID) if f.endswith(('.ogg'))]
        if audio_files:
            st.title("File caricati")
            selected_file = st.selectbox("Seleziona un file audio", audio_files)

            # Mostra il nome del file selezionato
            st.write(f"Hai selezionato: {selected_file}")

            # Riproduci l'audio selezionato
            file_path = os.path.join(FOLDER_ID, selected_file)
            with open(file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format="audio/wav" if selected_file.endswith(".wav") else "audio/mp3")
        else:
            st.warning("Nessun file audio trovato nella cartella.")
    else:
        st.error(f"La cartella {FOLDER_ID} non esiste. Creala e aggiungi file audio.")   
        # Pulsante per avviare la trascrizione
        if 1<0:#file_ids:
            transcriptions=[]
            # Itera su ciascun ID del file
            with st.spinner("Esecuzione della trascrizione..."):
                for file_id in file_ids:
                    st.success(f"trascrivendo {file_id}")
                    transcription=get_transcriptions_from_n8n(file_id)
                    transcriptions.append(transcription)
        else:
            st.error("Inserisci almeno un ID file per procedere.")
