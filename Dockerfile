# Use an official Python runtime as a parent image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /app

# Set build-time arguments for Git info
ARG GIT_COMMIT
ARG GIT_VERSION

# Write the vars to a text file
RUN echo "$GIT_COMMIT" > /app/git_commit.txt
RUN echo "$GIT_VERSION" > /app/git_version.txt

COPY . .
ENV FLASK_APP=wsgi:app
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]