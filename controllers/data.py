from flask import Blueprint, jsonify, session
import random
import os
import json
from faker import Faker
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from services.drive_service import create_folder, upload_to_drive, get_or_create_folder, upload_font_to_drive, download_font_from_drive
from services.utils import save_to_json


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

SERVICE_DESCRIPTION_EN = [
    "Cloud infrastructure optimization",
    "IT security assessment and penetration testing",
    "Data analytics and business intelligence",
    "Custom software development",
    "IT support and helpdesk services",
    "Cybersecurity consulting and risk assessment",
    "Digital transformation strategy",
    "Network architecture and implementation",
    "Database design and management",
    "System integration services",
    "Software quality assurance and testing",
    "Backup and disaster recovery solutions",
    "Enterprise resource planning (ERP) implementation",
    "Customer relationship management (CRM) solutions",
    "Website design and development",
    "Mobile app development",
    "Blockchain integration and consulting",
    "Machine learning model development",
    "IT project management",
    "Cloud migration services",
    "IT infrastructure auditing",
    "Big data solutions and strategy",
    "Managed IT services",
    "Technology roadmap planning",
    "IoT solutions and implementation",
    "Compliance and regulatory consulting",
    "Virtualization and containerization",
    "Digital marketing strategy and SEO",
    "Identity and access management solutions",
    "Artificial intelligence consulting",
    "Data migration and conversion services",
    "IT policy and governance consulting",
    "Supply chain optimization with IT tools",
    "Video conferencing and collaboration tools setup",
    "Open-source technology consulting",
    "Business continuity planning",
    "API development and integration",
    "E-commerce platform design",
    "Technology cost optimization",
    "Legacy system modernization",
    "Application performance monitoring and optimization",
    "Remote work enablement solutions",
    "IT asset management",
    "DevOps pipeline setup and automation",
    "Virtual private network (VPN) implementation",
    "Data warehouse design and optimization",
    "Training and workshops on emerging technologies",
    "IT staffing and recruitment services",
    "Technical documentation and user manuals",
    "Virtual reality and augmented reality solutions",
    "IT strategy consulting"
]

SERVICE_DESCRIPTION_ES = [
    "Optimización de infraestructura en la nube",
    "Evaluación de seguridad informática y pruebas de penetración",
    "Análisis de datos e inteligencia empresarial",
    "Desarrollo de software personalizado",
    "Soporte técnico y servicios de helpdesk",
    "Consultoría en ciberseguridad y evaluación de riesgos",
    "Estrategia de transformación digital",
    "Arquitectura de redes e implementación",
    "Diseño y gestión de bases de datos",
    "Servicios de integración de sistemas",
    "Garantía de calidad y pruebas de software",
    "Soluciones de respaldo y recuperación ante desastres",
    "Implementación de planificación de recursos empresariales (ERP)",
    "Soluciones de gestión de relaciones con clientes (CRM)",
    "Diseño y desarrollo de sitios web",
    "Desarrollo de aplicaciones móviles",
    "Integración y consultoría en blockchain",
    "Desarrollo de modelos de aprendizaje automático",
    "Gestión de proyectos de TI",
    "Servicios de migración a la nube",
    "Auditoría de infraestructura de TI",
    "Soluciones y estrategia de big data",
    "Servicios de TI gestionados",
    "Planificación de hoja de ruta tecnológica",
    "Soluciones e implementación de IoT",
    "Consultoría en cumplimiento normativo",
    "Virtualización y contenedores",
    "Estrategia de marketing digital y SEO",
    "Soluciones de gestión de identidad y acceso",
    "Consultoría en inteligencia artificial",
    "Servicios de migración y conversión de datos",
    "Consultoría en políticas y gobernanza de TI",
    "Optimización de la cadena de suministro con herramientas de TI",
    "Configuración de herramientas de videoconferencia y colaboración",
    "Consultoría en tecnologías de código abierto",
    "Planificación de continuidad empresarial",
    "Desarrollo e integración de APIs",
    "Diseño de plataformas de comercio electrónico",
    "Optimización de costos tecnológicos",
    "Modernización de sistemas heredados",
    "Monitoreo y optimización del rendimiento de aplicaciones",
    "Soluciones para habilitar el trabajo remoto",
    "Gestión de activos de TI",
    "Configuración de pipelines DevOps y automatización",
    "Implementación de redes privadas virtuales (VPN)",
    "Diseño y optimización de almacenes de datos",
    "Capacitación y talleres sobre tecnologías emergentes",
    "Servicios de reclutamiento y selección de personal de TI",
    "Documentación técnica y manuales de usuario",
    "Soluciones de realidad virtual y aumentada",
    "Consultoría en estrategia de TI"
]


