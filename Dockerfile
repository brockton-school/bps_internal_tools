# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Set build-time arguments for Git info
ARG GIT_COMMIT
ARG GIT_VERSION

# Write the vars to a text file
RUN echo "Build Version: $GIT_VERSION ($GIT_COMMIT)" > /app/version_info.txt

# Install any necessary dependencies
RUN pip install -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]