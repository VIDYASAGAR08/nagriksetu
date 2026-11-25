"""
NagrikSetu AI Engine - Configuration & Environment
"""

import os

class AIConfig:
    @staticmethod
    def get_provider() -> str:
        provider = os.getenv("AI_PROVIDER", "auto").lower()
        if provider == "auto":
            if os.getenv("GEMINI_API_KEY"):
                return "gemini"
            elif os.getenv("OPENAI_API_KEY"):
                return "openai"
            else:
                return "grounded_engine"
        return provider

    @staticmethod
    def get_gemini_key() -> str:
        return os.getenv("GEMINI_API_KEY", "").strip()

    @staticmethod
    def get_gemini_model() -> str:
        return os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()

    @staticmethod
    def get_openai_key() -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    @staticmethod
    def get_openai_model() -> str:
        return os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

    @classmethod
    def get_status(cls, question_bank_count: int = 200) -> dict:
        active_provider = cls.get_provider()
        has_external_key = bool(cls.get_gemini_key() or cls.get_openai_key())
        return {
            "assistant_name": "NagrikSetu AI Assistance",
            "active_provider": active_provider,
            "external_llm_configured": has_external_key,
            "gemini_configured": bool(cls.get_gemini_key()),
            "openai_configured": bool(cls.get_openai_key()),
            "question_bank_total": question_bank_count,
            "architecture": "Hybrid Grounded Knowledge Engine + LLM Provider Abstraction",
            "rbac_enforcement": "Strict Server-Side JWT Validation",
            "configuration_guide": (
                "External AI synthesis can be activated by adding GEMINI_API_KEY=<key> or "
                "OPENAI_API_KEY=<key> to backend/.env. If omitted, the assistant seamlessly runs "
                "on the Grounded Database & Official Knowledge Engine."
            )
        }
