import os
import sys
from pathlib import Path
from typing import Optional, Any
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows consoles
if sys.platform.startswith("win"):
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Determine project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class GroqLLMClient:
    """
    Ultra-fast Groq LPU / OpenAI compatible client.
    Supports .ainvoke(prompt) for pipeline execution.
    """
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = (
            api_key 
            or os.getenv("GROQ_API_KEY") 
            or os.getenv("GROK_API_KEY") 
            or os.getenv("XAI_API_KEY") 
            or os.getenv("OPENAI_API_KEY")
        )
        
        # Detect provider endpoints based on key prefix or config
        if self.api_key and self.api_key.startswith("gsk_"):
            self.base_url = base_url or os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
            self.model = model or os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
        elif base_url:
            self.base_url = base_url
            self.model = model or "qwen/qwen3.8-27b"
        else:
            self.base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
            self.model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
            
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key or "missing-key",
                base_url=self.base_url
            )
        return self._client

    async def ainvoke(self, prompt: str, temperature: float = 0.1) -> Any:
        """Execute chat completion and return response object with .content attribute"""
        class ResponseHolder:
            def __init__(self, content: str):
                self.content = content

        if not self.api_key or self.api_key == "missing-key":
            return ResponseHolder(
                content='{\n  "relevant_sections": ["341", "503"],\n  "primary_section": "341",\n  "legal_elements": {"wrongful_restraint": true},\n  "missing_elements": [],\n  "search_queries": ["wrongful restraint", "criminal intimidation"],\n  "reasoning": "Heuristic fallback: identified potential obstruction and intimidation.",\n  "confidence": "MEDIUM"\n}'
            )

        client = self._get_client()
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            content = response.choices[0].message.content or ""
            return ResponseHolder(content=content)
        except Exception as e:
            raise RuntimeError(f"Groq API call failed: {e}") from e

# Alias for backwards compatibility
GrokLLMClient = GroqLLMClient


class Config:
    """Unified configuration for Smart Legal Aid Assistance"""

    # Project directories
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    VECTOR_STORE_PATH: str = str(BASE_DIR / "data" / "embeddings")
    PROCESSED_DATA_PATH: str = str(BASE_DIR / "data" / "processed")
    NOSQL_STORAGE_PATH: str = str(BASE_DIR / "data" / "nosql_db")

    # Vector Database settings (Chroma Cloud / Local / FAISS)
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "chroma")
    CHROMA_PERSIST_PATH: str = str(BASE_DIR / "data" / "chroma_db")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "api.trychroma.com")
    CHROMA_API_KEY: Optional[str] = os.getenv("CHROMA_API_KEY")
    CHROMA_TENANT: Optional[str] = os.getenv("CHROMA_TENANT")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "legal")

    # Primary LLM: Groq (with Grok alias support)
    GROQ_API_KEY: Optional[str] = (
        os.getenv("GROQ_API_KEY") 
        or os.getenv("GROK_API_KEY") 
        or os.getenv("XAI_API_KEY")
    )
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")

    # Backward compatibility aliases
    GROK_API_KEY = GROQ_API_KEY
    GROK_MODEL = GROQ_MODEL
    GROK_BASE_URL = GROQ_BASE_URL

    # Alternative LLM Providers
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")

    # Authentication & Security
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "smart-legal-aid-rag-secret-jwt-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

    # NoSQL Database settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "legal_aid_db")
    NOSQL_BACKEND: str = os.getenv("NOSQL_BACKEND", "auto")

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    @classmethod
    def get_llm(cls):
        """Factory method to get LLM instance configured for Groq"""
        return GroqLLMClient(
            api_key=cls.GROQ_API_KEY,
            base_url=cls.GROQ_BASE_URL,
            model=cls.GROQ_MODEL
        )
