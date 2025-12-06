import requests
import json
import time
import sys
import os

# Add the project root to python path so we can import U0
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from U0_Envelope.schemas.envelope import MessageEnvelope

class StreamingEngine:
    def __init__(self, model_name="llama3"):
        # HARDCODED FIX: Point directly to Docker Bridge IP
        base_host = "http://172.17.0.1:11434"
        self.base_url = f"{base_host}/api/generate"
        self.model = model_name
    def generate(self, envelope: MessageEnvelope):
        """
        Receives a U0 Envelope, validates it, and streams the AI response.
        """
        # 1. Extract Prompt from Envelope
        prompt = envelope.payload.get("prompt")
        if not prompt:
            yield "Error: No prompt found in payload"
            return

        # 2. Prepare Request for Ollama
        # We disable 'stream' here for simplicity in v1, 
        # but normally set stream=True for real-time tokens.
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True  
        }

        print(f"🔄 [U1] Processing Trace ID: {envelope.trace_id}")

        try:
            # 3. Call Ollama (The AI Brain)
            with requests.post(self.base_url, json=payload, stream=True) as response:
                response.raise_for_status()
                
                # 4. Stream tokens back
                for line in response.iter_lines():
                    if line:
                        body = json.loads(line)
                        token = body.get("response", "")
                        
                        # Stop if done
                        if body.get("done"):
                            break
                            
                        # Yield token to the caller
                        yield token
                        
        except requests.exceptions.ConnectionError:
            yield "\n[!] Critical Error: Ollama is not running. Run 'ollama serve' in terminal."

# --- TEST CODE (Runs if executed directly) ---
if __name__ == "__main__":
    # Create a dummy envelope
    test_msg = MessageEnvelope(
        payload={"prompt": "Write a haiku about Linux."},
        priority=10
    )
    
    engine = StreamingEngine(model_name="llama3")
    
    print("🤖 AI is thinking...")
    full_response = ""
    
    # Run the stream
    for token in engine.generate(test_msg):
        print(token, end="", flush=True)
        full_response += token
        
    print("\n\n✅ Stream Complete.")