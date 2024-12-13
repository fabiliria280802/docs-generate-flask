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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)

