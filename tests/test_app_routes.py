import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from flask import Flask
import os
import json
import sys
import fitz
import flask
from dotenv import load_dotenv



# Importar la aplicación después de configurar las variables
from app import app

class TestAppRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Asegurar variables de entorno para pruebas
        os.environ['CREDENTIALS_FILE'] = 'credentials/credentials.json'
        os.environ['BUCKET_NAME'] = 'test-bucket'
        os.environ['PORT'] = '3000'

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.get_data')
    @patch('app.render_template')
    def test_generate_invoice_route_success(self, mock_render_template, mock_get_data):
        # Simular datos de factura
        mock_get_data.return_value = {
            'invoices': [{
                'invoice': {'number': 'INV-001'},
                'company': {'name': 'Test Company'}
            }]
        }
        mock_render_template.return_value = "Mocked HTML"

        with patch('app.HTML') as mock_html, \
             patch('app.pdf_to_png') as mock_pdf_to_png, \
             patch('app.generate_invoice_xml') as mock_generate_invoice_xml:
            
            response = self.app.get('/generate_invoice/0?lang=eng')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("Factura generada con éxito", response.get_data(as_text=True))
            
            # Verificar llamadas a funciones
            mock_html.assert_called_once()
            mock_pdf_to_png.assert_called_once()
            mock_generate_invoice_xml.assert_called_once()

    @patch('app.get_data')
    def test_generate_invoice_route_no_data(self, mock_get_data):
        # Simular error al obtener datos
        mock_get_data.return_value = None
        
        response = self.app.get('/generate_invoice/0')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch('app.get_data')
    def test_generate_invoice_route_index_error(self, mock_get_data):
        # Simular datos vacíos
        mock_get_data.return_value = {'invoices': []}
        
        response = self.app.get('/generate_invoice/0')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.render_template')
    def test_generate_contract_route_success(self, mock_render_template, mock_get_data):
        # Simular datos de contrato
        mock_get_data.return_value = {
            'contracts': [{
                'contract': {'number': 'CONTRACT-001'},
                'company': {'name': 'Test Company'}
            }]
        }
        mock_render_template.return_value = "Mocked HTML"

        with patch('app.HTML') as mock_html, \
             patch('app.generate_contract_xml') as mock_generate_contract_xml:
            
            response = self.app.get('/generate_contract/0?lang=eng')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("Factura generada con éxito", response.get_data(as_text=True))
            
            # Verificar llamadas a funciones
            mock_html.assert_called_once()
            mock_generate_contract_xml.assert_called_once()

    @patch('app.get_data')
    def test_generate_contract_route_no_data(self, mock_get_data):
        # Simular error al obtener datos
        mock_get_data.return_value = None
        
        response = self.app.get('/generate_contract/0')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("No se pudo cargar los datos de los contractos", response.get_data(as_text=True))

    @patch('app.get_data')
    def test_generate_contract_route_index_error(self, mock_get_data):
        # Simular datos vacíos
        mock_get_data.return_value = {'contracts': []}
        
        response = self.app.get('/generate_contract/0')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.render_template')
    def test_generate_delivery_route_success(self, mock_render_template, mock_get_data):
        # Simular datos de entrega
        mock_get_data.return_value = {
            'deliveries': [{
                'receiver': {
                    'number': 'DEL-001', 
                    'name': 'Test Company',
                    'date': '2024-01-01',
                    'orderNumber': 'ORD-001',
                    'invoiceNumber': 'INV-001',
                    'hes': 'HES-001',
                    'price': 100.00,
                    'endDate': '2024-02-01',
                    'employee_name': 'John Doe',
                    'employee_position': 'Manager'
                }
            }]
        }
        mock_render_template.return_value = "Mocked HTML"

        with patch('app.HTML') as mock_html, \
             patch('app.pdf_to_png') as mock_pdf_to_png, \
             patch('app.generate_delivery_xml') as mock_generate_delivery_xml:
            
            response = self.app.get('/generate_delivery/0?lang=eng')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn("Factura generada con éxito", response.get_data(as_text=True))
            
            # Verificar llamadas a funciones
            mock_html.assert_called_once()
            mock_pdf_to_png.assert_called_once()
            mock_generate_delivery_xml.assert_called_once()

    @patch('app.get_data')
    def test_generate_delivery_route_no_data(self, mock_get_data):
        # Simular error al obtener datos
        mock_get_data.return_value = None
        
        response = self.app.get('/generate_delivery/0')
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch('app.get_data')
    def test_generate_delivery_route_index_error(self, mock_get_data):
        # Simular datos vacíos
        mock_get_data.return_value = {'deliveries': []}
        
        response = self.app.get('/generate_delivery/0')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.upload_to_gcs')
    def test_generate_all_documents_route(self, mock_upload_to_gcs, mock_get_data):
        # Simular datos para todas las generaciones
        mock_get_data.side_effect = [
            {
                'invoices': [
                    {'invoice': {'number': 'INV-001'}, 'company': {'name': 'Company A'}},
                    {'invoice': {'number': 'INV-002'}, 'company': {'name': 'Company B'}}
                ]
            },
            {
                'contracts': [
                    {'contract': {'number': 'CONTRACT-001'}, 'company': {'name': 'Company C'}},
                    {'contract': {'number': 'CONTRACT-002'}, 'company': {'name': 'Company D'}}
                ]
            },
            {
                'deliveries': [
                    {'receiver': {'number': 'DEL-001', 'name': 'Company E'}},
                    {'receiver': {'number': 'DEL-002', 'name': 'Company F'}}
                ]
            }
        ]

        with patch('app.generate_all_invoices', return_value={'files': {'pdf': ['invoice1.pdf'], 'png': ['invoice1.png'], 'xml': ['invoice1.xml']}}), \
             patch('app.generate_all_contracts', return_value={'files': {'pdf': ['contract1.pdf'], 'xml': ['contract1.xml']}}), \
             patch('app.generate_all_deliveries', return_value={'files': {'pdf': ['delivery1.pdf'], 'png': ['delivery1.png'], 'xml': ['delivery1.xml']}}):
            
            response = self.app.get('/generate_all_documents')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertIn('message', data)
            self.assertIn('results', data)
            
            # Verificar que se llamó a upload_to_gcs para cada tipo de archivo
            mock_upload_to_gcs.assert_called()

        