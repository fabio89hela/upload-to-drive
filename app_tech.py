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
import base64

if "avvio" not in st.session_state:
    st.session_state["avvio"]=True
if "selezione1" not in st.session_state:
    st.session_state["selezione1"]=0
if "selezione2" not in st.session_state:
    st.session_state["selezione2"]=0
if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"]=None
if "uploaded_file2" not in st.session_state:
    st.session_state["uploaded_file2"]=None
if "ricomincia" not in st.session_state:
    st.session_state["ricomincia"]=False
if "file_upload_ids" not in st.session_state:
    st.session_state["file_upload_ids"] = []
if "transcription" not in st.session_state:
    st.session_state["transcription"]=""
if "transcription_saved" not in st.session_state:
    st.session_state["transcription_saved"] = False
if "transcription_text1" not in st.session_state:
    st.session_state["transcription_text1"]=""
if "salvato1" not in st.session_state:
    st.session_state["salvato1"]=False
if "data_fo" not in st.session_state:
    st.session_state["data_fo"]=None
if "completa_survey" not in st.session_state:
    st.session_state["completa_survey"]="FALSE"
if "vettore_opzioni" not in st.session_state:
    st.session_state["vettore_opzioni"]=["Carica un file", "Registra un nuovo audio"]

#N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook-test/trascrizione" #test link
N8N_WEBHOOK_URL = "https://develophela.app.n8n.cloud/webhook/trascrizione" #production link
c,FOLDER_ID,domanda_note,domanda1,domanda2,domanda3,domande_intervista=settings_folder("Ematologia")

def is_valid_media(input_path):
    try:
        info = ffmpeg.probe(input_path)
        return True
    except ffmpeg.Error as e:
        st.error(f"Il file non è leggibile da ffmpeg: {e.stderr.decode() if e.stderr else str(e)}")
        return False

def convert_webm_to_wav(input_path, wav_path):
    try:
        # Prima verifica che ffmpeg riesca a leggere il file
        if not is_valid_media(input_path):
            return False

        # Conversione con formato e codec forzato
        ffmpeg.input(input_path, format='webm').output(
            wav_path,
            format='wav',
            acodec='pcm_s16le'
        ).run(overwrite_output=True)
        return True

    except ffmpeg.Error as e:
        st.error(f"Errore nella conversione da WEBM a WAV: {e.stderr.decode() if e.stderr else str(e)}")
        return False


def convert_to_ogg(input_path, output_path):
    try:
        ext = os.path.splitext(input_path)[-1].lower()

        # Se è un file webm, convertilo prima in wav
        if ext == ".webm":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                wav_path = temp_wav.name

            if not convert_webm_to_wav(input_path, wav_path):
                return False  # Fallita la conversione da webm a wav

            input_path = wav_path  # Sovrascrivi l'input con il path WAV

        # Ora esegui la conversione in OGG
        ffmpeg.input(input_path).output(
            output_path,
            acodec="libopus",
            audio_bitrate="192k",
            format="ogg"
        ).run(overwrite_output=True)

        return True

    except ffmpeg.Error as e:
        st.error(f"Errore durante la conversione in OGG: {e.stderr.decode() if e.stderr else str(e)}")
        return False


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

#def convert_to_ogg(input_path, output_path):
#    try:
#        ffmpeg.input(input_path).output(
#            output_path,
#            acodec="libopus",  # Codec per OGG
#            audio_bitrate="192k",
#            format="ogg"
#        ).run(overwrite_output=True)
#        return True
#    except ffmpeg.Error as e:
#        st.error(f"Errore durante la conversione in OGG: {e}")
#        return False

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
    st.session_state["salvato1"]=False
    st.session_state["data_fo"]=None
    st.rerun()
    return True

def get_javascript_value(js_code,testo_key):
    value = st_javascript(js_code,key=testo_key)
    return value if value is not None else ""

