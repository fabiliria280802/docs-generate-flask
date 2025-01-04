import os
from dotenv import load_dotenv

load_dotenv()

CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE', 'credentials/credentials.json')
BUCKET_NAME = os.getenv('BUCKET_NAME', 'default-bucket')
PORT = int(os.getenv('PORT', 3000))
SCOPES = ['https://www.googleapis.com/auth/drive']
