## Requirements

* python3

## Setup

1. Contact @andymckay for the `.env` file and access to the App.

2. Go to https://github.com/organizations/bbq-beets/settings/apps/actions-insights-beta/installations and install the app and grant it access to one or more repos.

3. Install dependencies and start the server:

```
pip3 install -r requirements.txt
cd insights
source .env
python3 manage.py migrate
python3 manage.py runserver
```

4. Go to http://127.0.0.1:8000

## Database management
### Inspecting the django database

1. Create an admin user:

```
cd insights
source .env
python3 manage.py createsuperuser
```

2. Go to http://127.0.0.1:8000/admin/ and sign in with admin credentials

### Deleting the local dev database

Run `rm db.sqlite3` and complete setup again
