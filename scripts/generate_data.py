import random
import os
import json
from faker import Faker
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

fake_en = Faker("en_US")
fake_es = Faker("es_ES")

VALID_RUCS = [
    "1793168604001", "1757541519001", "1792256267001", "1790012345001", "1701234567001",
    "0101234540001", "0201234580001", "0301234530001", "0401234570001", "0501234520001",
    "0601234560001", "0701234510001", "0801234550001", "0901234500001", "1001234580001"
]

ACCOUNTING_POSITIONS_EN = [
    "Accounting Manager",
    "Accounts Payable Clerk",
    "Accounts Receivable Clerk",
    "Tax Accountant",
    "Payroll Specialist",
    "Financial Analyst",
    "Internal Auditor",
    "Cost Accountant",
    "Budget Analyst",
    "Financial Controller"
]

ACCOUNTING_POSITIONS_ES = [
    "Gerente de Contabilidad",
    "Asistente de Cuentas por Pagar",
    "Asistente de Cuentas por Cobrar",
    "Contador de Impuestos",
    "Especialista de Nómina",
    "Analista Financiero",
    "Auditor Interno",
    "Contador de Costos",
    "Analista Presupuestario",
    "Controlador Financiero"
]

SIGNATURE_DIR = "../static/signatures"

def generate_signature(name, filename):
    """Generar una imagen de firma realista basada en un nombre."""
    if not os.path.exists(SIGNATURE_DIR):
        os.makedirs(SIGNATURE_DIR)

    # Ruta a la fuente de firma (asegúrate de que exista)
    font_path = "../static/fonts/signature.ttf"
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

def generate_hes(index):
    last3 = str(index + 1).zfill(3)
    return f"81234{last3}"

