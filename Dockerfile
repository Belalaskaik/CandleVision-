# Python environment
FROM python:3.11-slim as python-base
WORKDIR /app
# Assuming all Python code and dependencies are in the 'app' directory
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt

# Node.js environment
FROM node:20-slim as node-base
WORKDIR /node-app
# Copy the capture.js file and package.json if needed
COPY ./capture.js /node-app/
# Check if you have package.json at the root, if not, you need to ensure it's there
COPY ./package.json ./package-lock.json /node-app/

# Allow Puppeteer to skip downloading Chromium.
ENV PUPPETEER_SKIP_DOWNLOAD true

# Install Node dependencies, assuming Puppeteer is needed
RUN npm install

# Final image for local testing or specific deployments
# Using Python base image again since the main application is a Python app
FROM python:3.11-slim
# Copy Python application from python-base stage
COPY --from=python-base /app /app
# Copy Node.js scripts and node_modules from node-base stage
COPY --from=node-base /node-app /node-app
WORKDIR /app
# Command to run the app. Adjust this if you need to start with a script or command that runs both Python and Node.js components
CMD ["python", "main.py"]
