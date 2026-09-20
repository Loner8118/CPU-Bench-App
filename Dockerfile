FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment defaults (overridable at runtime / via .env)
ENV PORT=5000 \
    MAX_N=35 \
    MAX_ITER=2000000 \
    DEFAULT_N=28

EXPOSE 5000

# Simple, dependable start (use gunicorn for slightly more realistic serving)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "app:app"]
