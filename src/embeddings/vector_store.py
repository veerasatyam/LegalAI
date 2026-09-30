import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from pathlib import Path
import pickle
import sys
from typing import Optional
from src.config import Config, BASE_DIR

class IPCVectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize with a sentence transformer model.
        'all-MiniLM-L6-v2' is lightweight and good for prototyping.
        """
        try:
            self.model = SentenceTransformer(model_name, local_files_only=True)
        except Exception:
            self.model = SentenceTransformer(model_name)
        self.index = None
        self.sections = []
        self.embeddings = None
        
    def load_sections(self, json_path: str):
        """Load structured IPC sections from JSON"""
        path = Path(json_path)
        if not path.is_absolute():
            path = BASE_DIR / path
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.sections = data['sections']
        print(f"[OK] Loaded {len(self.sections)} sections")
        return self.sections
    
    def create_embeddings(self, batch_size=32):
        """
        Create embeddings for each section.
        We'll combine title + main text for better context.
        """
        texts = []
        for section in self.sections:
            combined = f"{section['title']} {section['main_text']}"
            texts.append(combined)
        
        print(f"[INFO] Creating embeddings for {len(texts)} sections...")
        self.embeddings = self.model.encode(
            texts, 
            batch_size=batch_size, 
            show_progress_bar=True
        )
        return self.embeddings
    
    def build_faiss_index(self):
        """Build FAISS index for fast similarity search"""
        if self.embeddings is None:
            raise ValueError("Create embeddings first!")
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)  # L2 distance
        self.index.add(self.embeddings.astype('float32'))
        print(f"[OK] FAISS index built with {self.index.ntotal} vectors")
        return self.index
    
    def save(self, output_dir: str):
        """Save vector store and metadata"""
        output_path = Path(output_dir)
        if not output_path.is_absolute():
            output_path = BASE_DIR / output_path
            
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, str(output_path / 'ipc_index.faiss'))
        
        # Save sections metadata
        with open(output_path / 'sections.pkl', 'wb') as f:
            pickle.dump(self.sections, f)
        
        # Save embeddings
        np.save(output_path / 'embeddings.npy', self.embeddings)
        print(f"[OK] Vector store saved to {output_path}")
    
    def load(self, input_dir: Optional[str] = None):
        """Load saved vector store"""
        if input_dir is None:
            input_path = Path(Config.VECTOR_STORE_PATH)
        else:
            input_path = Path(input_dir)
            if not input_path.is_absolute():
                input_path = BASE_DIR / input_path
        
        index_file = input_path / 'ipc_index.faiss'
        sections_file = input_path / 'sections.pkl'
        embeddings_file = input_path / 'embeddings.npy'
        
        if not index_file.exists():
            raise FileNotFoundError(f"FAISS index file not found at {index_file}")
            
        self.index = faiss.read_index(str(index_file))
        
        with open(sections_file, 'rb') as f:
            self.sections = pickle.load(f)
        
        if embeddings_file.exists():
            self.embeddings = np.load(embeddings_file)
            
        print(f"[OK] Vector store loaded ({self.index.ntotal} vectors) from {input_path}")
        return self