# Using official ubuntu image as a parent image
FROM ubuntu:latest

# Setting the working directory to /app
WORKDIR /app

# Getting the updates for Ubuntu and installing python into our environment
RUN apt-get -y update  && apt-get install -y python3 python3-pip

# Install Python Dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
CMD ["python", "app.py"]