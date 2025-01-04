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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
