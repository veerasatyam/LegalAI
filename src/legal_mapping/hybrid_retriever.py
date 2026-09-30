from typing import List, Dict, Any, Tuple, Optional
import asyncio
from pathlib import Path

from src.models.legal_schemas import Scenario, IPCSection
from src.legal_mapping.llm_analyzer import LLMLegalAnalyzer, LegalAnalysis
from src.config import Config

class HybridRetriever:
    """
    Combines Grok LLM analysis with Vector Database search (ChromaDB / FAISS)
    """
    
    def __init__(self, vector_store_path: Optional[str] = None):
        self.vector_db_type = Config.VECTOR_DB_TYPE.lower()
        
        if self.vector_db_type == "chroma":
            try:
                from src.embeddings.chroma_store import IPCChromaStore
                print(f"[INFO] Using ChromaDB vector database from {Config.CHROMA_PERSIST_PATH}")
                self.vector_store = IPCChromaStore(Config.CHROMA_PERSIST_PATH)
            except Exception as e:
                print(f"[WARN] ChromaDB initialization failed: {e}. Falling back to FAISS.")
                self.vector_db_type = "faiss"
                from src.embeddings.vector_store import IPCVectorStore
                self.vector_store = IPCVectorStore()
                self.vector_store.load(vector_store_path or Config.VECTOR_STORE_PATH)
        else:
            from src.embeddings.vector_store import IPCVectorStore
            print(f"[INFO] Using FAISS vector database from {Config.VECTOR_STORE_PATH}")
            self.vector_store = IPCVectorStore()
            self.vector_store.load(vector_store_path or Config.VECTOR_STORE_PATH)
            
        self.llm_analyzer = LLMLegalAnalyzer()
        
    async def retrieve(self, scenario: Scenario, raw_input: str) -> Tuple[List[IPCSection], LegalAnalysis]:
        """
        Two-stage retrieval:
        1. Grok LLM identifies potential sections and generates search queries
        2. Vector search (ChromaDB / FAISS) retrieves relevant sections
        3. Combine, validate, and deduplicate results
        """
        
        # Stage 1: LLM Analysis
        print("[INFO] LLM analyzing scenario...")
        analysis = await self.llm_analyzer.analyze(scenario, raw_input)
        
        print(f"   [INFO] Identified sections: {analysis.relevant_sections}")
        print(f"   [INFO] Confidence: {analysis.confidence}")
        
        # Stage 2: Vector search with LLM-generated queries
        all_candidates = []
        
        # Search using each LLM-generated query
        for query in analysis.search_queries:
            candidates = self._vector_search(query, k=5)
            all_candidates.extend(candidates)
        
        # Also search with original text
        original_candidates = self._vector_search(raw_input, k=5)
        all_candidates.extend(original_candidates)
        
        # Also explicitly search for LLM-identified sections directly by section number
        for section_num in analysis.relevant_sections:
            section = self._get_section_by_number(section_num)
            if section:
                all_candidates.append(section)
        
        # Deduplicate by section number
        seen = set()
        unique_candidates = []
        for section in all_candidates:
            if section.section_number not in seen:
                seen.add(section.section_number)
                unique_candidates.append(section)
        
        print(f"   [INFO] Retrieved {len(unique_candidates)} unique candidate sections using {self.vector_db_type}")
        return unique_candidates, analysis
    
    def _vector_search(self, query: str, k: int) -> List[IPCSection]:
        """Vector search in ChromaDB or FAISS"""
        if hasattr(self.vector_store, "search"):
            # ChromaDB
            return self.vector_store.search(query, k=k)
            
        # FAISS
        query_embedding = self.vector_store.model.encode([query])
        distances, indices = self.vector_store.index.search(
            query_embedding.astype('float32'), k
        )
        
        sections = []
        for idx in indices[0]:
            if idx < 0 or idx >= len(self.vector_store.sections):
                continue
            section_data = self.vector_store.sections[idx]
            section = IPCSection(
                section_number=str(section_data['section_number']),
                title=section_data['title'],
                full_text=section_data.get('full_text', ''),
                main_text=section_data.get('main_text', ''),
                illustrations=section_data.get('illustrations', '')
            )
            sections.append(section)
        return sections
    
    def _get_section_by_number(self, section_num: str) -> Optional[IPCSection]:
        """Find specific section by number"""
        if hasattr(self.vector_store, "get_by_section_number"):
            return self.vector_store.get_by_section_number(section_num)
            
        target = str(section_num).strip().upper()
        for section_data in self.vector_store.sections:
            if str(section_data['section_number']).strip().upper() == target:
                return IPCSection(
                    section_number=str(section_data['section_number']),
                    title=section_data['title'],
                    full_text=section_data.get('full_text', ''),
                    main_text=section_data.get('main_text', ''),
                    illustrations=section_data.get('illustrations', '')
                )
        return None