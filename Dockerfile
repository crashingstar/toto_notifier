FROM python:3.12-bookworm

ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Playwright (Python package) and Chromium with all required OS deps
RUN python -m pip install -U pip setuptools wheel \
    && python -m pip install "playwright==1.55.0" \
    && python -m playwright install --with-deps chromium

# Copy the application source
COPY . /app

# Default command (Railway Schedule can override this with the job command)
CMD ["python", "-m", "notifier.toto_main"]
