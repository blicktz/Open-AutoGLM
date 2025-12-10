# AutoGLM-Phone-9B RunPod Deployment

Deploy AutoGLM-Phone-9B vision-language model on RunPod GPUs for use with your Mac M1 client.

## Overview

This directory contains everything needed to deploy AutoGLM-Phone-9B on RunPod.io using vLLM for fast inference. The deployment creates an OpenAI-compatible API endpoint that works seamlessly with the Phone Agent client.

## Why RunPod?

- **Mac M1 Compatible**: Your Mac M1 runs the Phone Agent client, RunPod hosts the GPU inference
- **Cost Effective**: Pay only for GPU time used (~$0.50-0.80/hour)
- **No Local GPU Required**: No need for expensive local NVIDIA GPUs
- **Fast Deployment**: Get running in ~15 minutes
- **Auto-scaling**: Pods can auto-stop when idle to save costs

## Requirements

### VRAM Requirements
AutoGLM-Phone-9B requires approximately 22-24GB VRAM. Recommended GPUs:

| GPU                           | VRAM  | Cost/Hour | Recommendation       |
|-------------------------------|-------|-----------|----------------------|
| NVIDIA RTX A6000              | 48GB  | ~$0.79    | Best (plenty headroom)|
| NVIDIA RTX 5000 Ada Generation| 32GB  | ~$0.69    | Excellent            |
| NVIDIA GeForce RTX 4090       | 24GB  | ~$0.50    | Good (tight fit)     |
| NVIDIA RTX A5000              | 24GB  | ~$0.69    | Good (tight fit)     |

### Local Requirements
- Docker installed and running
- RunPod account with API key
- Python 3.10+ (for testing)

## Quick Start

### 1. Setup Credentials

```bash
cd runpod_serve

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Add to `.env`:
```bash
RUNPOD_API_KEY=your-runpod-api-key-here
DOCKER_USERNAME=your-dockerhub-username
```

Get your RunPod API key from: https://www.runpod.io/console/user/settings

### 2. Docker Hub Authentication

Login to Docker Hub interactively (you'll be prompted for password):

```bash
docker login
```

This is required once per machine. The Makefile will check if you're logged in before pushing images.

### 3. Build and Deploy Docker Image

```bash
# Build and push to Docker Hub (uses credentials from .env and docker login)
make docker-deploy

# This will:
# - Check your credentials (.env file and docker login status)
# - Build Docker image with vLLM (fast - no model download during build)
# - Push to Docker Hub
# Takes ~2-3 minutes
```

**Note:** The model is NOT included in the Docker image. It will be automatically downloaded from Hugging Face when the RunPod container first starts.

### 4. Create RunPod Instance

```bash
# Create pod with default GPU (RTX A6000)
make runpod-create

# Or specify GPU type:
make runpod-create RUNPOD_GPU_TYPE="NVIDIA GeForce RTX 4090"
```

**First startup** will take 8-12 minutes to:
- Pull your Docker image (~2 minutes)
- Download model from Hugging Face (~18GB, ~5-8 minutes)
- Load the model into VRAM (~2 minutes)
- Start the vLLM server

**Subsequent starts** (after first run) are much faster (~2-3 minutes) because the model is cached on the pod volume.

### 5. Get Connection URL

```bash
make runpod-url
```

Example output: `https://abc123xyz-8000.proxy.runpod.net/v1`

### 6. Test Deployment

```bash
# Basic health check
make runpod-test

# Advanced testing with image
python test_client.py $(make runpod-url) /path/to/screenshot.png
```

### 7. Use with Phone Agent

```bash
# Go back to main directory
cd ..

# Interactive mode
python main.py --base-url https://YOUR-POD-ID-8000.proxy.runpod.net/v1 --model autoglm-phone-9b

# Single task
python main.py --base-url https://YOUR-POD-ID-8000.proxy.runpod.net/v1 "打开美团搜索附近的火锅店"
```

## Management Commands

### Check Status
```bash
make runpod-status    # Quick status check
make runpod-info      # Detailed information
make runpod-logs      # View container logs
```

### Control Pod
```bash
make runpod-stop      # Stop pod (saves money)
make runpod-start     # Restart stopped pod
make runpod-delete    # Delete single pod permanently
```

### Manage Multiple Pods
```bash
make runpod-list-all    # List all pods in your account
make runpod-delete-all  # Delete ALL pods (requires 'DELETE ALL' confirmation)
```

**Warning:** `runpod-delete-all` will delete **ALL** RunPod instances in your account, not just AutoGLM pods. Use with caution!

### Get Help
```bash
make help            # Show all available commands
```

## Architecture

### Deployment Flow
```
┌─────────────────┐
│   Mac M1 Client │
│  Phone Agent    │
└────────┬────────┘
         │ HTTPS API calls
         ▼
┌─────────────────┐
│  RunPod GPU Pod │
│  vLLM Server    │
│  AutoGLM-9B     │
└─────────────────┘
```

### Docker Image Contents
- Base: `vllm/vllm-openai:latest`
- Pre-downloaded: AutoGLM-Phone-9B model (~18GB)
- Server: vLLM OpenAI-compatible API
- Port: 8000 (exposed via RunPod proxy)

