# CUDA Compatibility Guide for AutoGLM RunPod Deployment

## Problem Statement

When deploying AutoGLM-Phone-9B on RunPod, you may encounter this error:

```
nvidia-container-cli: requirement error: unsatisfied condition: cuda>=12.9
please update your driver to a newer version, or use an earlier cuda container
```

This document explains the issue and provides solutions.

## Technical Details

### Version Compatibility Matrix

| Component | Version/Requirement | CUDA Support |
|-----------|-------------------|--------------|
| **Open-AutoGLM requirements.txt** | `vllm>=0.12.0` (commented/optional) | - |
| **vLLM 0.12.0** | Latest stable | **CUDA 12.9+** required |
| **vLLM 0.6.5** | Previous stable | CUDA 12.1-12.4 |
| **RunPod Standard GPUs** | A6000, A5000, RTX 4090 | **CUDA 12.1-12.4** |
| **RunPod Newer GPUs** | H100, H200, Blackwell | CUDA 12.8+ |

### The Mismatch

- **vLLM >=0.12.0** requires CUDA 12.9 (PyTorch 2.9.0 dependency)
- **RunPod standard GPUs** (RTX A6000, A5000, RTX 4090) have CUDA 12.1-12.4 drivers
- **Result**: `vllm/vllm-openai:latest` fails to start on standard RunPod GPUs

## Root Cause

### Why vLLM 0.12+ Requires CUDA 12.9

As of December 2025:
- vLLM v0.12.0 upgraded to PyTorch 2.9.0
- PyTorch 2.9.0 requires CUDA 12.9
- This is a **breaking change** affecting deployment on older GPUs

### Why This Affects RunPod

RunPod's most common GPU types use CUDA 12.1-12.4:
- **NVIDIA RTX A6000**: CUDA 12.1/12.4
- **NVIDIA RTX A5000**: CUDA 12.1/12.4
- **NVIDIA GeForce RTX 4090**: CUDA 12.1/12.4

Newer GPUs (H100, H200, Blackwell) support CUDA 12.8+, but are more expensive and less available.

## Solutions

### Option 1: Use vLLM 0.6.5 (RECOMMENDED)

**Dockerfile change:**
```dockerfile
FROM vllm/vllm-openai:v0.6.5
```

**Pros:**
- ✅ Compatible with CUDA 12.1-12.4 (works on all RunPod GPUs)
- ✅ Full multimodal/vision model support
- ✅ Stable and well-tested
- ✅ OpenAI-compatible API
- ✅ Supports AutoGLM-Phone-9B

**Cons:**
- ⚠️ Not the latest vLLM version
- ⚠️ Doesn't meet `vllm>=0.12.0` (but it's optional - see below)

**Why this works:**
The `vllm>=0.12.0` requirement in `requirements.txt` is **commented out**:
```python
# For Model Deployment
# vllm>=0.12.0  ← This is optional!
```

The **client** (Open-AutoGLM) only needs `openai>=2.9.0` to connect to the vLLM server via API. The server's vLLM version doesn't matter to the client.

### Option 2: Use RunPod GPUs with CUDA 12.9+

**Find newer GPU types:**
```bash
# Check RunPod console for:
- NVIDIA H100 (80GB) - CUDA 12.8+
- NVIDIA H200 (141GB) - CUDA 12.8+
- NVIDIA Blackwell B200/GB200 - CUDA 12.8+ required
```

**Update Makefile:**
```bash
make runpod-create RUNPOD_GPU_TYPE="NVIDIA H100 80GB HBM3"
```

**Pros:**
- ✅ Can use latest vLLM (0.12+)
- ✅ Future-proof

**Cons:**
- ❌ More expensive (~$2-4/hour vs $0.50-0.80/hour)
- ❌ Less available (often out of stock)
- ❌ Overkill for AutoGLM-Phone-9B (only needs ~24GB VRAM)

### Option 3: Use RunPod Pre-built Worker

**Dockerfile change:**
```dockerfile
FROM runpod/worker-v1-vllm:v2.5.0stable-cuda12.1.0
```