def salva_testo_drive(transcription_content,temp_name_personalised):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_text_file:
        temp_text_file.write(transcription_content.encode('utf-8'))
        temp_text_file_path = temp_text_file.name
        file_name = f"Trascrizione_{temp_name_personalised}.txt"
        try:
            file_id = authenticate_and_upload(file_name, temp_text_file_path)
            st.success(f"Salvataggio completato")
        except Exception as e:
            st.error(f"Errore durante il salvataggio su Google Drive: {e}")
    return file_id
            
st.set_page_config(
    page_title="T-EMA App",
    page_icon="https://t-ema.it/favicon.ico",
    layout="wide",
)

col_sn,col_cnt,col_dx=st.columns([2,3,1])
with col_cnt:
    st.image("https://t-ema.it/wp-content/uploads/2022/08/LOGO-TEMA-MENU.png", width=400)
    st.markdown('#')
col1,col2,col3,col4=st.columns(4)

with col2:
    #cartella=st.radio("Tema di riferimento:",["Ematologia","Emofilia","Oncoematologia"],index=st.session_state["selezione2"],disabled=st.session_state["ricomincia"])
    cartella=st.radio("Tema di riferimento:",["Ematologia","Emofilia","Oncoematologia"],index=st.session_state["selezione2"])
    if cartella=="Emofilia":
        st.session_state["selezione2"]=1
    elif cartella=="Oncoematologia":
        st.session_state["selezione2"]=2
    else:
        st.session_state["selezione2"]=0
    c,FOLDER_ID,domanda_note,domanda1,domanda2,domanda3,domande_intervista=settings_folder(cartella)
with col1:
    if not st.session_state["data_fo"]:
        gc = get_gsheet_connection()
        SHEET_ID = "1WmImKIOs20FjqSBUHgQkr5tltEWlxHJosCEOEZMI_HQ"  
        sh = gc.open_by_key(SHEET_ID)
        worksheet = sh.sheet1
        st.session_state["data_fo"] = worksheet.get_all_values()
    data_fo=st.session_state["data_fo"]
    df = pd.DataFrame(data_fo[1:], columns=data_fo[0])
    regional=df.loc[df["Specializzazione"] == c, "Label"].tolist()
    nome=df["Abbreviazione"].tolist()
    #if st.button("Riavvia",disabled=not(st.session_state["ricomincia"])):
    #    a=riavvia(0,False)
with col3:
    #if st.session_state["completa_survey"]=="TRUE":
        #st.session_state["vettore_opzioni"]=["Carica un file", "Registra un nuovo audio","Completa Fase 1"]
        #st.session_state["selezione1"]=2
    #else:
        #st.session_state["vettore_opzioni"]=["Carica un file", "Registra un nuovo audio"]
        #st.session_state["selezione1"]=0
    #mode = st.radio("Scegli un'opzione:", st.session_state["vettore_opzioni"],index=st.session_state["selezione1"],disabled=st.session_state["ricomincia"])
    mode = st.radio("Scegli un'opzione:", ["Carica un file", "Registra un nuovo audio"],index=st.session_state["selezione1"])
    if mode=="Registra un nuovo audio":
        st.session_state["selezione1"]=1
    elif mode=="Carica un file":
        st.session_state["selezione1"]=0
    #else:
    #    st.session_state["selezione1"]=2

col_left,col_center,col_right=st.columns([0.5,4,0.5])

