"""
Plagiarism detection algorithms for CodeGuard.

This package contains multiple complementary detection algorithms:
- TokenDetector: Lexical token-based similarity detection
- ASTDetector: Abstract syntax tree structural comparison
- HashDetector: Winnowing algorithm for fingerprinting
"""

from .token_detector import TokenDetector
from .ast_detector import ASTDetector
from .hash_detector import HashDetector

__all__ = ["TokenDetector", "ASTDetector", "HashDetector"]
