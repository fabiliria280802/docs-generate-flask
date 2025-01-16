import unittest
from unittest.mock import patch, MagicMock, mock_open, call
from flask import Flask
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

# Importar la aplicación después de configurar las variables
from app import app

"""
class TestApp(unittest.TestCase):
    @classmethod

    

    
    @patch('app.get_data')
    @patch('app.HTML')
    @patch('app.pdf_to_png')
    @patch('app.generate_delivery_xml')
    @patch('os.path.join')
    def test_generate_all_deliveries_full_coverage(
        self, 
        mock_path_join, 
        mock_generate_delivery_xml, 
        mock_pdf_to_png, 
        mock_html, 
        mock_get_data
    ):
        # Simular datos de entrega completos
        mock_delivery_data = {
            'deliveries': [
                {
                    'receiver': {
                        'number': 'DEL-001', 
                        'name': 'Test Company 1',
                        'from': 'Sender Company',
                        'ruc': '12345678901',
                        'date': '2024-01-01',
                        'orderNumber': 'ORD-001',
                        'invoiceNumber': 'INV-001',
                        'hes': 'HES-001',
                        'price': 100.00,
                        'endDate': '2024-02-01',
                        'employee_name': 'John Doe',
                        'employee_position': 'Manager',
                        'employee_signature': 'signature.png'
                    }
                },
                {
                    'receiver': {
                        'number': 'DEL-002', 
                        'name': 'Test Company 2',
                        'from': 'Another Sender Company',
                        'ruc': '98765432109',
                        'date': '2024-02-01',
                        'orderNumber': 'ORD-002',
                        'invoiceNumber': 'INV-002',
                        'hes': 'HES-002',
                        'price': 200.00,
                        'endDate': '2024-03-01',
                        'employee_name': 'Jane Smith',
                        'employee_position': 'Director',
                        'employee_signature': 'signature2.png'
                    }
                }
            ]
        }

        # Configurar mocks
        mock_get_data.return_value = mock_delivery_data
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        mock_html.return_value.write_pdf.return_value = None

        # Mockear render_template para devolver HTML
        with patch('app.render_template', return_value="<html>Mocked Delivery Receipt</html>") as mock_render_template:
            # Usar test_request_context para simular el contexto de solicitud
            with app.test_request_context('/?lang=en'):
                # Mockear request globalmente
                with patch('flask.request', wraps=flask.request):
                    # Llamar a la función directamente
                    response = self.app.get('/generate_all_deliveries?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se llamó a get_data
        mock_get_data.assert_called_once_with('delivery')
        
        # Verificar generación de documentos para cada idioma
        expected_languages = ['en', 'esp']
        
        # Verificar llamadas a funciones para cada entrega y cada idioma
        for lang in expected_languages:
            for delivery in mock_delivery_data['deliveries']:
                # Verificar llamada a HTML para renderizar
                mock_html.assert_any_call(
                    string=unittest.mock.ANY, 
                    base_url=unittest.mock.ANY
                )
                
                # Verificar generación de PDF
                mock_html.return_value.write_pdf.assert_any_call(
                    unittest.mock.ANY
                )
                
                # Verificar generación de XML
                mock_generate_delivery_xml.assert_any_call(
                    unittest.mock.ANY, 
                    unittest.mock.ANY
                )

        # Verificar respuesta JSON
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('files', response_data)
        self.assertIn('locations', response_data)
        
        # Verificar tipos de archivos generados
        self.assertIn('pdf', response_data['files'])
        self.assertIn('png', response_data['files'])
        self.assertIn('xml', response_data['files'])

    def test_generate_all_deliveries_missing_data(self):
        # Probar escenario con datos incompletos
        with patch('app.get_data', return_value={'deliveries': [
            {
                'receiver': {}  # Datos incompletos
            }
        ]}):
            response = self.app.get('/generate_all_deliveries')
            
            # Verificar manejo de datos incompletos
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIn('message', response_data)

    def test_generate_all_deliveries_no_data(self):
        # Probar escenario sin datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/generate_all_deliveries')
            
            # Verificar manejo de error cuando no hay datos
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de las actas de entrega", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.HTML')
    @patch('app.generate_contract_xml')
    @patch('os.path.join')
    def test_generate_all_contracts_full_coverage(
        self, 
        mock_path_join, 
        mock_generate_contract_xml, 
        mock_html, 
        mock_get_data
    ):
        mock_contract_data = {
            "contracts": [
                {
                    "company": {
                        "name": "jackson-riley",
                        "ruc": "1793168604001",
                        "address": "316 Anthony Islands, Hendersonmouth, AK 81929",
                        "city": "Port Ryanbury",
                        "country": "Peru",
                        "phone": "001-900-356-9146",
                        "website": "www.jackson-riley.com",
                        "email": "info@jackson-riley.com",
                        "taxId": "04319450"
                    },
                    "client": {
                        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
                        "ruc": "1791239245001",
                        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
                        "city": "Quito",
                        "country": "Ecuador",
                        "employee_name": "Cesar Joseph",
                        "employee_position": "Accounts Payable Clerk",
                        "employee_signature": "enap_signature_2.png",
                        "in_charge_info": {
                            "name": "Lisa Ellis",
                            "position": "Financial Controller",
                            "signature": "signature2_.png"
                        }
                    },
                    "items": [
                        {
                            "code": "36A1",
                            "description": "Software quality assurance and testing",
                            "hes": "81200001",
                            "quantity": 2,
                            "unitCost": 49.18,
                            "cost": 98.36
                        },
                        {
                            "code": "36A2",
                            "description": "Database design and management",
                            "hes": "81200001",
                            "quantity": 3,
                            "unitCost": 68.87,
                            "cost": 206.61
                        }
                    ],
                    "totals": {
                        "beforeTax": 304.97,
                        "taxRate": 15,
                        "tax": 45.75,
                        "totalDue": 350.72
                    },
                    "contract": {
                        "number": "6500001",
                        "startDate": "2025-01-02",
                        "endDate": "2025-09-22",
                        "invoiceNumber": "1100001",
                        "hes": "81200001",
                        "orderNumber": "3400001"
                    }
                },
                {
                    "company": {
                        "name": "jackson-riley",
                        "ruc": "1793168604001",
                        "address": "316 Anthony Islands, Hendersonmouth, AK 81929",
                        "city": "Port Ryanbury",
                        "country": "Peru",
                        "phone": "001-900-356-9146",
                        "website": "www.jackson-riley.com",
                        "email": "info@jackson-riley.com",
                        "taxId": "04319450"
                    },
                    "client": {
                        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
                        "ruc": "1791239245001",
                        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
                        "city": "Quito",
                        "country": "Ecuador",
                        "employee_name": "Cesar Joseph",
                        "employee_position": "Accounts Payable Clerk",
                        "employee_signature": "enap_signature_2.png",
                        "in_charge_info": {
                            "name": "Lisa Ellis",
                            "position": "Financial Controller",
                            "signature": "signature2_.png"
                        }
                    },
                    "items": [
                        {
                            "code": "36A1",
                            "description": "Software quality assurance and testing",
                            "hes": "81200001",
                            "quantity": 2,
                            "unitCost": 49.18,
                            "cost": 98.36
                        },
                        {
                            "code": "36A2",
                            "description": "Database design and management",
                            "hes": "81200001",
                            "quantity": 3,
                            "unitCost": 68.87,
                            "cost": 206.61
                        }
                    ],
                    "totals": {
                        "beforeTax": 304.97,
                        "taxRate": 15,
                        "tax": 45.75,
                        "totalDue": 350.72
                    },
                    "contract": {
                        "number": "6500001",
                        "startDate": "2025-01-02",
                        "endDate": "2025-09-22",
                        "invoiceNumber": "1100001",
                        "hes": "81200001",
                        "orderNumber": "3400001"
                    }
                }
            ]
        }

        # Configurar mocks
        mock_get_data.return_value = mock_contract_data
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        mock_html.return_value.write_pdf.return_value = None

        # Mockear render_template para devolver HTML
        with patch('app.render_template', return_value="<html>Mocked Contract</html>") as mock_render_template:
            # Usar test_request_context para simular el contexto de solicitud
            with app.test_request_context('/?lang=en'):
                # Mockear request globalmente
                with patch('flask.request', wraps=flask.request):
                    # Llamar a la función directamente
                    response = self.app.get('/generate_all_contracts?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se llamó a get_data
        mock_get_data.assert_called_once_with('contract')
        
        # Verificar generación de documentos para cada idioma
        expected_languages = ['en', 'esp']
        
        # Verificar llamadas a funciones para cada contrato y cada idioma
        for lang in expected_languages:
            for contract in mock_contract_data['contracts']:
                # Verificar llamada a HTML para renderizar
                mock_html.assert_any_call(
                    string=unittest.mock.ANY, 
                    base_url=unittest.mock.ANY
                )
                
                # Verificar generación de PDF
                mock_html.return_value.write_pdf.assert_any_call(
                    unittest.mock.ANY
                )
                
                # Verificar generación de XML
                mock_generate_contract_xml.assert_any_call(
                    unittest.mock.ANY, 
                    unittest.mock.ANY
                )

        # Verificar respuesta JSON
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('files', response_data)
        self.assertIn('locations', response_data)
        
        # Verificar tipos de archivos generados
        self.assertIn('pdf', response_data['files'])
        self.assertIn('xml', response_data['files'])

    def test_generate_all_contracts_missing_data(self):
        # Probar escenario con datos incompletos
        with patch('app.get_data', return_value={'contracts': [
            {
                'contract': {}  # Datos incompletos
            }
        ]}):
            response = self.app.get('/generate_all_contracts')
            
            # Verificar manejo de datos incompletos
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIn('message', response_data)

    def test_generate_all_contracts_no_data(self):
        # Probar escenario sin datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/generate_all_contracts')
            
            # Verificar manejo de error cuando no hay datos
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de los contratos", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.HTML')
    @patch('app.pdf_to_png')
    @patch('app.generate_invoice_xml')
    @patch('os.path.join')
    def test_generate_all_invoices_full_coverage(
        self, 
        mock_path_join, 
        mock_generate_invoice_xml, 
        mock_pdf_to_png, 
        mock_html, 
        mock_get_data
    ):
        # Simular datos de factura completos
        mock_invoice_data = {
            'invoices': [
                {
                    # Estructura exacta que coincide con la plantilla y la función
                    'company': {
                        'name': 'Tu Empresa',
                        'address': 'Dirección de la empresa',
                        'city': 'Ciudad',
                        'country': 'País',
                        'phone': '+1234567890',
                        'website': 'www.tuempresa.com',
                        'taxId': '123456789'
                    },
                    'invoice': {
                        'number': 'INV-001',
                        'date': '2024-03-20',
                        'payableAt': '2024-04-20',
                        'orderNumber': 'ORD-001'
                    },
                    'client': {
                        'name': 'Nombre del Cliente',
                        'ruc': 'RUC12345',
                        'address': 'Dirección del cliente',
                        'city': 'Ciudad del cliente',
                        'country': 'País del cliente'
                    },
                    'items': [
                        {
                            'code': 'ITEM1',
                            'description': 'Producto 1',
                            'quantity': 1,
                            'unitCost': 100.00,
                            'cost': 100.00
                        }
                    ],
                    'totals': {
                        'beforeTax': 100.00,
                        'taxRate': 18,
                        'tax': 18.00,
                        'totalDue': 118.00
                    }
                },
                {
                    'company': {
                        'name': 'Otra Empresa',
                        'address': 'Otra dirección',
                        'city': 'Otra ciudad',
                        'country': 'Otro país',
                        'phone': '+0987654321',
                        'website': 'www.otraempresa.com',
                        'taxId': '987654321'
                    },
                    'invoice': {
                        'number': 'INV-002',
                        'date': '2024-03-21',
                        'payableAt': '2024-04-21',
                        'orderNumber': 'ORD-002'
                    },
                    'client': {
                        'name': 'Otro Cliente',
                        'ruc': 'RUC54321',
                        'address': 'Otra dirección de cliente',
                        'city': 'Otra ciudad de cliente',
                        'country': 'Otro país de cliente'
                    },
                    'items': [
                        {
                            'code': 'ITEM2',
                            'description': 'Producto 2',
                            'quantity': 2,
                            'unitCost': 50.00,
                            'cost': 100.00
                        }
                    ],
                    'totals': {
                        'beforeTax': 100.00,
                        'taxRate': 18,
                        'tax': 18.00,
                        'totalDue': 118.00
                    }
                }
            ]
        }

        # Configurar mocks
        mock_get_data.return_value = mock_invoice_data
        mock_path_join.side_effect = lambda *args: '/'.join(args)
        mock_html.return_value.write_pdf.return_value = None

        # Mockear render_template para devolver HTML
        with patch('app.render_template', side_effect=lambda template, **kwargs: f"<html>Mocked {template}</html>") as mock_render_template:
            # Simular contexto de solicitud
            with patch('flask.request') as mock_request:
                # Configurar mocks de request
                mock_request.args.get.return_value = 'en'
                mock_request.host_url = 'http://localhost/'

                # Llamar a la función directamente
                response = self.app.get('/generate_all_invoices?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se llamó a get_data
        mock_get_data.assert_called_once_with('invoice')
        
        # Verificar generación de documentos para cada idioma
        expected_languages = ['en', 'esp']
        
        # Verificar llamadas a funciones para cada factura y cada idioma
        for lang in expected_languages:
            for invoice in mock_invoice_data['invoices']:
                # Verificar llamada a render_template con los parámetros correctos
                mock_render_template.assert_any_call(
                    'invoice.html', 
                    data=invoice, 
                    image_index=unittest.mock.ANY, 
                    lang=lang
                )
                
                # Verificar llamada a HTML para renderizar
                mock_html.assert_any_call(
                    string=unittest.mock.ANY, 
                    base_url=unittest.mock.ANY
                )
                
                # Verificar generación de PDF
                mock_html.return_value.write_pdf.assert_any_call(
                    unittest.mock.ANY
                )
                
                # Verificar generación de PNG
                mock_pdf_to_png.assert_any_call(
                    unittest.mock.ANY, 
                    unittest.mock.ANY
                )
                
                # Verificar generación de XML
                mock_generate_invoice_xml.assert_any_call(
                    unittest.mock.ANY, 
                    unittest.mock.ANY
                )

        # Verificar respuesta JSON
        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn('files', response_data)
        self.assertIn('locations', response_data)
        
        # Verificar tipos de archivos generados
        self.assertIn('pdf', response_data['files'])
        self.assertIn('png', response_data['files'])
        self.assertIn('xml', response_data['files'])

    def test_generate_all_invoices_missing_data(self):
        # Probar escenario con datos incompletos
        with patch('app.get_data', return_value={'invoices': [
            {
                'invoice': {}  # Datos incompletos
            }
        ]}):
            response = self.app.get('/generate_all_invoices')
            
            # Verificar manejo de datos incompletos
            self.assertEqual(response.status_code, 200)
            response_data = json.loads(response.data)
            self.assertIn('message', response_data)

    def test_generate_all_invoices_no_data(self):
        # Probar escenario sin datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/generate_all_invoices')
            
            # Verificar manejo de error cuando no hay datos
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    @patch('app.get_data')
    @patch('app.render_template')
    def test_show_delivery_success(self, mock_render_template, mock_get_data):
        # Simular datos de entrega completos
        mock_delivery_data = {
            'deliveries': [
                {
                    'receiver': {
                        'number': 'DEL-001', 
                        'name': 'Test Company 1',
                        'from': 'Sender Company',
                        'ruc': '12345678901',
                        'date': '2024-01-01',
                        'orderNumber': 'ORD-001',
                        'invoiceNumber': 'INV-001',
                        'hes': 'HES-001',
                        'price': 100.00,
                        'endDate': '2024-02-01',
                        'employee_name': 'John Doe',
                        'employee_position': 'Manager',
                        'employee_signature': 'signature.png'
                    }
                }
            ]
        }
        
        # Configurar mocks
        mock_get_data.return_value = mock_delivery_data
        mock_render_template.return_value = "Mocked Delivery Receipt HTML"

        # Simular contexto de solicitud
        with patch('flask.request') as mock_request:
            # Configurar mocks de request
            mock_request.args.get.return_value = 'en'

            # Llamar a la ruta
            response = self.app.get('/delivery/0?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar llamadas a funciones
        mock_get_data.assert_called_once_with('delivery')
        mock_render_template.assert_called_once_with(
            'deliveryReceipt.html', 
            data=mock_delivery_data['deliveries'][0], 
            image_index=1, 
            lang='en'
        )

    def test_show_delivery_no_data(self):
        # Simular error al obtener datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/delivery/0')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    def test_show_delivery_index_error(self):
        # Simular datos vacíos
        with patch('app.get_data', return_value={'deliveries': []}):
            response = self.app.get('/delivery/0')
            
            self.assertEqual(response.status_code, 404)
            self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    def test_show_delivery_multiple_languages(self):
        # Probar diferentes idiomas
        languages = ['en', 'esp']
        
        for lang in languages:
            # Simular datos de entrega
            mock_delivery_data = {
                'deliveries': [
                    {
                        'receiver': {
                            'number': 'DEL-001', 
                            'name': 'Test Company 1',
                            'from': 'Sender Company',
                            'ruc': '12345678901',
                            'date': '2024-01-01',
                            'orderNumber': 'ORD-001',
                            'invoiceNumber': 'INV-001',
                            'hes': 'HES-001',
                            'price': 100.00,
                            'endDate': '2024-02-01',
                            'employee_name': 'John Doe',
                            'employee_position': 'Manager',
                            'employee_signature': 'signature.png'
                        }
                    }
                ]
            }
            
            # Configurar mocks
            with patch('app.get_data', return_value=mock_delivery_data), \
                 patch('app.render_template', return_value="Mocked Delivery Receipt HTML") as mock_render_template:
                
                # Llamar a la ruta con diferentes idiomas
                response = self.app.get(f'/delivery/0?lang={lang}')

                # Verificaciones
                self.assertEqual(response.status_code, 200)
                mock_render_template.assert_called_once_with(
                    'deliveryReceipt.html', 
                    data=mock_delivery_data['deliveries'][0], 
                    image_index=1, 
                    lang=lang
                )

    @patch('app.get_data')
    @patch('app.render_template')
    def test_show_contract_success(self, mock_render_template, mock_get_data):
        # Simular datos de contrato completos
        mock_contract_data = {
            'contracts': [
                {
                    'company': {
                        'name': 'jackson-riley',
                        'ruc': '1793168604001',
                        'address': '316 Anthony Islands, Hendersonmouth, AK 81929',
                        'city': 'Port Ryanbury',
                        'country': 'Peru',
                        'phone': '001-900-356-9146',
                        'website': 'www.jackson-riley.com',
                        'email': 'info@jackson-riley.com',
                        'taxId': '04319450'
                    },
                    'client': {
                        'name': 'tu empresa',
                        'ruc': 'tu ruc',
                        'address': 'tu direccion',
                        'city': 'tu ciudad',
                        'country': 'tu pais',
                        'employee_name': 'tu nombre',
                        'employee_position': 'tu cargo',
                        'employee_signature': 'tu firma',
                        'in_charge_info': {
                            'name': 'tu nombre',
                            'position': 'tu cargo',
                            'signature': 'tu firma.png'
                        }
                    },
                    'items': [
                        {
                            'code': 'tu codigo',
                            'description': 'tu descripcion',
                            'hes': 'tu hes',
                            'quantity': 2,
                            'unitCost': 49.18,
                            'cost': 98.36
                        }
                    ],
                    'totals': {
                        'beforeTax': 304.97,
                        'taxRate': 15,
                        'tax': 45.75,
                        'totalDue': 350.72
                    },
                    'contract': {
                        'number': 'tu numero',
                        'startDate': 'tu fecha de inicio',
                        'endDate': 'tu fecha de fin',
                        'invoiceNumber': 'tu numero de factura',
                        'hes': 'tu hes',
                        'orderNumber': 'tu numero de orden'
                    }
                }
            ]
        }
        
        # Configurar mocks
        mock_get_data.return_value = mock_contract_data
        mock_render_template.return_value = "Mocked Contract Receipt HTML"

        # Simular contexto de solicitud
        with patch('flask.request') as mock_request:
            # Configurar mocks de request
            mock_request.args.get.return_value = 'en'

            # Llamar a la ruta
            response = self.app.get('/contract/0?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar llamadas a funciones
        mock_get_data.assert_called_once_with('contract')
        mock_render_template.assert_called_once_with(
            'contract.html', 
            data=mock_contract_data['contracts'][0], 
            image_index=1, 
            lang='en'
        )

    def test_show_contract_no_data(self):
        # Simular error al obtener datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/contract/0')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de los contratos", response.get_data(as_text=True))

    def test_show_contract_index_error(self):
        # Simular datos vacíos
        with patch('app.get_data', return_value={'contracts': []}):
            response = self.app.get('/contract/0')
            
            self.assertEqual(response.status_code, 404)
            self.assertIn("Contrato no encontrado", response.get_data(as_text=True))

    def test_show_contract_multiple_languages(self):
        # Probar diferentes idiomas
        languages = ['en', 'esp']
        
        for lang in languages:
            # Simular datos de contrato
            mock_contract_data = {
                'contracts': [
                    {
                        'company': {
                            'name': 'jackson-riley',
                            'ruc': '1793168604001',
                            'address': '316 Anthony Islands, Hendersonmouth, AK 81929',
                            'city': 'Port Ryanbury',
                            'country': 'Peru',
                            'phone': '001-900-356-9146',
                            'website': 'www.jackson-riley.com',
                            'email': 'info@jackson-riley.com',
                            'taxId': '04319450'
                        },
                        'client': {
                            'name': 'tu empresa',
                            'ruc': 'tu ruc',
                            'address': 'tu direccion',
                            'city': 'tu ciudad',
                            'country': 'tu pais',
                            'employee_name': 'tu nombre',
                            'employee_position': 'tu cargo',
                            'employee_signature': 'tu firma',
                            'in_charge_info': {
                                'name': 'tu nombre',
                                'position': 'tu cargo',
                                'signature': 'tu firma.png'
                            }
                        },
                        'items': [
                            {
                                'code': 'tu codigo',
                                'description': 'tu descripcion',
                                'hes': 'tu hes',
                                'quantity': 2,
                                'unitCost': 49.18,
                                'cost': 98.36
                            }
                        ],
                        'totals': {
                            'beforeTax': 304.97,
                            'taxRate': 15,
                            'tax': 45.75,
                            'totalDue': 350.72
                        },
                        'contract': {
                            'number': 'tu numero',
                            'startDate': 'tu fecha de inicio',
                            'endDate': 'tu fecha de fin',
                            'invoiceNumber': 'tu numero de factura',
                            'hes': 'tu hes',
                            'orderNumber': 'tu numero de orden'
                        }
                    }
                ]
            }
            
            # Configurar mocks
            with patch('app.get_data', return_value=mock_contract_data), \
                 patch('app.render_template', return_value="Mocked Contract Receipt HTML") as mock_render_template:
                
                # Llamar a la ruta con diferentes idiomas
                response = self.app.get(f'/contract/0?lang={lang}')

                # Verificaciones
                self.assertEqual(response.status_code, 200)
                mock_render_template.assert_called_once_with(
                    'contract.html', 
                    data=mock_contract_data['contracts'][0], 
                    image_index=1, 
                    lang=lang
                )

    @patch('app.get_data')
    @patch('app.render_template')
    def test_show_invoice_success(self, mock_render_template, mock_get_data):
        # Simular datos de factura completos
        mock_invoice_data = {
            'invoices': [
                {
                    'company': {
                        'name': 'Tu Empresa',
                        'address': 'Dirección de la empresa',
                        'city': 'Ciudad',
                        'country': 'País',
                        'phone': '+1234567890',
                        'website': 'www.tuempresa.com',
                        'taxId': '123456789'
                    },
                    'invoice': {
                        'number': 'INV-001',
                        'date': '2024-03-20',
                        'payableAt': '2024-04-20',
                        'orderNumber': 'ORD-001'
                    },
                    'client': {
                        'name': 'Nombre del Cliente',
                        'ruc': 'RUC12345',
                        'address': 'Dirección del cliente',
                        'city': 'Ciudad del cliente',
                        'country': 'País del cliente'
                    },
                    'items': [
                        {
                            'code': 'ITEM1',
                            'description': 'Producto 1',
                            'quantity': 1,
                            'unitCost': 100.00,
                            'cost': 100.00
                        }
                    ],
                    'totals': {
                        'beforeTax': 100.00,
                        'taxRate': 18,
                        'tax': 18.00,
                        'totalDue': 118.00
                    }
                }
            ]
        }
        
        # Configurar mocks
        mock_get_data.return_value = mock_invoice_data
        mock_render_template.return_value = "Mocked Invoice Receipt HTML"

        # Simular contexto de solicitud
        with patch('flask.request') as mock_request:
            # Configurar mocks de request
            mock_request.args.get.return_value = 'en'

            # Llamar a la ruta
            response = self.app.get('/invoice/0?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar llamadas a funciones
        mock_get_data.assert_called_once_with('invoice')
        mock_render_template.assert_called_once_with(
            'invoice.html', 
            data=mock_invoice_data['invoices'][0], 
            image_index=1, 
            lang='en'
        )

    def test_show_invoice_no_data(self):
        # Simular error al obtener datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/invoice/0')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de las facturas", response.get_data(as_text=True))

    def test_show_invoice_index_error(self):
        # Simular datos vacíos
        with patch('app.get_data', return_value={'invoices': []}):
            response = self.app.get('/invoice/0')
            
            self.assertEqual(response.status_code, 404)
            self.assertIn("Factura no encontrada", response.get_data(as_text=True))

    def test_show_invoice_multiple_languages(self):
        # Probar diferentes idiomas
        languages = ['en', 'esp']
        
        for lang in languages:
            # Simular datos de factura
            mock_invoice_data = {
                'invoices': [
                    {
                        'company': {
                            'name': 'Tu Empresa',
                            'address': 'Dirección de la empresa',
                            'city': 'Ciudad',
                            'country': 'País',
                            'phone': '+1234567890',
                            'website': 'www.tuempresa.com',
                            'taxId': '123456789'
                        },
                        'invoice': {
                            'number': 'INV-001',
                            'date': '2024-03-20',
                            'payableAt': '2024-04-20',
                            'orderNumber': 'ORD-001'
                        },
                        'client': {
                            'name': 'Nombre del Cliente',
                            'ruc': 'RUC12345',
                            'address': 'Dirección del cliente',
                            'city': 'Ciudad del cliente',
                            'country': 'País del cliente'
                        },
                        'items': [
                            {
                                'code': 'ITEM1',
                                'description': 'Producto 1',
                                'quantity': 1,
                                'unitCost': 100.00,
                                'cost': 100.00
                            }
                        ],
                        'totals': {
                            'beforeTax': 100.00,
                            'taxRate': 18,
                            'tax': 18.00,
                            'totalDue': 118.00
                        }
                    }
                ]
            }
            
            # Configurar mocks
            with patch('app.get_data', return_value=mock_invoice_data), \
                 patch('app.render_template', return_value="Mocked Invoice Receipt HTML") as mock_render_template:
                
                # Llamar a la ruta con diferentes idiomas
                response = self.app.get(f'/invoice/0?lang={lang}')

                # Verificaciones
                self.assertEqual(response.status_code, 200)
                mock_render_template.assert_called_once_with(
                    'invoice.html', 
                    data=mock_invoice_data['invoices'][0], 
                    image_index=1, 
                    lang=lang
                )

    @patch('app.get_data')
    @patch('app.render_template')
    def test_delivery_receipts_success(self, mock_render_template, mock_get_data):
        # Simular datos de entregas completos
        mock_delivery_data = {
            'deliveries': [
                {
                    'receiver': {
                        'number': 'DEL-001', 
                        'name': 'Test Company 1',
                        'from': 'Sender Company 1',
                        'ruc': '12345678901',
                        'date': '2024-01-01',
                        'orderNumber': 'ORD-001',
                        'invoiceNumber': 'INV-001',
                        'hes': 'HES-001',
                        'price': 100.00,
                        'endDate': '2024-02-01',
                        'employee_name': 'John Doe',
                        'employee_position': 'Manager',
                        'employee_signature': 'signature1.png'
                    }
                },
                {
                    'receiver': {
                        'number': 'DEL-002', 
                        'name': 'Test Company 2',
                        'from': 'Sender Company 2',
                        'ruc': '98765432109',
                        'date': '2024-02-01',
                        'orderNumber': 'ORD-002',
                        'invoiceNumber': 'INV-002',
                        'hes': 'HES-002',
                        'price': 200.00,
                        'endDate': '2024-03-01',
                        'employee_name': 'Jane Smith',
                        'employee_position': 'Director',
                        'employee_signature': 'signature2.png'
                    }
                }
            ]
        }
        
        # Configurar mocks
        mock_get_data.return_value = mock_delivery_data
        mock_render_template.return_value = "Mocked Delivery Receipts List HTML"

        # Simular contexto de solicitud
        with patch('flask.request') as mock_request:
            # Configurar mocks de request
            mock_request.args.get.return_value = 'en'

            # Llamar a la ruta
            response = self.app.get('/delivery_receipts?lang=en')

        # Verificaciones
        self.assertEqual(response.status_code, 200)
        
        # Verificar llamadas a funciones
        mock_get_data.assert_called_once_with('delivery')
        mock_render_template.assert_called_once_with(
            'deliveryReceipt_list.html', 
            data=mock_delivery_data['deliveries'], 
            lang='en'
        )

    def test_delivery_receipts_no_data(self):
        # Simular error al obtener datos
        with patch('app.get_data', return_value=None):
            response = self.app.get('/delivery_receipts')
            
            self.assertEqual(response.status_code, 500)
            self.assertIn("No se pudo cargar los datos de las actas de entrega", response.get_data(as_text=True))

    def test_delivery_receipts_empty_data(self):
        # Simular datos vacíos
        with patch('app.get_data', return_value={'deliveries': []}):
            response = self.app.get('/delivery_receipts')
            
            self.assertEqual(response.status_code, 200)
            
            # Verificar que se renderiza la plantilla con una lista vacía
            with patch('app.render_template') as mock_render_template:
                mock_render_template.assert_called_once_with(
                    'deliveryReceipt_list.html', 
                    data=[], 
                    lang='eng'
                )

    def test_delivery_receipts_multiple_languages(self):
        # Probar diferentes idiomas
        languages = ['en', 'esp']
        
        for lang in languages:
            # Simular datos de entregas
            mock_delivery_data = {
                'deliveries': [
                    {
                        'receiver': {
                            'number': 'DEL-001', 
                            'name': 'Test Company 1',
                            'from': 'Sender Company 1',
                            'ruc': '12345678901',
                            'date': '2024-01-01',
                            'orderNumber': 'ORD-001',
                            'invoiceNumber': 'INV-001',
                            'hes': 'HES-001',
                            'price': 100.00,
                            'endDate': '2024-02-01',
                            'employee_name': 'John Doe',
                            'employee_position': 'Manager',
                            'employee_signature': 'signature1.png'
                        }
                    },
                    {
                        'receiver': {
                            'number': 'DEL-002', 
                            'name': 'Test Company 2',
                            'from': 'Sender Company 2',
                            'ruc': '98765432109',
                            'date': '2024-02-01',
                            'orderNumber': 'ORD-002',
                            'invoiceNumber': 'INV-002',
                            'hes': 'HES-002',
                            'price': 200.00,
                            'endDate': '2024-03-01',
                            'employee_name': 'Jane Smith',
                            'employee_position': 'Director',
                            'employee_signature': 'signature2.png'
                        }
                    }
                ]
            }
            
            # Configurar mocks
            with patch('app.get_data', return_value=mock_delivery_data), \
                 patch('app.render_template', return_value="Mocked Delivery Receipts List HTML") as mock_render_template:
                
                # Llamar a la ruta con diferentes idiomas
                response = self.app.get(f'/delivery_receipts?lang={lang}')

                # Verificaciones
                self.assertEqual(response.status_code, 200)
                mock_render_template.assert_called_once_with(
                    'deliveryReceipt_list.html', 
                    data=mock_delivery_data['deliveries'], 
                    lang=lang
                )

    def test_delivery_receipts_partial_data(self):
        # Simular datos con información incompleta
        mock_delivery_data = {
            'deliveries': [
                {
                    'receiver': {
                        'number': 'DEL-001', 
                        'name': 'Test Company 1'
                        # Algunos campos faltantes
                    }
                }
            ]
        }
        
        # Configurar mocks
        with patch('app.get_data', return_value=mock_delivery_data), \
             patch('app.render_template', return_value="Mocked Delivery Receipts List HTML") as mock_render_template:
            
            # Llamar a la ruta
            response = self.app.get('/delivery_receipts?lang=en')

            # Verificaciones
            self.assertEqual(response.status_code, 200)
            mock_render_template.assert_called_once_with(
                'deliveryReceipt_list.html', 
                data=mock_delivery_data['deliveries'], 
                lang='en'
            )

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    @patch('flask.request')
    def test_get_data_success_default_language(self, mock_request, mock_json_load, mock_file_open):
        # Configurar mock para lenguaje por defecto
        mock_request.args.get.return_value = None
        
        # Datos simulados para cargar
        mock_json_data = {
            'invoices': [
                {
                    'invoice': {'number': 'INV-001'},
                    'company': {'name': 'Test Company'}
                }
            ]
        }
        mock_json_load.return_value = mock_json_data

        # Simular ruta de archivo
        with patch('os.path.join', return_value='static/data-eng/invoice-data.json'):
            # Llamar a la función
            result = app.get_data('invoice')

            # Verificaciones
            mock_file_open.assert_called_once_with('static/data-eng/invoice-data.json', 'r', encoding='utf-8')
            mock_json_load.assert_called_once()
            self.assertEqual(result, mock_json_data)

    def test_get_data_success_specific_language(self):
        # Configurar mock para lenguaje específico
        with patch('flask.request') as mock_request, \
             patch('builtins.open', new_callable=mock_open) as mock_file_open, \
             patch('json.load') as mock_json_load, \
             patch('os.path.join', return_value='static/data-esp/invoice-data.json'):
            
            # Configurar lenguaje específico
            mock_request.args.get.return_value = 'esp'
            
            # Datos simulados para cargar
            mock_json_data = {
                'invoices': [
                    {
                        'invoice': {'number': 'INV-001'},
                        'company': {'name': 'Empresa de Prueba'}
                    }
                ]
            }
            mock_json_load.return_value = mock_json_data

            # Llamar a la función
            result = app.get_data('invoice')

            # Verificaciones
            mock_file_open.assert_called_once_with('static/data-esp/invoice-data.json', 'r', encoding='utf-8')
            mock_json_load.assert_called_once()
            self.assertEqual(result, mock_json_data)

    def test_get_data_file_not_found(self):
        # Simular error de archivo no encontrado
        with patch('flask.request') as mock_request, \
             patch('builtins.open', side_effect=FileNotFoundError) as mock_file_open, \
             patch('os.path.join', return_value='static/data-eng/invoice-data.json'):
            
            # Configurar lenguaje por defecto
            mock_request.args.get.return_value = None
            
            # Llamar a la función
            result = app.get_data('invoice')

            # Verificaciones
            mock_file_open.assert_called_once_with('static/data-eng/invoice-data.json', 'r', encoding='utf-8')
            self.assertIsNone(result)

    def test_get_data_json_decode_error(self):
        # Simular error de decodificación JSON
        with patch('flask.request') as mock_request, \
             patch('builtins.open', new_callable=mock_open) as mock_file_open, \
             patch('json.load', side_effect=json.JSONDecodeError("Mocked error", "", 0)) as mock_json_load, \
             patch('os.path.join', return_value='static/data-eng/invoice-data.json'):
            
            # Configurar lenguaje por defecto
            mock_request.args.get.return_value = None
            
            # Llamar a la función
            result = app.get_data('invoice')

            # Verificaciones
            mock_file_open.assert_called_once_with('static/data-eng/invoice-data.json', 'r', encoding='utf-8')
            mock_json_load.assert_called_once()
            self.assertIsNone(result)

    def test_get_data_unsupported_type(self):
        # Simular tipo de datos no soportado
        with patch('flask.request') as mock_request:
            # Configurar lenguaje por defecto
            mock_request.args.get.return_value = None
            
            # Llamar a la función con tipo no soportado
            result = app.get_data('unsupported_type')

            # Verificaciones
            self.assertIsNone(result)

    def test_get_data_multiple_languages(self):
        # Probar múltiples idiomas
        languages = ['en', 'esp']
        
        for lang in languages:
            with patch('flask.request') as mock_request, \
                 patch('builtins.open', new_callable=mock_open) as mock_file_open, \
                 patch('json.load') as mock_json_load, \
                 patch('os.path.join', return_value=f'static/data-{lang}/invoice-data.json'):
                
                # Configurar lenguaje específico
                mock_request.args.get.return_value = lang
                
                # Datos simulados para cargar
                mock_json_data = {
                    'invoices': [
                        {
                            'invoice': {'number': 'INV-001'},
                            'company': {'name': f'Test Company {lang}'}
                        }
                    ]
                }
                mock_json_load.return_value = mock_json_data

                # Llamar a la función
                result = app.get_data('invoice')

                # Verificaciones
                mock_file_open.assert_called_once_with(f'static/data-{lang}/invoice-data.json', 'r', encoding='utf-8')
                mock_json_load.assert_called_once()
                self.assertEqual(result, mock_json_data)

    def test_get_data_fallback_to_default_language(self):
        # Simular error al cargar datos en un idioma específico, con fallback a inglés
        with patch('flask.request') as mock_request, \
             patch('builtins.open', side_effect=[
                 FileNotFoundError,  # Primer intento con idioma específico
                 mock_open(read_data='{"invoices": [{"invoice": {"number": "INV-001"}}]}').return_value  # Segundo intento con inglés
             ]) as mock_file_open, \
             patch('json.load') as mock_json_load, \
             patch('os.path.join', side_effect=[
                 'static/data-esp/invoice-data.json',
                 'static/data-eng/invoice-data.json'
             ]):
            
            # Configurar lenguaje específico
            mock_request.args.get.return_value = 'esp'
            
            # Llamar a la función
            result = app.get_data('invoice')

            # Verificaciones
            # Debe haber intentado cargar primero el archivo en español
            self.assertEqual(mock_file_open.call_count, 2)
            mock_json_load.assert_called_once()
            self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
"""