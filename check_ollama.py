#!/usr/bin/env python
"""
Quick test to verify Ollama is running and llama3.1 is available
"""
import requests
import sys

print("Checking Ollama service...")
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=3)
    if response.status_code == 200:
        models = response.json()
        print("✓ Ollama is running!")
        print(f"Available models: {models}")
        
        # Check for llama3.1
        model_names = [m.get('name', '') for m in models.get('models', [])]
        if any('llama3.1' in name for name in model_names):
            print("✓ llama3.1 is available")
            sys.exit(0)
        else:
            print("✗ llama3.1 not found. Run: ollama run llama3.1")
            sys.exit(1)
    else:
        print(f"✗ Ollama returned status {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to Ollama on localhost:11434")
    print("  Start Ollama with: ollama serve")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
