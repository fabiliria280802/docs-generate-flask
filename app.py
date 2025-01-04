from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from google.cloud import storage
from weasyprint import HTML
from dicttoxml import dicttoxml
from dotenv import load_dotenv, find_dotenv
import fitz
import os
import sys
import json

def find_env_file():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '.env'),  
        os.path.join(os.getcwd(), '.env'),               
        os.path.join(os.path.expanduser('~'), '.env'),   
        '.env'                                           
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    test_env_path = os.path.join(os.path.dirname(__file__), '.env.test')
    return test_env_path if os.path.exists(test_env_path) else None

env_path = find_env_file()
if env_path:
    load_dotenv(dotenv_path=env_path, override=True)
else:
    print("Advertencia: No se encontró archivo .env")


app = Flask(__name__)

credentials_path = os.getenv('CREDENTIALS_FILE', 'credentials/credentials.json')
bucket_name = os.getenv('BUCKET_NAME', 'default-bucket')
port = int(os.getenv('PORT', 3000))

if not os.path.exists(credentials_path):
    print(f"Advertencia: El archivo de credenciales {credentials_path} no existe")
    credentials = None
else:
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error al cargar credenciales: {e}")
        credentials = None
        drive_service = None

required_dirs = [
    "credentials/",
    "static/data-eng",
    "static/data-esp",
    "static/assets",
    "examples/invoices/pdf",
    "examples/invoices/png",
    "examples/invoices/xml",
    "examples/deliveries/pdf",
    "examples/deliveries/png",
    "examples/deliveries/xml",
    "examples/contract/pdf",
    "examples/contract/xml"
]

