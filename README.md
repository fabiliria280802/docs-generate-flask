# docs-generate-flask
This my repo is microservice for generate docs in pdf using flask and jinja2 template engine. Use this repo to generate docs in pdf.

## Project structure
```plaintext
.
├── app.py
├── requirements.txt
├── dockerfile
├── venv
│   └── ...
├── example
│   └── ...
├── static
│   ├── assets
│   │   └── ...
│   ├── data
│   │   └── ...
│   ├── fonts
│   │   └── ...
│   └── signatures
│       └── ...
├── tests
│   └── ...
└── templates
    ├── deliveryReceipt.html
    ├── deliveryReceipt-error.html
    ├── contract-error.html
    ├── contract.html
    ├── invoice-error.html
    └── invoice.html
```
- app.py: the main app
- invoice.html: the template for the docs
- deliveryReceipt.html: the template for the docs
- contract.html: the template for the docs
- invoice-error.html: the template for the docs with error
- deliveryReceipt-error.html: the template for the docs with error
- contract-error.html: the template for the docs with error
- requirements.txt: the dependencies
- templates: the templates for the invoice
- static: the static files for the invoice
- venv: the environment variables
- dockerfile: the dockerfile for the app
- example: the example data for the invoice
- tests: the tests for the app

---

## How to run app (windows)
**Description:** This is the main app that will be used to generate docs.
1. Create a virtual environment:
```bash
 python -m venv env
 ```
2. Activate the virtual environment:
```bash
    .\venv\Scripts\activate
```
3. Install the dependencies:
```bash
    python -m pip install -r requirements.txt
```
4. Run the app:
```bash
    python -m flask --app .\app.py run
```

**Note:** if you are having trouble with adding a new dependency, pliz go to requirements.txt then go back to step 3, finally use `pip list` to check if the dependency is installed, and write library_name==version in requirements.txt

---

## How to run generate_invoices.py
**Description:** This script is used to generate docs in json that will be used to generate docs in pdf.
1. Go to the directory:
```bash
cd scripts
```
2. Activate the virtual environment:
```bash
.\venv\Scripts\activate
```
3. Run the script:
```bash
 python generate_invoices.py
 ```

**Note:** If you have any issues with the virtual environment, you can try to install the dependencies manually and you will need to use command `deactivate` to deactivate the virtual environment and then run `.\venv\Scripts\activate` to activate it again.

---
## Endpoints
### How to generate invoice

```bash
curl http://localhost:3000/generate_invoice
```

### How to generate invoice with a specific data

```bash
curl http://localhost:3000/generate_invoice?data=
```
### How to generate invoice with a specific data and a specific template

```bash
curl http://localhost:3000/generate_invoice?data=
```
