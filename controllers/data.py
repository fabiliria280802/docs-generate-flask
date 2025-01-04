from flask import Blueprint, jsonify, session
import random
import os
import json
from faker import Faker
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from services.drive_service import create_folder, upload_to_drive
from services.utils import save_to_json


fake_en = Faker("en_US")
fake_es = Faker("es_ES")

data_blueprint = Blueprint('data', __name__)

def generate_signature(name, filename, lang="en"):
    """Generar una imagen de firma realista basada en un nombre y guardar en carpetas según idioma."""
    # Directorio específico para el idioma
    lang_dir = os.path.join(SIGNATURE_DIR, lang)
    if not os.path.exists(lang_dir):
        os.makedirs(lang_dir)

    # Ruta al archivo de la firma
    image_path = os.path.join(lang_dir, filename)

    # Ruta relativa del archivo para guardar solo el nombre
    relative_path = filename

    try:
        # Ruta a la fuente de firma (asegúrate de que exista)
        font_path = "../static/fonts/signature.ttf"

        # Crear una imagen en blanco
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        # Usar una fuente personalizada
        font = ImageFont.truetype(font_path, 48)

        # Dibujar el texto de la firma
        draw.text((10, 25), name, font=font, fill=(0, 0, 0))

        # Guardar la imagen
        img.save(image_path, "PNG")
        return relative_path  # Devuelve solo el nombre del archivo
    except Exception as e:
        print(f"Error al generar firma: {e}")
        return None

