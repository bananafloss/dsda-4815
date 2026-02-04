# Dockerfile for GitHub Codespaces
# Includes Python, Jupyter, Chrome for Selenium

FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Chromium for Selenium
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Chromium path for Selenium (no GUI in Codespaces)
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
