import os
import re
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(docs_dir: str) -> list[Document]:
    documents = []
    path = Path(docs_dir)
    for file_path in path.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        risk_match = re.search(r"RISK_LEVEL:\s*(LOW|HIGH|CRITICAL)", content)
        doc_risk = risk_match.group(1) if risk_match else "UNKNOWN"
        category = file_path.stem
        
        doc = Document(
            page_content=content,
            metadata={
                "source": file_path.name,
                "risk_level": doc_risk,
                "category": category
            }
        )
        documents.append(doc)
    return documents

def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n---\n", "\n## ", "\n### ", "\n\n", "\n", " "]
    )
    chunks = splitter.split_documents(docs)
    
    for chunk in chunks:
        risk_match = re.search(r"RISK_LEVEL:\s*(LOW|HIGH|CRITICAL)", chunk.page_content)
        chunk_risk = risk_match.group(1) if risk_match else chunk.metadata.get("risk_level", "UNKNOWN")
        
        es_match = re.search(r"Escalation_Required:\s*(TRUE|FALSE)", chunk.page_content, re.IGNORECASE)
        requires_escalation = False
        if es_match and es_match.group(1).upper() == "TRUE":
            requires_escalation = True
            
        chunk.metadata["chunk_risk"] = chunk_risk
        chunk.metadata["requires_escalation"] = requires_escalation
        
    return chunks
