#!/usr/bin/env python3
"""
Step 2: Model Signing with Cosign and Sigstore
Signs models for authenticity and integrity verification
"""

import os
import subprocess
import json
from pathlib import Path

def generate_cosign_keys():
    """Generate cosign key pair"""
    if not os.path.exists("security/cosign.key"):
        print("Generating cosign key pair...")
        os.makedirs("security", exist_ok=True)
        
        # Generate key pair (will prompt for password)
        subprocess.run([
            "cosign", "generate-key-pair",
            "--output-key-prefix", "security/cosign"
        ], check=True)
        print("✓ Cosign keys generated")

def create_modelkit(model_path, model_name):
    """Create a ModelKit for the model"""
    modelkit_config = {
        "manifestVersion": "1.0.0",
        "package": {
            "name": model_name.replace("/", "-"),
            "version": "1.0.0",
            "description": f"Signed model: {model_name}"
        },
        "model": {
            "path": model_path,
            "framework": "transformers"
        }
    }
    
    config_path = f"{model_path}/Kitfile"
    with open(config_path, "w") as f:
        json.dump(modelkit_config, f, indent=2)
    
    return config_path

def sign_model(model_path, model_name):
    """Sign model with cosign"""
    try:
        # Create ModelKit configuration
        create_modelkit(model_path, model_name)
        
        # Create a tar archive of the model
        archive_name = f"security/{model_name.replace('/', '_')}.tar"
        subprocess.run([
            "tar", "-czf", archive_name, "-C", model_path, "."
        ], check=True)
        
        # Sign the archive
        subprocess.run([
            "cosign", "sign-blob",
            "--key", "security/cosign.key",
            "--output-signature", f"{archive_name}.sig",
            archive_name
        ], check=True)
        
        print(f"✓ Signed {model_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to sign {model_name}: {e}")
        return False

def verify_model(model_name):
    """Verify model signature"""
    try:
        archive_name = f"security/{model_name.replace('/', '_')}.tar"
        subprocess.run([
            "cosign", "verify-blob",
            "--key", "security/cosign.pub",
            "--signature", f"{archive_name}.sig",
            archive_name
        ], check=True)
        
        print(f"✓ Verified {model_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to verify {model_name}: {e}")
        return False

def main():
    # Load download results
    with open("models/download_results.json", "r") as f:
        results = json.load(f)
    
    # Generate keys if needed
    generate_cosign_keys()
    
    # Sign all downloaded models
    signing_results = {}
    for model_name, info in results.items():
        if info["downloaded"]:
            success = sign_model(info["path"], model_name)
            signing_results[model_name] = {"signed": success}
            
            if success:
                verify_model(model_name)
    
    # Save signing results
    with open("security/signing_results.json", "w") as f:
        json.dump(signing_results, f, indent=2)
    
    print("\nModel signing complete!")

if __name__ == "__main__":
    main()