for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_data(data_type):
    """Función genérica para cargar datos desde JSON"""
    lang = request.args.get('lang', 'eng')
    json_path = os.path.join('static', f'data-{lang}', f'{data_type}-data.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al leer JSON {data_type} en idioma {lang}: {str(e)}")
        return None

def pdf_to_png(pdf_path, png_path):
    """
    Convierte la PRIMERA página del PDF en una imagen PNG usando PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    if doc.page_count > 0:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(png_path)
    doc.close()

def generate_invoice_xml(invoice_data, xml_path):
    xml = dicttoxml(invoice_data, custom_root='invoice', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

def generate_contract_xml(contract_data, xml_path):
    xml = dicttoxml(contract_data, custom_root='contract', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

def generate_delivery_xml(delivery_data, xml_path):
    xml = dicttoxml(delivery_data, custom_root='delivery', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def generate_public_url(bucket_name, blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    return blob.public_url

@app.route('/')
def home():
    """Ruta por defecto que muestra la lista de facturas"""
    invoice_data = get_data('invoice')
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    current_lang = request.args.get('lang', 'eng')

    return render_template('invoice_list.html',
                           invoices=invoice_data['invoices'],
                           active_page='invoices',
                           current_lang=current_lang)

@app.route('/contracts')
def contracts():
    """Ruta para mostrar la lista de contratos"""
    contract_data = get_data('contract')
    if contract_data is None:
        return "Error: No se pudo cargar los datos de los contratos", 500

    current_lang = request.args.get('lang', 'eng')

    return render_template('contract_list.html',
                         contracts=contract_data['contracts'],
                         active_page='contracts',
                         current_lang=current_lang)

@app.route('/delivery-receipts')
def delivery_receipts():
    """Ruta para mostrar la lista de actas de entrega"""
    delivery_data = get_data('delivery')
    if delivery_data is None:
        return "Error: No se pudo cargar los datos de las actas de entrega", 500

    current_lang = request.args.get('lang', 'eng')

    return render_template('deliveryReceipt_list.html',
                         deliveries=delivery_data['deliveries'],
                         active_page='delivery_receipts',
                         current_lang=current_lang)

@app.route('/invoice/<int:index>')
def show_invoice(index):
    invoice_data = get_data('invoice')
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        invoice = invoice_data['invoices'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        current_lang = request.args.get('lang', 'eng')

        return render_template('invoice.html', data=invoice, image_index=image_index, lang=current_lang)
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/contract/<int:index>')
def show_contract(index):
    contract_data = get_data('contract')
    if contract_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        contract = contract_data['contracts'][index]
        total_images = 21
        image_index = (index % total_images) + 1

        current_lang = request.args.get('lang', 'eng')

        return render_template('contract.html', data=contract, image_index=image_index,lang=current_lang)
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/delivery/<int:index>')
def show_delivery(index):
    delivery_data = get_data('delivery')
    if delivery_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        delivery = delivery_data['deliveries'][index]
        total_images = 21
        image_index = (index % total_images) + 1

        current_lang = request.args.get('lang', 'eng')

        return render_template('deliveryReceipt.html', data=delivery, image_index=image_index,lang=current_lang)
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_delivery/<int:index>')
def generate_delivery(index):
    delivery_data = get_data('delivery')
    if delivery_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    lang = request.args.get('lang', 'en')
    try:
        delivery = delivery_data['deliveries'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        rendered = render_template('deliveryReceipt.html', data=delivery, image_index=image_index, lang=lang)

        # Generar PDF
        pdf_filename = f"delivery_{delivery['receiver']['number']}_{lang}.pdf"
        pdf_path = os.path.join('examples', 'deliveries', 'pdf', pdf_filename)
        base_url = request.host_url.rstrip('/')
        HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)

        # Generar PNG
        png_filename = f"delivery_{delivery['receiver']['number']}_{lang}.png"
        png_path = os.path.join('examples', 'deliveries', 'png', png_filename)
        pdf_to_png(pdf_path, png_path)

        # Generar XML
        xml_filename = f"delivery_{delivery['receiver']['number']}_{lang}.xml"
        xml_path = os.path.join('examples', 'deliveries', 'xml', xml_filename)
        generate_delivery_xml(delivery, xml_path)

        return f"Factura generada con éxito en PDF, PNG y XML"
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_invoice/<int:index>')
def generate_invoice(index):
    invoice_data = get_data('invoice')
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    lang = request.args.get('lang', 'en')

    try:
        invoice = invoice_data['invoices'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        rendered = render_template('invoice.html', data=invoice, image_index=image_index, lang=lang)

        # Generar PDF
        pdf_filename = f"invoice_{invoice['invoice']['number']}.pdf"
        pdf_path = os.path.join('examples', 'invoices', 'pdf', pdf_filename)
        base_url = request.host_url.rstrip('/')
        HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)

        # Generar PNG
        png_filename = f"invoice_{invoice['invoice']['number']}.png"
        png_path = os.path.join('examples', 'invoices', 'png', png_filename)
        pdf_to_png(pdf_path, png_path)

        # Generar XML
        xml_filename = f"invoice_{invoice['invoice']['number']}.xml"
        xml_path = os.path.join('examples', 'invoices', 'xml', xml_filename)
        generate_invoice_xml(invoice, xml_path)

        return f"Factura generada con éxito en PDF, PNG y XML"
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_contract/<int:index>')
def generate_contract(index):
    contract_data = get_data('contract')
    if contract_data is None:
        return "Error: No se pudo cargar los datos de los contractos", 500

    lang = request.args.get('lang', 'en')
    try:
        contract = contract_data['contracts'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        rendered = render_template('contract.html', data=contract, image_index=image_index, lang=lang)

        # Generar PDF
        pdf_filename = f"contract_{contract['contract']['number']}_{lang}.pdf"
        pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_filename)
        base_url = request.host_url.rstrip('/')
        HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)

        # Generar XML
        xml_filename = f"contract_{contract['contract']['number']}_{lang}.xml"
        xml_path = os.path.join('examples', 'contract', 'xml', xml_filename)
        generate_contract_xml(contract, xml_path)

        return f"Factura generada con éxito en PDF, PNG y XML"
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_all_invoices')
def generate_all_invoices():
    invoice_data = get_data('invoice')
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    total_images = 21
    generated_files = {
        'pdf': [],
        'png': [],
        'xml': []
    }
    languages = ['en', 'esp']
    base_url = request.host_url.rstrip('/')

    for lang in languages:
        for index, invoice in enumerate(invoice_data['invoices']):
            try:
                image_index = (index % total_images) + 1

                # Renderizar la plantilla con el idioma correspondiente
                rendered = render_template('invoice.html', data=invoice, image_index=image_index, lang=lang)

                # Generar PDF con el idioma en el nombre
                pdf_filename = f"invoice_{invoice['invoice']['number']}_{lang}.pdf"
                pdf_path = os.path.join('examples', 'invoices', 'pdf', pdf_filename)
                HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
                generated_files['pdf'].append(pdf_filename)

                # Generar PNG con el idioma en el nombre
                png_filename = f"invoice_{invoice['invoice']['number']}_{lang}.png"
                png_path = os.path.join('examples', 'invoices', 'png', png_filename)
                pdf_to_png(pdf_path, png_path)
                generated_files['png'].append(png_filename)

                # Generar XML con el idioma en el nombre
                xml_filename = f"invoice_{invoice['invoice']['number']}_{lang}.xml"
                xml_path = os.path.join('examples', 'invoices', 'xml', xml_filename)
                generate_invoice_xml(invoice, xml_path)
                generated_files['xml'].append(xml_filename)

            except Exception as e:
                print(f"Error generando factura {invoice['invoice']['number']} en {lang}: {str(e)}")
                continue

    return jsonify({
        "message": "Todas las facturas fueron generadas con éxito en PDF, PNG y XML en ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/invoices/pdf/",
            "png": "examples/invoices/png/",
            "xml": "examples/invoices/xml/"
        }
    })

@app.route('/generate_all_contracts')
def generate_all_contracts():
    contract_data = get_data('contract')
    if contract_data is None:
        return "Error: No se pudo cargar los datos de los contratos", 500

    generated_files = {
        'pdf': [],
        'xml': []
    }
    languages = ['en', 'esp']  # Idiomas disponibles
    base_url = request.host_url.rstrip('/')

    for lang in languages:
        for index, contract in enumerate(contract_data['contracts']):
            try:
                # Renderizar la plantilla para el idioma actual
                rendered = render_template('contract.html', data=contract, lang=lang)

                # Generar PDF
                pdf_filename = f"contract_{index+1}_{lang}.pdf"
                pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_filename)
                HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
                generated_files['pdf'].append(pdf_filename)

                # Generar XML
                xml_filename = f"contract_{index+1}_{lang}.xml"
                xml_path = os.path.join('examples', 'contract', 'xml', xml_filename)
                generate_contract_xml(contract, xml_path)
                generated_files['xml'].append(xml_filename)

            except Exception as e:
                print(f"Error generando contrato {index+1} en {lang}: {str(e)}")
                continue

    return jsonify({
        "message": "Todos los contratos fueron generados con éxito en PDF y XML para ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/contract/pdf/",
            "xml": "examples/contract/xml/"
        }
    })

@app.route('/generate_all_deliveries')
def generate_all_deliveries():
    delivery_data = get_data('delivery')
    if delivery_data is None:
        return "Error: No se pudo cargar los datos de las actas de entrega", 500

    generated_files = {
        'pdf': [],
        'png': [],
        'xml': []
    }
    base_url = request.host_url.rstrip('/')
    languages = ['en', 'esp']  # Idiomas disponibles

    for lang in languages:
        for index, delivery in enumerate(delivery_data['deliveries']):
            try:
                # Validar los datos necesarios
                required_keys = ['date', 'name','number','from', 'orderNumber', 'invoiceNumber', 'hes', 'price', 'endDate', 'employee_name', 'employee_position']
                if not all(key in delivery['receiver'] for key in required_keys):
                    print(f"Datos faltantes en el acta de entrega {index}: {delivery['receiver']}")
                    continue

                # Renderizar la plantilla para el idioma actual
                rendered = render_template('deliveryReceipt.html', data=delivery, lang=lang)

                # Generar PDF
                pdf_filename = f"delivery_{delivery['receiver']['number']}_{lang}.pdf"
                pdf_path = os.path.join('examples', 'deliveries', 'pdf', pdf_filename)
                HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
                generated_files['pdf'].append(pdf_filename)

                # Generar PNG
                png_filename = f"delivery_{delivery['receiver']['number']}_{lang}.png"
                png_path = os.path.join('examples', 'deliveries', 'png', png_filename)
                pdf_to_png(pdf_path, png_path)
                generated_files['png'].append(png_filename)

                # Generar XML
                xml_filename = f"delivery_{delivery['receiver']['number']}_{lang}.xml"
                xml_path = os.path.join('examples', 'deliveries', 'xml', xml_filename)
                generate_delivery_xml(delivery, xml_path)
                generated_files['xml'].append(xml_filename)
            except KeyError as e:
                print(f"Falta la clave {e} en el acta de entrega {index}")
                continue
            except Exception as e:
                print(f"Error inesperado generando acta de entrega {index} en {lang}: {e}")
                continue

    return jsonify({
        "message": "Todas las actas de entrega fueron generadas con éxito en PDF, PNG y XML para ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/deliveries/pdf/",
            "png": "examples/deliveries/png/",
            "xml": "examples/deliveries/xml/"
        }
    })

@app.route('/generate_all_documents', methods=['GET'])
def generate_all_documents():
    bucket_name = 'your-bucket-name'  # Reemplaza con el nombre de tu bucket en GCS
    results = {}

    # Generar facturas
    try:
        invoice_result = generate_all_invoices()
        if isinstance(invoice_result, dict) and 'files' in invoice_result:
            for pdf_file in invoice_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'invoices', 'pdf', pdf_file)
                upload_to_gcs(bucket_name, pdf_path, f'pdf/{pdf_file}')
            for png_file in invoice_result['files']['png']:
                png_path = os.path.join('examples', 'invoices', 'png', png_file)
                upload_to_gcs(bucket_name, png_path, f'png/{png_file}')
            for xml_file in invoice_result['files']['xml']:
                xml_path = os.path.join('examples', 'invoices', 'xml', xml_file)
                upload_to_gcs(bucket_name, xml_path, f'xml/{xml_file}')
        results['invoices'] = invoice_result
    except Exception as e:
        results['invoices'] = {"error": str(e)}

    # Generar contratos
    try:
        contract_result = generate_all_contracts()
        if isinstance(contract_result, dict) and 'files' in contract_result:
            for pdf_file in contract_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_file)
                upload_to_gcs(bucket_name, pdf_path, f'pdf/{pdf_file}')
            for xml_file in contract_result['files']['xml']:
                xml_path = os.path.join('examples', 'contract', 'xml', xml_file)
                upload_to_gcs(bucket_name, xml_path, f'xml/{xml_file}')
        results['contracts'] = contract_result
    except Exception as e:
        results['contracts'] = {"error": str(e)}

    # Generar actas de entrega
    try:
        delivery_result = generate_all_deliveries()
        if isinstance(delivery_result, dict) and 'files' in delivery_result:
            for pdf_file in delivery_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'deliveries', 'pdf', pdf_file)
                upload_to_gcs(bucket_name, pdf_path, f'pdf/{pdf_file}')
            for png_file in delivery_result['files']['png']:
                png_path = os.path.join('examples', 'deliveries', 'png', png_file)
                upload_to_gcs(bucket_name, png_path, f'png/{png_file}')
            for xml_file in delivery_result['files']['xml']:
                xml_path = os.path.join('examples', 'deliveries', 'xml', xml_file)
                upload_to_gcs(bucket_name, xml_path, f'xml/{xml_file}')
        results['deliveries'] = delivery_result
    except Exception as e:
        results['deliveries'] = {"error": str(e)}

    return jsonify({
        "message": "Todos los documentos fueron generados y subidos con éxito.",
        "results": results
    })


"""
@app.route('/check_logos')
def check_logos():
    logos_dir = os.path.join(os.path.dirname(__file__), 'static', 'assets')
    available_logos = os.listdir(logos_dir)

    invoice_data = get_data('invoice')
    companies = []
    if invoice_data and 'invoices' in invoice_data:
        for invoice in invoice_data['invoices']:
            company_name = invoice.get('company', {}).get('name', '').lower().replace(' ', '')
            expected_logo = f"{company_name}-logo.png"
            companies.append({
                'name': company_name,
                'expected_logo': expected_logo,
                'logo_exists': expected_logo in available_logos
            })

    return jsonify({
        'available_logos': available_logos,
        'companies': companies
    })

@app.route('/debug_logos')
def debug_logos():
    logos_dir = os.path.join('static', 'assets')
    return jsonify({
        'logos_available': os.listdir(logos_dir),
        'logos_needed': [
            'kappa-logo.png',
            'aws-logo.png',
            'google-logo.png',
            'microsoft-logo.png',
            'dell-logo.png',
            'salesforce-logo.png',
            'ibm-logo.png',
            'default-logo.png'
        ]
    })

@app.route('/list_all')
def list_all():
    invoice_data = get_data('invoice')
    if invoice_data and 'invoices' in invoice_data:
        return jsonify({
            'total_invoices': len(invoice_data['invoices']),
            'companies': [inv['company']['name'] for inv in invoice_data['invoices']]
        })
    return "No hay datos", 404
"""
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
