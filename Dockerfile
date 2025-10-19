FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app
COPY . /app

# Ensure stdout/stderr are unbuffered for clear logs
ENV PYTHONUNBUFFERED=1

# Default command (Railway Schedule can override this with the job command)
CMD ["python", "-m", "notifier.toto_main"]

