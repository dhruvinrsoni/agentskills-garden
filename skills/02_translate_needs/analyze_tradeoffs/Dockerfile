# Dockerfile for analyze_tradeoffs skill
FROM python:3.11-slim

# Labels
LABEL skill_id="analyze_tradeoffs"
LABEL skill_level="2"
LABEL skill_domain="translate_needs"

# Create non-root user
RUN useradd --create-home skilluser

# Set working directory
WORKDIR /app

# Copy requirements first for layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY schema.json .

# Switch to non-root user
USER skilluser

# Expose default port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the skill server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
