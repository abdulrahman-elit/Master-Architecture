import chromadb
import requests
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class MemorySystem:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./U8_Local_VSS/data/chroma_db")
        self.collection = self.client.get_or_create_collection(name="ai_memories")
        self.embed_model = "nomic-embed-text"

    def get_embedding(self, text):
        # HARDCODED DOCKER IP
        base_host = "http://172.17.0.1:11434"
        url = f"{base_host}/api/embeddings"
        
        try:
            response = requests.post(url, json={
                "model": self.embed_model,
                "prompt": text
            })
            return response.json()["embedding"]
        except Exception as e:
            print(f"❌ Error talking to Ollama at {url}: {e}")
            return []

    def add_memory(self, text_id, text_content):
        print(f"💾 Memorizing: {text_content}...")
        vector = self.get_embedding(text_content)
        if vector:
            self.collection.add(ids=[text_id], embeddings=[vector], documents=[text_content])

    def search_memory(self, query_text, n_results=1):
        print(f"🔍 Searching memory for: {query_text}")
        vector = self.get_embedding(query_text)
        if not vector: return "Error: Could not talk to Ollama."
        results = self.collection.query(query_embeddings=[vector], n_results=n_results)
        if results["documents"] and results["documents"][0]:
            return results["documents"][0][0]
        return "No relevant memory found."

if __name__ == "__main__":
    memory = MemorySystem()
    print("Memory System Loaded")
