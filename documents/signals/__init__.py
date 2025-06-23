"""
Signals de la aplicación documents.
"""

# Importar signals para que se registren
from .handle_knowledge_changes import handle_knowledge_changes

__all__ = [
    "handle_knowledge_changes",
]
