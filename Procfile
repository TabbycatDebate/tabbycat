# production
# Note this assumes a Heroku environment (http timeout of 30s is premature elsewhere)
# Note websocket timeout is set at 2 hours, this is to try and compensate for connections accidentally being left open (say on an idle machine) indefinitely
web: sh -c 'cd ./tabbycat/ && daphne asgi:application --http-timeout 29 --websocket_timeout 7200 --port $PORT --bind 0.0.0.0 --verbosity 2'