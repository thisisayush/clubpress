# Installation Instructions

- Requirements are stored in: `requirements/local.txt`
- Database: `PostgreSQL`
- Python: 3.x
- Django: 2.x

Designed and Developed by: [@thisisayush](https://www.thisisayush.com/)

### For Development Mode:
Navigate to `cms/settings/__init__.py` and add `from .local import *`

### For Production Mode:
Navigate to `cms/settings/__init__.py` and add `from .production import *`

### .env File
All Credentials and API Keys are stored in a .env file in `cms/settings/.env`

```
DEVELOPMENT_MODE=True
DATABASE_NAME=YOUR_DATABASE_NAME
DATABASE_USER=YOUR_DATABASE_USER
DATABASE_PASS=YOUR_DATABASE_PASS
DATABASE_HOST=YOUR_DATABASE_HOST
DATABASE_PORT=YOUR_DATABASE_PORT
DJANGO_SECRET=YOUR_DJANGO_SECRET
STATIC_ROOT=ROOT_OF_STATIC_FILES
```

### Initialize Database

```
python manage.py makemigrations
python manage.py migrate
python manage.py initializedb
```

### Create Super User

```
python manage.py createsuperuser
```

### Collect StaticFiles (Production Mode)

```
python manage.py collectstatic
```

Help and Support: support@theletstream.com