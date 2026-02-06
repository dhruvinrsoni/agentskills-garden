# Dockerfile for analyze_history skill
# Part of agentskills-garden

FROM python:3.11-slim

# Install git (required for this skill)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy skill files
COPY schema.json main.py ./

# Create non-root user
RUN useradd -m -r skilluser && chown -R skilluser /app
USER skilluser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run the skill
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
