# Dockerfile for map_dependencies skill
# Part of agentskills-garden

FROM python:3.11-slim

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
