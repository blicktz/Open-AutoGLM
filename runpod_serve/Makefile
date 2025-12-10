.PHONY: help docker-build docker-push docker-deploy runpod-create runpod-info runpod-logs runpod-stop runpod-start runpod-delete runpod-delete-all runpod-list-all runpod-test runpod-url runpod-status runpod-check
.DEFAULT_GOAL := help

# Load environment variables from .env file
-include .env
export

# Docker and RunPod variables
DOCKER_IMAGE_NAME := autoglm-phone-9b-vllm
DOCKER_TAG ?= latest
DOCKER_FULL_NAME := $(DOCKER_USERNAME)/$(DOCKER_IMAGE_NAME):$(DOCKER_TAG)
RUNPOD_POD_NAME ?= autoglm-phone-$(shell date +%s)

# GPU selection - AutoGLM-Phone-9B requires ~22-24GB VRAM
# IMPORTANT: AutoGLM requires vLLM 0.12+ which needs CUDA 12.9
#
# CUDA 12.8/12.9 Compatible GPUs (REQUIRED for vLLM 0.12+):
# NVIDIA L40S (48GB) - $0.79/hr - RECOMMENDED: Best value, Ada Lovelace
# NVIDIA RTX 5090 (32GB) - $0.89/hr - Blackwell (newest), verify vLLM support
# NVIDIA L40 (48GB) - $0.79/hr - Ada Lovelace
# NVIDIA RTX 6000 Ada Generation (48GB) - $0.79/hr - Ada Lovelace
# NVIDIA H100 PCIe (80GB) - $1.99-2.39/hr - Hopper, confirmed CUDA 12.9
# NVIDIA H100 NVL (94GB) - $2.59/hr - Hopper
# NVIDIA H100 SXM (80GB) - $2.69/hr - Hopper
# NVIDIA H200 (141GB) - $3.05-3.59/hr - Hopper
#
# ⚠️ OLD GPUs (CUDA 12.4 only - NOT compatible with vLLM 0.12+):
# NVIDIA RTX A6000 (48GB) - Not supported
# NVIDIA RTX A5000 (24GB) - Not supported
# NVIDIA GeForce RTX 4090 (24GB) - Not supported
# NVIDIA RTX 5000 Ada Generation (32GB) - Not supported
RUNPOD_GPU_TYPE ?= NVIDIA L40S

help: ## Show this help message
	@echo "AutoGLM-Phone-9B RunPod Deployment"
	@echo "==================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  1. Setup credentials:"
	@echo "     cp .env.example .env"
	@echo "     nano .env  # Add RUNPOD_API_KEY and DOCKER_USERNAME"
	@echo ""
	@echo "  2. Login to Docker Hub (interactive):"
	@echo "     docker login"
	@echo ""
	@echo "  3. Build and push Docker image:"
	@echo "     make docker-deploy"
	@echo ""
	@echo "  4. Create RunPod instance:"
	@echo "     make runpod-create"
	@echo ""
	@echo "  5. Get connection URL:"
	@echo "     make runpod-url"
	@echo ""
	@echo "  6. Test the deployment:"
	@echo "     make runpod-test"
	@echo ""
	@echo "  7. Use from Mac M1 client:"
	@echo "     cd .."
	@echo "     python main.py --base-url https://POD_ID-8000.proxy.runpod.net/v1 --model autoglm-phone-9b"
	@echo ""
	@echo "GPU Options (set with RUNPOD_GPU_TYPE=...):"
	@echo "  CUDA 12.8/12.9 Compatible (Required for vLLM 0.12+):"
	@echo "  - NVIDIA L40S (48GB, $$0.79/hr, RECOMMENDED)"
	@echo "  - NVIDIA RTX 5090 (32GB, $$0.89/hr, Blackwell)"
	@echo "  - NVIDIA L40 (48GB, $$0.79/hr)"
	@echo "  - NVIDIA RTX 6000 Ada Generation (48GB, $$0.79/hr)"
	@echo "  - NVIDIA H100 PCIe (80GB, $$1.99-2.39/hr)"
	@echo "  - NVIDIA H100 SXM (80GB, $$2.69/hr)"
	@echo "  - NVIDIA H200 (141GB, $$3.05-3.59/hr)"

