# Dockerfile for summarize_code skill
FROM python:3.11-slim

LABEL maintainer="AgentSkills Garden"
LABEL org.opencontainers.image.source="https://github.com/dhruvinrsoni/agentskills-garden"
LABEL org.opencontainers.image.description="Code Summarizer Skill - Summarizes code with context"

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash agentskill && \
    chown -R agentskill:agentskill /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY schema.json main.py ./

# Switch to non-root user
USER agentskill

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the skill
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
