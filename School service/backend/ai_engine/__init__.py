"""
NagrikSetu AI Engine Package
Universal School Service AI Assistant with Grounded RAG, Question-Bank Integration,
and Role-Based Data Isolation.
"""

from .orchestrator import assistant_orchestrator, UniversalAIAssistant
from .config import AIConfig
from .conversation import conversation_manager
from .question_matcher import QuestionMatcher
from .knowledge_base import search_official_knowledge

__all__ = [
    "assistant_orchestrator",
    "UniversalAIAssistant",
    "AIConfig",
    "conversation_manager",
    "QuestionMatcher",
    "search_official_knowledge"
]
