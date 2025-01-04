from flask import Blueprint, request, render_template
import os

home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/', methods=['GET'])
def home():

    current_lang = request.args.get('lang', 'eng')

    return render_template('home.html', current_lang=current_lang)