**Pros:**
- ✅ Pre-cached on RunPod (instant startup)
- ✅ CUDA 12.1 compatible
- ✅ Optimized for RunPod

**Cons:**
- ⚠️ Uses vLLM 0.10 (older than 0.12)
- ⚠️ May need customization for OpenAI API format
- ⚠️ Less control over configuration

## Recommended Solution

**Use CUDA 12.9 Compatible GPUs** (Required for AutoGLM)

⚠️ **IMPORTANT UPDATE**: AutoGLM-Phone-9B requires vLLM >= 0.12.0, which requires CUDA 12.9.
The previous recommendation of vLLM 0.6.5 is **NOT compatible** with AutoGLM-Phone-9B.

**Best Option: NVIDIA L40S at $0.79/hr**
- Lowest cost CUDA 12.9 GPU
- 48GB VRAM (2x what you need)
- Ada Lovelace architecture
- 60% cheaper than H100 PCIe

### Implementation Steps

1. **Keep Dockerfile as-is:**
```dockerfile
FROM vllm/vllm-openai:latest  # Uses vLLM 0.12+ with CUDA 12.9
```

2. **Use CUDA 12.9 compatible GPU:**
```bash
cd /Users/blickt/Documents/software/Open-AutoGLM/runpod_serve

# Option 1: L40S (RECOMMENDED - cheapest at $0.79/hr)
make runpod-create RUNPOD_GPU_TYPE="NVIDIA L40S"

# Option 2: H100 PCIe (confirmed CUDA 12.9 support)
make runpod-create RUNPOD_GPU_TYPE="NVIDIA H100 PCIe"

# Wait 8-12 minutes for first startup (model download)
```

3. **Test deployment:**
```bash
make runpod-test
```

## Why L40S Works

### AutoGLM Model Requirements

AutoGLM-Phone-9B is based on GLM-4.1V-9B-Thinking architecture, which requires:
- **vLLM version**: >= 0.12.0 (officially required)
- **CUDA version**: 12.9 (required by vLLM 0.12+)
- **VRAM**: ~22-24GB

### L40S Specifications

```
┌─────────────────┐
│  Mac M1 Client  │  ← Only needs: openai>=2.9.0
│  Open-AutoGLM   │
└────────┬────────┘
         │ HTTP API (OpenAI compatible)
         ▼
┌─────────────────┐
│  RunPod L40S    │  ← vLLM 0.12+ with CUDA 12.9
│  48GB VRAM      │     Ada Lovelace (Compute 8.9)
│  $0.79/hr       │
└─────────────────┘
```

**L40S Advantages**:
- ✅ Ada Lovelace architecture supports CUDA 12.9
- ✅ 48GB VRAM (2x model requirements)
- ✅ Lowest cost CUDA 12.9 GPU on RunPod
- ✅ Same cost as old A6000, but compatible!

## Verification Steps

After deploying with L40S GPU:

### 1. Check Container Startup
```bash
make runpod-logs

# Should see:
# INFO: Started server process
# INFO: Waiting for application startup.
# INFO: Application startup complete.
```

### 2. Test Health Endpoint
```bash
make runpod-test

# Should see:
# ✅ Health check passed
# ✅ AutoGLM model available
```

### 3. Test from Mac M1 Client
```bash
cd /Users/blickt/Documents/software/Open-AutoGLM

# Get RunPod URL
export RUNPOD_URL=$(cd runpod_serve && make runpod-url)

# Test connection
python main.py --base-url $RUNPOD_URL --model autoglm-phone-9b --list-apps
```

## Troubleshooting

### Error: "unsatisfied condition: cuda>=12.9"

**Cause:** Using `vllm/vllm-openai:latest` which requires CUDA 12.9

**Fix:** Update Dockerfile to use specific version:
```dockerfile
FROM vllm/vllm-openai:v0.6.5
```

### Error: "Model not found"

**Cause:** Model still downloading on first startup

**Fix:** Wait 8-12 minutes for initial download, check logs:
```bash
make runpod-logs
```

### Error: Container crashes immediately

**Cause:** Possible CUDA version mismatch

