# Base image
FROM python:3.13

# Working dir
WORKDIR /autopilot-os

# Requirements
COPY requirements.txt .

# Upgrade pip
RUN python3 -m pip install --upgrade pip

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Debug flag
ENV DEBUG=True

