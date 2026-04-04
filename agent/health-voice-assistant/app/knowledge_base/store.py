from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.config import get_settings
from app.knowledge_base.loader import load_documents, split_documents
import os
import glob

class VectorStore:
    _instance = None

    def __init__(self):
        settings = get_settings()
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=settings.google_api_key
        )
        self.db = Chroma(
            collection_name="medical_protocols",
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_persist_dir
        )
        
        kb_dir = os.path.join(os.path.dirname(__file__), "documents")
        
        # Count source .md files in the knowledge base
        md_files = glob.glob(os.path.join(kb_dir, "*.md"))
        num_source_files = len(md_files)
        
        # Get unique source files already indexed in ChromaDB
        existing_count = self.db._collection.count()
        needs_reindex = False
        
        if existing_count == 0:
            needs_reindex = True
        else:
            # Check if new document files have been added by comparing source metadata
            try:
                all_metadata = self.db._collection.get()["metadatas"]
                indexed_sources = set(m.get("source", "") for m in all_metadata)
                current_sources = set(os.path.basename(f) for f in md_files)
                if not current_sources.issubset(indexed_sources):
                    needs_reindex = True
                    print(f"[VectorStore] New documents detected! Re-indexing knowledge base...")
                    print(f"  New files: {current_sources - indexed_sources}")
            except Exception:
                needs_reindex = True
        
        if needs_reindex:
            # Clear existing data and re-index
            if existing_count > 0:
                self.db._collection.delete(where={"source": {"$ne": ""}})
                # Recreate the collection
                self.db = Chroma(
                    collection_name="medical_protocols",
                    embedding_function=self.embeddings,
                    persist_directory=settings.chroma_persist_dir
                )
            
            docs = load_documents(kb_dir)
            chunks = split_documents(docs)
            if chunks:
                print(f"[VectorStore] Indexing {len(chunks)} chunks from {num_source_files} documents...")
                self.db.add_documents(chunks)
                print(f"[VectorStore] Knowledge base indexed successfully!")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def search(self, query: str, k: int = 4):
        return self.db.similarity_search_with_relevance_scores(query, k=k)
