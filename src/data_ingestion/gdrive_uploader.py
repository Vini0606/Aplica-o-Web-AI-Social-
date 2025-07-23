# src/gdrive_uploader.py

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']
# !!! IMPORTANTE: Cole aqui o ID da pasta principal que você compartilhou com a conta de serviço
PARENT_FOLDER_ID = '18n8KQ64qTslKCl5tfu6hFqJK6Ao1wfdI' 

def get_gdrive_service(credentials_path):
    creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_or_create_folder(service, folder_name, parent_id):
    try:
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed=false"
        response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = response.get('files', [])
        if files:
            print(f"Pasta '{folder_name}' encontrada.")
            return files[0].get('id')
        else:
            file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder', 'parents': [parent_id]}
            folder = service.files().create(body=file_metadata, fields='id').execute()
            print(f"Pasta '{folder_name}' criada.")
            return folder.get('id')
    except HttpError as error:
        print(f"Ocorreu um erro ao buscar/criar a pasta: {error}")
        return None

def upload_file_to_folder(service, file_path, folder_id):
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)
    request = service.files().create(media_body=media, body={'name': file_name, 'parents': [folder_id]})
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload de {file_name}: {int(status.progress() * 100)}%")
    print(f"✅ Arquivo '{file_name}' enviado com sucesso.")
    
def upload_reports_to_drive(client_name: str, file_paths: list, credentials_path: str):
    """Orquestra o upload de uma lista de arquivos para uma pasta de cliente no Drive."""
    if not PARENT_FOLDER_ID or PARENT_FOLDER_ID == 'SEU_ID_DA_PASTA_PRINCIPAL_AQUI':
        raise ValueError("PARENT_FOLDER_ID não foi configurado em src/gdrive_uploader.py")

    service = get_gdrive_service(credentials_path)
    client_folder_id = find_or_create_folder(service, client_name, PARENT_FOLDER_ID)
    if not client_folder_id:
        raise Exception("Falha ao encontrar/criar a pasta do cliente no Google Drive.")
    
    for path in file_paths:
        if os.path.exists(path):
            upload_file_to_folder(service, path, client_folder_id)
            os.remove(path) # Remove o arquivo local após o upload
            print(f"Arquivo local '{path}' removido.")
        else:
            print(f"⚠️ Aviso: Arquivo '{path}' não encontrado para upload.")