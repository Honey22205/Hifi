# Hifi
# 🍽️ Infosys HiFi Delivery Eats – CRUD Food Delivery App
This project is a full-stack food delivery web application built using HTML, CSS, Python, Flask, and MySQL. It allows users to register, log in, browse food items, manage their cart, and place orders. An admin panel is also included to manage users, orders, and menu items.

✨ CRUD Features
Create: Users can register and add items to their cart. Admins can add new food items and users.

Read: Users can view food menus and cart contents. Admins can view all user details and order history.

Update: Users can modify cart quantities. Admins can update user information and food item details.

Delete: Users can remove items from their cart. Admins can delete food items, users, and order records.

This project showcases a complete implementation of CRUD operations with real-time user interaction, role-based access, and a clean UI for a seamless experience.
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
