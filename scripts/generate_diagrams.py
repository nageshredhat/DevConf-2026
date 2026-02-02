#!/usr/bin/env python3
"""
Generate detailed architecture diagrams using Python
"""

def generate_sequence_diagram():
    """Generate sequence diagram for request flow"""
    sequence = '''
@startuml
title LLM Security Pipeline - Request Flow Sequence

actor User
participant "API Gateway" as Gateway
participant "Rate Limiter" as RateLimit
participant "Input Guardrails" as InputGuard
participant "Model Service" as Model
participant "Output Guardrails" as OutputGuard
participant "Monitoring" as Monitor
database "Redis Cache" as Cache
database "Model Storage" as Storage

User -> Gateway: POST /v1/chat/completions
activate Gateway

Gateway -> RateLimit: Check rate limits
activate RateLimit
RateLimit -> Cache: Get user quota
Cache --> RateLimit: Current usage
RateLimit --> Gateway: Rate limit OK
deactivate RateLimit

Gateway -> InputGuard: Filter input text
activate InputGuard
InputGuard -> InputGuard: PII detection
InputGuard -> InputGuard: Toxicity check
InputGuard -> InputGuard: Bias assessment
InputGuard --> Gateway: Filtered input
deactivate InputGuard

Gateway -> Model: Generate response
activate Model
Model -> Storage: Load model weights
Storage --> Model: Model artifacts
Model -> Model: Inference processing
Model --> Gateway: Raw response
deactivate Model

Gateway -> OutputGuard: Validate output
activate OutputGuard
OutputGuard -> OutputGuard: Content sanitization
OutputGuard -> OutputGuard: Safety validation
OutputGuard --> Gateway: Safe response
deactivate OutputGuard

Gateway -> Monitor: Log metrics
activate Monitor
Monitor -> Monitor: Record latency
Monitor -> Monitor: Update counters
deactivate Monitor

Gateway --> User: Final response
deactivate Gateway

@enduml
'''
    return sequence

def main():
    """Generate all architecture diagrams"""
    import os
    os.makedirs("diagrams", exist_ok=True)
    
    with open("diagrams/sequence_diagram.puml", "w") as f:
        f.write(generate_sequence_diagram())
    
    print("✅ Architecture diagrams generated in diagrams/ directory")

if __name__ == "__main__":
    main()
