from flask import Blueprint, request, render_template
from controllers.invoices import generate_all_invoices
from controllers.contracts import generate_all_contracts
from controllers.deliveries import generate_all_deliveries
from services.drive_service import upload_to_drive
import os

documents_blueprint = Blueprint('documents', __name__)

@documents_blueprint.route('/generate_all_documents', methods=['GET'])
def generate_all_documents():
    results = {}

    # Generar y subir facturas
    try:
        invoice_result = generate_all_invoices()
        if isinstance(invoice_result, dict) and 'files' in invoice_result:
            for pdf_file in invoice_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'invoices', 'pdf', pdf_file)
                upload_to_drive(pdf_path, None)  # Subir a Google Drive (raíz o carpeta especificada)
            for png_file in invoice_result['files']['png']:
                png_path = os.path.join('examples', 'invoices', 'png', png_file)
                upload_to_drive(png_path, None)
            for xml_file in invoice_result['files']['xml']:
                xml_path = os.path.join('examples', 'invoices', 'xml', xml_file)
                upload_to_drive(xml_path, None)
        results['invoices'] = invoice_result
    except Exception as e:
        results['invoices'] = {"error": str(e)}

    # Generar y subir contratos
    try:
        contract_result = generate_all_contracts()
        if isinstance(contract_result, dict) and 'files' in contract_result:
            for pdf_file in contract_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'contract', 'pdf', pdf_file)
                upload_to_drive(pdf_path, None)
            for xml_file in contract_result['files']['xml']:
                xml_path = os.path.join('examples', 'contract', 'xml', xml_file)
                upload_to_drive(xml_path, None)
        results['contracts'] = contract_result
    except Exception as e:
        results['contracts'] = {"error": str(e)}

    # Generar y subir actas de entrega
    try:
        delivery_result = generate_all_deliveries()
        if isinstance(delivery_result, dict) and 'files' in delivery_result:
            for pdf_file in delivery_result['files']['pdf']:
                pdf_path = os.path.join('examples', 'deliveries', 'pdf', pdf_file)
                upload_to_drive(pdf_path, None)
            for png_file in delivery_result['files']['png']:
                png_path = os.path.join('examples', 'deliveries', 'png', png_file)
                upload_to_drive(png_path, None)
            for xml_file in delivery_result['files']['xml']:
                xml_path = os.path.join('examples', 'deliveries', 'xml', xml_file)
                upload_to_drive(xml_path, None)
        results['deliveries'] = delivery_result
    except Exception as e:
        results['deliveries'] = {"error": str(e)}

    return {
        "message": "Todos los documentos fueron generados y subidos con éxito a Google Drive.",
        "results": results
    }