"""
LLM Client Wrapper for City Care Clinics.
Supports OpenRouter API (OPENROUTER_API_KEY) and OpenAI API (OPENAI_API_KEY).
Native .env loader with fallback support for python-dotenv.
"""

import os
import json
import urllib.request
from typing import Dict, Any, List, Optional

def load_env_file(env_path: str = ".env"):
    """Native parser for .env file to load OPENROUTER_API_KEY and environment variables."""
    possible_paths = [
        env_path,
        os.path.join("..", env_path),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
        r"d:\Netixsol\Week9\.env",
        r"d:\Netixsol\Week9\ai-clinic-assistant\.env"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line_strip = line.strip()
                    if line_strip and not line_strip.startswith("#") and "=" in line_strip:
                        key, val = line_strip.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'").strip('"')
                        if key not in os.environ or not os.environ[key]:
                            os.environ[key] = val

# Automatically load .env on import
load_env_file()

class LLMClient:
    def __init__(self, model_name: Optional[str] = None):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # OpenRouter Base URL & headers (guarantee /chat/completions endpoint)
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
        if not base_url.endswith("/chat/completions"):
            base_url = base_url.rstrip("/") + "/chat/completions"
        self.openrouter_url = base_url

        configured_model = model_name or os.getenv("LLM_MODEL_NAME", "openai/gpt-4o-mini")
        # Ensure fast, reliable production model
        if "free" in configured_model.lower():
            self.default_model = "openai/gpt-4o-mini"
        else:
            self.default_model = configured_model

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Sends chat completion request to OpenRouter API (or OpenAI) using OPENROUTER_API_KEY.
        """
        api_key = self.openrouter_api_key or self.openai_api_key
        
        if not api_key:
            # Fallback when no API key is configured (Local Heuristic / Sandbox Mode)
            return {
                "status": "SANDBOX_MOCK",
                "content": "API Key not provided in .env. Operating in sandbox mode.",
                "model": "sandbox-local"
            }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://citycareclinics.pk",
            "X-Title": "City Care Clinics Assistant"
        }

        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            req = urllib.request.Request(
                self.openrouter_url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data["choices"][0]["message"]["content"]
                return {
                    "status": "SUCCESS",
                    "content": choice,
                    "model": data.get("model", self.default_model),
                    "usage": data.get("usage", {})
                }
        except Exception as e:
            return {
                "status": "ERROR",
                "content": f"LLM API Error: {str(e)}",
                "model": self.default_model
            }

if __name__ == "__main__":
    client = LLMClient()
    print("OPENROUTER_API_KEY Detected:", bool(client.openrouter_api_key))
    if client.openrouter_api_key:
        print(f"API Key configured! Testing connection to OpenRouter ({client.default_model})...")
        res = client.generate_completion([{"role": "user", "content": "Hello! Confirm OpenRouter connection."}])
        print("Response Status:", res["status"])
        print("Response Content:\n", res["content"])
    else:
        print("No OPENROUTER_API_KEY detected in .env yet.")

