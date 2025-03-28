import streamlit as st 

def settings_folder(cartella):
  c=""
  FOLDER_ID=""
  domanda1=[]
  domanda2=[]
  domande_intervista=[]
  domanda_note="""<b>Campo note: registra o scrivi eventuali note</b><br><br>"""
  if cartella=="Ematologia":
    c="Ematologia"
    FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"  
    domanda1="""
              <b>Domande Fase 2</b><br><br><b>Impatto della presenza di Centri Hub/Spoke e modello erogativo/assistenziale</b><br><br>
              - Come viene coordinata l'erogazione di farmaci per l’ematologia tra centro Hub e centro Spoke, nella sua attuale esperienza?<br>
              - Considerando il caso in cui la diagnosi viene fatta in un Centro Hub e il farmaco ad alto costo viene erogato da un Centro Spoke o da una farmacia territoriale, è prevista una procedura ben definita tra i due Centri per poter condividere fabbisogni e consentire al Centro che dovrà prendere in carico il paziente di ricevere il budget necessario per avviare la terapia?<br>
                - Se sì, puoi descrivere il processo?<br>"""
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
    domande_intervista=["""<b>Domande Fase 1</b><br><br>Nella sua regione/ASL di appartenenza è stato implementato un modello hub/spoke? Se no, riterrebbe utile implementare un modello hub/ spoke nella sua regione? <br>""",
      """Solo se ha risposto sì alla precedente domanda, quali vantaggi vede nella organizzazione Hub/Spoke?<br>""","""Quali potrebbero essere le aree di miglioramento?<br>""",
"""Quali sono le principali sfide associate alla gestione dei pazienti in un modello Hub/Spoke?<br>""","""Qual è il ruolo del farmacista ospedaliero nel modello Hub/Spoke e in particolare nel suo centro?<br>""",
"""Qual è il ruolo del farmacista territoriale nel modello Hub/Spoke e in particolare nella sua ASL di appartenenza?<br>""",
"""Relativamente alle patologie ematologiche, come ad esempio la trombocitopenia immune (ITP), il suo centro ha funzione di Hub o di Spoke? Come giudica la comunicazione esistente tra la sua ASL e i centri Hub o tra la sua ASL e i centri Spoke?<br>""",
"""Esistono dei Patient Support Program (PSP) attualmente attivi nel suo Centro? Se non sono attivi, perchè? (Non è necessario, non è possibile la dispensazione territoriale, il paziente ritira il farmaco direttamente nel Centro, non vi è la presenza di un centro Spoke, il centro ha specifiche caratteristiche che non ne permettono l'attivazione, ...)<br>""",
"""Se i PSP sono attivi, quanti di questi sono strutturati per le persone con malattie ematologiche?<br>
- Per quali patologie ematologiche sono stati implementati tali PSP? <br>
- Quali sono i principali obiettivi di tali PSP? <br>
- Come ne viene monitorata l'efficacia dal clinico e dal farmacista?<br>
- Qual è il feedback dei pazienti riguardo ai PSP e quali i principali problemi riportati?<br>""","""<b>Campo note: registra o scrivi eventuali note</b><br><br>"""]
            
  elif cartella=="Emofilia":
    c="Emofilia"
    FOLDER_ID = "1CH9Pw0ZoWFFF2gSlOEo9UVa45akAgrz-"  
    domanda1="""
              <b>Domande Fase 2</b><br><br><b>Prescrizione dei farmaci</b><br><br>
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
    domande_intervista=["""<b>Domande Fase 1</b><br><br>Qual è l'attuale procedura di erogazione e distribuzione dei farmaci per l’emofilia nella sua azienda ospedaliera o territoriale/locale? Esistono già pratiche standardizzate o modelli predefiniti da seguire per le malattie rare?<b>""", 
    """Quali sono le principali difficoltà nella gestione dei farmaci per le malattie rare, in particolare per l'emofilia, e quali passi sarebbero prioritari per implementare un modello di armonizzazione delle procedure a livello regionale o nazionale?<b>""",
    """Come viene utilizzato il Sistema Informativo Malattie Rare (SIMaRRP) e quale tipo di supporto offre? Quali sono i limiti di questo portale? <b>""",
    """Quali criteri utilizzate attualmente per la prescrizione dei farmaci LEA ed extra-LEA per le malattie rare? Quali criteri utilizzate per i dispositivi medici? <br>""",
                        """<b>Campo note: registra o scrivi eventuali note</b><br><br>"""]
  else:
    c="Oncoematologia"
    FOLDER_ID = "15FhRa5wa7zxNEN4GyGzJKtwc6q7jK2rR"  
    domanda1="""
              <b>Domande Fase 2</b><br><br><b>Creazione di mini-network (rete di Centri che trattano patologie analoghe in un’area geografica limitata)</b><br><br>
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
    domande_intervista=["""<b>Domande Fase 1</b><br><br>Quali sono le principali sfide che incontra nella gestione delle terapie infusionali per le malattie oncoematologiche rare?  In particolare:<br>
- In che modo queste sfide influiscono sull'efficienza e sugli sprechi? <br> 
- Quali sono gli sprechi indiretti principali che possono essere evitati nella gestione delle terapie infusionali (sprechi di tempo, risorse umane o ligistiche, sprechi economici o legati a ricoveri non necessari)? <br>
- Esistono differenze nella gestione dei farmaci inclusi nei LEA rispetto a quelli extra-LEA?  <br>""",
""" Attualmente, come viene organizzata la somministrazione dei farmaci che richiedono infusione per le malattie rare? Quali sono i vantaggi e gli svantaggi delle pratiche attuali? <br>""",
"""Quali benefici, per il paziente e per il Centro, prevede dall'organizzazione di giornate dedicate all'infusione di specifici farmaci per le malattie rare?  <br>""",
"""Quali sarebbero i tuoi principali ostacoli da superare per implementare delle giornate dedicate all’infusione del farmaco (pianificazione logistica, disponibilità del personale, gestione delle scorte del farmaco, sicurezza e monitoraggio dei pazienti, costi e sostenibilità, coordinamento multidisciplinare)? <br>""",
""" Quali indicatori utilizzate per valutare l'efficacia delle procedure di erogazione dei farmaci per le malattie rare (tempo medio di erogazione, personale sanitario necessario per l’erogazione, numero medio di pazienti trattati nell’unità di tempo, numero medio di giornate dedicate all’infusione, ...)? <br>""",
"""Come raccogliete e utilizzate il feedback dai pazienti e dal personale sanitario per migliorare continuamente le procedure?  <br>""","""<b>Campo note: registra o scrivi eventuali note</b><br><br>"""]
                      
  return c,FOLDER_ID,domanda_note,domanda1,domanda2,domanda3,domande_intervista
