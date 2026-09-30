"""
Root configuration shim for backwards compatibility.
Imports everything from src.config.
"""
from src.config import Config, GrokLLMClient, BASE_DIR

__all__ = ["Config", "GrokLLMClient", "BASE_DIR"]
