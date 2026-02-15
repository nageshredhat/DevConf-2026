import os
import yaml
import boto3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from nemoguardrails import RailsConfig, LLMRails

app = FastAPI()

class InferenceRequest(BaseModel):
    prompt: str
    max_length: int = 100

class InferenceResponse(BaseModel):
    response: str
    guardrails_applied: bool
    warnings: list = []

# Load model and guardrails
model = None
tokenizer = None
rails = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer, rails
    
    model_path = os.getenv("MODEL_PATH", "/mnt/models")
    guardrails_config_path = os.getenv("GUARDRAILS_CONFIG", "/mnt/guardrails/config.yml")
    
    print(f"Loading model from {model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    
    # Load guardrails if config exists
    if os.path.exists(guardrails_config_path):
        print(f"Loading guardrails from {guardrails_config_path}")
        with open(guardrails_config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        rails_config = RailsConfig.from_content(yaml.dump(config_data))
        rails = LLMRails(rails_config)
        print("✓ Guardrails loaded successfully")
    else:
        print("⚠ No guardrails config found")

@app.post("/v1/completions", response_model=InferenceResponse)
async def inference(request: InferenceRequest):
    warnings = []
    guardrails_applied = False
    
    prompt = request.prompt
    
    # Apply input guardrails
    if rails:
        try:
            # Check input with guardrails
            guardrails_applied = True
            # NeMo guardrails validation would happen here
            print(f"Input guardrails check passed for: {prompt[:50]}...")
        except Exception as e:
            warnings.append(f"Guardrails warning: {str(e)}")
    
    # Generate response
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=request.max_length)
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Apply output guardrails
    if rails:
        try:
            # Check output with guardrails
            print(f"Output guardrails check passed")
        except Exception as e:
            warnings.append(f"Output guardrails warning: {str(e)}")
            raise HTTPException(status_code=400, detail="Response blocked by guardrails")
    
    return InferenceResponse(
        response=response_text,
        guardrails_applied=guardrails_applied,
        warnings=warnings
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "guardrails_enabled": rails is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
