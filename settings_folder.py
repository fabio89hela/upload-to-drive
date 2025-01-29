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
    regional=["Alessandro D'Arpino, Dirigente farmacista Ospedale di Perugia","Andrea Di Mattia, Dirigente farmacista Campus Bio Medico di Roma","Lorenzo Fiorino, Dirigente farmacista Policlinico S.Orsola-Malpighi","Gaspare Guglielmi, Dirigente farmacista Ospedale Cardarelli di Napoli","Paolo Silimbani, Responsabile Aziendale di Farmacovigilanza IRST IRCCS Dino Amadori"]
    nome={
      "Alessandro D'Arpino, Dirigente farmacista Ospedale di Perugia":"AlessandroDArpino",
      "Andrea Di Mattia, Dirigente farmacista Campus Bio Medico di Roma":"AndreaDiMattia",
      "Lorenzo Fiorino, Dirigente farmacista Policlinico S.Orsola-Malpighi":"LorenzoFiorino",
      "Gaspare Guglielmi, Dirigente farmacista Ospedale Cardarelli di Napoli":"GaspareGuglielmi",
      "Paolo Silimbani, Responsabile Aziendale di Farmacovigilanza IRST IRCCS Dino Amadori":"PaoloSilimbani"
      }
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
  else:
    c="Oncoematologia"
    FOLDER_ID = "15FhRa5wa7zxNEN4GyGzJKtwc6q7jK2rR"  
  return c,FOLDER_ID,regional,nome,domanda1,domanda2
