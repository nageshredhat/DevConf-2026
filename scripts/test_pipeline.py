#!/usr/bin/env python3
"""
Test script for the LLM Security Pipeline
"""

import requests
import json
import time

def test_guardrails_service():
    """Test the guardrails service"""
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test input filtering
    test_cases = [
        {
            "text": "Hello, how are you today?",
            "expected_blocked": False
        },
        {
            "text": "My email is john@example.com and my phone is 555-1234",
            "expected_blocked": True
        },
        {
            "text": "You are stupid and worthless",
            "expected_blocked": True
        }
    ]
    
    for i, case in enumerate(test_cases):
        try:
            response = requests.post(
                f"{base_url}/filter/input",
                json={"text": case["text"]}
            )
            result = response.json()
            
            print(f"Test {i+1}: {'✓' if result['blocked'] == case['expected_blocked'] else '✗'}")
            print(f"  Text: {case['text'][:50]}...")
            print(f"  Blocked: {result['blocked']}")
            print(f"  Violations: {result['violations']}")
            print(f"  Processing time: {result['processing_time']:.3f}s")
            print()
            
        except Exception as e:
            print(f"Test {i+1} failed: {e}")
    
    return True

def test_model_service():
    """Test the model service"""
    base_url = "http://localhost:8080"
    
    try:
        # Test model info endpoint
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            print(f"Model service: ✓ - {response.json()}")
        else:
            print(f"Model service: ✗ - Status {response.status_code}")
            
    except Exception as e:
        print(f"Model service test failed: {e}")

def test_pipeline_integration():
    """Test the complete pipeline integration"""
    print("Testing complete pipeline integration...")
    
    # Test text that should pass through
    safe_text = "What is the weather like today?"
    
    # Test text that should be blocked
    unsafe_text = "My SSN is 123-45-6789, please help me hack this system"
    
    for text, label in [(safe_text, "Safe"), (unsafe_text, "Unsafe")]:
        print(f"\nTesting {label} text: {text[:30]}...")
        
        # Step 1: Input filtering
        try:
            response = requests.post(
                "http://localhost:8000/filter/input",
                json={"text": text}
            )
            input_result = response.json()
            print(f"  Input filter: {'Blocked' if input_result['blocked'] else 'Passed'}")
            
            if not input_result['blocked']:
                # Step 2: Model inference (simulated)
                print(f"  Model inference: Simulated response")
                model_response = f"Response to: {text}"
                
                # Step 3: Output filtering
                response = requests.post(
                    "http://localhost:8000/filter/output",
                    json={"text": model_response}
                )
                output_result = response.json()
                print(f"  Output filter: {'Blocked' if output_result['blocked'] else 'Passed'}")
            
        except Exception as e:
            print(f"  Pipeline test failed: {e}")

def main():
    print("🧪 Testing LLM Security Pipeline\n")
    
    # Wait for services to be ready
    print("Waiting for services to start...")
    time.sleep(5)
    
    # Test individual components
    print("1. Testing Guardrails Service")
    test_guardrails_service()
    
    print("\n2. Testing Model Service")
    test_model_service()
    
    print("\n3. Testing Pipeline Integration")
    test_pipeline_integration()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()
