# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Open-AutoGLM (Phone Agent) is an Android phone automation framework that uses vision-language models to understand screen content and execute tasks via ADB. Users describe tasks in natural language (e.g., "Open Xiaohongshu and search for food"), and the agent autonomously plans and executes actions.

## Common Commands

### Installation
```bash
# Install dependencies
pip install -r requirements.txt
pip install -e .

# Development mode (includes pytest, black, mypy, ruff)
pip install -e ".[dev]"
```

### Running the Agent
```bash
# Interactive mode
python main.py --base-url http://localhost:8000/v1 --model "autoglm-phone-9b"

# Execute single task
python main.py --base-url http://localhost:8000/v1 "打开美团搜索附近的火锅店"

# Use English prompts
python main.py --lang en --base-url http://localhost:8000/v1 "Open Chrome browser"

# List supported apps
python main.py --list-apps

# List connected devices
python main.py --list-devices

# Connect to remote Android device
python main.py --connect 192.168.1.100:5555
```

### Model Deployment
The agent requires a separately deployed vision-language model server (vLLM or SGlang):

```bash
# vLLM deployment (requires NVIDIA GPU)
python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm_processor_cache_type shm \
  --mm_processor_kwargs "{\"max_pixels\":5000000}" \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt "{\"image\":10}" \
  --model zai-org/AutoGLM-Phone-9B \
  --port 8000
```

### Testing
```bash
pytest tests/
```

### ADB Setup
```bash
# Check connected devices
adb devices

# Restart ADB service if needed
adb kill-server && adb start-server

# Enable wireless debugging
adb tcpip 5555
adb connect <device-ip>:5555
```

## Architecture

### Client-Server Design
The architecture separates the agent client from the model inference server:

- **Agent Client** (this codebase): Orchestrates task execution, ADB control, and API calls
- **Model Server** (deployed separately): Runs vision-language model inference (vLLM/SGlang)
- Communication: OpenAI-compatible REST API

### Core Components

#### 1. ADB Layer (`phone_agent/adb/`)
- **connection.py**: Manages local/remote ADB connections via WiFi or USB
- **device.py**: Device control primitives (tap, swipe, back, home, long press)
- **screenshot.py**: Captures and encodes screenshots to base64
- **input.py**: Text input via ADB Keyboard

#### 2. Model Client (`phone_agent/model/client.py`)
- **ModelClient**: Wraps OpenAI client for vision-language API calls
- **MessageBuilder**: Constructs multimodal messages with images and text
- **Response Parsing**: Extracts `<think>` and `<answer>` tags from model output

#### 3. Action Handler (`phone_agent/actions/handler.py`)
- Parses JSON actions from model responses
- Executes device operations: Launch, Tap, Type, Swipe, Back, Home, Wait, Take_over
- Manages sensitive operation confirmations and manual takeovers
- Translates normalized coordinates to absolute pixel positions

#### 4. Agent Orchestrator (`phone_agent/agent.py`)
- **PhoneAgent**: Main agent loop coordinating all components
- Maintains conversation context with vision-language model
- Captures screen state, requests model decisions, executes actions
- Handles errors and max step limits

### Agent Execution Loop

1. **Capture State**: Screenshot + current app detection
2. **Build Context**: Multimodal message with screen image and task description
3. **Model Request**: Send to vision-language model via OpenAI API
4. **Parse Response**: Extract thinking process and action JSON
5. **Execute Action**: Use ADB to perform device operation
6. **Update Context**: Add assistant response, remove images to save tokens
7. **Repeat**: Continue until task finished or max steps reached

### Multimodal Message Format

Messages follow OpenAI's vision API format:
```python
{
  "role": "user",
  "content": [
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
    {"type": "text", "text": "Task description\n\n{\"current_app\": \"...\"}"}
  ]
}
```

Images are removed from context after each turn to reduce token usage.

## Platform Compatibility

### macOS (including M1/M2)
**Agent Client**: Fully compatible
- Pure Python with minimal dependencies (Pillow, openai)
- ADB works natively on macOS
- No GPU requirements for client

**Model Server**: Requires workaround
- vLLM and SGlang require NVIDIA GPUs (not available on M1/M2)
- **Recommended**: Deploy model on remote server with NVIDIA GPU, connect via `--base-url`
- **Alternative**: Use other inference backends (transformers with MPS) - not officially documented

### Remote Deployment Pattern
```bash
# On remote GPU server (Linux + NVIDIA)
python3 -m vllm.entrypoints.openai.api_server --model zai-org/AutoGLM-Phone-9B --port 8000

# On Mac M1 client
python main.py --base-url http://remote-server-ip:8000/v1 "打开淘宝"
```

## Configuration

### Environment Variables
- `PHONE_AGENT_BASE_URL`: Model API URL (default: `http://localhost:8000/v1`)
- `PHONE_AGENT_MODEL`: Model name (default: `autoglm-phone-9b`)
- `PHONE_AGENT_MAX_STEPS`: Max steps per task (default: `100`)
- `PHONE_AGENT_DEVICE_ID`: ADB device ID for multi-device setups
- `PHONE_AGENT_LANG`: Language `cn` or `en` (default: `cn`)

### System Prompts
The agent supports Chinese and English prompts:
- Chinese: `phone_agent/config/prompts_zh.py` (default)
- English: `phone_agent/config/prompts_en.py`

Switch via `--lang` parameter. Modify these files to enhance domain-specific capabilities or disable certain apps.

### Supported Apps
50+ Chinese apps including WeChat, Taobao, Meituan, Bilibili, etc. Full list in `phone_agent/config/apps.py`.

## Development Notes

- The model architecture is identical to `GLM-4.1V-9B-Thinking`
- Two model variants: `AutoGLM-Phone-9B` (Chinese), `AutoGLM-Phone-9B-Multilingual` (English)
- ADB Keyboard must be installed and enabled on Android device for text input
- Sensitive operations (login, payments) trigger confirmation callbacks or manual takeover
- Screenshot failures (black screens) indicate sensitive content - agent requests takeover
