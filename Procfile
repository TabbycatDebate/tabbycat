# production
web: sh -c 'cd ./tabbycat/ && daphne asgi:channel_layer --port $PORT --bind 0.0.0.0 -v2'
worker: sh -c 'cd ./tabbycat/ && python manage.py runworker -v2'
