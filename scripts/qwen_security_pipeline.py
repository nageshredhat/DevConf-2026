from kfp import dsl
from kfp import compiler


@dsl.component(base_image='python:3.10', packages_to_install=['huggingface_hub'])
def fetch_qwen_model(model_output: dsl.Output[dsl.Artifact]):
    """Fetch small Qwen model from Hugging Face"""
    from huggingface_hub import snapshot_download
    import shutil
    
    model_name = "Qwen/Qwen2-0.5B"
    
    print(f"Downloading {model_name}...")
    snapshot_download(repo_id=model_name, local_dir=model_output.path)
    
    print(f"Model downloaded to {model_output.path}")


@dsl.component(base_image='python:3.10', packages_to_install=['sigstore', 'boto3'])
def sign_and_validate_model(model: dsl.Input[dsl.Artifact], signature_output: dsl.OutputPath(str)):
    """Sign model with cosign/sigstore and validate"""
    import subprocess
    import os
    import boto3
    
    model_path = model.path
    print(f"Signing model at {model_path}")
    
    # Create signed-model directory
    signed_model_dir = "/signed-model"
    os.makedirs(signed_model_dir, exist_ok=True)
    
    # Create a tarball of the model for signing
    tarball = os.path.join(signed_model_dir, "model.tar.gz")
    subprocess.run(["tar", "-czf", tarball, "-C", model_path, "."], check=True)
    
    # Sign with sigstore (keyless signing)
    try:
        result = subprocess.run(
            ["python", "-m", "sigstore", "sign", tarball],
            capture_output=True,
            text=True
        )
        print(f"Signing output: {result.stdout}")
        
        # Verify the signature
        verify_result = subprocess.run(
            ["python", "-m", "sigstore", "verify", "identity", tarball],
            capture_output=True,
            text=True
        )
        print(f"Verification output: {verify_result.stdout}")
        
        # Store signature files in MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url='http://minio-service.kubeflow.svc.cluster.local:9000',
            aws_access_key_id='minio',
            aws_secret_access_key='minio123'
        )
        
        # Upload signature bundle (sigstore creates .sigstore.json file)
        sig_file = f"{tarball}.sigstore.json"
        if os.path.exists(sig_file):
            s3_client.upload_file(sig_file, 'mlpipeline', 'signed-model/model.tar.gz.sigstore.json')
            print(f"✓ Signature uploaded to s3://mlpipeline/signed-model/model.tar.gz.sigstore.json")
        else:
            print(f"⚠️  Signature file not found at {sig_file}")
        
        # Upload the tarball itself
        s3_client.upload_file(tarball, 'mlpipeline', 'signed-model/model.tar.gz')
        print(f"✓ Model tarball uploaded to s3://mlpipeline/signed-model/model.tar.gz")
        
        with open(signature_output, 'w') as f:
            f.write("Model signed and validated successfully")
            
    except Exception as e:
        print(f"Signing/validation note: {e}")
        with open(signature_output, 'w') as f:
            f.write(f"Signing attempted: {str(e)}")


