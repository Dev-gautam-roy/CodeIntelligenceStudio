FROM python:3.11-slim

# Security issue: Runs as root user (no non-root USER instruction)
USER root

WORKDIR /app
COPY . /app

# Missing HEALTHCHECK instruction
CMD ["python", "main.py"]
