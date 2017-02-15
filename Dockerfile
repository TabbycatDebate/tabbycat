# Docker file lists all the commands needed to setup a fresh linux instance to
# run the application specified. docker-compose does not use this.

# Grab a python image
FROM python:3.6

# Just needed for all things python (note this is setting an env variable)
ENV PYTHONUNBUFFERED 1

# Setup Node/NPM
RUN apt-get update && apt-get install curl
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash && apt-get install -y nodejs

# Copy all our files into the baseimage and cd to that directory
RUN mkdir /tcd
WORKDIR /tcd
# Can this be skipped? Takes ages
ADD . /tcd/

# Set git to use HTTPS (SSH is often blocked by firewalls)
RUN git config --global url."https://".insteadOf git://

# Install our node/python requirements
RUN pip install -r ./requirements_common.txt
RUN npm install

# Compile all the static files
RUN npm rebuild node-sass
RUN python ./tabbycat/manage.py collectstatic --no-input
