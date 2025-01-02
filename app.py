from flask import Flask, render_template, request, jsonify
from weasyprint import HTML
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString
import fitz
import os
import json

app = Flask(__name__)

required_dirs = [
    "static/data-eng",
    "static/data-esp",
    "static/assets",
    "examples/invoices/pdf",
    "examples/invoices/png",
    "examples/invoices/xml",
    "examples/actService/pdf",
    "examples/actService/png",
    "examples/actService/xml",
    "examples/contract/pdf",
    "examples/contract/png",
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

        return render_template('invoice.html', data=invoice, image_index=image_index)
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

@app.route('/generate_invoice/<int:index>')
def generate_invoice(index):
    invoice_data = get_data('invoice')
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        invoice = invoice_data['invoices'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        rendered = render_template('invoice.html', data=invoice, image_index=image_index)

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

    try:
        contract = contract_data['contracts'][index]
        total_images = 21
        image_index = (index % total_images) + 1
        rendered = render_template('contract.html', data=contract, image_index=image_index)

        # Generar PDF
        pdf_filename = f"contract_{contract['contract']['number']}.pdf"
        pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_filename)
        base_url = request.host_url.rstrip('/')
        HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)

        # Generar PNG
        png_filename = f"contract_{contract['contract']['number']}.png"
        png_path = os.path.join('examples', 'contract', 'png', png_filename)
        pdf_to_png(pdf_path, png_path)


        # Generar XML
        xml_filename = f"contract_{contract['contract']['number']}.xml"
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
    base_url = request.host_url.rstrip('/')

    for index, invoice in enumerate(invoice_data['invoices']):
        try:
            image_index = (index % total_images) + 1
            rendered = render_template('invoice.html', data=invoice, image_index=image_index)

            # Generar PDF
            pdf_filename = f"invoice_{invoice['invoice']['number']}.pdf"
            pdf_path = os.path.join('examples', 'invoices', 'pdf', pdf_filename)
            HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
            generated_files['pdf'].append(pdf_filename)

            # Generar PNG
            png_filename = f"invoice_{invoice['invoice']['number']}.png"
            png_path = os.path.join('examples', 'invoices', 'png', png_filename)
            pdf_to_png(pdf_path, png_path)


            # Generar XML
            xml_filename = f"invoice_{invoice['invoice']['number']}.xml"
            xml_path = os.path.join('examples', 'invoices', 'xml', xml_filename)
            generate_invoice_xml(invoice, xml_path)
            generated_files['xml'].append(xml_filename)

        except Exception as e:
            print(f"Error generando factura {invoice['invoice']['number']}: {str(e)}")
            continue

    return jsonify({
        "message": "Todas las facturas fueron generadas con éxito en PDF, PNG y XML",
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

    # Cantidad total de imágenes disponibles (para rotar si fuese necesario)
    total_images = 21
    generated_files = {
        'pdf': [],
        'png': [],
        'xml': []
    }

    # Removemos la barra final para usar en base_url
    base_url = request.host_url.rstrip('/')

    # Iteramos cada contrato
    for index, contract in enumerate(contract_data['contracts']):
        try:
            # Índice para las imágenes (opcional, si quieres rotarlas como en invoices)
            image_index = (index % total_images) + 1

            # Renderizamos la plantilla contract.html, pasando 'contract' como 'data'
            rendered = render_template('contract.html',
                                       data=contract,
                                       image_index=image_index)

            # Generar nombres de archivos con base al índice (o si tienes un "number", úsalo)
            pdf_filename = f"contract_{index+1}.pdf"
            pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_filename)

            # Convertir HTML a PDF
            HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
            generated_files['pdf'].append(pdf_filename)

            # Generar PNG (tomando la primera página del PDF)
            png_filename = f"contract_{index+1}.png"
            png_path = os.path.join('examples', 'contract', 'png', png_filename)

            images = convert_from_path(pdf_path)
            if images:
                images[0].save(png_path, 'PNG')
                generated_files['png'].append(png_filename)
            else:
                print(f"Error: No se pudo convertir a PNG el contrato {index+1}")

            # Generar XML
            xml_filename = f"contract_{index+1}.xml"
            xml_path = os.path.join('examples', 'contract', 'xml', xml_filename)
            
            # Puedes reusar la misma función generate_invoice_xml o crear una para contratos
            generate_invoice_xml(contract, xml_path)
            generated_files['xml'].append(xml_filename)

        except Exception as e:
            print(f"Error generando contrato {index+1}: {str(e)}")
            continue

    return jsonify({
        "message": "Todos los contratos fueron generados con éxito en PDF, PNG y XML",
        "files": generated_files,
        "locations": {
            "pdf": "examples/contract/pdf/",
            "png": "examples/contract/png/",
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

