# Winning Strategy Bot - Contest Optimized Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for performance
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy base template first (shared infrastructure)
COPY base-bot-template/ /app/base/

# Copy our winning strategy template
COPY winning-strategy-template/ /app/strategy/

# Install Python dependencies
COPY winning-strategy-template/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Create logs directory
RUN mkdir -p /app/logs

# Set Python path to include base template
ENV PYTHONPATH="/app/base:/app/strategy:$PYTHONPATH"

# Performance optimizations
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Contest-specific environment variables
ENV STRATEGY_NAME="winning"
ENV BOT_NAME="winning-strategy-bot"
ENV LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports for monitoring
EXPOSE 8000 8001

# Run the winning strategy bot
CMD ["python", "/app/strategy/startup.py"]

# Labels for contest submission
LABEL version="1.0"
LABEL description="Winning Strategy Bot for Trading Contest"
LABEL author="Contest Participant"
LABEL strategy="Adaptive Momentum-Reversal"
LABEL target="Maximum PnL with <50% drawdown"