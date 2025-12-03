"""
Core module for CodeGuard.

This module contains core system components including configuration presets
for the voting system.
"""

from src.core.config_presets import (
    STANDARD_PRESET,
    SIMPLE_PRESET,
    PRESET_STANDARD,
    PRESET_SIMPLE,
    get_preset,
    get_preset_config,
    get_available_presets,
    apply_preset_to_voting_system,
    validate_preset,
    get_preset_summary,
)

__all__ = [
    "STANDARD_PRESET",
    "SIMPLE_PRESET",
    "PRESET_STANDARD",
    "PRESET_SIMPLE",
    "get_preset",
    "get_preset_config",
    "get_available_presets",
    "apply_preset_to_voting_system",
    "validate_preset",
    "get_preset_summary",
]
