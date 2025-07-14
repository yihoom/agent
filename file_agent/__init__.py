"""
File Agent - A file management agent with AI capabilities.
"""

from .agent import FileAgent
from .config import Config
from .file_manager import FileManager
from .ai_providers import AIProviderFactory

__version__ = "0.1.0"
__author__ = "Your Name"

__all__ = [
    "FileAgent",
    "Config", 
    "FileManager",
    "AIProviderFactory",
]
