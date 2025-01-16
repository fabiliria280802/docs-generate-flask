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

    @patch("app.get_data")
    @patch("app.render_template")
    def test_home_success(self, mock_render_template, mock_get_data):
        mock_get_data.return_value = {"invoices": [{"id": 1, "company": "Mock Company"}]}
        mock_render_template.return_value = "Mock Rendered HTML"

        response = self.app.get("/?lang=eng")

        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once_with("invoice")
        mock_render_template.assert_called_once_with(
            "invoice_list.html",
            invoices=[{"id": 1, "company": "Mock Company"}],
            active_page="invoices",
            current_lang="eng"
        )

    @patch("app.get_data", return_value=None)
    def test_home_no_data(self, mock_get_data):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

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

    @patch('app.get_data')
    @patch('app.render_template')
    def test_show_invoice_success(self, mock_render_template, mock_get_data):
        # Mocking get_data to return a valid invoice
        mock_get_data.return_value = {
            "invoices": [{"id": 1, "company": "Mock Company"}]
        }
        # Mocking render_template to return a successful response
        mock_render_template.return_value = "Mock Rendered HTML"

        # Call the endpoint
        response = self.app.get("/invoice/0?lang=eng")

        # Assertions
        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once_with("invoice")
        mock_render_template.assert_called_once_with(
            "invoice.html",
            data={"id": 1, "company": "Mock Company"},
            image_index=1,
            lang="eng"
        )

    @patch('app.get_data', return_value=None)
    def test_show_invoice_no_data(self, mock_get_data):
        # Simulate no data returned from get_data
        response = self.app.get("/invoice/0")

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch('app.get_data', return_value={"invoices": []})
    def test_show_invoice_index_error(self, mock_get_data):
        # Simulate an empty invoices list
        response = self.app.get("/invoice/0")

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    def test_show_contract_success(self, mock_render_template, mock_get_data):
        mock_get_data.return_value = {"contracts": [{"id": 1, "company": "Mock Company"}]}
        mock_render_template.return_value = "Mock Rendered HTML"

        response = self.app.get("/contract/0?lang=eng")

        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once_with("contract")
        mock_render_template.assert_called_once_with(
            "contract.html", data={"id": 1, "company": "Mock Company"}, image_index=1, lang="eng"
        )

    @patch("app.get_data", return_value=None)
    def test_show_contract_no_data(self, mock_get_data):
        response = self.app.get("/contract/0")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch("app.get_data", return_value={"contracts": []})
    def test_show_contract_index_error(self, mock_get_data):
        response = self.app.get("/contract/0")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    def test_show_delivery_success(self, mock_render_template, mock_get_data):
        mock_get_data.return_value = {"deliveries": [{"id": 1, "details": "Mock Details"}]}
        mock_render_template.return_value = "Mock Rendered HTML"

        response = self.app.get("/delivery/0?lang=eng")

        self.assertEqual(response.status_code, 200)
        mock_get_data.assert_called_once_with("delivery")
        mock_render_template.assert_called_once_with(
            "deliveryReceipt.html", data={"id": 1, "details": "Mock Details"}, image_index=1, lang="eng"
        )

    @patch("app.get_data", return_value=None)
    def test_show_delivery_no_data(self, mock_get_data):
        response = self.app.get("/delivery/0")
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch("app.get_data", return_value={"deliveries": []})
    def test_show_delivery_index_error(self, mock_get_data):
        response = self.app.get("/delivery/0")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.pdf_to_png")
    @patch("app.generate_invoice_xml")
    def test_generate_all_invoices_success(self, mock_generate_xml, mock_pdf_to_png, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return invoice data
        mock_get_data.return_value = {
            "invoices": [
                {"invoice": {"number": "123"}},
                {"invoice": {"number": "456"}}
            ]
        }
        mock_render_template.return_value = "Mock Rendered HTML"

        # Mock HTML to simulate PDF generation
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        response = self.app.get("/generate_all_invoices")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Todas las facturas fueron generadas con ", response.get_data(as_text=True))

        # Verify function calls
        mock_get_data.assert_called_once_with("invoice")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 invoices x 2 languages
        self.assertEqual(mock_html.call_count, 4)
        self.assertEqual(mock_pdf_to_png.call_count, 4)
        self.assertEqual(mock_generate_xml.call_count, 4)

    @patch("app.get_data", return_value=None)
    def test_generate_all_invoices_no_data(self, mock_get_data):
        response = self.app.get("/generate_all_invoices")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.pdf_to_png")
    @patch("app.generate_invoice_xml")
    def test_generate_all_invoices_error_handling(self, mock_generate_xml, mock_pdf_to_png, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return invoice data
        mock_get_data.return_value = {
            "invoices": [
                {"invoice": {"number": "123"}},
                {"invoice": {"number": "456"}}
            ]
        }
        # Simulate an exception during rendering
        mock_render_template.side_effect = Exception("Render Error")

        response = self.app.get("/generate_all_invoices")

        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("Todas las facturas fueron generadas con ", response.get_data(as_text=True))

        # Verify function calls
        mock_get_data.assert_called_once_with("invoice")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 invoices x 2 languages
        self.assertEqual(mock_html.call_count, 0)  # HTML generation skipped due to exceptions
        self.assertEqual(mock_pdf_to_png.call_count, 0)  # PNG generation skipped
        self.assertEqual(mock_generate_xml.call_count, 0)  # XML generation skipped

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.generate_contract_xml")
    def test_generate_all_contracts_success(self, mock_generate_xml, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return contract data
        mock_get_data.return_value = {
            "contracts": [
                {"contract": {"number": "123"}},
                {"contract": {"number": "456"}}
            ]
        }
        mock_render_template.return_value = "Mock Rendered HTML"

        # Mock HTML to simulate PDF generation
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        response = self.app.get("/generate_all_contracts")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Todos los contratos fueron generados con ", response.get_data(as_text=True))

        # Verify function calls
        mock_get_data.assert_called_once_with("contract")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 contracts x 2 languages
        self.assertEqual(mock_html.call_count, 4)
        self.assertEqual(mock_generate_xml.call_count, 4)

    @patch("app.get_data", return_value=None)
    def test_generate_all_contracts_no_data(self, mock_get_data):
        response = self.app.get("/generate_all_contracts")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de los contratos", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.generate_contract_xml")
    def test_generate_all_contracts_error_handling(self, mock_generate_xml, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return contract data
        mock_get_data.return_value = {
            "contracts": [
                {"contract": {"number": "123"}},
                {"contract": {"number": "456"}}
            ]
        }
        mock_render_template.side_effect = Exception("Render Error")

        response = self.app.get("/generate_all_contracts")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Todos los contratos fueron generados con ", response.get_data(as_text=True))

        # Verify that errors were logged but processing continued
        mock_get_data.assert_called_once_with("contract")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 contracts x 2 languages

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.pdf_to_png")
    @patch("app.generate_delivery_xml")
    def test_generate_all_deliveries_success(self, mock_generate_xml, mock_pdf_to_png, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return delivery data
        mock_get_data.return_value = {
            "deliveries": [
                {"receiver": {"number": "123", "date": "2023-01-01", "name": "Test", "from": "Sender", "orderNumber": "001", "invoiceNumber": "INV001", "hes": "HES001", "price": 100.0, "endDate": "2023-01-10", "employee_name": "Employee", "employee_position": "Position"}},
                {"receiver": {"number": "456", "date": "2023-01-01", "name": "Test", "from": "Sender", "orderNumber": "002", "invoiceNumber": "INV002", "hes": "HES002", "price": 200.0, "endDate": "2023-01-10", "employee_name": "Employee", "employee_position": "Position"}}
            ]
        }
        mock_render_template.return_value = "Mock Rendered HTML"

        # Mock HTML to simulate PDF generation
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        response = self.app.get("/generate_all_deliveries")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Todas las actas de entrega fueron generadas con ", response.get_data(as_text=True))

        # Verify function calls
        mock_get_data.assert_called_once_with("delivery")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 deliveries x 2 languages
        self.assertEqual(mock_html.call_count, 4)
        self.assertEqual(mock_pdf_to_png.call_count, 4)
        self.assertEqual(mock_generate_xml.call_count, 4)

    @patch("app.get_data", return_value=None)
    def test_generate_all_deliveries_no_data(self, mock_get_data):
        response = self.app.get("/generate_all_deliveries")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Error: No se pudo cargar los datos de las actas de entrega", response.get_data(as_text=True))

    @patch("app.get_data")
    @patch("app.render_template")
    @patch("app.HTML")
    @patch("app.pdf_to_png")
    @patch("app.generate_delivery_xml")
    def test_generate_all_deliveries_error_handling(self, mock_generate_xml, mock_pdf_to_png, mock_html, mock_render_template, mock_get_data):
        # Mock get_data to return delivery data
        mock_get_data.return_value = {
            "deliveries": [
                {"receiver": {"number": "123", "date": "2023-01-01", "name": "Test", "from": "Sender", "orderNumber": "001", "invoiceNumber": "INV001", "hes": "HES001", "price": 100.0, "endDate": "2023-01-10", "employee_name": "Employee", "employee_position": "Position"}},
                {"receiver": {"number": "456", "date": "2023-01-01", "name": "Test", "from": "Sender", "orderNumber": "002", "invoiceNumber": "INV002", "hes": "HES002", "price": 200.0, "endDate": "2023-01-10", "employee_name": "Employee", "employee_position": "Position"}}
            ]
        }
        mock_render_template.side_effect = Exception("Render Error")

        response = self.app.get("/generate_all_deliveries")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Todas las actas de entrega fueron generadas con ", response.get_data(as_text=True))

        # Verify that errors were logged but processing continued
        mock_get_data.assert_called_once_with("delivery")
        self.assertEqual(mock_render_template.call_count, 4)  # 2 deliveries x 2 languages

    @patch("app.get_data")
    def test_generate_all_deliveries_missing_keys(self, mock_get_data):
        # Mock get_data to return delivery data with missing keys
        mock_get_data.return_value = {
            "deliveries": [
                {"receiver": {"number": "123", "name": "Test"}},  # Missing required keys
                {"receiver": {"number": "456", "date": "2023-01-01", "name": "Test", "from": "Sender", "orderNumber": "002", "invoiceNumber": "INV002", "hes": "HES002", "price": 200.0, "endDate": "2023-01-10", "employee_name": "Employee", "employee_position": "Position"}}
            ]
        }

        with self.assertLogs(level="INFO") as log:
            response = self.app.get("/generate_all_deliveries")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Datos faltantes en el acta de entrega", "\n".join(log.output))