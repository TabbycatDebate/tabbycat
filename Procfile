# production
web: sh -c 'cd ./tabbycat/ && waitress-serve --port=$PORT wsgi:application'

# debug
web: sh -c 'cd tabbycat && waitress-serve --port=$PORT --expose-tracebacks wsgi:application'
