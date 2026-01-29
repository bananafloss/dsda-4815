# Dockerfile for GitHub Codespaces
# Includes Python, Jupyter, Chrome for Selenium

FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome to run in headless mode by default (no GUI in Codespaces)
ENV CHROME_BIN=/usr/bin/google-chrome-stable

# Install Python packages
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
