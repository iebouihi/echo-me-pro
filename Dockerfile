
FROM python:3.12-slim AS builder
# Set working directory
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies with UV (system-wide for production)
# --system: Install to system Python (not venv)
# --no-cache: Don't cache for smaller layer size
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Runtime (minimal production image)
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder (UV installs to system Python)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser me/ ./me/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    GRADIO_SERVER_NAME=0.0.0.0 \
    GRADIO_SERVER_PORT=7860 \
    PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

# Expose Gradio port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860', timeout=5)"

# Run the application
CMD ["python", "app.py"]
