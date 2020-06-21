# Docker file lists all the commands needed to setup a fresh linux instance to
# run the application specified. docker-compose does not use this.

# Grab a python image
FROM python:3.6

# Just needed for all things python (note this is setting an env variable)
ENV PYTHONUNBUFFERED 1

# Setup Node/NPM
RUN apt-get update
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get install -y nodejs

# Copy all our files into the baseimage and cd to that directory
RUN mkdir /tcd
WORKDIR /tcd
# Can this be skipped? Takes ages
ADD . /tcd/

# Set git to use HTTPS (SSH is often blocked by firewalls)
RUN git config --global url."https://".insteadOf git://

# Install our node/python requirements
RUN npm install -g npm@6.14.5
RUN pip install -r ./config/requirements_core.txt
RUN npm install --only=production

# Compile all the static files
RUN npm run build
RUN python ./tabbycat/manage.py collectstatic --noinput -v 0
