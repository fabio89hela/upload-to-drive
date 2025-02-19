def settings_folder(cartella):
  c=""
  FOLDER_ID=""
  regional=[]
  nome={}
  domanda1=[]
  domanda2=[]
  if cartella=="Ematologia":
    c="Ematologia"
    FOLDER_ID = "1NjGZpL9XFdTdWcT-BbYit9fvOuTB6W7t"  
    regional = st.secrets["fo_name_emato"]["regional"]
    nome=st.secrets["fo_name_emato"]["nome"]
    domanda1="""
              **Impatto della presenza di Centri Hub/Spoke e modello erogativo/assistenziale**\n
              - Come viene coordinata l'erogazione di farmaci per l’ematologia tra centro Hub e centro Spoke, nella sua attuale esperienza?
              - Considerando il caso in cui la diagnosi viene fatta in un Centro Hub e il farmaco ad alto costo viene erogato da un Centro Spoke o da una farmacia territoriale, è prevista una procedura ben definita tra i due Centri per poter condividere fabbisogni e consentire al Centro che dovrà prendere in carico il paziente di ricevere il budget necessario per avviare la terapia?
                - Se sì, puoi descrivere il processo? 
              """
    domanda2="""
             **Gestione trasferimenti tra centri o tra regioni**\n
             - Quali sono le procedure attuali per gestire i trasferimenti dei pazienti come indicato?
             - Ci sono dei protocolli specifici per garantire la continuità delle cure durante un trasferimento di residenza?
             - Quali sono le principali sfide incontrate nella gestione dei trasferimenti dei pazienti?
             """
  elif cartella=="Emofilia":
    c="Emofilia"
    FOLDER_ID = "1CH9Pw0ZoWFFF2gSlOEo9UVa45akAgrz-"  
    regional=["Stefano Stoppa, Dirigente farmacista ASST Ovest-Milano","Calogero Russo, Direttore della Farmacia Territoriale dell’ASP di Enna","Angela Dovinola, Farmacista ASL Salerno, Distretto sanitario 67 - Mercato San Severino","Nicola Petragnani, Farmacista ospedaliero presso ASL Lanciano Vasto Chieti"]
    nome={
      "Stefano Stoppa, Dirigente farmacista ASST Ovest-Milano":"StefanoStoppa",
      "Calogero Russo, Direttore della Farmacia Territoriale dell’ASP di Enna":"CalogeroRusso",
      "Angela Dovinola, Farmacista ASL Salerno, Distretto sanitario 67 - Mercato San Severino":"AngelaDovinola",
      "Nicola Petragnani, Farmacista ospedaliero presso ASL Lanciano Vasto Chieti":"NicolaPetragnani",
      }
    domanda1="""
              **Prescrizione dei farmaci**\n
              - Come viene gestito e tracciato il flusso dell’erogazione dei farmaci off-label per le malattie rare nella vostra azienda ospedaliera o territoriale/locale per garantire l'appropriatezza delle prescrizioni? 
              """
    domanda2="""
              **Erogazione e approvvigionamento**\n
              - Come gestite l'urgenza di erogazione dei farmaci per pazienti con malattie rare?
              - Quali sono le principali barriere burocratiche e amministrative che influenzano l'erogazione tempestiva dei farmaci?
              """
  else:
    c="Oncoematologia"
    FOLDER_ID = "15FhRa5wa7zxNEN4GyGzJKtwc6q7jK2rR"  
    regional=["Erika Caravaggio, farmacista UFA dell’ospedale di Alessandria","Giuseppe De Marco,  Direttore della Farmacia dell’Azienda Ospedaliera Annunziata di Cosenza","Maria Cammarota, A.O.R.N. Cardarelli/U.O.C. Farmacia-UMACA","Giancarlo Torquati, Policlinico Tor Vergata di Roma"]
    nome={
      "Erika Caravaggio, farmacista UFA dell’ospedale di Alessandria":"ErikaCaravaggio",
      "Giuseppe De Marco,  Direttore della Farmacia dell’Azienda Ospedaliera Annunziata di Cosenza":"GiuseppeDeMarco",
      "Maria Cammarota, A.O.R.N. Cardarelli/U.O.C. Farmacia-UMACA":"MariaCammarota",
      "Giancarlo Torquati, Policlinico Tor Vergata di Roma":"GiancarloTorquati",
      }
    domanda1="""
              **Creazione di mini-network (rete di Centri che trattano patologie analoghe in un’area geografica limitata)**\n
              - Quali sarebbero i vantaggi della creazione di mini-network di area dedicati alla gestione dei farmaci per le malattie rare? Come dovrebbe essere strutturato un mini-network di area dedicato per ottimizzare l'erogazione dei farmaci?
              - Quali sono le pratiche di formazione e sensibilizzazione del personale sanitario per evitare sprechi nella gestione dei farmaci per le malattie rare?
                - Avete ricevuto suggerimenti pratici dal personale sanitario che potrebbero essere implementati?
              """
    domanda2="""
              **Mininetwork e ottimizzazione tecnologica e pratica**\n
              - Quali tecnologie vengono attualmente utilizzate per migliorare l'efficienza nella gestione dei farmaci per le malattie rare?
              - E’ in grado di fornirci un esempio di efficientamento di processo che potrebbe essere implementato per migliorare la gestione dei farmaci infusivi per le malattie rare? Esistono collaborazioni con altre strutture per condividere e implementare queste misure di efficientamento? Quali?
              """    
  return c,FOLDER_ID,regional,nome,domanda1,domanda2
