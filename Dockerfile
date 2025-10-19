FROM python:3.11-slim

WORKDIR /app

# Install Python deps and Playwright with Chromium and system deps
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m playwright install --with-deps chromium

# Copy the application source
COPY . /app

# Ensure stdout/stderr are unbuffered for clear logs
ENV PYTHONUNBUFFERED=1

# Default command (Railway Schedule can override this with the job command)
CMD ["python", "-m", "notifier.toto_main"]
