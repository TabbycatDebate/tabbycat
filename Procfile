# production
web: waitress-serve --port=$PORT wsgi:application
# debug
#web: waitress-serve --port=$PORT --expose-tracebacks wsgi:application

release: python manage.py migrate && python manage.py checkpreferences
