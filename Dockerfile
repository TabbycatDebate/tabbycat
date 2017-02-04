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

# Install our node/python requirements
RUN pip install -r ./requirements_common.txt && npm install

# This needs to happen else sass gets angry
RUN npm rebuild node-sass
