from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
import os
import io
import json

CREDENTIALS_FILE = 'credentials/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

try:
    credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=credentials)
    print("Conexión exitosa con Google Drive.")
except Exception as e:
    print(f"Error al autenticar con Google Drive: {e}")
    drive_service = None

def create_folder(folder_name, parent_id=None):
    """Crea una carpeta en Google Drive."""
    if drive_service is None:
        print("Servicio de Google Drive no está configurado correctamente.")
        return None

    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]

        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Carpeta '{folder_name}' creada con éxito. ID: {folder.get('id')}")
        return folder.get('id')
    except Exception as e:
        print(f"Error al crear la carpeta '{folder_name}': {e}")
        return None

def upload_to_drive(file_path, parent_folder_id):
    """Sube un archivo a Google Drive dentro de una carpeta específica."""
    if drive_service is None:
        print("Servicio de Google Drive no está configurado correctamente.")
        return None

    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [parent_folder_id]}
    media = MediaFileUpload(file_path, resumable=True)

    try:
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Archivo '{file_name}' subido con éxito a la carpeta ID: {parent_folder_id}")
        return uploaded_file.get('id')
    except Exception as e:
        print(f"Error al subir el archivo '{file_name}': {e}")
        return None

def get_data_from_google_drive(data_type, lang='eng'):
    drive_paths = {
        "invoice_en": "data-eng/invoice-data.json",
        "delivery_en": "data-eng/delivery-data.json",
        "contract_en": "data-eng/contract-data.json",
        "invoice_es": "data-esp/invoice-data.json",
        "delivery_es": "data-esp/delivery-data.json",
        "contract_es": "data-esp/contract-data.json",
    }

    drive_key = f"{data_type}_{lang}"
    file_name = drive_paths.get(drive_key)

    if not file_name:
        print(f"Archivo no encontrado para {drive_key}")
        return None

    try:
        # Buscar el archivo en Google Drive por nombre
        query = f"name='{file_name}' and trashed=false"
        response = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = response.get('files', [])

        if not files:
            print(f"No se encontró el archivo en Google Drive: {file_name}")
            return None

        # Tomar el primer archivo coincidente
        file_id = files[0]['id']

        # Obtener el contenido del archivo
        request = drive_service.files().get_media(fileId=file_id)
        file_content = request.execute()

        # Parsear el contenido como JSON
        data = json.loads(file_content.decode('utf-8'))
        return data

    except HttpError as e:
        print(f"Error al acceder a Google Drive: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el JSON del archivo {file_name}: {e}")
        return None

# TODO: Implementar la función para leer json en google drive
def get_json_data_from_google_drive(data_type):
    print(f"Fetching {data_type} data from Google Drive...")
    return {"data": "Sample data from Google Drive"}

# TODO: Implementar la función get_data_from_google_drive
def get_documents_from_google_drive(data_type):
    """Simulación de obtener datos desde Google Drive."""
    # Implementar lógica para descargar archivos de Google Drive y procesarlos
    print(f"Fetching {data_type} data from Google Drive...")
    return {"data": "Sample data from Google Drive"}