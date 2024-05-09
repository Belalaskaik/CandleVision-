# Base image for Python
FROM python:3.11-slim as python-base

# Set the working directory in the container
WORKDIR /app

# Copy the Python specific files and directories
COPY app /app/app
COPY static /app/static
COPY train9 /app/train9
COPY requirements.txt /app/
COPY setup.py /app/

# Install Python dependencies from setup.py
RUN pip install .

# Install Node.js and the specific Node.js files
# This assumes that Node.js is required for the application to function, such as for your capture.js script
FROM node:20-slim as node-base

# Set working directory for Node
WORKDIR /node-app

# Copy Node.js specific files
COPY capture.js /node-app/
COPY package*.json /node-app/

# Install Node.js dependencies
RUN npm install

# Set environment variable to skip Puppeteer's Chromium download if not necessary
ENV PUPPETEER_SKIP_DOWNLOAD true

# Final stage to assemble the Python app with Node assets
FROM python:3.11-slim

# Copy Python app and weights from the python-base stage
COPY --from=python-base /app /app

# Copy Node.js scripts and node_modules from the node-base stage
COPY --from=node-base /node-app /node-app

# Set the working directory to /app for CMD to execute properly
WORKDIR /app

# Install Uvicorn for running the application
RUN pip install uvicorn

# Expose the port the app runs on
EXPOSE 80

# Command to run the application using Uvicorn without the --reload flag for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
