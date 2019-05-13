#web: gunicorn --log-file=- --workers=1 --bind=0.0.0.0:$PORT service:app
#web: python run.py
web: gunicorn --bind 0.0.0.0:$PORT --log-level=info app:app
