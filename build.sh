#!/bin/bash

# Initialize a variable to track if the -d flag is set
DETACHED=""

# Parse command-line options
while getopts ":d" opt; do
  case ${opt} in
    d )
      DETACHED="-d"
      ;;
    \? )
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Get the latest Git commit hash and version tag
export GIT_COMMIT=$(git rev-parse --short HEAD)
export GIT_VERSION=$(git describe --tags --abbrev=0)

# generate and export a flask secret key, more on the what/why in config.py
export FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(16))")

# Run docker-compose with the build arguments
docker-compose build

# Run docker-compose up with or without the -d flag
docker-compose up $DETACHED