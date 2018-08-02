# production
# Note this assumes a Heroku environment (http timeout of 30s is premature elsewhere)
# Note websocket timeout is set at 2 hours, this is to try and compensate for connections accidentally being left open (say on an idle machine) indefinitely
web: sh -c 'cd ./tabbycat/ && uvicorn asgi:application --host 0.0.0.0 --port $PORT --timeout-response 29'