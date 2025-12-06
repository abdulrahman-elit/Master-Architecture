from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import sys
import os
import json

# Add Project Root to Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# --- UPDATED IMPORTS (Using Underscores) ---
from U0_Envelope.schemas.envelope import MessageEnvelope
from U1_Streaming_Engine.src.engine import StreamingEngine
from U8_Local_VSS.data.vector_store import MemorySystem

app = FastAPI()

# Initialize Modules
print("🔌 Loading Memory System...")
memory = MemorySystem()
print("🔌 Loading AI Engine...")
engine = StreamingEngine(model_name="llama3")

class UserRequest(BaseModel):
    prompt: str
    trace_id: str = "mobile-123"

@app.post("/v1/chat")
async def chat_endpoint(request: UserRequest):
    print(f"📞 API Received: {request.prompt}")

    # 1. Search Memory
    context = memory.search_memory(request.prompt)
    print(f"🧠 Context Found: {context}")

    # 2. Build Prompt
    full_prompt = f"""
    Context: {context}
    
    User Question: {request.prompt}
    """

    # 3. Create Envelope
    envelope = MessageEnvelope(
        trace_id=request.trace_id,
        payload={"prompt": full_prompt},
        priority=10
    )

    # 4. Stream Response
    return StreamingResponse(
        engine.generate(envelope), 
        media_type="text/event-stream"
    )

@app.get("/health")
def health_check():
    return {"status": "active", "model": "llama3"}