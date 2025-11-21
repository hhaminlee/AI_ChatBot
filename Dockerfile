# Multi-stage build for optimized image
FROM ollama/ollama:latest as ollama-base

# Install Python and dependencies
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy ollama binary from ollama image
COPY --from=ollama-base /bin/ollama /bin/ollama

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY app.py .

# Install Python dependencies
RUN uv sync

# Create directory for Ollama models
RUN mkdir -p /root/.ollama

# Expose ports
EXPOSE 8501 11434

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama server in background\n\
ollama serve &\n\
\n\
# Wait for Ollama to start\n\
echo "Waiting for Ollama server to start..."\n\
sleep 10\n\
\n\
# Download required models (only if not exists)\n\
echo "Checking and downloading models..."\n\
\n\
# Function to check and download model if not exists\n\
download_model_if_not_exists() {\n\
    local model=$1\n\
    if ! ollama list | grep -q "$model"; then\n\
        echo "Downloading $model..."\n\
        ollama pull "$model"\n\
    else\n\
        echo "$model already exists, skipping download"\n\
    fi\n\
}\n\
\n\
download_model_if_not_exists "embeddinggemma"\n\
download_model_if_not_exists "qwen3:8b"\n\
\n\
echo "Models downloaded successfully!"\n\
\n\
# Start Streamlit app\n\
exec uv run streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port 8501\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]