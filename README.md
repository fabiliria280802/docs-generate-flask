# Flask Docs Generator Microservice

This repository contains a Flask application that generates documentation and serves as a microservice for the SALEM project.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Project Description

The Flask Docs Generator Microservice is designed to generate documentation for various services and act as a microservice within the SALEM project. This application provides a streamlined way to generate and serve documentation, ensuring that all necessary information is readily accessible.

```plaintext
.
├── app.py
├── requirements.txt
├── dockerfile
├── credentials/
│   └── ...
├── examples/
│   └── ...
├── venv/
│   └── ...
├── example/
│   └── ...
├── static/
│   ├── assets
│   │   └── ...
│   ├── data-esp
│   │   └── ...
│   ├── data-esp
│   │   └── ...
│   ├── fonts
│   │   └── ...
│   └── signatures
│       └── ...
├── tests/
│   └── ...
└── templates/
    ├── base.html
    ├── deliveryReceipt-list.html
    ├── deliveryReceipt.html
    ├── contract.html
    ├── contract-list.html
    ├── invoice-list.html
    └── invoice.html
```

## Features

- Generate documentation for various services.
- Serve documentation through a simple API.
- Easy to integrate into the SALEM project.
- Built with Flask and supports both Python and HTML.

## Installation

To install and run the Flask Docs Generator Microservice, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/fabiliria280802/docs-generate-flask.git
    cd docs-generate-flask
    ```

2. **Create a virtual environment:**

    ```bash
    python3 -m venv venv # On windows use `python -m venv venv
    `
    source venv/bin/activate  # On Windows use `.\venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt # On Windows use ` python -m pip install -r requirements.txt`
    ```
If your are having any trouble with installing the  dependencies for linux/Mac, try using:

    ```bash
    python3 -m pip install -r requirements.txt
    ```

4. **Run the Flask application:**

    ```bash
    flask run --port=5500 # On Windows use `python -m flask --app .\app.py run`
    ```

If your are having any trouble with running teh app on linux/Mac, try using the command for windows:

    ```bash
     python3 -m flask --app .\app.py run
    ```

The application will be available at `http://127.0.0.1:5000`.

## Usage

Once the application is running, you can use the provided API endpoints to generate and retrieve documentation.

### Example

```bash
curl http://127.0.0.1:5000/generate-docs -d "service_name=example_service"
```

## API Endpoints

- **`POST /generate-docs`**: Generate documentation for a specified service.
    - Request Body:
        - `service_name` (string): The name of the service for which to generate documentation.
    - Response: The generated documentation in HTML format.

- **`GET /docs/<service_name>`**: Retrieve documentation for a specified service.
    - URL Parameters:
        - `service_name` (string): The name of the service for which to retrieve documentation.
    - Response: The documentation in HTML format.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
    - We recommend the use of key words at the begin of the commit like feat, fix, bug, ect.
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.