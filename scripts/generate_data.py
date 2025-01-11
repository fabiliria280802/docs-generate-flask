import random
import os
import json
from faker import Faker
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

fake_en = Faker("en_US")
fake_es = Faker("es_ES")

COMPANY_RUC_MAP = {
    "Alphazed Inc": "0992760737001", 
    "Beta Group SA": "1793168604001", 
    "Tech Solutions": "1757541519001", 
    "SONY Tecnologias": "1790012345001", 
    "Servicios Empresariales SA": "1701234567001", 
    "Verndale": "0101234540001", 
    "Deuna SA": "0301234530001", 
    "Genius Corp": "0401234570001", 
    "Kuger Corp": "0501234520001", 
    "YT Music": "0601234560001", 
    "Netflife SA": "0701234510001", 
    "Telefonica SA": "0801234550001", 
    "Deep Note SA": "0901234500001", 
    "Warner SA": "1001234580001", 
    "SUDO ADmin SA": "1101234530001", 
    "ZorE SA": "1301234520001", 
    "Danvers Corp": "0104123450001", 
    "Susuki SA": "1401234560001",
    "X Rest SA": "1501234510001",
    "TATA SA": "0201234580001", 
    "L Corp":"1201234570001" ,
    "Amazon AWS":"0205182033001",
    "Microsoft":"0301234563001",
    "Google":"0591234567001",
    "SAP":"0999999999001",
    "Zendesk SA": "0190000009001",
    "IBM":"2396543219001",
    "Deloitte":"2290001119001",
    "Thoughtworks":"0161234567001",
    "Salesforce":"1469999996001",
    "Kimobil":"2461234567001",
    "Huawei":"1757797202001",
    "Samsung":"0190054683001",
    "LG Computers":"1792256267001"
}

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

