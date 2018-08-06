# Production

# Command after start-nginx is directly run by nginx script; so dont use &&
# Running multiple processes (with the wait) as per:
# https://help.heroku.com/CTFS2TJK/how-do-i-run-multiple-processes-on-a-dyno
# Preping FORCE=1 prevents nginx for waiting on the touch to /tmp/ file

# Run waitress and uvicorn through nginx
web: bin/start-nginx python ./tabbycat/run-waitress.py & python ./tabbycat/run-uvicorn.py  & wait -n
