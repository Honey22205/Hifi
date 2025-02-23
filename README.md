# Hifi

## Setting up a Virtual Environment

1. Create a virtual environment:
    ```sh
    python -m venv .venv
    ```

2. Activate the virtual environment:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```sh
        source .venv/bin/activate
        ```

## Generating a Requirements File

1. After installing the necessary packages, generate a `requirements.txt` file:
    ```sh
    pip freeze > requirements.txt
    ```

## Installing from Requirements File

1. To install the dependencies listed in `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Code

1. Ensure the virtual environment is activated:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On macOS and Linux:
        ```sh
        source .venv/bin/activate
        ```

2. Run the code:
    ```sh
    python main.py
    ```