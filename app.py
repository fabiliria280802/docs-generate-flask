from flask import Flask, render_template, send_from_directory, request, jsonify
from weasyprint import HTML
import os
import json

app = Flask(__name__)

# Create necessary directories if they don't exist
required_dirs = ["static/data", "static/assets", "examples"]
for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_invoice_data():
    try:
        json_path = os.path.join('static', 'data', 'invoice-data.json')
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al leer JSON: {str(e)}")
        return None

@app.route('/')
def home():
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500
    # Mostrar la lista de facturas disponibles
    return render_template('invoice_list.html', invoices=invoice_data['invoices'])

@app.route('/invoice/<int:index>')
def show_invoice(index):
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        invoice = invoice_data['invoices'][index]
        company_name = invoice['company']['name'].lower().replace(' ', '')
        print(f"Mostrando factura para compañía: {company_name}")  # Debug
        return render_template('invoice.html', data=invoice)
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_invoice/<int:index>')
def generate_invoice(index):
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    try:
        invoice = invoice_data['invoices'][index]
        rendered = render_template('invoice.html', data=invoice)

        # Crear nombre de archivo único basado en el número de factura
        filename = f"invoice_{invoice['invoice']['number']}.pdf"
        pdf_path = os.path.join('examples', filename)

        HTML(string=rendered, base_url=request.base_url).write_pdf(pdf_path)
        return f"Factura generada con éxito en /examples/{filename}"
    except IndexError:
        return "Factura no encontrada", 404

@app.route('/generate_all_invoices')
def generate_all_invoices():
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de las facturas", 500

    generated_files = []
    for index, invoice in enumerate(invoice_data['invoices']):
        rendered = render_template('invoice.html', data=invoice)
        filename = f"invoice_{invoice['invoice']['number']}.pdf"
        pdf_path = os.path.join('examples', filename)
        HTML(string=rendered, base_url=request.base_url).write_pdf(pdf_path)
        generated_files.append(filename)

    return jsonify({
        "message": "Todas las facturas fueron generadas con éxito",
        "files": generated_files
    })

@app.route('/check_logos')
def check_logos():
    logos_dir = os.path.join(os.path.dirname(__file__), 'static', 'assets')
    available_logos = os.listdir(logos_dir)

    invoice_data = get_invoice_data()
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
    invoice_data = get_invoice_data()
    if invoice_data and 'invoices' in invoice_data:
        return jsonify({
            'total_invoices': len(invoice_data['invoices']),
            'companies': [inv['company']['name'] for inv in invoice_data['invoices']]
        })
    return "No hay datos", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)

