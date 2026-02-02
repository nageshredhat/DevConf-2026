#!/usr/bin/env python3
"""
Step 1: Model Fetch from HuggingFace
Downloads and prepares models for security pipeline
"""

import os
from huggingface_hub import snapshot_download
import json

MODELS = [
    "Qwen/Qwen2.5-0.5B",  # Using available Qwen model
    "google/gemma-2-2b-it",  # Using available Gemma model
    "microsoft/DialoGPT-medium"  # Alternative for OCR testing
]

def download_model(model_name, local_dir):
    """Download model from HuggingFace"""
    print(f"Downloading {model_name}...")
    try:
        snapshot_download(
            repo_id=model_name,
            local_dir=local_dir,
            local_dir_use_symlinks=False
        )
        print(f"✓ Downloaded {model_name}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {model_name}: {e}")
        return False

def main():
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    results = {}
    for model in MODELS:
        model_dir = os.path.join(models_dir, model.replace("/", "_"))
        success = download_model(model, model_dir)
        results[model] = {"downloaded": success, "path": model_dir}
    
    # Save results
    with open("models/download_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDownload complete. Results saved to models/download_results.json")

if __name__ == "__main__":
    main()
