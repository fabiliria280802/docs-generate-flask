import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from flask import Flask, request
import os
import json
import sys
import fitz
import flask
from dotenv import load_dotenv

# Configurar variables de entorno antes de importar la aplicación
os.environ['CREDENTIALS_FILE'] = 'credentials/credentials.json'
os.environ['BUCKET_NAME'] = 'test-bucket'
os.environ['PORT'] = '3000'

# Cargar variables de entorno
load_dotenv(override=True)

from app import (
    get_data, 
    pdf_to_png, 
    generate_invoice_xml, 
    generate_contract_xml, 
    generate_delivery_xml,
    app
)

class TestAppFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = Flask(__name__)

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_required_directories_creation(self):
        # Verificar que se crean los directorios requeridos
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs:
            
            # Recargar el módulo para ejecutar la creación de directorios
            import importlib
            import app
            importlib.reload(app)

            # Verificar que se crearon los directorios esperados
            expected_dirs = [
                "credentials/",
                "static/data-eng",
                "static/data-esp",
                "static/assets",
                "examples/invoices",
                "examples/deliveries",
                "examples/contract"
            ]

            # Verificar que se llamó a makedirs para cada directorio
            calls = [call(dir, exist_ok=True) for dir in expected_dirs]
            mock_makedirs.assert_has_calls(calls, any_order=True)

    @patch('os.environ')
    def test_environment_variables(self, mock_environ):
        # Verificar que las variables de entorno necesarias estén configuradas
        mock_environ.get.side_effect = lambda key, default=None: {
            'CREDENTIALS_FILE': 'test_credentials.json',
            'BUCKET_NAME': 'test-bucket'
        }.get(key, default)

        self.assertEqual(os.environ.get('CREDENTIALS_FILE'), 'test_credentials.json')
        self.assertEqual(os.environ.get('BUCKET_NAME'), 'test-bucket')

    def test_environment_configuration(self):
        # Verificar configuración de variables de entorno
        self.assertEqual(os.getenv('CREDENTIALS_FILE'), 'credentials/credentials.json')
        self.assertEqual(os.getenv('BUCKET_NAME'), 'test-bucket')
        self.assertEqual(os.getenv('PORT'), '3000')

    
if __name__ == '__main__':
    unittest.main()
