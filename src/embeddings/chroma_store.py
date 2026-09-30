import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer

from src.config import Config, BASE_DIR
from src.models.legal_schemas import IPCSection

class IPCChromaStore:
    """
    ChromaDB Vector Store for IPC Sections.
    Supports both Chroma Cloud and local persistent storage.
    """
    def __init__(self, persist_directory: Optional[str] = None):
        self.persist_dir = Path(persist_directory or Config.CHROMA_PERSIST_PATH)
        
        # Initialize SentenceTransformer embedding model for queries
        try:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Check if Chroma Cloud credentials are provided
        if Config.CHROMA_API_KEY and Config.CHROMA_TENANT:
            print(f"[INFO] Connecting to Chroma Cloud (tenant: {Config.CHROMA_TENANT[:8]}..., database: {Config.CHROMA_DATABASE})...")
            try:
                self.client = chromadb.CloudClient(
                    tenant=Config.CHROMA_TENANT,
                    database=Config.CHROMA_DATABASE,
                    api_key=Config.CHROMA_API_KEY
                )
                self.is_cloud = True
                print("[OK] Connected to Chroma Cloud!")
            except Exception as e:
                print(f"[WARN] CloudClient failed ({e}). Trying HttpClient...")
                self.client = chromadb.HttpClient(
                    host=Config.CHROMA_HOST,
                    ssl=True,
                    headers={"x-chroma-token": Config.CHROMA_API_KEY},
                    tenant=Config.CHROMA_TENANT,
                    database=Config.CHROMA_DATABASE
                )
                self.is_cloud = True
        else:
            self.persist_dir.mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=str(self.persist_dir))
            self.is_cloud = False
            print(f"[OK] Connected to local ChromaDB at {self.persist_dir}")
            
        self.collection = self.client.get_or_create_collection(
            name="ipc_sections",
            metadata={"description": "Indian Penal Code, 1860 - Bare Act"}
        )
        
        count = self.collection.count()
        print(f"[OK] ChromaDB collection 'ipc_sections' ready with {count} sections.")
        
        if count == 0 and not self.is_cloud:
            print("[INFO] Local collection empty, building from JSON...")
            self.build_index()

    def build_index(self, json_path: Optional[str] = None):
        """Populate collection from JSON if empty"""
        path = Path(json_path or (Config.PROCESSED_DATA_PATH + "/ipc_sections.json"))
        if not path.is_absolute():
            path = BASE_DIR / path
            
        if not path.exists():
            return
            
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        sections = data.get("sections", [])
        if not sections:
            return
            
        ids = []
        docs = []
        metas = []
        
        for i, sec in enumerate(sections):
            sec_num = str(sec.get("section_number", "")).strip()
            title = sec.get("title", "")
            main_text = sec.get("main_text", "")
            full_text = sec.get("full_text", f"{title}—{main_text}")
            
            ids.append(f"ipc_{sec_num}_{i}")
            docs.append(f"Section {sec_num}: {title}. {main_text}")
            metas.append({
                "section_number": sec_num,
                "title": title[:500],
                "main_text": main_text[:1500],
                "full_text": full_text[:3000]
            })
            
        batch_size = 100
        for j in range(0, len(ids), batch_size):
            end = j + batch_size
            self.collection.upsert(
                ids=ids[j:end],
                documents=docs[j:end],
                metadatas=metas[j:end]
            )

    def search(self, query: str, k: int = 5) -> List[IPCSection]:
        """Perform semantic search using query embeddings in ChromaDB"""
        total = self.collection.count()
        if total == 0:
            return []
            
        n_results = min(k, total)
        query_emb = self.embedding_model.encode([query]).tolist()
        
        results = self.collection.query(
            query_embeddings=query_emb,
            n_results=n_results
        )
        
        sections: List[IPCSection] = []
        if results and "metadatas" in results and results["metadatas"]:
            matched_metas = results["metadatas"][0]
            for meta in matched_metas:
                sec = IPCSection(
                    section_number=str(meta.get("section_number", "")),
                    title=meta.get("title", ""),
                    full_text=meta.get("full_text", ""),
                    main_text=meta.get("main_text", ""),
                    illustrations=meta.get("illustrations", "") or ""
                )
                sections.append(sec)
                
        return sections

    def get_by_section_number(self, section_num: str) -> Optional[IPCSection]:
        """Retrieve specific section by section number"""
        target = str(section_num).strip().upper()
        results = self.collection.get(
            where={"section_number": target},
            limit=1
        )
        if results and results.get("metadatas"):
            meta = results["metadatas"][0]
            return IPCSection(
                section_number=str(meta.get("section_number", "")),
                title=meta.get("title", ""),
                full_text=meta.get("full_text", ""),
                main_text=meta.get("main_text", ""),
                illustrations=meta.get("illustrations", "") or ""
            )
        return None