def generate_hes(index):
    last5 = str(index + 1).zfill(5)
    return f"812{last5}"

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

        # Generar entre 1 y 5 ítems
        num_items = random.randint(1, 5)
        items = []
        before_tax = 0

        for j in range(num_items):
            quantity = random.randint(1, 10)
            unit_cost = round(random.uniform(20, 500), 2)
            cost = round(quantity * unit_cost, 2)
            before_tax += round(cost, 2)
            service_description = random.choice(SERVICE_DESCRIPTION_EN)

            item = {
                "code": f"36{chr(65 + (i % 26))}{j+1}",
                "description": service_description,
                "hes": generate_hes(i),
                "quantity": quantity,
                "unitCost": unit_cost,
                "cost": cost
            }
            items.append(item)

        # Calcular impuestos y total
        tax_rate = 15
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
        enap_signature_path_en = generate_signature(enap_employee_name_en, enap_signature_filename_en, lang="en")

        client_data_en = dict(base_client_data_en)
        client_data_en["employee_name"] = enap_employee_name_en
        client_data_en["employee_position"] = enap_employee_position_en
        client_data_en["employee_signature"] = enap_signature_filename_en

        in_charge_name_en = fake_en.name()
        in_charge_position_en = random.choice(ACCOUNTING_POSITIONS_EN)
        generic_signature_filename_en = f"signature{i+1}_.png"
        signature_path_en = generate_signature(in_charge_name_en, generic_signature_filename_en, lang="en")

        client_data_en["in_charge_info"] = {
            "name": in_charge_name_en,
            "position": in_charge_position_en,
            "signature": signature_path_en
        }

        invoice_en = {
            "company": company_data_en,
            "invoice": {
                "number": f"11{i+1:05}",
                "date": invoice_date_obj.isoformat(),
                "payableAt": payable_at_date.isoformat(),
                "orderNumber": f"34{i+1:05}"
            },
            "client": client_data_en,
            "items": items,
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
                "number": f"14{i+1:05}",
                "name": base_client_data_en["name"],
                "from": company_data_en["name"],
                "ruc": company_data_en["ruc"],
                "invoiceNumber": invoice_en["invoice"]["number"],
                "hes": items[0]["hes"],  # Usar el HES del primer ítem
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
            "items": items,
            "totals": invoice_en["totals"],
            "contract": {
                "number": f"65{i+1:05}",
                "startDate": invoice_en["invoice"]["date"],
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "invoiceNumber": invoice_en["invoice"]["number"],
                "hes": items[0]["hes"],
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

        # Generar entre 1 y 5 ítems
        num_items = random.randint(1, 5)
        items = []
        before_tax = 0

        for j in range(num_items):
            quantity = random.randint(1, 10)
            unit_cost = round(random.uniform(20, 500), 2)
            cost = round(quantity * unit_cost, 2)
            before_tax += round(cost, 2)
            service_description = random.choice(SERVICE_DESCRIPTION_ES)

            item = {
                "code": f"36{chr(65 + (i % 26))}{j+1}",
                "description": service_description,
                "hes": generate_hes(i),
                "quantity": quantity,
                "unitCost": unit_cost,
                "cost": cost
            }
            items.append(item)

        # Calcular impuestos y total
        tax_rate = 15
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
        enap_signature_path_esp = generate_signature(enap_employee_name_esp, enap_signature_filename_esp, lang="es")

        client_data_esp = dict(base_client_data_esp)
        client_data_esp["employee_name"] = enap_employee_name_esp
        client_data_esp["employee_position"] = enap_employee_position_esp
        client_data_esp["employee_signature"] = enap_signature_filename_esp

        in_charge_name_esp = fake_es.name()
        in_charge_position_esp = random.choice(ACCOUNTING_POSITIONS_ES)
        generic_signature_filename_esp = f"signature{i+1}_.png"
        signature_path_esp = generate_signature(in_charge_name_esp, generic_signature_filename_esp, lang="es")

        client_data_esp["in_charge_info"] = {
            "name": in_charge_name_esp,
            "position": in_charge_position_esp,
            "signature": signature_path_esp
        }

        invoice_esp = {
            "company": company_data_esp,
            "invoice": {
                "number": f"11{i+1:05}",
                "date": invoice_date_obj.isoformat(),
                "payableAt": payable_at_date.isoformat(),
                "orderNumber": f"34{i+1:05}"
            },
            "client": client_data_esp,
            "items": items,
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
                "number": f"14{i+1:05}",
                "name": base_client_data_esp["name"],
                "from": company_data_esp["name"],
                "ruc": company_data_esp["ruc"],
                "invoiceNumber": invoice_esp["invoice"]["number"],
                "hes": items[0]["hes"],  # Usar el HES del primer ítem
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
            "items": items,
            "totals": invoice_esp["totals"],
            "contract": {
                "number": f"65{i+1:05}",
                "startDate": invoice_esp["invoice"]["date"],
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "invoiceNumber": invoice_esp["invoice"]["number"],
                "hes": items[0]["hes"],
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

def generate_and_save_data_to_drive():
    # Generar datos
    invoice_data_en, delivery_data_en, contract_data_en = generate_random_invoice_and_delivery_data_and_contract_data_eng(900)
    invoice_data_es, delivery_data_es, contract_data_es = generate_random_invoice_and_delivery_data_and_contract_data_esp(900)

    # Crear estructura de carpetas en Google Drive
    static_folder_id = create_folder('static')
    data_eng_folder_id = create_folder('data-eng', static_folder_id)
    data_esp_folder_id = create_folder('data-esp', static_folder_id)

    # Guardar datos localmente y subirlos a Google Drive
    local_paths = {
        "invoice_en": "../static/data-eng/invoice-data.json",
        "delivery_en": "../static/data-eng/delivery-data.json",
        "contract_en": "../static/data-eng/contract-data.json",
        "invoice_es": "../static/data-esp/invoice-data.json",
        "delivery_es": "../static/data-esp/delivery-data.json",
        "contract_es": "../static/data-esp/contract-data.json",
    }

    save_to_json(invoice_data_en, local_paths["invoice_en"])
    upload_to_drive(local_paths["invoice_en"], data_eng_folder_id)

    save_to_json(delivery_data_en, local_paths["delivery_en"])
    upload_to_drive(local_paths["delivery_en"], data_eng_folder_id)

    save_to_json(contract_data_en, local_paths["contract_en"])
    upload_to_drive(local_paths["contract_en"], data_eng_folder_id)

    save_to_json(invoice_data_es, local_paths["invoice_es"])
    upload_to_drive(local_paths["invoice_es"], data_esp_folder_id)

    save_to_json(delivery_data_es, local_paths["delivery_es"])
    upload_to_drive(local_paths["delivery_es"], data_esp_folder_id)

    save_to_json(contract_data_es, local_paths["contract_es"])
    upload_to_drive(local_paths["contract_es"], data_esp_folder_id)

    return "Datos generados y guardados con éxito en local y Google Drive."

@data_blueprint.route('/generate_data', methods=['POST'])
def generate_data():
    try:
        message = generate_and_save_data_to_drive()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500