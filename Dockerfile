# Use Python 3.9.16 as the base image
FROM python:3.9.16

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the static/audio directory
RUN mkdir -p static/audio

# Copy the rest of the application code into the container
COPY . .

EXPOSE 5000

# Set the default command to run when the container starts
CMD ["flask", "run", "--host", "0.0.0.0"]
