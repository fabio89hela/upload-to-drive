from googleapiclient.errors import HttpError

def file_already_uploaded(service, folder_id, file_name):
    """
    Verifica se un file con il nome specificato esiste già nella cartella Google Drive.

    Args:
        service: Oggetto autenticato per l'accesso all'API di Google Drive.
        folder_id: ID della cartella di Google Drive dove controllare l'esistenza del file.
        file_name: Nome del file da verificare.

    Returns:
        bool: True se il file esiste, False altrimenti.
    """
    try:
        # Query per verificare se il file esiste nella cartella specificata
        query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()

        files = response.get('files', [])

        # Se la lista dei file non è vuota, il file esiste già
        return len(files) > 0

    except HttpError as error:
        print(f"Errore durante il controllo del file su Google Drive: {error}")
        return False
