import os 
import io
import json
import streamlit as st
from upload_handler import authenticate_drive, upload_to_drive,get_gsheet_connection
from audio_recorder2 import get_audio_recorder_html
from settings_folder import settings_folder
import requests
import ffmpeg 
import tempfile
from datetime import datetime
import time
import pandas as pd
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript

if "avvio" not in st.session_state:
    st.session_state["avvio"]=True
if "selezione1" not in st.session_state:
    st.session_state["selezione1"]=0
if "selezione2" not in st.session_state:
    st.session_state["selezione2"]=0
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"]=None
if "ricomincia" not in st.session_state:
    st.session_state["ricomincia"]=False
if "file_upload_ids" not in st.session_state:
    st.session_state["file_upload_ids"] = []
if "transcription" not in st.session_state:
    st.session_state["transcription"]=""
if "transcription_saved" not in st.session_state:
    st.session_state["transcription_saved"] = False
if "transcription_text" not in st.session_state:
    st.session_state["transcription_text"]=""
if "salvato" not in st.session_state:
    st.session_state["salvato"]=False

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link
c,FOLDER_ID,domanda1,domanda2=settings_folder("Ematologia")
domande=[domanda1,domanda2]

def convert_mp3_to_wav(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(output_path, format="wav").run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione MP3 -> WAV: {e.stderr.decode()}")
        return False

def authenticate_and_upload(file_name, file_path):
    service = authenticate_drive()
    # Carica il file su Google Drive
    file_id = upload_to_drive(service, file_name, file_path, FOLDER_ID)
    return file_id

def convert_to_ogg(input_path, output_path):
    try:
        ffmpeg.input(input_path).output(
            output_path,
            acodec="libopus",  # Codec per OGG
            audio_bitrate="192k",
            format="ogg"
        ).run(overwrite_output=True)
        return True
    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione in OGG: {e.stderr.decode()}")
        return False

def get_transcriptions_from_n8n(file_id,nome,cartella):
    payload = {"file_id": file_id}
    payload["file_name"]=nome
    payload["folder"]=cartella
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        transcription = response.json().get("text", "Errore: nessuna trascrizione ricevuta.")
    else:
        transcription=(f"Errore: {response.status_code} - {response.text}")
    return transcription

def riavvia(selection,restart):
    st.session_state["ricomincia"]=restart
    st.session_state["transcription"]=""
    st.session_state["uploaded_file"]=None
    st.session_state["avvio"]=True
    st.session_state["selezione1"]=selection
    st.session_state["salvato"]
    st.rerun()
    return True

def get_javascript_value(js_code,testo_key):
    value = st_javascript(js_code,key=testo_key)
    return value if len(str(value))>1 else None

st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
)

# Layout della pagina
st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=200)

# Titolo dell'app Streamlit
st.title("Carica un file già registrato")

col1,col2,col3=st.columns(3)

with col3:
    # Scelta modalità: Caricamento o Registrazione
    mode = st.radio("Scegli un'opzione:", ["Carica un file audio", "Registra un nuovo audio"],index=st.session_state["selezione1"],disabled=st.session_state["ricomincia"])
    if mode=="Registra un nuovo audio":
        st.session_state["selezione1"]=1
    else:
        st.session_state["selezione1"]=0
with col2:
    cartella=st.radio("Tema di riferimento:",["Ematologia","Emofilia","Oncoematologia"],index=st.session_state["selezione2"],disabled=st.session_state["ricomincia"])
    if cartella=="Emofilia":
        st.session_state["selezione2"]=1
    elif cartella=="Oncoematologia":
        st.session_state["selezione2"]=2
    else:
        st.session_state["selezione2"]=0
    c,FOLDER_ID,domanda1,domanda2=settings_folder(cartella)
    domande=[domanda1,domanda2]
with col1:
    gc = get_gsheet_connection()
    SHEET_ID = "1WmImKIOs20FjqSBUHgQkr5tltEWlxHJosCEOEZMI_HQ"  
    sh = gc.open_by_key(SHEET_ID)
    worksheet = sh.sheet1
    data_fo = worksheet.get_all_values()
    df = pd.DataFrame(data_fo[1:], columns=data_fo[0])
    regional=df.loc[df["Specializzazione"] == c, "Label"].tolist()
    nome=df["Abbreviazione"].tolist()
    if st.button("Riavvia",disabled=not(st.session_state["ricomincia"])):
        a=riavvia(0,False)