docker-build: ## Build Docker image for RunPod deployment
	@echo "Building Docker image: $(DOCKER_FULL_NAME)"
	@echo "========================================"
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "❌ Docker not found. Please install Docker first."; \
		exit 1; \
	fi
	@if ! docker info >/dev/null 2>&1; then \
		echo "❌ Docker is not running. Please start Docker."; \
		exit 1; \
	fi
	@echo "✓ Docker is running"
	@echo "Building image..."
	@echo "📦 Building image for linux/amd64 (RunPod architecture)"
	@echo "💡 Building on Mac M1? Platform flag ensures AMD64 compatibility"
	@echo "💡 Note: Model will download on RunPod first startup (~8-12 min)"
	docker build --platform linux/amd64 -t $(DOCKER_FULL_NAME) .
	@echo "✅ Docker image built successfully: $(DOCKER_FULL_NAME)"

docker-push: docker-build ## Push Docker image to Docker Hub
	@echo "Pushing Docker image: $(DOCKER_FULL_NAME)"
	@echo "========================================="
	@if ! docker info | grep -q "Username"; then \
		echo "🔑 Logging into Docker Hub..."; \
		docker login; \
	fi
	@echo "📤 Pushing image..."
	docker push $(DOCKER_FULL_NAME)
	@echo "✅ Image pushed successfully to Docker Hub"

docker-deploy: docker-push ## Build and push Docker image (shortcut)
	@echo "🎉 Docker deployment complete!"
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. Create RunPod instance: make runpod-create"
	@echo "2. Get connection URL: make runpod-info"
	@echo "3. Test deployment: make runpod-test"
	@echo ""
	@echo "🐳 Your image: $(DOCKER_FULL_NAME)"
	@echo "🌐 Docker Hub: https://hub.docker.com/r/$(DOCKER_USERNAME)/$(DOCKER_IMAGE_NAME)"

runpod-check: ## Check RunPod CLI installation and credentials
	@echo "Checking RunPod CLI installation..."
	@if ! command -v runpodctl >/dev/null 2>&1; then \
		echo "❌ runpodctl not found. Installing..."; \
		pip install runpodctl; \
	fi
	@echo "✓ runpodctl installed"
	@if [ ! -f ".env" ]; then \
		echo "❌ .env file not found"; \
		echo "Please create .env file with your RunPod API key:"; \
		echo "  cp .env.example .env"; \
		echo "  nano .env  # Add your RUNPOD_API_KEY"; \
		echo ""; \
		echo "Get your API key from: https://www.runpod.io/console/user/settings"; \
		exit 1; \
	fi
	@if [ -z "$(RUNPOD_API_KEY)" ]; then \
		echo "❌ RUNPOD_API_KEY not set in .env file"; \
		echo "Please edit .env and add:"; \
		echo "  RUNPOD_API_KEY=your-api-key-here"; \
		echo ""; \
		echo "Get your API key from: https://www.runpod.io/console/user/settings"; \
		exit 1; \
	fi
	@echo "✓ RUNPOD_API_KEY configured"
	@if [ -z "$(DOCKER_USERNAME)" ]; then \
		echo "❌ DOCKER_USERNAME not set in .env file"; \
		echo "Please edit .env and add:"; \
		echo "  DOCKER_USERNAME=your-dockerhub-username"; \
		exit 1; \
	fi
	@echo "✓ DOCKER_USERNAME configured"

runpod-create: runpod-check ## Create and deploy RunPod instance
	@echo "Creating RunPod instance for AutoGLM-Phone-9B..."
	@echo "==============================================="
	@echo "📦 Image: $(DOCKER_FULL_NAME)"
	@echo "🔧 GPU: $(RUNPOD_GPU_TYPE)"
	@echo "🏷️  Name: $(RUNPOD_POD_NAME)"
	@echo "💾 VRAM Required: ~22-24GB"
	@echo ""
	@read -p "Continue? (y/N): " confirm; \
	if [ "$$confirm" != "y" ] && [ "$$confirm" != "Y" ]; then \
		echo "Cancelled."; \
		exit 1; \
	fi
	@echo "🚀 Creating pod..."
	@pod_output=$$(runpodctl create pod \
		--name "$(RUNPOD_POD_NAME)" \
		--imageName "$(DOCKER_FULL_NAME)" \
		--gpuType "$(RUNPOD_GPU_TYPE)" \
		--gpuCount 1 \
		--volumeSize 50 \
		--containerDiskSize 30 \
		--ports "8000/http" 2>&1); \
	if echo "$$pod_output" | grep -q "error\|Error\|ERROR"; then \
		echo "❌ Failed to create pod:"; \
		echo "$$pod_output"; \
		exit 1; \
	fi; \
	pod_id=$$(echo "$$pod_output" | grep -oE '"[a-z0-9-]+"' | head -1 | tr -d '"'); \
	if [ -n "$$pod_id" ]; then \
		echo "$$pod_id" > .runpod_pod_id; \
		echo "✅ Pod created successfully!"; \
		echo "🆔 Pod ID: $$pod_id"; \
		echo "💾 Pod ID saved to .runpod_pod_id"; \
		echo ""; \
		echo "⏳ Pod is starting up..."; \
		echo "⚠️  FIRST STARTUP: Will take 8-12 minutes (model download ~18GB + load to VRAM)"; \
		echo "⚡ SUBSEQUENT STARTS: Only 2-3 minutes (model already cached)"; \
		echo "🔍 Check status: make runpod-info"; \
		echo "🌐 Get URL: make runpod-url"; \
	else \
		echo "❌ Could not extract pod ID from output:"; \
		echo "$$pod_output"; \
	fi