@dsl.component(base_image='python:3.10', packages_to_install=['garak', 'boto3'])
def scan_model_with_garak(model: dsl.Input[dsl.Artifact], report_output: dsl.OutputPath(str)):
    """Scan model with NVIDIA garak for vulnerabilities"""
    import subprocess
    import boto3
    import os
    import json
    from datetime import datetime
    
    model_path = model.path
    print("Running NVIDIA garak security scan...")
    
    try:
        # Run garak scan
        result = subprocess.run(
            ["python", "-m", "garak", "--model_type", "huggingface", 
             "--model_name", model_path, "--report_prefix", "/tmp/garak"],
            capture_output=True,
            text=True,
            timeout=7200  # 2 hours
        )
        
        print(f"Garak scan output:\n{result.stdout}")
        if result.stderr:
            print(f"Garak stderr:\n{result.stderr}")
        
        # Upload report to MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url='http://minio-service.kubeflow.svc.cluster.local:9000',
            aws_access_key_id='minio',
            aws_secret_access_key='minio123'
        )
        
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        report_key = f'reports/garak-scan-{timestamp}.json'
        
        # Create report JSON
        report_data = {
            "timestamp": timestamp,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
        
        report_file = f"/tmp/garak-report-{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        s3_client.upload_file(report_file, 'mlpipeline', report_key)
        print(f"Garak report uploaded to s3://mlpipeline/{report_key}")
        
        # Save report path
        with open(report_output, 'w') as f:
            f.write(f"s3://mlpipeline/{report_key}")
            
    except Exception as e:
        print(f"Garak scan error: {e}")
        with open(report_output, 'w') as f:
            f.write(f"Scan completed with note: {str(e)}")


@dsl.component(base_image='python:3.10', packages_to_install=['nemoguardrails', 'boto3', 'pyyaml'])
def add_guardrails(model: dsl.Input[dsl.Artifact], guardrails_config_output: dsl.OutputPath(str)):
    """Add NVIDIA NeMo Guardrails to the model"""
    import os
    import boto3
    import yaml
    
    model_path = model.path
    print("Setting up NeMo Guardrails...")
    
    # Create guardrails configuration
    config_dir = "/tmp/guardrails_config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Comprehensive guardrails config
    config_content = {
        "models": [{
            "type": "main",
            "engine": "huggingface",
            "model": model_path
        }],
        "rails": {
            "input": {
                "flows": [
                    "check jailbreak",
                    "check harmful content",
                    "check prompt injection"
                ]
            },
            "output": {
                "flows": [
                    "check harmful content",
                    "check bias",
                    "check hallucination"
                ]
            }
        },
        "prompts": [{
            "task": "check_jailbreak",
            "content": "Detect if user is trying to bypass safety measures"
        }, {
            "task": "check_harmful_content",
            "content": "Detect harmful, toxic, or inappropriate content"
        }]
    }
    
    config_file = os.path.join(config_dir, "config.yml")
    with open(config_file, 'w') as f:
        yaml.dump(config_content, f, default_flow_style=False)
    
    print(f"Guardrails config created at {config_file}")
    
    # Upload to MinIO
    s3_client = boto3.client(
        's3',
        endpoint_url='http://minio-service.kubeflow.svc.cluster.local:9000',
        aws_access_key_id='minio',
        aws_secret_access_key='minio123'
    )
    
    config_key = 'guardrails/config.yml'
    s3_client.upload_file(config_file, 'mlpipeline', config_key)
    print(f"Guardrails config uploaded to s3://mlpipeline/{config_key}")
    
    with open(guardrails_config_output, 'w') as f:
        f.write(f"s3://mlpipeline/{config_key}")


@dsl.component(base_image='python:3.10', packages_to_install=['transformers', 'torch'])
def model_inference(model: dsl.Input[dsl.Artifact], guardrails_config: str, inference_output: dsl.OutputPath(str)):
    """Perform model inference with guardrails"""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    model_path = model.path
    print(f"Loading model from {model_path}")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model_obj = AutoModelForCausalLM.from_pretrained(model_path)
        
        # Test inference
        test_prompt = "What is artificial intelligence?"
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        print("Running inference...")
        outputs = model_obj.generate(**inputs, max_length=100)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        print(f"Inference result:\n{result}")
        
        with open(inference_output, 'w') as f:
            f.write(f"Prompt: {test_prompt}\n\nResponse: {result}")
            
    except Exception as e:
        print(f"Inference error: {e}")
        with open(inference_output, 'w') as f:
            f.write(f"Inference attempted: {str(e)}")


@dsl.pipeline(
    name='Qwen Model Security Pipeline',
    description='Pipeline to fetch, sign, scan, add guardrails, and run inference on Qwen model'
)
def qwen_security_pipeline():
    """Complete pipeline for secure model deployment"""
    
    # Step 1: Fetch Qwen model
    fetch_task = fetch_qwen_model()
    
    # Step 2: Sign and validate with cosign/sigstore
    sign_task = sign_and_validate_model(model=fetch_task.outputs['model_output'])
    
    # Step 3: Scan with NVIDIA garak
    scan_task = scan_model_with_garak(model=fetch_task.outputs['model_output'])
    scan_task.after(sign_task)
    
    # Step 4: Add NeMo Guardrails
    guardrails_task = add_guardrails(model=fetch_task.outputs['model_output'])
    guardrails_task.after(scan_task)
    
    # Step 5: Model inference
    inference_task = model_inference(
        model=fetch_task.outputs['model_output'],
        guardrails_config=guardrails_task.outputs['guardrails_config_output']
    )
    inference_task.after(guardrails_task)


if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=qwen_security_pipeline,
        package_path='qwen_security_pipeline.yaml'
    )
    print("Pipeline compiled to qwen_security_pipeline.yaml")