**Fix:** Verify Dockerfile base image:
```bash
docker inspect vllm/vllm-openai:v0.6.5 | grep CUDA
```

### Slow First Startup

**Expected:** First startup takes 8-12 minutes to download ~18GB model

**Monitoring:**
```bash
# Watch logs in real-time
make runpod-logs

# Look for:
# Downloading model files...
# Loading weights into VRAM...
# Server ready
```

## Version History

| Date | vLLM Version | CUDA Version | Status |
|------|--------------|--------------|--------|
| Dec 2025 | 0.12.0+ | 12.9+ | ❌ Incompatible with standard RunPod GPUs |
| Dec 2025 | 0.6.5 | 12.1-12.4 | ✅ **Recommended** - Works on all RunPod GPUs |
| Nov 2025 | 0.6.3 | 12.1 | ✅ Alternative if 0.6.5 has issues |

## References

### Official Documentation
- [vLLM Installation Guide](https://docs.vllm.ai/en/stable/getting_started/installation/)
- [vLLM Release Notes](https://github.com/vllm-project/vllm/releases)
- [RunPod vLLM Guide](https://docs.runpod.io/serverless/vllm/overview)

### Related Issues
- [vLLM CUDA 12.9 Breaking Change](https://github.com/vllm-project/vllm/releases/tag/v0.12.0)
- [RunPod CUDA Compatibility](https://www.runpod.io/articles/guides/best-docker-image-vllm-inference-cuda-12-4)

### Docker Images
- [vLLM Docker Hub](https://hub.docker.com/r/vllm/vllm-openai/tags)
- [RunPod Worker vLLM](https://hub.docker.com/r/runpod/worker-vllm/tags)

## Quick Reference

### Current Working Configuration

**Dockerfile:**
```dockerfile
FROM vllm/vllm-openai:latest
# Uses vLLM 0.12+ with CUDA 12.9
```

**RunPod GPU:**
```bash
RUNPOD_GPU_TYPE="NVIDIA L40S"  # RECOMMENDED: Cheapest CUDA 12.9 GPU
# Or: "NVIDIA H100 PCIe" for confirmed support
# Or: "NVIDIA L40", "NVIDIA RTX 6000 Ada Generation"
```

**Cost:**
- L40S: ~$0.79/hour (BEST VALUE)
- H100 PCIe: ~$1.99-2.39/hour
- H100 SXM: ~$2.69/hour
- H200: ~$3.05-3.59/hour
- First startup: 8-12 minutes (one-time)
- Subsequent starts: 2-3 minutes

### Alternative If L40S Has Issues

If L40S has CUDA 12.9 compatibility issues:

**Fall back to H100 PCIe (confirmed CUDA 12.9 support):**
```bash
make runpod-create RUNPOD_GPU_TYPE="NVIDIA H100 PCIe"
# Cost: $1.99-2.39/hour (2.5-3x more expensive)
```

**Or try other Ada Lovelace GPUs:**
```bash
make runpod-create RUNPOD_GPU_TYPE="NVIDIA L40"
# Or: "NVIDIA RTX 6000 Ada Generation"
```

## Summary

AutoGLM-Phone-9B requires vLLM 0.12+ which needs CUDA 12.9. Standard RunPod GPUs (A6000, RTX 4090) only support CUDA 12.4 and are **NOT compatible**.

**Solution: Use CUDA 12.9 Compatible GPUs**
- **NVIDIA L40S** at $0.79/hr - RECOMMENDED ✅
  - Ada Lovelace architecture (Compute 8.9)
  - 48GB VRAM (sufficient for AutoGLM)
  - Same cost as old A6000 but compatible!
  - 60% cheaper than H100
- **NVIDIA H100 PCIe** at $1.99-2.39/hr - Confirmed support ✅
  - Hopper architecture (Compute 9.0)
  - 80GB VRAM (plenty of headroom)
  - Most reliable option

**Key Insight**: The client (Mac M1) only needs `openai>=2.9.0`. The server GPU must support CUDA 12.9 for vLLM 0.12+ to run AutoGLM-Phone-9B.