runpod-info: ## Get RunPod instance status and connection URL
	@echo "RunPod Instance Information"
	@echo "=========================="
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "🆔 Pod ID: $$pod_id"; \
	echo ""; \
	echo "📊 Status:"; \
	pod_info=$$(runpodctl get pod $$pod_id 2>/dev/null); \
	if [ $$? -eq 0 ]; then \
		echo "$$pod_info" | grep -E "(Status|Runtime|GPU|Container)"; \
		echo ""; \
		if echo "$$pod_info" | grep -q "RUNNING"; then \
			echo "✅ Pod is running!"; \
			echo ""; \
			echo "🔗 Connection URL: https://$$pod_id-8000.proxy.runpod.net"; \
			echo "🏥 Health check: curl https://$$pod_id-8000.proxy.runpod.net/health"; \
			echo "📋 Models list: curl https://$$pod_id-8000.proxy.runpod.net/v1/models"; \
			echo ""; \
			echo "🎉 Ready for use!"; \
			echo "💡 Test: make runpod-test"; \
			echo "💡 Use from Mac: python main.py --base-url https://$$pod_id-8000.proxy.runpod.net/v1"; \
		else \
			echo "⏳ Pod is not yet running. Status check:"; \
			echo "$$pod_info" | grep "Status"; \
		fi; \
	else \
		echo "❌ Could not get pod information. Pod may not exist."; \
	fi

runpod-url: ## Get just the RunPod connection URL
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "https://$$pod_id-8000.proxy.runpod.net/v1"

runpod-test: ## Test RunPod instance health and model availability
	@echo "Testing RunPod AutoGLM instance..."
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	url="https://$$pod_id-8000.proxy.runpod.net"; \
	echo "🔗 Testing: $$url"; \
	echo ""; \
	echo "1️⃣  Health Check:"; \
	response=$$(curl -s -w "\n%{http_code}" "$$url/health" 2>&1); \
	http_code=$$(echo "$$response" | tail -1); \
	body=$$(echo "$$response" | head -n -1); \
	if [ "$$http_code" = "200" ]; then \
		echo "✅ Health check passed"; \
		echo "$$body" | python3 -m json.tool 2>/dev/null || echo "$$body"; \
	else \
		echo "❌ Health check failed (HTTP $$http_code)"; \
		echo "$$body"; \
	fi; \
	echo ""; \
	echo "2️⃣  Models Check:"; \
	models=$$(curl -s "$$url/v1/models" 2>&1); \
	if echo "$$models" | grep -q "autoglm-phone-9b"; then \
		echo "✅ AutoGLM model available"; \
		echo "$$models" | python3 -m json.tool 2>/dev/null || echo "$$models"; \
	else \
		echo "❌ AutoGLM model not found"; \
		echo "$$models"; \
	fi; \
	echo ""; \
	if [ "$$http_code" = "200" ] && echo "$$models" | grep -q "autoglm-phone-9b"; then \
		echo "🎉 All tests passed! Your AutoGLM deployment is ready."; \
		echo ""; \
		echo "📝 Use from Mac M1:"; \
		echo "   cd .."; \
		echo "   python main.py --base-url $$url/v1 --model autoglm-phone-9b"; \
	else \
		echo "⚠️  Some tests failed. Pod might still be starting up."; \
		echo "💡 Try: make runpod-logs"; \
	fi

runpod-logs: ## Show RunPod instance logs
	@echo "RunPod Instance Logs"
	@echo "==================="
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "🆔 Pod ID: $$pod_id"; \
	echo ""; \
	runpodctl logs $$pod_id

