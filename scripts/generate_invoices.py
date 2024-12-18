import random
import os
import json
from faker import Faker
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

fake = Faker()

# Lista de RUCs permitidos
VALID_RUCS = [
    "1793168604001", "1757541519001", "1792256267001", "1790012345001", "1701234567001",
    "0101234540001", "0201234580001", "0301234530001", "0401234570001", "0501234520001",
    "0601234560001", "0701234510001", "0801234550001", "0901234500001", "1001234580001"
]

# Directorio donde se guardarán las imágenes de firmas
SIGNATURE_DIR = "../static/signatures"

def generate_signature(name, filename):
    """Generar una imagen de firma realista basada en un nombre."""
    if not os.path.exists(SIGNATURE_DIR):
        os.makedirs(SIGNATURE_DIR)

    # Ruta a la fuente de firma
    font_path = "../static/fonts/signature.ttf"  # Asegúrate de tener la fuente
    image_path = os.path.join(SIGNATURE_DIR, filename)

    try:
        # Crear una imagen en blanco
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Usar una fuente personalizada
        font = ImageFont.truetype(font_path, 48)

        # Dibujar el texto de la firma
        draw.text((10, 25), name, font=font, fill=(0, 0, 0))

        # Guardar la imagen
        img.save(image_path, "PNG")
        return image_path
    except Exception as e:
        print(f"Error al generar firma: {e}")
        return None

def generate_random_invoice_and_delivery_data_and_contract_data(num_invoices=900):
    invoices = []
    deliveries = []
    contracts = []
    client_data = {
        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
        "ruc": "1791239245001",
        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
        "city": "Quito",
        "country": "Ecuador"
    }

    for i in range(num_invoices):
        company_name = fake.company().replace(",", "").replace(".", "").lower()
        united_company_name = company_name.replace(" ", "")
        quantity = random.randint(1, 5)
        unit_cost = round(random.uniform(20, 200), 2)
        before_tax = round(quantity * unit_cost, 2)
        tax_rate = 18
        tax = round(before_tax * tax_rate / 100, 2)
        total_due = round(before_tax + tax, 2)

        # Generar la fecha "date" y "payableAt"
        invoice_date_obj = fake.date_this_year()  # Ya es un objeto datetime.date
        max_payable_days = 30
        payable_at_date = invoice_date_obj + timedelta(days=random.randint(0, max_payable_days))

        # Generar firma
        in_charge_name = fake.name()
        signature_filename = f"signature_{i+1}.png"
        signature_path = generate_signature(in_charge_name, signature_filename)

        # Crear factura
        invoice = {
            "company": {
                "name": company_name,
                "ruc": random.choice(VALID_RUCS),
                "address": fake.address(),
                "city": fake.city(),
                "country": fake.country(),
                "phone": fake.phone_number(),
                "website": f"www.{united_company_name}.com",
                "email": f"info@{united_company_name}.com",
                "taxId": fake.ean8()
            },
            "invoice": {
                "number": f"INV-{i+1:03}",
                "date": invoice_date_obj.isoformat(),  # Convertir a string ISO
                "payableAt": payable_at_date.isoformat(),  # Convertir a string ISO
                "orderNumber": f"ORD-{i+1:03}"
            },
            "client": client_data,
            "items": [
                {
                    "code": f"PROD-{chr(65 + (i % 26))}1",
                    "description": fake.catch_phrase(),
                    "hes": fake.ean8(),
                    "quantity": quantity,
                    "unitCost": unit_cost,
                    "cost": before_tax
                }
            ],
            "totals": {
                "beforeTax": before_tax,
                "taxRate": tax_rate,
                "tax": tax,
                "totalDue": total_due
            }
        }

        # Crear acta de recepción (delivery)
        delivery = {
            "receiver": {
                "name": client_data["name"],
                "from": invoice["company"]["name"],
                "ruc": invoice["company"]["ruc"],
                "invoiceNumber": invoice["invoice"]["number"],
                "hes": invoice["items"][0]["hes"],  # Arreglo: Acceder al primer ítem
                "orderNumber": invoice["invoice"]["orderNumber"],
                "date": invoice_date_obj.isoformat(),
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "price": invoice["totals"]["totalDue"],
                "inCharge": in_charge_name,
                "position": fake.job(),
                "firma": signature_path
            }
        }

        contracts_data = {
            "company": invoice["company"],
            "client": client_data,
            "items": invoice["items"],
            "totals": invoice["totals"]
        }

        invoices.append(invoice)
        deliveries.append(delivery)
        contracts.append(contracts_data)

    return {"invoices": invoices, "enap": [client_data]}, {"deliveries": deliveries}, {"contracts": contracts, "enap": [client_data]}

def save_to_json(data, filename):
    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # Generar datos
    invoice_data, delivery_data, contract_data = generate_random_invoice_and_delivery_data_and_contract_data(900)

    # Guardar facturas
    save_to_json(invoice_data, '../static/data/invoice-data.json')
    print("Datos de facturas generados y guardados en invoice-data.json")

    # Guardar actas de recepción
    save_to_json(delivery_data, '../static/data/delivery-data.json')
    print("Datos de actas de recepción generados y guardados en delivery-data.json")

    # Guardar contratos
    save_to_json(contract_data, '../static/data/contract-data.json')
    print("Datos de contratos generados y guardados en contract-data.json")