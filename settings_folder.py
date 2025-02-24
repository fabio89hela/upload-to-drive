import streamlit as st 

def settings_folder(cartella):
  c=""
  FOLDER_ID=""
  domanda1=[]
  domanda2=[]
  if cartella=="Ematologia":
    c="Ematologia"
    FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"  
    domanda1="""
              <b>Impatto della presenza di Centri Hub/Spoke e modello erogativo/assistenziale</b><br><br>
              - Come viene coordinata l'erogazione di farmaci per l’ematologia tra centro Hub e centro Spoke, nella sua attuale esperienza?<br>
              - Considerando il caso in cui la diagnosi viene fatta in un Centro Hub e il farmaco ad alto costo viene erogato da un Centro Spoke o da una farmacia territoriale, è prevista una procedura ben definita tra i due Centri per poter condividere fabbisogni e consentire al Centro che dovrà prendere in carico il paziente di ricevere il budget necessario per avviare la terapia?<br>
                - Se sì, puoi descrivere il processo?<br>
              """
    domanda2="""
             <b>Gestione trasferimenti tra centri o tra regioni</b><br><br>
             - Quali sono le procedure attuali per gestire i trasferimenti dei pazienti come indicato?<br>
             - Ci sono dei protocolli specifici per garantire la continuità delle cure durante un trasferimento di residenza<br>
             - Quali sono le principali sfide incontrate nella gestione dei trasferimenti dei pazienti?<br>
             """
    domanda3="""
             <b>Altre considerazioni</b><br><br>
             - Ci sono iniziative in corso o pianificate per migliorare l'integrazione e la collaborazione tra i diversi centri? <br>
             - Quali sono le tecnologie o strumenti che facilitano la gestione dei pazienti e la comunicazione tra i centri? <br>
             """
  elif cartella=="Emofilia":
    c="Emofilia"
    FOLDER_ID = "1CH9Pw0ZoWFFF2gSlOEo9UVa45akAgrz-"  
    domanda1="""
              <b>Prescrizione dei farmaci</b><br><br>
              - Come viene gestito e tracciato il flusso dell’erogazione dei farmaci off-label per le malattie rare nella vostra azienda ospedaliera o territoriale/locale per garantire l'appropriatezza delle prescrizioni? <br>
              """
    domanda2="""
              <b>Erogazione e approvvigionamento</b><br><br>
              - Come gestite l'urgenza di erogazione dei farmaci per pazienti con malattie rare?<br>
              - Quali sono le principali barriere burocratiche e amministrative che influenzano l'erogazione tempestiva dei farmaci?<br>
              - Quanto è efficiente il flusso di comunicazione tra il farmacista ospedaliero e quello territoriale in relazione alle necessità dei pazienti con malattie rare? <br>
              """
    domanda3="""
              <b>Erogazione e approvvigionamento</b><br><br>
              - Come avviene il flusso di comunicazione quando centro e farmacia territoriale appartengono a regioni diverse? <br>
              - Esistono piattaforme o sistemi informatici che facilitano la comunicazione e il coordinamento tra i diversi stakeholders coinvolti nella cura delle malattie rare?  <br>
              - Avete suggerimenti specifici per migliorare la procedura di prescrizione ed erogazione dei farmaci per le malattie rare? Se si, quali? <br>
              - Quali innovazioni o miglioramenti tecnologici potrebbero facilitare la gestione dei farmaci per le malattie rare? <br>
              """
  else:
    c="Oncoematologia"
    FOLDER_ID = "15FhRa5wa7zxNEN4GyGzJKtwc6q7jK2rR"  
    domanda1="""
              <b>Creazione di mini-network (rete di Centri che trattano patologie analoghe in un’area geografica limitata)</b><br><br>
              - Quali sarebbero i vantaggi della creazione di mini-network di area dedicati alla gestione dei farmaci per le malattie rare? <br>
                - Come dovrebbe essere strutturato un mini-network di area dedicato per ottimizzare l'erogazione dei farmaci?<br>
              - Quali sono le pratiche di formazione e sensibilizzazione del personale sanitario per evitare sprechi nella gestione dei farmaci per le malattie rare?<br>
                - Avete ricevuto suggerimenti pratici dal personale sanitario che potrebbero essere implementati?<br>
              """
    domanda2="""
              <b>Mininetwork e ottimizzazione tecnologica e pratica</b><br><br>
              - Quali tecnologie vengono attualmente utilizzate per migliorare l'efficienza nella gestione dei farmaci per le malattie rare?<br>
                - In che modo l'adozione di nuove tecnologie potrebbe contribuire a ridurre gli sprechi e ottimizzare le procedure di erogazione?<br>
              """
    domanda3="""
              <b>Esempi di efficientamento</b><br><br>
              - E’ in grado di fornirci un esempio di efficientamento di processo che potrebbe essere implementato per migliorare la gestione dei farmaci infusivi per le malattie rare? <br>
                - Esistono collaborazioni con altre strutture per condividere e implementare queste misure di efficientamento? Quali?<br>
              """    
  return c,FOLDER_ID,domanda1,domanda2,domanda3