runpod-stop: ## Stop RunPod instance (saves money)
	@echo "Stopping RunPod instance..."
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "🆔 Pod ID: $$pod_id"; \
	echo "🛑 Stopping pod..."; \
	runpodctl stop pod $$pod_id; \
	echo "✅ Pod stopped successfully"; \
	echo "💰 Pod is no longer consuming credits"

runpod-start: ## Start stopped RunPod instance
	@echo "Starting RunPod instance..."
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Run 'make runpod-create' first."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "🆔 Pod ID: $$pod_id"; \
	echo "🚀 Starting pod..."; \
	runpodctl start pod $$pod_id; \
	echo "✅ Pod started successfully"; \
	echo "⏳ Give it 2-3 minutes to load the model"; \
	echo "🔍 Check status: make runpod-info"

runpod-delete: ## Delete RunPod instance
	@echo "Deleting RunPod instance..."
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod ID found. Nothing to delete."; \
		exit 1; \
	fi
	@pod_id=$$(cat .runpod_pod_id); \
	echo "🆔 Pod ID: $$pod_id"; \
	echo "⚠️  This will permanently delete the pod and all its data."; \
	read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "🗑️  Deleting pod..."; \
		runpodctl remove pod $$pod_id; \
		rm -f .runpod_pod_id; \
		echo "✅ Pod deleted successfully"; \
	else \
		echo "Cancelled."; \
	fi

runpod-list-all: runpod-check ## List all RunPod instances
	@echo "Listing all RunPod instances..."
	@echo "=============================="
	@runpodctl get pod 2>/dev/null || echo "❌ Failed to list pods. Check your RUNPOD_API_KEY."

runpod-delete-all: runpod-check ## Delete ALL RunPod instances (use with caution!)
	@echo "⚠️  WARNING: Delete ALL RunPod Instances"
	@echo "========================================"
	@echo ""
	@echo "This will DELETE ALL pods in your RunPod account!"
	@echo ""
	@echo "📋 Current pods:"
	@runpodctl get pod 2>/dev/null | grep -E "(ID|Running|Stopped)" || echo "No pods found"
	@echo ""
	@pod_ids=$$(runpodctl get pod 2>/dev/null | grep -oE '[a-z0-9-]{36}' || echo ""); \
	if [ -z "$$pod_ids" ]; then \
		echo "✅ No pods to delete"; \
		exit 0; \
	fi; \
	pod_count=$$(echo "$$pod_ids" | wc -l | tr -d ' '); \
	echo "Found $$pod_count pod(s) to delete"; \
	echo ""; \
	read -p "Type 'DELETE ALL' to confirm: " confirm; \
	if [ "$$confirm" = "DELETE ALL" ]; then \
		echo ""; \
		echo "🗑️  Deleting all pods..."; \
		deleted=0; \
		failed=0; \
		for pod_id in $$pod_ids; do \
			echo "Deleting pod: $$pod_id..."; \
			if runpodctl remove pod $$pod_id 2>/dev/null; then \
				deleted=$$((deleted + 1)); \
				echo "  ✅ Deleted"; \
			else \
				failed=$$((failed + 1)); \
				echo "  ❌ Failed"; \
			fi; \
		done; \
		rm -f .runpod_pod_id; \
		echo ""; \
		echo "📊 Summary:"; \
		echo "  Deleted: $$deleted"; \
		echo "  Failed: $$failed"; \
		echo ""; \
		echo "✅ Cleanup complete"; \
	else \
		echo ""; \
		echo "Cancelled. No pods were deleted."; \
	fi

runpod-status: ## Quick status check of RunPod instance
	@if [ ! -f ".runpod_pod_id" ]; then \
		echo "❌ No pod found. Run 'make runpod-create' to deploy."; \
	else \
		pod_id=$$(cat .runpod_pod_id); \
		echo "🆔 Pod: $$pod_id"; \
		status=$$(runpodctl get pod $$pod_id 2>/dev/null | grep "Status" || echo "Status: Unknown"); \
		echo "📊 $$status"; \
		if echo "$$status" | grep -q "RUNNING"; then \
			url="https://$$pod_id-8000.proxy.runpod.net"; \
			echo "🌐 URL: $$url/v1"; \
		fi; \
	fi

clean: ## Clean up local files
	@echo "Cleaning up..."
	@rm -f .runpod_pod_id
	@echo "✓ Cleaned up!"
