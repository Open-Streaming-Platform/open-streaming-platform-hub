# Using official ubuntu image as a parent image
FROM python:3.9-bullseye

# Setting the working directory to /app
WORKDIR /app

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