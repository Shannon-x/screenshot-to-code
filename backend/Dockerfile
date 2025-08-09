FROM python:3.12.3-slim-bullseye

ENV POETRY_VERSION=1.7.1

# Install system dependencies
RUN pip install "poetry==$POETRY_VERSION"

# Set work directory
WORKDIR /app

# Install ffmpeg for moviepy
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Copy only pyproject.toml first
COPY pyproject.toml /app/

# Disable the creation of virtual environments
RUN poetry config virtualenvs.create false

# Install dependencies without lock file
RUN poetry install --no-interaction --no-ansi

# Copy the current directory contents into the container at /app
COPY ./ /app/