with col_center:
    regional_list=regional+["Altro"]
    fo_lungo=st.selectbox("Nome del farmacista intervistato",regional_list,index=len(regional_list)-2)
    if fo_lungo=="Altro":
        fo_lungo=st.text_input("Farmacista",placeholder="Nome Cognome")
        ruolo=st.text_input("Ruolo")
        if st.button("Aggiungi farmacista"):
            try:
                if fo_lungo and ruolo:
                    worksheet.append_row([fo_lungo, ruolo,c,'TRUE'])  
                    st.session_state["data_fo"] = worksheet.get_all_values()
                    st.rerun()
                else:
                    st.error("Inserisci tutti i campi!")
            except:
                gc = get_gsheet_connection()
                SHEET_ID = "1WmImKIOs20FjqSBUHgQkr5tltEWlxHJosCEOEZMI_HQ"  
                sh = gc.open_by_key(SHEET_ID)
                worksheet = sh.sheet1
                st.session_state["data_fo"] = worksheet.get_all_values()    
                if fo_lungo and ruolo:
                    worksheet.append_row([fo_lungo, ruolo,c,'TRUE'])  
                    st.session_state["data_fo"] = worksheet.get_all_values()
                    st.rerun()
                else:
                    st.error("Inserisci tutti i campi!")
    else:
        fo=df.loc[df["Label"] == fo_lungo, "Abbreviazione"].tolist()
        fo=fo[0]
        completa_survey=df.loc[df["Label"]==fo_lungo,"Surveymonkey"].tolist()
        if completa_survey[0]!=st.session_state["completa_survey"]:
            st.session_state["completa_survey"]=completa_survey[0]
            #if st.session_state["completa_survey"]=="TRUE":
            #    st.session_state["vettore_opzioni"]=["Carica un file", "Registra un nuovo audio","Completa Fase 1"]
            #    st.session_state["selezione1"]=2
            #else:
            #    st.session_state["vettore_opzioni"]=["Carica un file", "Registra un nuovo audio"]
            #    st.session_state["selezione1"]=0
            st.rerun()
        data_valore=st.date_input("Data dell'intervista", value="today",format="DD/MM/YYYY")
        now = datetime.now()
        data=data_valore.strftime("%Y-%m-%d")+"_"+now.strftime("%H-%M-%S")
        if st.session_state["completa_survey"]=="TRUE":
            st.warning("Attenzione: serve completare anche la fase 1, le cui domande sono riportate per ultime.")
            #st.session_state["selezione1"]=2

    if mode == "Carica un file":
        file_ids=[]
        if =st.radio("Cosa vuoi caricare?",["Audio","Testo"])=="Audio":
            # Caricamento di un file audio locale
            st.session_state["uploaded_file"] = st.file_uploader("Carica un file audio (WAV, WEBM o MP3)", type=["wav","webm","mp3"])
            if st.session_state["uploaded_file"]:
                if st.session_state["ricomincia"]==False:
                    st.session_state["ricomincia"]=True
                    st.session_state["uploaded_file"]=None
                    st.session_state["avvio"]=True
                    st.rerun()
                with st.spinner("Caricando..."):
                    ext = st.session_state["uploaded_file"].name.split('.')[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
                    #with tempfile.NamedTemporaryFile(delete=False, suffix=f".{st.session_state["uploaded_file"].name.split('.')[-1]}") as temp_file:
                        temp_file.write(st.session_state["uploaded_file"].getbuffer())
                        input_path = temp_file.name

                    # Percorso per il file convertito
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
                        output_path = temp_ogg_file.name
        
                    # Conversione in OGG
                    if convert_to_ogg(input_path, output_path):
                        # Carica su Google Drive
                        temp_name_personalised=c+"_"+data+"_"+fo+".ogg"
                        temp_name_personalised_noogg=c+"_"+data+"_"+fo
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
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_text_file:
                                temp_text_file.write(transcription_content.encode('utf-8'))
                                temp_text_file_path = temp_text_file.name
                            file_name = f"Trascrizione_{temp_name_personalised_noogg}.txt"
                            try:
                                file_id = authenticate_and_upload(file_name, temp_text_file_path)
                                st.success(f"Salvataggio completato")
                            except Exception as e:
                                st.error(f"Errore durante il salvataggio su Google Drive: {e}")
        else:
            # Caricamento di un file txt
            st.session_state["uploaded_file2"] = st.file_uploader("Carica un file di testo (TXT, DOC o DOCX)", type=["txt","doc","docx"])
            if st.session_state["uploaded_file2"]:
                with st.spinner("Caricando..."):
                    ext = st.session_state["uploaded_file2"].name.split('.')[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
                        temp_file.write(st.session_state["uploaded_file2"].getbuffer())
                        input_path = temp_file.name

                    # Percorso per il file convertito
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as temp_ogg_file:
                        output_path = temp_ogg_file.name
        
                    if 1>0:
                        # Carica su Google Drive
                        temp_name_personalised=c+"_"+data+"_"+fo+".txt"
                        temp_name_personalised_noogg=c+"_"+data+"_"+fo
                        if st.button("Salva su Drive"):
                            file_ids = authenticate_and_upload(temp_name_personalised, output_path)
                            st.success("File caricato su Drive")

    elif mode == "Registra un nuovo audio":
        if st.session_state["ricomincia"]==False:
            st.session_state["ricomincia"]=True
            st.session_state["uploaded_file"]=None
            st.session_state["avvio"]=True
            st.rerun()

        with st.expander("Domande cui rispondere",expanded=not st.session_state["salvato1"]):
            domande=[domanda_note,domanda1,domanda2,domanda3]
            if st.session_state["completa_survey"]=="TRUE":
                domande=domande+domande_intervista
            n_canvas=len(domande)
            prev_timestamp = str(int(time.time() * 1000))
            components.html(get_audio_recorder_html(n_canvas,domande), height=600,scrolling=True)
            i=0
            with st.empty():
                while True:
                    i=i+1
                    timestamp = get_javascript_value("localStorage.getItem('update_time');","tempo_trascr1"+str(i)) 
                    if timestamp and timestamp > prev_timestamp:
                        transcription_text = get_javascript_value("localStorage.getItem('combined_transcriptions');","testo_trascr1"+str(i)) 
                        st.session_state["transcription_text1"]=str(transcription_text)
                        st.session_state["salvato1"]=True
                        break
                    #st.markdown("<p style="color:white;font-size:24px;">1</p>", unsafe_allow_html=True)
                    time.sleep(1)
            if st.session_state["salvato1"]==True:
                testo_da_salvare=st.session_state["transcription_text1"]
                temp_name_personalised1=c+"_"+data+"_"+fo
                if 1>0:
                    if testo_da_salvare.strip():
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_text_file:
                            temp_text_file.write(testo_da_salvare)
                            temp_text_file.flush()
                            temp_text_file_path = temp_text_file.name
                            file_name = f"Fase2_Domanda1_{temp_name_personalised1}.txt"
                            try:
                                file_id = authenticate_and_upload(file_name, temp_text_file_path)
                                st.success(f"Salvataggio completato")
                            except Exception as e:
                                st.error(f"Errore durante il salvataggio su Google Drive: {e}")
    
    elif mode=="Completa Fase 1": 
        if st.session_state["ricomincia"]==False:
            st.session_state["ricomincia"]=True
            st.session_state["uploaded_file"]=None
            st.session_state["avvio"]=True
            st.rerun()

        with st.expander("Intervista Fase 1",expanded=not st.session_state["salvato1"]):
            n_canvas=len(domande_intervista)
            domande=domande_intervista
            prev_timestamp = str(int(time.time() * 1000))
            components.html(get_audio_recorder_html(n_canvas,domande), height=600,scrolling=True)
            i=0
            with st.empty():
                while True:
                    i=i+1
                    timestamp = get_javascript_value("localStorage.getItem('update_time');","tempo_inter"+str(i)) 
                    if timestamp and timestamp > prev_timestamp:
                        transcription_text = get_javascript_value("localStorage.getItem('combined_transcriptions');","testo_inter"+str(i)) 
                        st.session_state["transcription_text1"]=str(transcription_text)
                        st.session_state["salvato1"]=True
                        break
                    time.sleep(1)
            if st.session_state["salvato1"]==True:
                testo_da_salvare=st.session_state["transcription_text1"]
                temp_name_personalised1=c+"_"+data+"_"+fo
                if 1>0:
                    if testo_da_salvare.strip():
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_text_file:
                            temp_text_file.write(testo_da_salvare)
                            temp_text_file.flush()
                            temp_text_file_path = temp_text_file.name
                            file_name = f"Fase2_Domanda1_{temp_name_personalised1}.txt"
                            try:
                                file_id = authenticate_and_upload(file_name, temp_text_file_path)
                                st.success(f"Salvataggio completato")
                            except Exception as e:
                                st.error(f"Errore durante il salvataggio su Google Drive: {e}")
