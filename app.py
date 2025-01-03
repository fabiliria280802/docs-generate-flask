from flask import Flask, render_template, request, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from weasyprint import HTML
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import fitz
import os
import json

app = Flask(__name__)

CREDENTIALS_FILE = 'credentials/'

SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

required_dirs = [
    "credencials/"
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
        os.makedirs(directory)

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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
