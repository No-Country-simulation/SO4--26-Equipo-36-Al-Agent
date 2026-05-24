FROM python:3.12-slim

WORKDIR /code

# Install system dependencies
# Added g++ and python3-dev as they are often required by chroma-hnswlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install 'uv' (A blazing fast Python package installer written in Rust)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# OPTIMIZATION: Install PyTorch (CPU-only version). 
# By default, sentence-transformers downloads the GPU version of PyTorch which is ~2.5GB.
# Since you have no GPU, downloading the CPU version (~150MB) saves enormous time and space.
RUN uv pip install --system torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install the rest extremely fast using uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
