# Using official ubuntu image as a parent image
FROM python:3.9-bullseye

# Setting the working directory to /app
WORKDIR /app

# Install Python Dependencies
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run app.py when the container launches
CMD ["python3", "app.py"]