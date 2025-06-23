"""
Signals de la aplicación knowledge.
"""

# Importar signals para que se registren
from .handle_document_changes import handle_document_changes

__all__ = [
    "handle_document_changes",
]
