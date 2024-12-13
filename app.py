from flask import Flask, render_template, send_from_directory, request
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
            data = json.load(file)
            print("Datos cargados:", data)  # Debug print
            return data
    except Exception as e:
        print(f"Error al leer JSON: {str(e)}")
        return None

@app.route('/')
def home():
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de la factura", 500
    print("Datos para el template:", invoice_data)  # Debug print
    return render_template('invoice.html', data=invoice_data)

@app.route('/generate_invoice')
def generate_invoice():
    invoice_data = get_invoice_data()
    if invoice_data is None:
        return "Error: No se pudo cargar los datos de la factura", 500

    print("Datos para generar PDF:", invoice_data)  # Debug print
    rendered = render_template('invoice.html', data=invoice_data)

    pdf_path = os.path.join('examples', 'invoice.pdf')
    HTML(string=rendered, base_url=request.base_url).write_pdf(pdf_path)

    return "Factura generada con éxito en /examples/invoice.pdf"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=True)

