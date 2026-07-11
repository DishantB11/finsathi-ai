# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
# Empty API URL = relative paths (/chat/async) in the same container.
ENV REACT_APP_API_URL=
RUN npm run build

# Stage 2: Python backend + React build
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy React build into backend/static/
COPY --from=frontend-build /app/frontend/build ./static

# Expose Render's default web port
EXPOSE 10000

# Start FastAPI on the port provided by Render
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-10000}"]
