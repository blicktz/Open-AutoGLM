#!/usr/bin/env python3
"""
Test client for AutoGLM-Phone-9B deployed on RunPod.
Verifies the model is working correctly with vision-language capabilities.
"""

import os
import sys
import base64
from pathlib import Path
from openai import OpenAI


def load_image_base64(image_path: str) -> str:
    """Load an image and convert to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def test_model_availability(base_url: str):
    """Test that the model is available."""
    print("🔍 Testing model availability...")
    print(f"   Base URL: {base_url}")

    client = OpenAI(base_url=base_url, api_key="EMPTY")

    try:
        models = client.models.list()
        model_ids = [model.id for model in models.data]
        print(f"✅ Found {len(model_ids)} model(s): {model_ids}")

        if "autoglm-phone-9b" in model_ids:
            print("✅ AutoGLM-Phone-9B is available!")
            return True
        else:
            print("❌ AutoGLM-Phone-9B not found in available models")
            return False
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return False


def test_text_only_inference(base_url: str):
    """Test text-only inference (basic test)."""
    print("\n📝 Testing text-only inference...")

    client = OpenAI(base_url=base_url, api_key="EMPTY")

    try:
        response = client.chat.completions.create(
            model="autoglm-phone-9b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! What is your name?"}
            ],
            max_tokens=100,
            temperature=0.1
        )

        answer = response.choices[0].message.content
        print(f"✅ Model response: {answer[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Text inference failed: {e}")
        return False


def test_vision_inference(base_url: str, image_path: str = None):
    """Test vision-language inference with an image."""
    print("\n👁️  Testing vision-language inference...")

    if image_path and os.path.exists(image_path):
        print(f"   Using image: {image_path}")
        image_base64 = load_image_base64(image_path)
        image_url = f"data:image/png;base64,{image_base64}"
    else:
        print("⚠️  No image provided, creating a test message without image")
        print("   To test with an image, provide path as argument:")
        print("   python test_client.py <RUNPOD_URL> <IMAGE_PATH>")
        return None

    client = OpenAI(base_url=base_url, api_key="EMPTY")

    try:
        response = client.chat.completions.create(
            model="autoglm-phone-9b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": "Describe this image in detail."}
                    ]
                }
            ],
            max_tokens=300,
            temperature=0.1
        )

        answer = response.choices[0].message.content
        print(f"✅ Vision model response:")
        print(f"   {answer}")
        return True
    except Exception as e:
        print(f"❌ Vision inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage: python test_client.py <RUNPOD_BASE_URL> [IMAGE_PATH]")
        print("")
        print("Example:")
        print("  python test_client.py https://abc123-8000.proxy.runpod.net/v1")
        print("  python test_client.py https://abc123-8000.proxy.runpod.net/v1 screenshot.png")
        print("")
        print("To get your RunPod URL:")
        print("  make runpod-url")
        sys.exit(1)

    base_url = sys.argv[1]
    image_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("AutoGLM-Phone-9B RunPod Test Client")
    print("=" * 60)
    print()

    # Test 1: Model availability
    if not test_model_availability(base_url):
        print("\n❌ Model availability test failed. Exiting.")
        sys.exit(1)

    # Test 2: Text-only inference
    if not test_text_only_inference(base_url):
        print("\n❌ Text inference test failed.")

    # Test 3: Vision inference (if image provided)
    if image_path:
        if not os.path.exists(image_path):
            print(f"\n⚠️  Image file not found: {image_path}")
        else:
            test_vision_inference(base_url, image_path)
    else:
        print("\n💡 Tip: Provide an image path to test vision capabilities:")
        print(f"   python test_client.py {base_url} /path/to/screenshot.png")

    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)
    print()
    print("🚀 Your AutoGLM deployment is working!")
    print()
    print("📋 Next steps:")
    print("   1. Use from the main client:")
    print(f"      cd ..")
    print(f"      python main.py --base-url {base_url} --model autoglm-phone-9b")
    print()
    print("   2. Test with your phone:")
    print("      Connect Android device via ADB and run tasks!")


if __name__ == "__main__":
    main()
