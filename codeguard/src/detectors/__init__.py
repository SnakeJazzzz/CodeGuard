"""
Plagiarism detection algorithms for CodeGuard.

This package contains multiple complementary detection algorithms:
- TokenDetector: Lexical token-based similarity detection
- ASTDetector: Abstract syntax tree structural comparison (to be implemented)
- HashDetector: Winnowing algorithm for fingerprinting (to be implemented)
"""

from .token_detector import TokenDetector

__all__ = ['TokenDetector']
