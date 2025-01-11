import os
from flask import Blueprint, request, render_template, session
from services.utils import generate_invoice_xml, pdf_to_png, get_data_from_local
from services.drive_service import get_data_from_google_drive
from weasyprint import HTML

invoices_blueprint = Blueprint('invoices', __name__)

@invoices_blueprint.route('/invoice/<int:index>', methods=['GET'])
def show_invoice(index):

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        invoice_data = get_data_from_local('invoice')
    elif data_source == 'google_drive':
        invoice_data = get_data_from_google_drive('invoice')
    else:
        return "Invalid data source", 400

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

@invoices_blueprint.route('/generate_invoice/<int:index>', methods=['GET'])
def generate_invoice(index):

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        invoice_data = get_data_from_local('invoice')
    elif data_source == 'google_drive':
        invoice_data = get_data_from_google_drive('invoice')
    else:
        return "Invalid data source", 400

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
        pdf_path = os.path.join('examples', 'invoices', pdf_filename)
        base_url = request.host_url.rstrip('/')
        HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)

        # Generar PNG
        png_filename = f"invoice_{invoice['invoice']['number']}.png"
        png_path = os.path.join('examples', 'invoices', png_filename)
        pdf_to_png(pdf_path, png_path)

        # Generar XML
        xml_filename = f"invoice_{invoice['invoice']['number']}.xml"
        xml_path = os.path.join('examples', 'invoices', xml_filename)
        generate_invoice_xml(invoice, xml_path)

        return f"Factura generada con éxito en PDF, PNG y XML"
    except IndexError:
        return "Factura no encontrada", 404

@invoices_blueprint.route('/invoices', methods=['GET'])
def get_invoices():
    """Ruta por defecto que muestra la lista de facturas"""

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        invoice_data = get_data_from_local('invoice')
    elif data_source == 'google_drive':
        invoice_data = get_data_from_google_drive('invoice')
    else:
        return "Invalid data source", 400

    current_lang = request.args.get('lang', 'eng')

    return render_template('invoice_list.html',
                           invoices=invoice_data['invoices'],
                           active_page='invoices',
                           current_lang=current_lang)

@invoices_blueprint.route('/generate_all_invoices', methods=['GET'])
def generate_all_invoices():

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        invoice_data = get_data_from_local('invoice')
    elif data_source == 'google_drive':
        invoice_data = get_data_from_google_drive('invoice')
    else:
        return "Invalid data source", 400
    
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
                pdf_path = os.path.join('examples', 'invoices', pdf_filename)
                HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
                generated_files['pdf'].append(pdf_filename)

                # Generar PNG con el idioma en el nombre
                png_filename = f"invoice_{invoice['invoice']['number']}_{lang}.png"
                png_path = os.path.join('examples', 'invoices', png_filename)
                pdf_to_png(pdf_path, png_path)
                generated_files['png'].append(png_filename)

                # Generar XML con el idioma en el nombre
                xml_filename = f"invoice_{invoice['invoice']['number']}_{lang}.xml"
                xml_path = os.path.join('examples', 'invoices', xml_filename)
                generate_invoice_xml(invoice, xml_path)
                generated_files['xml'].append(xml_filename)

            except Exception as e:
                print(f"Error generando factura {invoice['invoice']['number']} en {lang}: {str(e)}")
                continue

    return {
        "message": "Todas las facturas fueron generadas con éxito en PDF, PNG y XML en ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/invoices/",
            "png": "examples/invoices/",
            "xml": "examples/invoices/"
        }
    }
