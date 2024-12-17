import json
import random
from faker import Faker

fake = Faker()

def generate_random_invoice_data(num_invoices=10):
    invoices = []
    client_data = {
        "name": "ENAP SIPETROL S.A. ENAP SIPEC",
        "ruc": "1791239245001",
        "address": "AV. GRANADOS VIA A NAYON EDIFICIO EKOPARK OFICINA 3 PISO 3",
        "city": "Quito",
        "country": "Ecuador"
    }

    for i in range(num_invoices):
        company_name = fake.company().split()[0].lower()
        before_tax = round(random.uniform(100, 1000), 2)
        tax_rate = 18
        tax = round(before_tax * tax_rate / 100, 2)
        total_due = round(before_tax + tax, 2)

        invoice = {
            "company": {
                "name": company_name,
                "address": fake.address(),
                "city": fake.city(),
                "country": fake.country(),
                "phone": fake.phone_number(),
                "website": f"www.{company_name}.com",
                "email": f"info@{company_name}.com",
                "taxId": fake.ean8()
            },
            "invoice": {
                "number": f"INV-{i+1:03}",
                "date": fake.date_this_year().isoformat(),
                "payableAt": fake.date_this_year().isoformat(),
                "orderNumber": f"ORD-{i+1:03}"
            },
            "client": client_data,
            "items": [
                {
                    "code": f"PROD-{chr(65+i)}1",
                    "description": fake.catch_phrase(),
                    "hes": fake.ean8(),
                    "quantity": random.randint(1, 5),
                    "unitCost": round(before_tax / random.randint(1, 5), 2),
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
        invoices.append(invoice)

    return {"invoices": invoices, "enap": [client_data]}

def save_to_json(data, filename='docs-generate-flask/static/data/invoice-data.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    data = generate_random_invoice_data(10)
    save_to_json(data)
    print("Datos de facturas generados y guardados en invoice-data.json")