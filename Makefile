.PHONY: help run run-task list-apps test-adb
.DEFAULT_GOAL := help

# Get RunPod URL from runpod_serve directory
RUNPOD_URL := $(shell cd runpod_serve && if [ -f ".runpod_pod_id" ]; then pod_id=$$(cat .runpod_pod_id); echo "https://$$pod_id-8000.proxy.runpod.net/v1"; else echo ""; fi)

help: ## Show this help message
	@echo "Open-AutoGLM - Phone Agent"
	@echo "=========================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  1. Make sure ADB device/emulator is connected:"
	@echo "     adb devices"
	@echo ""
	@echo "  2. Make sure RunPod instance is running:"
	@echo "     cd runpod_serve && make runpod-status"
	@echo ""
	@echo "  3. Run interactive mode:"
	@echo "     make run"
	@echo ""

run: ## Run Open-AutoGLM in interactive mode with RunPod
	@echo "Starting Open-AutoGLM Client (Interactive Mode)"
	@echo "=============================================="
	@if [ -z "$(RUNPOD_URL)" ]; then \
		echo "❌ No RunPod instance found."; \
		echo ""; \
		echo "Please deploy RunPod first:"; \
		echo "  cd runpod_serve"; \
		echo "  make docker-deploy"; \
		echo "  make runpod-create"; \
		exit 1; \
	fi
	@echo "🔗 RunPod endpoint: $(RUNPOD_URL)"
	@echo "📱 Checking ADB connection..."
	@if ! command -v adb >/dev/null 2>&1; then \
		echo "❌ ADB not found in PATH"; \
		echo "   Make sure ADB is installed and configured"; \
		exit 1; \
	fi
	@devices=$$(adb devices | grep -v "List of devices" | grep "device$$" | wc -l | tr -d ' '); \
	if [ "$$devices" = "0" ]; then \
		echo "❌ No Android device/emulator connected"; \
		echo "   Connect device and run: adb devices"; \
		exit 1; \
	fi
	@echo "✅ ADB connected ($$devices device(s))"
	@echo ""
	@echo "Interactive mode starting..."
	@echo "Type your tasks or 'exit' to quit."
	@echo ""
	python main.py --base-url $(RUNPOD_URL) --model autoglm-phone-9b

run-task: ## Run a specific task (usage: make run-task TASK="Open Chrome")
	@echo "Running Open-AutoGLM Task"
	@echo "========================"
	@if [ -z "$(RUNPOD_URL)" ]; then \
		echo "❌ No RunPod instance found."; \
		exit 1; \
	fi
	@if [ -z "$(TASK)" ]; then \
		echo "❌ No task specified. Usage:"; \
		echo "   make run-task TASK=\"Open Chrome browser\""; \
		echo "   make run-task TASK=\"Go to home screen\""; \
		exit 1; \
	fi
	@echo "🔗 RunPod endpoint: $(RUNPOD_URL)"
	@echo "📱 Task: $(TASK)"
	@echo ""
	python main.py --base-url $(RUNPOD_URL) --model autoglm-phone-9b --lang en "$(TASK)"

list-apps: ## List all supported apps
	@python main.py --list-apps

test-adb: ## Test ADB connection to device/emulator
	@echo "Testing ADB Connection"
	@echo "====================="
	@if ! command -v adb >/dev/null 2>&1; then \
		echo "❌ ADB not found in PATH"; \
		exit 1; \
	fi
	@echo "✅ ADB installed"
	@echo ""
	@echo "Connected devices:"
	@adb devices
