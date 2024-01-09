# Use a Python base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application code to the working directory
COPY . .

# Expose the port on which the Flask application will run
EXPOSE 8000

# Run the Flask application
COPY runapp.sh /runapp.sh
CMD ["sh", "/runapp.sh"]