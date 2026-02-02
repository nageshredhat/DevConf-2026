#!/usr/bin/env python3
"""
Step 4: Guardrails Implementation
Implements pre/post filtering with monitoring and alerting
"""

import json
import yaml
from guardrails import Guard
from guardrails.hub import ToxicLanguage, PII, Bias

def create_nemo_guardrails_config():
    """Create NeMo Guardrails configuration"""
    config = {
        "models": [
            {
                "type": "main",
                "engine": "transformers",
                "model": "microsoft/DialoGPT-medium"
            }
        ],
        "rails": {
            "input": {
                "flows": [
                    {
                        "elements": [
                            {"_type": "UserMessage"},
                            {"_type": "run_input_rails"},
                            {"_type": "BotMessage"}
                        ]
                    }
                ]
            },
            "output": {
                "flows": [
                    {
                        "elements": [
                            {"_type": "BotMessage"},
                            {"_type": "run_output_rails"}
                        ]
                    }
                ]
            }
        },
        "prompts": [
            {
                "task": "input_filtering",
                "content": "Check if the user input contains harmful content, PII, or inappropriate requests."
            },
            {
                "task": "output_filtering", 
                "content": "Ensure the bot response is safe, appropriate, and doesn't contain sensitive information."
            }
        ]
    }
    
    os.makedirs("guardrails", exist_ok=True)
    with open("guardrails/nemo_config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config

def create_guardrails_ai_config():
    """Create Guardrails AI configuration"""
    
    # Input guardrails
    input_guard = Guard().use_many(
        ToxicLanguage(threshold=0.8, validation_method="sentence"),
        PII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "SSN"]),
        Bias(threshold=0.8)
    )
    
    # Output guardrails  
    output_guard = Guard().use_many(
        ToxicLanguage(threshold=0.7, validation_method="sentence"),
        PII(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "SSN", "CREDIT_CARD"]),
        Bias(threshold=0.7)
    )
    
    # Save configurations
    with open("guardrails/input_guard.json", "w") as f:
        json.dump(input_guard.to_dict(), f, indent=2)
    
    with open("guardrails/output_guard.json", "w") as f:
        json.dump(output_guard.to_dict(), f, indent=2)
    
    return input_guard, output_guard

def create_monitoring_config():
    """Create monitoring and alerting configuration"""
    monitoring_config = {
        "metrics": {
            "blocked_requests": {
                "type": "counter",
                "description": "Number of requests blocked by guardrails"
            },
            "toxicity_score": {
                "type": "histogram",
                "description": "Distribution of toxicity scores"
            },
            "response_time": {
                "type": "histogram", 
                "description": "Guardrails processing time"
            }
        },
        "alerts": {
            "high_toxicity": {
                "condition": "toxicity_score > 0.9",
                "action": "log_and_notify",
                "webhook": "http://localhost:8080/alerts"
            },
            "pii_detected": {
                "condition": "pii_entities_found > 0",
                "action": "block_and_alert",
                "webhook": "http://localhost:8080/pii-alerts"
            }
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "file": "logs/guardrails.log"
        }
    }
    
    with open("guardrails/monitoring.yaml", "w") as f:
        yaml.dump(monitoring_config, f, default_flow_style=False)
    
    return monitoring_config

def create_guardrails_service():
    """Create FastAPI service with guardrails"""
    service_code = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import time
import logging
from guardrails import Guard

app = FastAPI(title="LLM Guardrails Service")

# Load guardrails
with open("guardrails/input_guard.json", "r") as f:
    input_guard = Guard.from_dict(json.load(f))

with open("guardrails/output_guard.json", "r") as f:
    output_guard = Guard.from_dict(json.load(f))

class TextRequest(BaseModel):
    text: str
    model: str = "default"

class GuardResponse(BaseModel):
    filtered_text: str
    blocked: bool
    violations: list
    processing_time: float

@app.post("/filter/input", response_model=GuardResponse)
async def filter_input(request: TextRequest):
    start_time = time.time()
    
    try:
        result = input_guard.validate(request.text)
        processing_time = time.time() - start_time
        
        return GuardResponse(
            filtered_text=result.validated_output or request.text,
            blocked=not result.validation_passed,
            violations=[str(e) for e in result.validation_errors],
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/filter/output", response_model=GuardResponse)
async def filter_output(request: TextRequest):
    start_time = time.time()
    
    try:
        result = output_guard.validate(request.text)
        processing_time = time.time() - start_time
        
        return GuardResponse(
            filtered_text=result.validated_output or request.text,
            blocked=not result.validation_passed,
            violations=[str(e) for e in result.validation_errors],
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "guardrails"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("guardrails/service.py", "w") as f:
        f.write(service_code)

def main():
    print("Setting up guardrails...")
    
    # Create NeMo Guardrails config
    nemo_config = create_nemo_guardrails_config()
    print("✓ NeMo Guardrails configuration created")
    
    # Create Guardrails AI config
    input_guard, output_guard = create_guardrails_ai_config()
    print("✓ Guardrails AI configuration created")
    
    # Create monitoring config
    monitoring_config = create_monitoring_config()
    print("✓ Monitoring configuration created")
    
    # Create guardrails service
    create_guardrails_service()
    print("✓ Guardrails service created")
    
    print("\nGuardrails setup complete!")
    print("Start the service with: python guardrails/service.py")

if __name__ == "__main__":
    import os
    main()
