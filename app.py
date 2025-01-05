from flask import Flask
from controllers.invoices import invoices_blueprint
from controllers.contracts import contracts_blueprint
from controllers.deliveries import deliveries_blueprint
from controllers.documents import documents_blueprint
from controllers.data import data_blueprint
from controllers.home import home_blueprint
app = Flask(__name__)

# Registrar Blueprints
app.register_blueprint(invoices_blueprint, url_prefix='/invoices')
app.register_blueprint(contracts_blueprint, url_prefix='/contracts')
app.register_blueprint(deliveries_blueprint, url_prefix='/deliveries')
app.register_blueprint(documents_blueprint, url_prefix='/documents')
app.register_blueprint(data_blueprint, url_prefix='/data')
app.register_blueprint(home_blueprint)
app.secret_key = 'AIzaSyDlGhz9JO1RAHRjvemXbjYFg_Rh7MrDQlQ'

# Ruta para iniciar la autenticación
@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive'],
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

# Ruta de callback para manejar la respuesta de Google
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive'],
        state=state,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    service = build('drive', 'v3', credentials=credentials)
    # Ahora puedes usar 'service' para interactuar con la API de Google Drive
    return 'Autenticación exitosa'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
