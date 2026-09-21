FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install Vulkan development libraries and C++ build tools inside the container
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    vulkan-tools \
    libvulkan-dev \
    vulkan-validationlayers \
    spirv-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY pyproject.toml uv.lock ./

# Compile llama-cpp-python with Vulkan support inside the container
ENV CMAKE_ARGS="-DGGML_VULKAN=on"
RUN uv sync --no-cache

# Copy project source and knowledgebase
COPY src/ ./src/
COPY knowledgebase/ ./knowledgebase/

EXPOSE 8000 8501