import fitz
import os
import json
from xml.dom.minidom import parseString
from dicttoxml import dicttoxml
from flask import request, session

def get_data_from_local(data_type):
    """Leer datos desde las carpetas locales."""
    lang = session.get('current_lang', 'eng')
    json_path = os.path.join('static', f'data-{lang}', f'{data_type}-data.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading local data for {data_type}: {e}")
        return None

def pdf_to_png(pdf_path, png_path):
    """
    Convierte la PRIMERA página del PDF en una imagen PNG usando PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    if doc.page_count > 0:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(png_path)
    doc.close()

def save_to_json(data, file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    try:
        # Guardar los datos en formato JSON
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"Datos guardados exitosamente en {file_path}")
    except Exception as e:
        print(f"Error al guardar datos en {file_path}: {e}")

def generate_invoice_xml(invoice_data, xml_path):
    xml = dicttoxml(invoice_data, custom_root='invoice', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

def generate_contract_xml(contract_data, xml_path):
    xml = dicttoxml(contract_data, custom_root='contract', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

def generate_delivery_xml(delivery_data, xml_path):
    xml = dicttoxml(delivery_data, custom_root='delivery', attr_type=False)
    dom = parseString(xml)
    formatted_xml = dom.toprettyxml(indent="    ")
    with open(xml_path, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)

