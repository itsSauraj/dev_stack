# DEV_STACK

## Description

A django based applicaiton for making a developer's profile with feature like showcasing skills, tech Stack and Peojects.

## Technologies Used

- Django
- Python 3.12.x
- HTML/CSS/JS
- JavaScript (optional)
- Database name - can be used any on your preference (PostgreSQL, MySQL, SQLite)
- Tailwincss

# Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.12
- Django 3.x+
- pip (Python package manager)
- [Optional] Virtual environment tool (`virtualenv` or `venv`)

### Steps

1. **Clone the repository**:

   ```bash
   git clone https://github.com/CodeWithSaurabhYadav/dev_stack
   ```
2. **Navigate to the project directory**:

   ```bash
   cd dev_stack
   ```
3. **Create and activate a virtual environment (recommended)**:

   ```bash
    # For virtualenv
    virtualenv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

    # For venv (Python 3 built-in)
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`  
   ```
4. **Install project dependencies**:

   ```bash
    pip install -r requirements.txt
   ```
5. **Set up the database**:
 - If you are using the default SQLite database, Django will create it automatically. Otherwise, configure your database settings in the settings.py file, and then run:
   ```bash  
    python manage.py migrate
   ```
6. **Create a superuser (admin account)**:

   ```bash
    python manage.py createsuperuser
   ```
7. **Run the development server**:

   ```bash
    python manage.py runserver
   ```
   Open your browser and navigate to http://127.0.0.1:8000/ to access the project.

### Configuration

#### Database
To change the database settings, open the settings.py file and modify the DATABASES setting. Example for PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
or
#####  For using SQLite
```python
# To use this you will need to create a file named 'db.sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Stactic files
Django collects static files using the collectstatic command. Ensure that STATIC_URL and STATIC_ROOT are properly configured in settings.py. Run:
```bash
python manage.py collectstatic
```

