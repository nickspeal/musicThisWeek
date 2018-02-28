# Base Image:
FROM amazon/aws-eb-python:3.4.2-onbuild-3.5.1

# Environment Variables:
ENV SPOTIPY_CLIENT_ID 'copy from creds file'
ENV SPOTIPY_CLIENT_SECRET 'copy from creds file'
ENV SPOTIPY_REDIRECT_URI 'http://localhost:8888/callback'
ENV DJANGO_SECRET_KEY ''copy from creds file'
ENV EVENTFUL_KEY 'copy from creds file'

ENV PYTHONUNBUFFERED 1

# Copy Source code into the VM
RUN mkdir /code
WORKDIR /code
COPY . /code/

# Apache Config:
# apt get install doesn't work on this amazon (non-ubuntu?) image. Maybe it already has apache?
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y apache2 libapache2-mod-wsgi
RUN sudo a2enmod wsgi
ADD apache-config.conf /etc/apache2/sites-available/musicthisweek.conf
RUN a2ensite musicthisweek.conf
EXPOSE 80

# Python Config
RUN pip install -r requirements.txt


# TODO
# Move files nicely into deploy dir
