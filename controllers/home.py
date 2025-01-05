from flask import Blueprint, request, redirect, url_for, session, jsonify, render_template
from services.drive_service import upload_to_drive, create_folder
from controllers.data import generate_and_save_data_to_drive
import os

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():
    current_lang = request.args.get('lang', 'eng')
    return render_template('home.html', current_lang=current_lang)

@home_blueprint.route('/set_data_source', methods=['POST'])
def set_data_source():
    data_source = request.form.get('data_source')
    if data_source not in ['local', 'google_drive']:
        return "Invalid data source", 400

    session['data_source'] = data_source
    return redirect(url_for('home.home'))


@home_blueprint.route('/create_data_source', methods=['POST'])
def create_data_source():
    data_source = request.form.get('data_source')
    if data_source not in ['local', 'google_drive']:
        return "Invalid data source", 400

    if data_source == 'local':
        try:
            # Generar datos en local
            message = generate_and_save_data_to_drive(local_only=True)
            return jsonify({"message": message}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    elif data_source == 'google_drive':
        try:
            # Generar datos y subirlos a Google Drive
            message = generate_and_save_data_to_drive(local_only=False)
            return jsonify({"message": message}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500