# Python environment
FROM python:3.11-slim as python-base
WORKDIR /app
COPY ./app /app
COPY train9 /app/train9  # Add this line to copy the train9 directory
RUN pip install --no-cache-dir -r requirements.txt
RUN pip list | grep fastapi

# Node.js environment
FROM node:20-slim as node-base
WORKDIR /node-app
COPY ./capture.js /node-app/
COPY ./package.json ./package-lock.json /node-app/
ENV PUPPETEER_SKIP_DOWNLOAD true
RUN npm install

# Final image for local testing or specific deployments
FROM python:3.11-slim
COPY --from=python-base /app /app
COPY --from=node-base /node-app /node-app
WORKDIR /app
CMD ["python", "main.py"]
