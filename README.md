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

### Using Poetry

1. Install Poetry if you haven't already:
   ```sh
    # For Linux/MacOS
   curl -sSL https://install.python-poetry.org | python3 -
   ```
    for Windows users, you can follow the instructions on the [Poetry installation page](https://python-poetry.org/docs/#installation).


2. To activate the virtual environment created by Poetry, use:
   ```sh
   poetry shell
   ```

3. Install the project dependencies using Poetry:
   ```sh
   poetry install
   ```