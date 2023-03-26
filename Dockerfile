# Using official ubuntu image as a parent image
FROM ubuntu:22.04

# Setting the working directory to /app
WORKDIR /app

# Get initial dependancies
RUN apt update
RUN apt install -y wget build-essential libpcre3 libpcre3-dev libssl-dev unzip libpq-dev curl git

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y install tzdata

ENV TZ=$DEFAULT_TZ

RUN apt install -y bash

# Install Python, Gunicorn, and uWSGI
RUN apt install -y python3 python3-pip uwsgi-plugin-python3 python3-dev python3-setuptools

# Install Python Dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Install Supervisor
RUN apt install -y supervisor
RUN mkdir -p /var/log/supervisor

RUN mkdir /app/logs

# Copy the current directory contents into the container at /app
COPY . /app
RUN chmod +x /app/entrypoint.sh

VOLUME /app/db

# Run app.py when the container launches
ENTRYPOINT ["/app/entrypoint.sh"]