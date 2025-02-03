# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir prometheus-client

# Expose the port your app runs on (optional but recommended)
EXPOSE 8080

# Command to run the application
CMD ["python3", "app.py"]
