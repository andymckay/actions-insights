## Requirements

* python3

## Setup

Contact @andymckay for the `.env` file and access to the App.

```
pip3 install -r requirements.txt
cd insights
source .env
python3 manage.py migrate
python3 manage.py runserver
```

Go to:
`http://127.0.0.1:8000`

## Inspecting the django database

Create an admin user

```
cd insights
source .env
python3 manage.py createsuperuser
```

Go to http://127.0.0.1:8000/admin/ and sign in with admin credentials
