# Fzscraper (buzzstezz_api01)

A Django REST API that scrappes and collects content from the web using `mechanize` and `BeautifulSoup`, exposed through class-based DRF serializers and views.

Stack: Django 4.1, Django REST Framework, mechanize, BeautifulSoup, django-cors-headers, django-user-agents, SQLite.

## Run

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

A SQLite database (`db.sqlite3`) is included with scrapped data.