if mode == "Carica un file audio":
    file_ids=[]
    # Scelta farmacista e data
    regional_list=regional+["Altro"]
    fo_lungo=st.selectbox("Nome del farmacista intervistato",regional_list,index=len(regional_list)-2)
    if fo_lungo=="Altro":
        fo_lungo=st.text_input("Specificare")
        ruolo=st.text_input("Ruolo")
        if st.button("Aggiungi farmacista"):
            if fo_lungo and ruolo:
                worksheet.append_row([fo_lungo, ruolo,c])  
                st.rerun()
            else:
                st.error("Inserisci tutti i campi!")
    else:
        fo=df.loc[df["Label"] == fo_lungo, "Abbreviazione"].tolist()
        fo=fo[0]
        data_valore=st.date_input("Data dell'intervista", value="today",format="DD/MM/YYYY")
        now = datetime.now()
        data=data_valore.strftime("%Y-%m-%d")+"_"+now.strftime("%H-%M-%S")
        # Caricamento di un file audio locale
        st.session_state["uploaded_file"] = st.file_uploader("Carica un file audio (WAV o MP3)", type=["wav","mp3"])
        if st.session_state["uploaded_file"]:
            if st.session_state["ricomincia"]==False:
                st.session_state["ricomincia"]=True
                st.session_state["uploaded_file"]=None
                st.session_state["avvio"]=True
                st.rerun()
            with st.spinner("Caricando..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{st.session_state["uploaded_file"].name.split('.')[-1]}") as temp_file:
                    temp_file.write(st.session_state["uploaded_file"].getbuffer())
                    input_path = temp_file.name

                # Percorso per il file convertito
                with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
                    output_path = temp_ogg_file.name
        
                # Conversione in OGG
                if convert_to_ogg(input_path, output_path):
                    # Carica su Google Drive
                    temp_name_personalised=c+"_"+data+"_"+fo+".ogg"
                    if st.button("Salva su Drive"):
                        file_ids = authenticate_and_upload(temp_name_personalised, output_path)
                        st.session_state["file_upload_ids"]=file_ids
                        st.success("File caricato su Drive")
                        st.session_state["avvio"]=False
                if st.button("Trascrivi il file caricato",disabled=st.session_state["avvio"]):
                        file_ids=st.session_state["file_upload_ids"]
                        if file_ids:
                            transcriptions=[]
                            # Itera su ciascun ID del file
                            for file_id in file_ids:
                                transcription=get_transcriptions_from_n8n(file_id,c+"_"+data+"_"+fo+".txt",FOLDER_ID)
                                transcriptions.append(transcription)
                        else:
                            st.error("Inserisci almeno un ID file per procedere.")       
                        combined_transcription = "\n".join(transcriptions)
                        st.session_state["transcription"] = combined_transcription
                        st.session_state["transcription_saved"] = False
        if st.session_state["transcription"]:
            with st.form(key="save_transcription_form"):
                    st.subheader("Trascrizione:")
                    transcription_content = st.text_area("Puoi modificare la trascrizione prima di salvarla:", st.session_state["transcription"], height=300)
                    submit_button = st.form_submit_button("Salva la trascrizione su Google Drive")
                    if submit_button and not st.session_state["transcription_saved"]:
                        if transcription_content != st.session_state["transcription"]:
                            st.session_state["transcription"]=transcription_content
                        # Salva il contenuto temporaneamente come file di testo
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_text_file:
                            temp_text_file.write(transcription_content.encode('utf-8'))
                            temp_text_file_path = temp_text_file.name
                        # Carica il file su Google Drive
                        file_name = f"Trascrizione_{temp_name_personalised}.txt"
                        try:
                            file_id = authenticate_and_upload(file_name, temp_text_file_path)
                            st.success(f"Salvataggio completato")
                        except Exception as e:
                            st.error(f"Errore durante il salvataggio su Google Drive: {e}")

elif mode == "Registra un nuovo audio":
    if st.session_state["ricomincia"]==False:
        st.session_state["ricomincia"]=True
        st.session_state["uploaded_file"]=None
        st.session_state["avvio"]=True
        st.rerun()

    st.markdown(domanda1)
    n_canvas=3
    prev_timestamp = str(int(time.time() * 1000))
    components.html(get_audio_recorder_html(n_canvas), height=500,scrolling=True)
    i=0
    while True:
        i=i+1
        transcription_text = get_javascript_value("localStorage.getItem('combined_transcriptions');","testo_trascr"+str(i)) 
        timestamp = get_javascript_value("localStorage.getItem('update_time');","tempo_trascr"+str(i)) 
        #timestamp = get_javascript_value("""localStorage.getItem('update_time');""",key="tempo_trascr"+str(i)) 
        if timestamp and timestamp > prev_timestamp:
            st.session_state["transcription_text"]=transcription_text
            st.session_state["salvato"]=True
            break
        time.sleep(1)
    if st.session_state["salvato"]==True:
        st.text_area("prova",st.session_state["transcription_text"])
        st.success("Salvato")
    
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
                    transcription=get_transcriptions_from_n8n(file_id,"",FOLDER_ID)
                    transcriptions.append(transcription)
        else:
            st.error("Inserisci almeno un ID file per procedere.")
