# Use the official Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port your app will run on
EXPOSE 8080

# This is the crucial command that starts Gunicorn on port 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]