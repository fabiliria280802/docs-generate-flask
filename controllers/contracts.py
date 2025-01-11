import os
from flask import Blueprint, request, render_template, session
from services.utils import generate_contract_xml, get_data_from_local, pdf_to_png
from services.drive_service import get_data_from_google_drive
from weasyprint import HTML

contracts_blueprint = Blueprint('contracts', __name__)

@contracts_blueprint.route('/contract/<int:index>', methods=['GET'])
def show_contract(index):
    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        contract_data = get_data_from_local('contract')
    elif data_source == 'google_drive':
        contract_data = get_data_from_google_drive('contract')
    else:
        return "Invalid data source", 400

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
    
@contracts_blueprint.route('/generate_contract/<int:index>', methods=['GET'])
def generate_contract(index):

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        contract_data = get_data_from_local('contract')
    elif data_source == 'google_drive':
        contract_data = get_data_from_google_drive('contract')
    else:
        return "Invalid data source", 400

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

@contracts_blueprint.route('/contracts', methods=['GET'])
def get_contracts():
    """Ruta para mostrar la lista de contratos"""

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        contract_data = get_data_from_local('contract')
    elif data_source == 'google_drive':
        contract_data = get_data_from_google_drive('contract')
    else:
        return "Invalid data source", 400

    if contract_data is None:
        return "Error: No se pudo cargar los datos de los contratos", 500

    current_lang = request.args.get('lang', 'eng')

    return render_template('contract_list.html',
                         contracts=contract_data['contracts'],
                         active_page='contracts',
                         current_lang=current_lang)

@contracts_blueprint.route('/generate_all_contracts', methods=['GET'])
def generate_all_contracts():

    data_source = session.get('data_source', 'local')

    if data_source == 'local':
        contract_data = get_data_from_local('contract')
    elif data_source == 'google_drive':
        contract_data = get_data_from_google_drive('contract')
    else:
        return "Invalid data source", 400

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
                # Renderizar la plantilla con el idioma correspondiente
                rendered = render_template('contract.html', data=contract, lang=lang)

                # Generar PDF con el idioma en el nombre
                pdf_filename = f"contract_{contract['contract']['number']}_{lang}.pdf"
                pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_filename)
                HTML(string=rendered, base_url=base_url).write_pdf(pdf_path)
                generated_files['pdf'].append(pdf_filename)


                # Generar XML con el idioma en el nombre
                xml_filename = f"contract_{contract['contract']['number']}_{lang}.xml"
                xml_path = os.path.join('examples', 'contract', 'xml', xml_filename)
                generate_contract_xml(contract, xml_path)
                generated_files['xml'].append(xml_filename)

            except Exception as e:
                print(f"Error generando contrato {contract['contract']['number']} en {lang}: {str(e)}")
                continue

    return {
        "message": "Todos los contratos fueron generados con éxito en PDF, PNG y XML para ambos idiomas",
        "files": generated_files,
        "locations": {
            "pdf": "examples/contract/",
            "xml": "examples/contract/"
        }
    }