### vLLM Configuration
The Dockerfile configures vLLM with these parameters (from README):
```bash
--served-model-name autoglm-phone-9b
--allowed-local-media-path /
--mm-encoder-tp-mode data
--mm_processor_cache_type shm
--mm_processor_kwargs {"max_pixels":5000000}
--max-model-len 25480
--chat-template-content-format string
--limit-mm-per-prompt {"image":10}
```

## Cost Estimation

### Typical Usage Scenarios

**Development/Testing** (intermittent use):
- Cost: ~$2-5/day
- Usage: 2-4 hours active pod time
- Strategy: Stop pod when not in use

**Active Development** (8 hour day):
- Cost: ~$4-6/day
- Usage: Full day pod running
- Strategy: Use auto-stop when idle

**Batch Processing** (100 phone tasks):
- Cost: ~$1-2
- Usage: 1-2 hours continuous
- Strategy: Delete pod after completion

### Cost Saving Tips
1. **Always stop pods when not in use**: `make runpod-stop`
2. **Use auto-stop feature**: Pods auto-stop after 5-10 minutes idle
3. **Delete after batch jobs**: `make runpod-delete`
4. **Choose appropriate GPU**: RTX 4090 is cheapest but has tighter VRAM

## Troubleshooting

### Pod Not Starting
```bash
# Check logs
make runpod-logs

# Common issues:
# - Model still downloading (takes 5-10 min first time)
# - Out of VRAM (use larger GPU)
# - Image not found (check Docker Hub)
```

### Connection Refused
```bash
# Verify pod is running
make runpod-info

# Wait a few more minutes for model loading
# Check health endpoint
curl https://YOUR-POD-ID-8000.proxy.runpod.net/health
```

### Model Not Found Error
```bash
# Check available models
curl https://YOUR-POD-ID-8000.proxy.runpod.net/v1/models

# If autoglm-phone-9b not listed, check logs:
make runpod-logs
```

### Out of VRAM
```bash
# Recreate with larger GPU
make runpod-delete
make runpod-create RUNPOD_GPU_TYPE="NVIDIA RTX A6000"
```

### Docker Build Fails
```bash
# Ensure Docker is running
docker info

# Check disk space (need ~15GB for build)
df -h

# If low on space, clean up Docker
docker system prune -a

# Try building again
make docker-build
```

**Note:** With the optimized Dockerfile, builds only need ~15GB disk space (down from ~40GB) since the model downloads on RunPod instead of during build.

### Authentication Errors

**Missing .env file:**
```bash
# Error: .env file not found
cp .env.example .env
nano .env  # Add your RUNPOD_API_KEY and DOCKER_USERNAME
```

**Not logged into Docker Hub:**
```bash
# Error: denied: requested access to the resource is denied
docker login
# Enter your Docker Hub credentials when prompted
```

**RUNPOD_API_KEY not set:**
```bash
# Edit .env file and add your API key
nano .env
# Add: RUNPOD_API_KEY=your-api-key-here

# Verify it's loaded
make runpod-check
```

**Docker Hub push unauthorized:**
```bash
# Make sure you're logged in
docker login

# Verify login status
docker info | grep Username

# If still failing, try logging out and back in
docker logout
docker login
```

## Development Workflow

### Typical Development Session

```bash
# Morning: Start pod
cd runpod_serve
make runpod-start
# Wait 2-3 minutes for warmup

# Verify it's ready
make runpod-test

# Get URL for the day
export AUTOGLM_URL=$(make runpod-url)

# Work with Phone Agent
cd ..
python main.py --base-url $AUTOGLM_URL --model autoglm-phone-9b

# Evening: Stop pod to save money
cd runpod_serve
make runpod-stop
```

### Quick Test Cycle

```bash
# Test a code change
make runpod-test

# View logs if issues
make runpod-logs

# Test with real phone task
cd ..
python main.py --base-url $(cd runpod_serve && make runpod-url) "打开微信"
```

## Files Overview

```
runpod_serve/
├── Dockerfile           # vLLM container with AutoGLM-Phone-9B
├── Makefile            # Deployment automation
├── test_client.py      # Test script for deployed model
├── .env.example        # Environment template
├── .runpod_pod_id      # Created automatically (pod ID)
└── README.md           # This file
```

## Advanced Configuration

### Custom GPU Type
```bash
make runpod-create RUNPOD_GPU_TYPE="NVIDIA RTX 5000 Ada Generation"
```

### Custom Docker Tag
```bash
make docker-deploy DOCKER_TAG=v1.0
```

### Custom Pod Name
```bash
make runpod-create RUNPOD_POD_NAME=my-dev-pod
```

## FAQ

**Q: Can I use this with multiple clients?**
A: Yes! The RunPod endpoint can be shared across multiple Mac/Linux clients.

**Q: How long does first startup take?**
A: ~5-10 minutes for model loading into VRAM. Subsequent starts are ~2-3 minutes.

**Q: Can I use a different model?**
A: Yes, edit the Dockerfile to use a different model. Remember to update VRAM requirements.

**Q: Does this work on Windows?**
A: Yes! The client works on Windows too. Just install Python and ADB.

**Q: How do I update the model?**
A: Rebuild the Docker image: `make docker-deploy` and recreate the pod.

## Support

- **RunPod Docs**: https://docs.runpod.io/
- **vLLM Docs**: https://docs.vllm.ai/
- **AutoGLM Repo**: https://github.com/zai-org/Open-AutoGLM
- **Issues**: File issues in the main repository

## License

This deployment configuration is part of the Open-AutoGLM project. See main repository for license details.
