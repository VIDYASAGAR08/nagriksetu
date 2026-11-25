"""
NagrikSetu AI Engine - Provider Abstraction Layer
Supports Google Gemini, OpenAI, and Grounded Knowledge Engine.
Never exposes API keys to frontend or hardcodes secrets.
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from .config import AIConfig

logger = logging.getLogger("nagriksetu_ai_engine")

class BaseAIProvider(ABC):
    @abstractmethod
    def generate(
        self,
        user_prompt: str,
        system_context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def generate(
        self,
        user_prompt: str,
        system_context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        contents = []
        if history:
            for turn in history[-6:]:
                role = "user" if turn["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": turn["content"]}]})
        
        contents.append({"role": "user", "parts": [{"text": f"SYSTEM KNOWLEDGE & DATABASE EVIDENCE:\n{system_context}\n\nUSER QUESTION: {user_prompt}"}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.8,
                "maxOutputTokens": 1024
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            
        return ""

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "Google Gemini",
            "model": self.model_name,
            "status": "active"
        }


class OpenAIProvider(BaseAIProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model_name = model_name

    def generate(
        self,
        user_prompt: str,
        system_context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        messages = [{"role": "system", "content": system_context}]
        if history:
            for turn in history[-6:]:
                messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": user_prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1024
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")

        return ""

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "OpenAI",
            "model": self.model_name,
            "status": "active"
        }


class GroundedEngineProvider(BaseAIProvider):
    """
    Deterministic Grounded Knowledge Engine.
    Ensures 100% facts without hallucinations, working out-of-the-box
    even if external LLM API keys are not supplied.
    """
    def generate(
        self,
        user_prompt: str,
        system_context: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        # Directly synthesized in the orchestrator
        return system_context

    def get_info(self) -> Dict[str, Any]:
        return {
            "provider": "Grounded Knowledge & Database Engine",
            "model": "NagrikSetu-Grounded-v2",
            "status": "active"
        }


def get_ai_provider() -> BaseAIProvider:
    provider_type = AIConfig.get_provider()
    
    if provider_type == "gemini":
        key = AIConfig.get_gemini_key()
        if key:
            return GeminiProvider(key, AIConfig.get_gemini_model())
    elif provider_type == "openai":
        key = AIConfig.get_openai_key()
        if key:
            return OpenAIProvider(key, AIConfig.get_openai_model())
            
    return GroundedEngineProvider()