data_blueprint = Blueprint('data', __name__)

def ensure_font_availability(file_name, local_path, folder_name="static/fonts"):
    """
    Asegura que la fuente esté disponible tanto localmente como en Google Drive.
    Si no está localmente, la descarga de Google Drive.
    Si no está en Google Drive, la sube desde el sistema local.
    """
    # Verificar si el archivo existe localmente
    if os.path.exists(local_path):
        print(f"Fuente encontrada localmente en {local_path}. Verificando en Google Drive...")
        upload_font_to_drive(file_name, local_path, folder_name)
        return local_path

    # Intentar descargar desde Google Drive
    print(f"Archivo de fuente no encontrado localmente. Intentando descargar de Google Drive...")
    downloaded_path = download_font_from_drive(file_name, local_path)
    if downloaded_path:
        return downloaded_path

    print(f"Fuente no disponible en local ni en Google Drive. Por favor, asegúrate de cargarla manualmente.")
    return None


def generate_signature(name, filename, lang="en", upload_to_cloud=True):
    """Generar una imagen de firma realista y subirla a Google Drive si es necesario."""
    lang_dir = os.path.join(SIGNATURE_DIR, lang)
    if not os.path.exists(lang_dir):
        os.makedirs(lang_dir)

    image_path = os.path.join(lang_dir, filename)
    relative_path = filename

    try:
        # Construir la ruta absoluta de la fuente
        base_dir = os.path.dirname(__file__)
        font_path = os.path.abspath(os.path.join(base_dir, "../static/fonts/signature.ttf"))
        font_path = ensure_font_availability("signature.ttf", font_path)

        if not font_path:
            print("No se pudo encontrar o garantizar la disponibilidad de la fuente.")
            return None

        # Crear imagen
        img = Image.new('RGBA', (400, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, 48)
        draw.text((10, 25), name, font=font, fill=(0, 0, 0))
        img.save(image_path, "PNG")
        print(f"Firma guardada localmente en {image_path}")

        if upload_to_cloud:
            signature_folder_id = get_or_create_folder("static/signature")
            if signature_folder_id:
                upload_to_drive(image_path, signature_folder_id)
                print(f"Firma subida a Google Drive: {filename}")

        return relative_path
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

def generate_and_save_data_to_drive(local_only=True):
    # Generar datos
    invoice_data_en, delivery_data_en, contract_data_en = generate_random_invoice_and_delivery_data_and_contract_data_eng(900)
    invoice_data_es, delivery_data_es, contract_data_es = generate_random_invoice_and_delivery_data_and_contract_data_esp(900)

    # Guardar en local
    save_to_json(invoice_data_en, '../static/data-eng/invoice-data.json')
    save_to_json(delivery_data_en, '../static/data-eng/delivery-data.json')
    save_to_json(contract_data_en, '../static/data-eng/contract-data.json')
    save_to_json(invoice_data_es, '../static/data-esp/invoice-data.json')
    save_to_json(delivery_data_es, '../static/data-esp/delivery-data.json')
    save_to_json(contract_data_es, '../static/data-esp/contract-data.json')

    if local_only:
        return "Datos generados y guardados en local."

    # Subir a Google Drive
    data_eng_folder_id = create_folder("data-eng")
    data_esp_folder_id = create_folder("data-esp")

    upload_to_drive('../static/data-eng/invoice-data.json', data_eng_folder_id)
    upload_to_drive('../static/data-eng/delivery-data.json', data_eng_folder_id)
    upload_to_drive('../static/data-eng/contract-data.json', data_eng_folder_id)

    upload_to_drive('../static/data-esp/invoice-data.json', data_esp_folder_id)
    upload_to_drive('../static/data-esp/delivery-data.json', data_esp_folder_id)
    upload_to_drive('../static/data-esp/contract-data.json', data_esp_folder_id)

    return "Datos generados y subidos a Google Drive."


@data_blueprint.route('/generate_data', methods=['POST'])
def generate_data():
    try:
        message = generate_and_save_data_to_drive()
        return jsonify({"message": message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500