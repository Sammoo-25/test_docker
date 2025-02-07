# Use an official Python runtime as a parent image
FROM python:3.9-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python3", "app.py"]
