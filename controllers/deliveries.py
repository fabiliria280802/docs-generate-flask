import os
from flask import Blueprint, request, render_template, session
from services.utils import generate_delivery_xml, pdf_to_png, get_data_from_local
from services.drive_service import get_data_from_google_drive
from weasyprint import HTML

deliveries_blueprint = Blueprint('deliveries', __name__)

@deliveries_blueprint.route('/delivery/<int:index>', methods=['GET'])
def show_delivery(index):

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        delivery_data = get_data_from_local('delivery')
    elif data_source == 'google_drive':
        delivery_data = get_data_from_google_drive('delivery')
    else:
        return "Invalid data source", 400

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

@deliveries_blueprint.route('/generate_delivery/<int:index>', methods=['GET'])
def generate_delivery(index):

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        delivery_data = get_data_from_local('delivery')
    elif data_source == 'google_drive':
        delivery_data = get_data_from_google_drive('delivery')
    else:
        return "Invalid data source", 400

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

@deliveries_blueprint.route('/delivery-receipts', methods=['GET'])
def get_delivery_receipts():
    """Ruta para mostrar la lista de actas de entrega"""

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        delivery_data = get_data_from_local('delivery')
    elif data_source == 'google_drive':
        delivery_data = get_data_from_google_drive('delivery')
    else:
        return "Invalid data source", 400

    if delivery_data is None:
        return "Error: No se pudo cargar los datos de las actas de entrega", 500

    current_lang = request.args.get('lang', 'eng')

    return render_template('deliveryReceipt_list.html',
                         deliveries=delivery_data['deliveries'],
                         active_page='delivery_receipts',
                         current_lang=current_lang)

@deliveries_blueprint.route('/generate_all_deliveries', methods=['GET'])
def generate_all_deliveries():

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        delivery_data = get_data_from_local('delivery')
    elif data_source == 'google_drive':
        delivery_data = get_data_from_google_drive('delivery')
    else:
        return "Invalid data source", 400

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

    return {
        "message": "Todas las actas de entrega fueron generadas con éxito en PDF, PNG y XML para ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/deliveries/pdf/",
            "png": "examples/deliveries/png/",
            "xml": "examples/deliveries/xml/"
        }
    }
