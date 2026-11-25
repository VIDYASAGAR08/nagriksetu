"""
NagrikSetu AI Engine - Multi-turn Conversation Memory
Maintains conversational context, entity tracking, and topic continuity across multi-turn exchanges.
"""

import time
from typing import Dict, Any, List, Optional

class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
        self.context_entities: Dict[str, Any] = {
            "last_district": None,
            "last_school_ids": [],
            "last_school_name": None,
            "last_student_id": None,
            "last_standard": None,
            "last_topic": None,
            "last_intent": None
        }
        self.last_active = time.time()

    def update_context(self, entities: Dict[str, Any], topic: Optional[str] = None):
        if entities.get("district"):
            self.context_entities["last_district"] = entities["district"]
        if entities.get("institution_ids"):
            self.context_entities["last_school_ids"] = entities["institution_ids"]
        if entities.get("institution_name"):
            self.context_entities["last_school_name"] = entities["institution_name"]
        if entities.get("student_id"):
            self.context_entities["last_student_id"] = entities["student_id"]
        if entities.get("standard"):
            self.context_entities["last_standard"] = entities["standard"]
        if topic:
            self.context_entities["last_topic"] = topic
        self.last_active = time.time()

    def add_turn(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        if len(self.history) > 20:
            self.history = self.history[-20:]
        self.last_active = time.time()


class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}

    def get_or_create(self, session_id: Optional[str]) -> ConversationSession:
        now = time.time()
        # Clean up stale sessions older than 2 hours
        stale = [sid for sid, s in self.sessions.items() if now - s.last_active > 7200]
        for sid in stale:
            del self.sessions[sid]

        if not session_id or session_id not in self.sessions:
            import uuid
            sid = session_id or str(uuid.uuid4())
            self.sessions[sid] = ConversationSession(sid)
            return self.sessions[sid]

        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

conversation_manager = ConversationManager()
