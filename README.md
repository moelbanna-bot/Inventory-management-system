# Inventory-management-system

## Setup Instructions

### Using the .env File

1. Copy the `.env.example` file to create a new `.env` file:

   ```sh
   # For Linux/MacOS
   cp .env.example .env
   ```
   or just copy the file manually if you are on Windows.


2. Open the `.env` file and update the required environment variables with your specific configuration.

### Option 1: Using Poetry

1. Install Poetry if you haven't already:
   ```sh
    # For Linux/MacOS
   curl -sSL https://install.python-poetry.org | python3 -
   ```
   for Windows users, you can follow the instructions on
   the [Poetry installation page](https://python-poetry.org/docs/#installation).

2. Create & activate virtual environment.
   Using poetry shell (the easiest way)
    - Install the Shell Plugin
        ```sh
        poetry self add poetry-plugin-shell
        ```
    - Activate the virtual environment.
        ```sh
        poetry shell
        ```
      Or you can use your preferred virtual environment manager (like `venv` or `virtualenv`) to create a virtual
      environment and activate it.


3. Install the project dependencies using Poetry:
   ```sh
   poetry install --no-root
   #or
   poetry sync
   ```

### Option 2: Using requirements.txt

1. Create and activate a virtual environment:
   ```sh
   # For Linux/MacOS
   python -m venv venv
   source venv/bin/activate
   
   # For Windows
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies from requirements.txt:
   ```sh
   pip install -r requirements.txt
   ```

### Starting the Server

After setting up using either option above:

1. Make sure you have the required database set up (in this case its PostgreSQL).
2. Run the following commands to create a superuser so you can access the system:

```sh
python manage.py createsuperuser
```

3. Run the following commands to apply migrations and start the server:

```sh
# Apply migrations
python manage.py migrate
python manage.py runserver
```