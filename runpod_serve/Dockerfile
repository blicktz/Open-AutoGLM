# Dockerfile for AutoGLM-Phone-9B on RunPod using vLLM
# Provides OpenAI-compatible API for vision-language inference

# IMPORTANT: RunPod uses AMD64/x86_64 architecture
# Force linux/amd64 platform even when building on Mac M1 (ARM64)
FROM --platform=linux/amd64 vllm/vllm-openai:latest

# Set working directory
WORKDIR /workspace

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install additional dependencies if needed
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for optimal GPU performance
ENV CUDA_VISIBLE_DEVICES=0
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Model will be auto-downloaded from Hugging Face on first container start
# This keeps the Docker image small and fast to build
# First startup will take ~8-12 minutes to download the model (~18GB)
# Subsequent starts are fast (~2-3 minutes) as model is cached
ENV MODEL_NAME=zai-org/AutoGLM-Phone-9B

# Expose API port (matching OpenAI format)
EXPOSE 8000

# Health check endpoint
# Extended start-period to allow time for model download on first start
HEALTHCHECK --interval=30s --timeout=10s --start-period=600s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start vLLM OpenAI-compatible server with AutoGLM-specific parameters
# IMPORTANT: vllm/vllm-openai image has ENTRYPOINT ["vllm", "serve"]
# So CMD only needs to provide the model (as positional arg) and other flags
# Final command: vllm serve zai-org/AutoGLM-Phone-9B --served-model-name ...
# vLLM will automatically download the model from Hugging Face on first start
CMD ["zai-org/AutoGLM-Phone-9B", \
     "--served-model-name", "autoglm-phone-9b", \
     "--allowed-local-media-path", "/", \
     "--mm-encoder-tp-mode", "data", \
     "--mm_processor_cache_type", "shm", \
     "--mm_processor_kwargs", "{\"max_pixels\":5000000}", \
     "--max-model-len", "25480", \
     "--chat-template-content-format", "string", \
     "--limit-mm-per-prompt", "{\"image\":10}", \
     "--port", "8000", \
     "--host", "0.0.0.0"]
