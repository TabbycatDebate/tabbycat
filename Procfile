# Production

# Note that this runs honcho, which in turn runs a second 'MultiProcfile'
# This better allows for multiple processes to be run simultaneously

web: honcho -f ProcfileMulti start
worker: python manage.py runworker notifications adjallocation venues
