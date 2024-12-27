import os
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Abilita CORS su tutte le rotte

# Leggi le credenziali dalla variabile di ambiente
credentials_info = json.loads(os.environ['GOOGLE_CREDENTIALS'])
credentials = Credentials.from_service_account_info(credentials_info)

# Configura il servizio Google Drive
drive_service = build('drive', 'v3', credentials=credentials)

# ID della cartella di Google Drive
FOLDER_ID = '1D-J3C13090LyeI4R7z6efTl-i1mMET7w'

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(file.filename)

    file_metadata = {
        'name': file.filename,
        'parents': [FOLDER_ID]
    }
    media = MediaFileUpload(file.filename, resumable=True)

    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return jsonify({'file_id': uploaded_file.get('id')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
