import time

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def get_or_create(self, caller_id: str) -> dict:
        now = time.time()
        self._cleanup(now)
        
        if caller_id not in self.sessions:
            self.sessions[caller_id] = {
                "caller_id": caller_id,
                "created_at": now,
                "last_active": now,
                "conversation_history": [],
                "escalated": False,
                "preferred_language": "en",
            }
        else:
            self.sessions[caller_id]["last_active"] = now
            
        return self.sessions[caller_id]

    def add_message(self, caller_id: str, role: str, content: str):
        if caller_id in self.sessions:
            self.sessions[caller_id]["conversation_history"].append({"role": role, "content": content})
            self.sessions[caller_id]["last_active"] = time.time()

    def get_history(self, caller_id: str) -> list:
        if caller_id in self.sessions:
            return self.sessions[caller_id]["conversation_history"]
        return []

    def mark_escalated(self, caller_id: str):
        if caller_id in self.sessions:
            self.sessions[caller_id]["escalated"] = True

    def set_language(self, caller_id: str, language: str):
        if caller_id in self.sessions and language:
            self.sessions[caller_id]["preferred_language"] = language
            self.sessions[caller_id]["last_active"] = time.time()

    def get_language(self, caller_id: str) -> str:
        if caller_id in self.sessions:
            return self.sessions[caller_id].get("preferred_language", "en")
        return "en"
            
    def _cleanup(self, now: float):
        expired = [cid for cid, sess in self.sessions.items() if now - sess["last_active"] > 1800]
        for cid in expired:
            del self.sessions[cid]

session_mgr = SessionManager()
