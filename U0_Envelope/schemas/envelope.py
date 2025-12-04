import time
import uuid
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

# --- ENUMS ---
class SecurityLevel(str):
    # Matches your U12 Security Tiers
    PUBLIC = "public"
    INTERNAL = "internal"
    CRITICAL = "critical"

class Region(str):
    # Matches your U10 Edge Deployment
    EU_WEST = "eu-west"
    US_EAST = "us-east"
    LOCAL = "local-yemen"

# --- THE MASTER ENVELOPE (U0) ---
class MessageEnvelope(BaseModel):
    """
    The Single Source of Truth for all data moving in Master v6.1.
    No module talks to another without wrapping data in this class.
    """
    
    # 1. Identity & Tracing (Distributed Systems)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = Field(default_factory=time.time)
    
    # 2. Vector Clock for Sync (U6 Conflict Resolution)
    # Example: {"node_1": 1, "node_2": 5}
    vector_clock: Dict[str, int] = Field(default_factory=dict)
    
    # 3. Routing & Priority (U5 Queue System)
    priority: int = Field(default=1, ge=0, le=10)  # 10 = Critical, 1 = Background
    target_region: str = Region.LOCAL
    
    # 4. The Payload (The actual AI content)
    payload: Dict[str, Any]
    
    # 5. Security & Governance (U4 & U12)
    security_level: str = SecurityLevel.INTERNAL
    hmac_signature: Optional[str] = None  # To be filled by U12 Security Module
    
    # 6. Observability Metadata (U9)
    # Tracks cost, latency, and model version used
    meta: Dict[str, Any] = Field(default_factory=dict)

    def sign_envelope(self, secret_key: str):
        """Placeholder for U12 HMAC signing logic"""
        # In real impl, this would hash the payload + timestamp
        self.hmac_signature = f"signed-{hash(self.trace_id + secret_key)}"

# --- TEST CODE (Runs if you execute this file directly) ---
if __name__ == "__main__":
    # Simulate a user query coming in
    msg = MessageEnvelope(
        priority=10, # Critical (User is waiting)
        payload={
            "action": "chat_completion",
            "model": "llama3",
            "prompt": "Explain Quantum Physics"
        },
        meta={"source": "user_frontend"}
    )
    
    print(f"✅ Envelope Created: {msg.trace_id}")
    print(f"📦 Payload: {msg.payload}")
    print(f"🕒 Timestamp: {msg.timestamp}")