def generate_random_invoice_and_delivery_data_and_contract_data_eng(num_invoices=900):
    invoices = []
    deliveries = []
    contracts = []

    base_client_data_en = {
        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
        "ruc": "1791239245001",
        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
        "city": "Quito",
        "country": "Ecuador"
    }

    for i in range(num_invoices):
        company_name_en = fake_en.company().replace(",", "").replace(".", "").lower()
        united_company_name_en = company_name_en.replace(" ", "")
        quantity = random.randint(1, 5)
        unit_cost = round(random.uniform(20, 500), 2)
        before_tax = round(quantity * unit_cost, 2)
        tax_rate = 18
        tax = round(before_tax * tax_rate / 100, 2)
        total_due = round(before_tax + tax, 2)

        invoice_date_obj = fake_en.date_this_year()
        max_payable_days = 30
        payable_at_date = invoice_date_obj + timedelta(days=random.randint(0, max_payable_days))

        company_data_en = {
            "name": company_name_en,
            "ruc": random.choice(VALID_RUCS),
            "address": fake_en.address().replace("\n", ", "),
            "city": fake_en.city(),
            "country": fake_en.country(),
            "phone": fake_en.phone_number(),
            "website": f"www.{united_company_name_en}.com",
            "email": f"info@{united_company_name_en}.com",
            "taxId": fake_en.ean8()
        }

        enap_employee_name_en = fake_en.name()
        enap_employee_position_en = random.choice(ACCOUNTING_POSITIONS_EN)
        enap_signature_filename_en = f"enap_signature_{i+1}.png"
        enap_signature_path_en = generate_signature(enap_employee_name_en, enap_signature_filename_en)

        client_data_en = dict(base_client_data_en)
        client_data_en["employee_name"] = enap_employee_name_en
        client_data_en["employee_position"] = enap_employee_position_en
        client_data_en["employee_signature"] = enap_signature_path_en

        in_charge_name_en = fake_en.name()
        in_charge_position_en = random.choice(ACCOUNTING_POSITIONS_EN)
        generic_signature_filename_en = f"signature{i+1}_.png"
        signature_path_en = generate_signature(in_charge_name_en, generic_signature_filename_en)

        client_data_en["in_charge_info"] = {
            "name": in_charge_name_en,
            "position": in_charge_position_en,
            "signature": signature_path_en
        }

        invoice_en = {
            "company": company_data_en,
            "invoice": {
                "number": f"INV-{i+1:03}",
                "date": invoice_date_obj.isoformat(),
                "payableAt": payable_at_date.isoformat(),
                "orderNumber": f"ORD-{i+1:03}"
            },
            "client": client_data_en,
            "items": [
                {
                    "code": f"PROD-{chr(65 + (i % 26))}1",
                    "description": fake_en.sentence(), 
                    "hes": generate_hes(i),
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
            },
            "in_charge_info": {
                "name": in_charge_name_en,
                "position": in_charge_position_en,
                "signature": signature_path_en
            }
        }

        delivery_en = {
            "receiver": {
                "name": base_client_data_en["name"],
                "from": company_data_en["name"],
                "ruc": company_data_en["ruc"],
                "invoiceNumber": invoice_en["invoice"]["number"],
                "hes": invoice_en["items"][0]["hes"],
                "orderNumber": invoice_en["invoice"]["orderNumber"],
                "date": invoice_date_obj.isoformat(),
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "price": invoice_en["totals"]["totalDue"],
                "employee_name": enap_employee_name_en,
                "employee_position": enap_employee_position_en,
                "employee_signature": enap_signature_path_en
            }
        }

        contract_data_en = {
            "company": company_data_en,
            "client": client_data_en,
            "items": invoice_en["items"],
            "totals": invoice_en["totals"],
            "contract": {
                "number": f"CNT-{i+1:03}",
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "invoiceNumber": invoice_en["invoice"]["number"],
                "hes": invoice_en["items"][0]["hes"],
                "orderNumber": invoice_en["invoice"]["orderNumber"],
            },
        }

        invoices.append(invoice_en)
        deliveries.append(delivery_en)
        contracts.append(contract_data_en)

    return (
        {"invoices": invoices, "enap": [base_client_data_en]},
        {"deliveries": deliveries},
        {"contracts": contracts, "enap": [base_client_data_en]}
    )


def generate_random_invoice_and_delivery_data_and_contract_data_esp(num_invoices=900):
    invoices = []
    deliveries = []
    contracts = []

    base_client_data_esp = {
        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
        "ruc": "1791239245001",
        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
        "city": "Quito",
        "country": "Ecuador"
    }

    for i in range(num_invoices):
        company_name_esp = fake_es.company().replace(",", "").replace(".", "").lower()
        united_company_name_esp = company_name_esp.replace(" ", "")
        quantity = random.randint(1, 5)
        unit_cost = round(random.uniform(20, 500), 2)
        before_tax = round(quantity * unit_cost, 2)
        tax_rate = 18
        tax = round(before_tax * tax_rate / 100, 2)
        total_due = round(before_tax + tax, 2)

        invoice_date_obj = fake_es.date_this_year()
        max_payable_days = 30
        payable_at_date = invoice_date_obj + timedelta(days=random.randint(0, max_payable_days))

        company_data_esp = {
            "name": company_name_esp,
            "ruc": random.choice(VALID_RUCS),
            "address": fake_es.address().replace("\n", ", "),
            "city": fake_es.city(),
            "country": fake_es.country(),
            "phone": fake_es.phone_number(),
            "website": f"www.{united_company_name_esp}.com",
            "email": f"info@{united_company_name_esp}.com",
            "taxId": fake_es.ean8()
        }

        enap_employee_name_esp = fake_es.name()
        enap_employee_position_esp = random.choice(ACCOUNTING_POSITIONS_ES)
        enap_signature_filename_esp = f"enap_signature_{i+1}.png"
        enap_signature_path_esp = generate_signature(enap_employee_name_esp, enap_signature_filename_esp)

        client_data_esp = dict(base_client_data_esp)
        client_data_esp["employee_name"] = enap_employee_name_esp
        client_data_esp["employee_position"] = enap_employee_position_esp
        client_data_esp["employee_signature"] = enap_signature_path_esp

        in_charge_name_esp = fake_es.name()
        in_charge_position_esp = random.choice(ACCOUNTING_POSITIONS_ES)
        generic_signature_filename_esp = f"signature{i+1}_.png"
        signature_path_esp = generate_signature(in_charge_name_esp, generic_signature_filename_esp)

        client_data_esp["in_charge_info"] = {
            "name": in_charge_name_esp,
            "position": in_charge_position_esp,
            "signature": signature_path_esp
        }

        invoice_esp = {
            "company": company_data_esp,
            "invoice": {
                "number": f"INV-{i+1:03}",
                "date": invoice_date_obj.isoformat(),
                "payableAt": payable_at_date.isoformat(),
                "orderNumber": f"ORD-{i+1:03}"
            },
            "client": client_data_esp,
            "items": [
                {
                    "code": f"PROD-{chr(65 + (i % 26))}1",
                    "description": fake_es.sentence(),
                    "hes": generate_hes(i),
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
            },
            "in_charge_info": {
                "name": in_charge_name_esp,
                "position": in_charge_position_esp,
                "signature": signature_path_esp
            }
        }

        delivery_esp = {
            "receiver": {
                "name": base_client_data_esp["name"],
                "from": company_data_esp["name"],
                "ruc": company_data_esp["ruc"],
                "invoiceNumber": invoice_esp["invoice"]["number"],
                "hes": invoice_esp["items"][0]["hes"],
                "orderNumber": invoice_esp["invoice"]["orderNumber"],
                "date": invoice_date_obj.isoformat(),
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "price": invoice_esp["totals"]["totalDue"],
                "employee_name": enap_employee_name_esp,
                "employee_position": enap_employee_position_esp,
                "employee_signature": enap_signature_path_esp
            }
        }

        contract_data_esp = {
            "company": company_data_esp,
            "client": client_data_esp,
            "items": invoice_esp["items"],
            "totals": invoice_esp["totals"],
            "contract": {
                "number": f"CNT-{i+1:03}",
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "invoiceNumber": invoice_esp["invoice"]["number"],
                "hes": invoice_esp["items"][0]["hes"],
                "orderNumber": invoice_esp["invoice"]["orderNumber"],
            },
        }

        invoices.append(invoice_esp)
        deliveries.append(delivery_esp)
        contracts.append(contract_data_esp)

    return (
        {"invoices": invoices, "enap": [base_client_data_esp]},
        {"deliveries": deliveries},
        {"contracts": contracts, "enap": [base_client_data_esp]}
    )

def save_to_json(data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    invoice_data_en, delivery_data_en, contract_data_en = generate_random_invoice_and_delivery_data_and_contract_data_eng(900)
    save_to_json(invoice_data_en, '../static/data-eng/invoice-data.json')
    print("Datos de facturas (inglés) generados en invoice-data.json (data-eng)")

    save_to_json(delivery_data_en, '../static/data-eng/delivery-data.json')
    print("Datos de actas de recepción (inglés) generados en delivery-data.json (data-eng)")

    save_to_json(contract_data_en, '../static/data-eng/contract-data.json')
    print("Datos de contratos (inglés) generados en contract-data.json (data-eng)")

    invoice_data_es, delivery_data_es, contract_data_es = generate_random_invoice_and_delivery_data_and_contract_data_esp(900)
    save_to_json(invoice_data_es, '../static/data-esp/invoice-data.json')
    print("Datos de facturas (español) generados en invoice-data.json (data-esp)")

    save_to_json(delivery_data_es, '../static/data-esp/delivery-data.json')
    print("Datos de actas de recepción (español) generados en delivery-data.json (data-esp)")

    save_to_json(contract_data_es, '../static/data-esp/contract-data.json')
    print("Datos de contratos (español) generados en contract-data.json (data-esp)")