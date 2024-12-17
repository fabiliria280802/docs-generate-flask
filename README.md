# docs-generate-flask
This my repo for an flask app that can generate docs

## Project structure
.
├── app.py
├── requirements.txt
├── data
│   └── ...
├── env
│   └── ...
├── example
│   └── ...
├── static
│   └── ...
└── templates
    └── invoice.html

- app.py: the main app
- invoice.html: the template for the invoice
- requirements.txt: the dependencies
- templates: the templates for the invoice
- static: the static files for the invoice
- env: the environment variables

## How to run (windows)
1. Create a virtual environment: `python -m venv env`
2. Activate the virtual environment: `.\venv\Scripts\activate`
3. Install the dependencies: `python -m pip install -r requirements.txt`
4. Run the app: `python -m flask --app .\app.py run`

```bash
pip install -r requirements.txt
python app.py
```

**Note:** If you have any issues with the virtual environment, you can try to install the dependencies manually and you will need to use command `deactivate` to deactivate the virtual environment and then run `env/Scripts/activate` to activate it again.

## How to generate invoice

```bash
curl http://localhost:3000/generate_invoice
```

## How to generate invoice with a specific data

```bash
curl http://localhost:3000/generate_invoice?data=
```
### How to generate invoice with a specific data and a specific template

```bash
curl http://localhost:3000/generate_invoice?data=
```
