FROM mcr.microsoft.com/playwright/python:v1.47.0-jammy

WORKDIR /app

# Copy the application source
COPY . /app

# Ensure stdout/stderr are unbuffered for clear logs
ENV PYTHONUNBUFFERED=1

# Safety: ensure the Python package is present/up-to-date
# (Base image already includes Playwright and browsers.)
RUN python -m pip install --no-cache-dir -U pip setuptools wheel \
    && python -m pip install --no-cache-dir -U playwright

# Default command (Railway Schedule can override this with the job command)
CMD ["python", "-m", "notifier.toto_main"]