def generate_random_invoice_and_delivery_data_and_contract_data_eng(num_invoices=1500):
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
        if i >= 1250:
            if random.random() < 0.5: 
                company_name_en = ""  
                company_ruc = random.choice(["", "123INVALID"])
            else:
                company_name_en = random.choice(list(COMPANY_RUC_MAP.keys()))
                company_ruc = COMPANY_RUC_MAP[company_name_en]
        else:
            company_name_en = random.choice(list(COMPANY_RUC_MAP.keys()))
            company_ruc = COMPANY_RUC_MAP[company_name_en]

        # Generar datos de la empresa
        united_company_name_en = company_name_en.replace(" ", "").lower()

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
        payable_at_date = invoice_date_obj + timedelta(days=max_payable_days)

        random_days = random.randint(1, 365)
        end_date = invoice_date_obj + timedelta(days=random_days)
        invoice_date_str = invoice_date_obj.strftime('%d-%m-%Y')
        payable_at_date_str = payable_at_date.strftime('%d-%m-%Y')
        end_date_str = end_date.strftime('%d-%m-%Y')

        company_data_en = {
            "name": company_name_en,
            "ruc": company_ruc,
            "address": fake_en.address().replace("\n", ", ") if i < 1250 or random.random() > 0.3 else "",
            "city": fake_en.city() if i < 1250 or random.random() > 0.2 else "",
            "country": fake_en.country() if i < 1250 or random.random() > 0.1 else "",
            "phone": fake_en.phone_number() if i < 1250 or random.random() > 0.3 else "",
            "website": f"www.{united_company_name_en}.com" if i < 1250 or random.random() > 0.3 else "",
            "email": f"info@{united_company_name_en}.com" if i < 1250 or random.random() > 0.1 else "",
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
            "name": in_charge_name_en if i < 1250 or random.random() > 0.1 else "",
            "position": in_charge_position_en if i < 1250 or random.random() > 0.1 else "",
            "signature": signature_path_en
        }

        invoice_en = {
            "company": company_data_en,
            "invoice": {
                "number": f"11{i+1:05}" if i < 1250 or random.random() > 0.3 else "",
                "date": invoice_date_str if i < 1250 or random.random() > 0.3 else None,
                "payableAt": payable_at_date_str if i < 1250 or random.random() > 0.3 else None,
                "orderNumber": f"34{i+1:05}"
            },
            "client": client_data_en,
            "items": items,
            "totals": {
                "beforeTax": before_tax if i < 1250 or random.random() > 0.2 else None,
                "taxRate": tax_rate if i < 1250 or random.random() > 0.1 else None,
                "tax": tax,
                "totalDue": total_due if i < 1250 or random.random() > 0.2 else None
            },
            "in_charge_info": {
                "name": in_charge_name_en,
                "position": in_charge_position_en,
                "signature": signature_path_en
            }
        }

        delivery_en = {
            "receiver": {
                "number": f"14{i+1:05}" if i < 1250 or random.random() > 0.3 else "",
                "name": base_client_data_en["name"] if i < 1250 or random.random() > 0.3 else "",
                "from": company_data_en["name"] if i < 1250 or random.random() > 0.1 else "",
                "ruc": company_data_en["ruc"] if i < 1250 or random.random() > 0.3 else "",
                "invoiceNumber": invoice_en["invoice"]["number"],
                "hes": items[0]["hes"],  
                "orderNumber": invoice_en["invoice"]["orderNumber"] if i < 1250 or random.random() > 0.1 else "",
                "date": invoice_date_str if i < 1250 or random.random() > 0.1 else "",
                "endDate": end_date_str if i < 1250 or random.random() > 0.3 else "",
                "price": invoice_en["totals"]["totalDue"] if i < 1250 or random.random() > 0.2 else "",
                "employee_name": enap_employee_name_en if i < 1250 or random.random() > 0.3 else "",
                "employee_position": enap_employee_position_en if i < 1250 or random.random() > 0.3 else "",
                "employee_signature": enap_signature_path_en
            }
        }

        contract_data_en = {
            "company": company_data_en if i < 1250 or random.random() > 0.3 else "",
            "client": client_data_en if i < 1250 or random.random() > 0.3 else "",
            "items": items,
            "totals": invoice_en["totals"],
            "contract": {
                "number": f"65{i+1:05}",
                "startDate": invoice_en["invoice"]["date"],
                "endDate": end_date_str,
                "invoiceNumber": invoice_en["invoice"]["number"] if i < 1250 or random.random() > 0.3 else "",
                "hes": items[0]["hes"] if i < 1250 or random.random() > 0.3 else "",
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

def generate_random_invoice_and_delivery_data_and_contract_data_esp(num_invoices=1500):
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
        if i > 1250:
            if random.random() < 0.5:  
                company_name_esp = ""  
                company_ruc = random.choice(["", "123INVALID"]) 
            else:
                company_name_esp = random.choice(list(COMPANY_RUC_MAP.keys()))
                company_ruc = COMPANY_RUC_MAP[company_name_esp]
        else:
            company_name_esp = random.choice(list(COMPANY_RUC_MAP.keys()))
            company_ruc = COMPANY_RUC_MAP[company_name_esp]

        united_company_name_esp = company_name_esp.replace(" ", "").lower()

        num_items = random.randint(1, 5)
        items = []
        before_tax = 0

        for j in range(num_items):
            quantity = random.randint(1, 10) if i < 1250 or random.random() > 0.2 else None
            unit_cost = round(random.uniform(20, 500), 2) if i < 1250 or random.random() > 0.2 else None
            cost = round(quantity * unit_cost, 2) if quantity and unit_cost else 0
            before_tax += round(cost, 2) 
            service_description = random.choice(SERVICE_DESCRIPTION_ES) if i < 1250 or random.random() > 0.3 else ""

            item = {
                "code": f"36{chr(65 + (i % 26))}{j+1}",
                "description": service_description,
                "hes": generate_hes(i),
                "quantity": quantity,
                "unitCost": unit_cost,
                "cost": cost
            }
            items.append(item)

        tax_rate = 15
        tax = round(before_tax * tax_rate / 100, 2)
        total_due = round(before_tax + tax, 2)

        invoice_date_obj = fake_en.date_this_year()
        max_payable_days = 30
        payable_at_date = invoice_date_obj + timedelta(days=max_payable_days)

        random_days = random.randint(1, 365)
        end_date = invoice_date_obj + timedelta(days=random_days)
        invoice_date_str = invoice_date_obj.strftime('%d-%m-%Y')
        payable_at_date_str = payable_at_date.strftime('%d-%m-%Y')
        end_date_str = end_date.strftime('%d-%m-%Y')

        company_data_esp = {
            "name": company_name_esp,
            "ruc": company_ruc,
            "address": fake_es.address().replace("\n", ", ") if i < 1250 or random.random() > 0.3 else "", 
            "city": fake_es.city() if i < 1250 or random.random() > 0.3 else "",
            "country": fake_es.country(),
            "phone": fake_es.phone_number() if i < 1250 or random.random() > 0.3 else "",
            "website": f"www.{united_company_name_esp}.com" if i < 1250 or random.random() > 0.3 else "",
            "email": f"info@{united_company_name_esp}.com" if i < 1250 or random.random() > 0.3 else "",
            "taxId": fake_es.ean8() if i < 1250 or random.random() > 0.3 else ""
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
                "number": f"11{i+1:05}" if i < 1250 or random.random() > 0.3 else "",
                "date": invoice_date_str if i < 1250 or random.random() > 0.3 else "",
                "payableAt": payable_at_date_str if i < 1250 or random.random() > 0.3 else "",
                "orderNumber": f"34{i+1:05}" if i < 1250 or random.random() > 0.3 else ""
            },
            "client": client_data_esp,
            "items": items,
            "totals": {
                "beforeTax": before_tax if i < 1250 or random.random() > 0.3 else None,
                "taxRate": tax_rate,
                "tax": tax if i < 1250 or random.random() > 0.3 else None,
                "totalDue": total_due if i < 1250 or random.random() > 0.3 else None
            },
            "in_charge_info": {
                "name": in_charge_name_esp,
                "position": in_charge_position_esp,
                "signature": signature_path_esp
            }
        }

        delivery_esp = {
            "receiver": {
                "number": f"14{i+1:05}" if i < 1250 or random.random() > 0.3 else None,
                "name": base_client_data_esp["name"] if i < 1250 or random.random() > 0.2 else "",
                "from": company_data_esp["name"] if i < 1250 or random.random() > 0.2 else "",
                "ruc": company_data_esp["ruc"] if i < 1250 or random.random() > 0.1 else "",
                "invoiceNumber": invoice_esp["invoice"]["number"] if i < 1250 or random.random() > 0.1 else "",
                "hes": items[0]["hes"] if i < 1250 or random.random() > 0.3 else None, 
                "orderNumber": invoice_esp["invoice"]["orderNumber"] if i < 1250 or random.random() > 0.3 else "",
                "date": invoice_date_str if i < 1250 or random.random() > 0.3 else "",
                "endDate": end_date_str if i < 1250 or random.random() > 0.1 else "",
                "price": invoice_esp["totals"]["totalDue"],
                "employee_name": enap_employee_name_esp if i < 1250 or random.random() > 0.1 else "",
                "employee_position": enap_employee_position_esp if i < 1250 or random.random() > 0.1 else "",
                "employee_signature": enap_signature_path_esp
            }
        }

        contract_data_esp = {
            "company": company_data_esp if i < 1250 or random.random() > 0.1 else "",
            "client": client_data_esp if i < 1250 or random.random() > 0.3 else "",
            "items": items,
            "totals": invoice_esp["totals"],
            "contract": {
                "number": f"65{i+1:05}" if i < 1250 or random.random() > 0.3 else "",
                "startDate": invoice_esp["invoice"]["date"] if i < 1250 or random.random() > 0.1 else "",
                "endDate": (invoice_date_obj + timedelta(days=random.randint(1, 365))).isoformat(),
                "invoiceNumber": invoice_esp["invoice"]["number"] if i < 1250 or random.random() > 0.2 else "",
                "hes": items[0]["hes"] if i < 1250 or random.random() > 0.2 else "",
                "orderNumber": invoice_esp["invoice"]["orderNumber"] if i < 1250 or random.random() > 0.3 else "",
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
    invoice_data_en, delivery_data_en, contract_data_en = generate_random_invoice_and_delivery_data_and_contract_data_eng(1500)
    save_to_json(invoice_data_en, '../static/data-eng/invoice-data.json')
    print("Datos de facturas (inglés) generados en invoice-data.json (data-eng)")

    save_to_json(delivery_data_en, '../static/data-eng/delivery-data.json')
    print("Datos de actas de recepción (inglés) generados en delivery-data.json (data-eng)")

    save_to_json(contract_data_en, '../static/data-eng/contract-data.json')
    print("Datos de contratos (inglés) generados en contract-data.json (data-eng)")

    invoice_data_es, delivery_data_es, contract_data_es = generate_random_invoice_and_delivery_data_and_contract_data_esp(1500)
    save_to_json(invoice_data_es, '../static/data-esp/invoice-data.json')
    print("Datos de facturas (español) generados en invoice-data.json (data-esp)")

    save_to_json(delivery_data_es, '../static/data-esp/delivery-data.json')
    print("Datos de actas de recepción (español) generados en delivery-data.json (data-esp)")

    save_to_json(contract_data_es, '../static/data-esp/contract-data.json')
    print("Datos de contratos (español) generados en contract-data.json (data-esp)")
    