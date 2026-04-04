from app.knowledge_base.store import VectorStore

class RAGService:
    def __init__(self):
        self.vector_store = None

    def get_store(self):
        if not self.vector_store:
            self.vector_store = VectorStore.get_instance()
        return self.vector_store

    def retrieve(self, query: str):
        store = self.get_store()
        results = store.search(query, k=4)
        
        documents = []
        max_risk_level = "UNKNOWN"
        requires_escalation = False
        relevance_scores = []
        sources = []
        
        risk_priority = {"LOW": 1, "UNKNOWN": 2, "HIGH": 3, "CRITICAL": 4}
        current_max_priority = 0
        
        for doc, score in results:
            documents.append(doc)
            relevance_scores.append(score)
            sources.append(doc.metadata.get("source", "Unknown"))
            
            chunk_risk = doc.metadata.get("chunk_risk", "UNKNOWN")
            priority = risk_priority.get(chunk_risk.upper(), 2)
            if priority > current_max_priority:
                current_max_priority = priority
                max_risk_level = chunk_risk.upper()
                
            if doc.metadata.get("requires_escalation") is True:
                requires_escalation = True

        risk_analysis = {
            "max_risk_level": max_risk_level,
            "requires_escalation": requires_escalation,
            "relevance_scores": relevance_scores,
            "sources": sources
        }
        
        return documents, risk_analysis

    def build_context(self, documents: list) -> str:
        context_parts = []
        for i, doc in enumerate(documents, 1):
            source = doc.metadata.get("source", "Unknown")
            risk = doc.metadata.get("chunk_risk", "UNKNOWN")
            content = doc.page_content.strip()
            context_parts.append(f"--- PROTOCOL #{i} (Source: {source}, Risk: {risk}) ---\n{content}\n")
        return "\n".join(context_parts)

rag = RAGService()
