"""
Comprehensive unit tests for ThresholdManager class.

This test suite achieves 100% code coverage for src/voting/thresholds.py
by testing all methods, branches, edge cases, and error conditions.

Test Categories:
- Initialization (default and from file)
- Getter/Setter methods for thresholds, weights, and confidence weights
- File I/O operations (load/save JSON)
- Configuration validation
- Error handling and edge cases
- String representation methods
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.voting.thresholds import ThresholdManager


class TestInitialization:
    """Test ThresholdManager initialization."""

    def test_default_initialization(self):
        """Test initialization with default configuration."""
        manager = ThresholdManager()

        # Verify default thresholds
        assert manager.get_threshold("token") == 0.70
        assert manager.get_threshold("ast") == 0.80
        assert manager.get_threshold("hash") == 0.60

        # Verify default weights
        assert manager.get_weight("token") == 1.0
        assert manager.get_weight("ast") == 2.0
        assert manager.get_weight("hash") == 1.5

        # Verify default confidence weights
        assert manager.get_confidence_weight("token") == 0.3
        assert manager.get_confidence_weight("ast") == 0.4
        assert manager.get_confidence_weight("hash") == 0.3

        # Verify default decision threshold
        assert manager.get_decision_threshold() == 0.50

    def test_initialization_from_valid_file(self, tmp_path):
        """Test initialization from valid JSON configuration file."""
        config_file = tmp_path / "test_config.json"
        config_data = {
            "thresholds": {"token": 0.75, "ast": 0.85, "hash": 0.65},
            "weights": {"token": 1.5, "ast": 2.5, "hash": 2.0},
            "confidence_weights": {"token": 0.25, "ast": 0.5, "hash": 0.25},
            "decision_threshold": 0.60,
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager(config_path=str(config_file))

        # Verify loaded values
        assert manager.get_threshold("token") == 0.75
        assert manager.get_threshold("ast") == 0.85
        assert manager.get_weight("token") == 1.5
        assert manager.get_decision_threshold() == 0.60

    def test_initialization_nonexistent_file(self):
        """Test that nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            ThresholdManager(config_path="/nonexistent/path/config.json")

    def test_initialization_invalid_json(self, tmp_path):
        """Test that invalid JSON raises JSONDecodeError."""
        config_file = tmp_path / "invalid.json"
        with open(config_file, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            ThresholdManager(config_path=str(config_file))


class TestGetThreshold:
    """Test get_threshold method."""

    def test_get_threshold_token(self):
        """Test getting token threshold."""
        manager = ThresholdManager()
        assert manager.get_threshold("token") == 0.70

    def test_get_threshold_ast(self):
        """Test getting AST threshold."""
        manager = ThresholdManager()
        assert manager.get_threshold("ast") == 0.80

    def test_get_threshold_hash(self):
        """Test getting hash threshold."""
        manager = ThresholdManager()
        assert manager.get_threshold("hash") == 0.60

    def test_get_threshold_case_insensitive(self):
        """Test that detector name is case-insensitive."""
        manager = ThresholdManager()
        assert manager.get_threshold("TOKEN") == 0.70
        assert manager.get_threshold("AsT") == 0.80
        assert manager.get_threshold("HASH") == 0.60

    def test_get_threshold_invalid_detector(self):
        """Test that invalid detector name raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="Invalid detector name"):
            manager.get_threshold("invalid")


class TestSetThreshold:
    """Test set_threshold method."""

    def test_set_threshold_valid(self):
        """Test setting valid threshold."""
        manager = ThresholdManager()

        manager.set_threshold("token", 0.75)
        assert manager.get_threshold("token") == 0.75

        manager.set_threshold("ast", 0.85)
        assert manager.get_threshold("ast") == 0.85

    def test_set_threshold_at_boundaries(self):
        """Test setting threshold at valid boundaries."""
        manager = ThresholdManager()

        # Lower boundary
        manager.set_threshold("token", 0.0)
        assert manager.get_threshold("token") == 0.0

        # Upper boundary
        manager.set_threshold("token", 1.0)
        assert manager.get_threshold("token") == 1.0

    def test_set_threshold_below_range(self):
        """Test that threshold < 0.0 raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be in range"):
            manager.set_threshold("token", -0.1)

    def test_set_threshold_above_range(self):
        """Test that threshold > 1.0 raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be in range"):
            manager.set_threshold("token", 1.5)

    def test_set_threshold_invalid_detector(self):
        """Test that invalid detector name raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="Invalid detector name"):
            manager.set_threshold("invalid", 0.75)

    def test_set_threshold_non_numeric(self):
        """Test that non-numeric value raises TypeError."""
        manager = ThresholdManager()

        with pytest.raises(TypeError, match="must be numeric"):
            manager.set_threshold("token", "invalid")

    def test_set_threshold_case_insensitive(self):
        """Test that detector name is case-insensitive."""
        manager = ThresholdManager()

        manager.set_threshold("TOKEN", 0.75)
        assert manager.get_threshold("token") == 0.75


class TestGetWeight:
    """Test get_weight method."""

    def test_get_weight_token(self):
        """Test getting token weight."""
        manager = ThresholdManager()
        assert manager.get_weight("token") == 1.0

    def test_get_weight_ast(self):
        """Test getting AST weight."""
        manager = ThresholdManager()
        assert manager.get_weight("ast") == 2.0

    def test_get_weight_hash(self):
        """Test getting hash weight."""
        manager = ThresholdManager()
        assert manager.get_weight("hash") == 1.5

    def test_get_weight_case_insensitive(self):
        """Test that detector name is case-insensitive."""
        manager = ThresholdManager()
        assert manager.get_weight("TOKEN") == 1.0
        assert manager.get_weight("AsT") == 2.0

    def test_get_weight_invalid_detector(self):
        """Test that invalid detector name raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="Invalid detector name"):
            manager.get_weight("invalid")


class TestSetWeight:
    """Test set_weight method."""

    def test_set_weight_valid(self):
        """Test setting valid weight."""
        manager = ThresholdManager()

        manager.set_weight("token", 1.5)
        assert manager.get_weight("token") == 1.5

        manager.set_weight("ast", 3.0)
        assert manager.get_weight("ast") == 3.0

    def test_set_weight_very_small(self):
        """Test setting very small positive weight."""
        manager = ThresholdManager()

        manager.set_weight("token", 0.001)
        assert manager.get_weight("token") == 0.001

    def test_set_weight_zero(self):
        """Test that zero weight raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be positive"):
            manager.set_weight("token", 0.0)

    def test_set_weight_negative(self):
        """Test that negative weight raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be positive"):
            manager.set_weight("token", -1.0)

    def test_set_weight_invalid_detector(self):
        """Test that invalid detector name raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="Invalid detector name"):
            manager.set_weight("invalid", 1.5)

    def test_set_weight_non_numeric(self):
        """Test that non-numeric value raises TypeError."""
        manager = ThresholdManager()

        with pytest.raises(TypeError, match="must be numeric"):
            manager.set_weight("token", "invalid")

    def test_set_weight_case_insensitive(self):
        """Test that detector name is case-insensitive."""
        manager = ThresholdManager()

        manager.set_weight("TOKEN", 1.5)
        assert manager.get_weight("token") == 1.5


class TestGetConfidenceWeight:
    """Test get_confidence_weight method."""

    def test_get_confidence_weight_token(self):
        """Test getting token confidence weight."""
        manager = ThresholdManager()
        assert manager.get_confidence_weight("token") == 0.3

    def test_get_confidence_weight_ast(self):
        """Test getting AST confidence weight."""
        manager = ThresholdManager()
        assert manager.get_confidence_weight("ast") == 0.4

    def test_get_confidence_weight_hash(self):
        """Test getting hash confidence weight."""
        manager = ThresholdManager()
        assert manager.get_confidence_weight("hash") == 0.3

    def test_get_confidence_weight_case_insensitive(self):
        """Test that detector name is case-insensitive."""
        manager = ThresholdManager()
        assert manager.get_confidence_weight("TOKEN") == 0.3

    def test_get_confidence_weight_invalid_detector(self):
        """Test that invalid detector name raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="Invalid detector name"):
            manager.get_confidence_weight("invalid")


class TestDecisionThreshold:
    """Test decision threshold getter and setter."""

    def test_get_decision_threshold_default(self):
        """Test getting default decision threshold."""
        manager = ThresholdManager()
        assert manager.get_decision_threshold() == 0.50

    def test_set_decision_threshold_valid(self):
        """Test setting valid decision threshold."""
        manager = ThresholdManager()

        manager.set_decision_threshold(0.60)
        assert manager.get_decision_threshold() == 0.60

    def test_set_decision_threshold_at_boundaries(self):
        """Test setting decision threshold at boundaries."""
        manager = ThresholdManager()

        manager.set_decision_threshold(0.0)
        assert manager.get_decision_threshold() == 0.0

        manager.set_decision_threshold(1.0)
        assert manager.get_decision_threshold() == 1.0

    def test_set_decision_threshold_below_range(self):
        """Test that decision threshold < 0.0 raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be in range"):
            manager.set_decision_threshold(-0.1)

    def test_set_decision_threshold_above_range(self):
        """Test that decision threshold > 1.0 raises ValueError."""
        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be in range"):
            manager.set_decision_threshold(1.5)

    def test_set_decision_threshold_non_numeric(self):
        """Test that non-numeric value raises TypeError."""
        manager = ThresholdManager()

        with pytest.raises(TypeError, match="must be numeric"):
            manager.set_decision_threshold("invalid")


class TestValidateThresholds:
    """Test validate_thresholds method."""

    def test_validate_default_configuration(self):
        """Test that default configuration validates successfully."""
        manager = ThresholdManager()
        assert manager.validate_thresholds() is True

    def test_validate_after_modifications(self):
        """Test validation after modifying configuration."""
        manager = ThresholdManager()

        manager.set_threshold("token", 0.75)
        manager.set_weight("ast", 2.5)
        manager.set_decision_threshold(0.60)

        assert manager.validate_thresholds() is True

    def test_validate_missing_threshold(self):
        """Test that missing threshold raises ValueError."""
        manager = ThresholdManager()
        # Manually corrupt the configuration
        del manager._thresholds["token"]

        with pytest.raises(ValueError, match="Missing threshold"):
            manager.validate_thresholds()

    def test_validate_missing_weight(self):
        """Test that missing weight raises ValueError."""
        manager = ThresholdManager()
        # Manually corrupt the configuration
        del manager._weights["ast"]

        with pytest.raises(ValueError, match="Missing weight"):
            manager.validate_thresholds()

    def test_validate_missing_confidence_weight(self):
        """Test that missing confidence weight raises ValueError."""
        manager = ThresholdManager()
        # Manually corrupt the configuration
        del manager._confidence_weights["hash"]

        with pytest.raises(ValueError, match="Missing confidence weight"):
            manager.validate_thresholds()

    def test_validate_threshold_non_numeric(self):
        """Test that non-numeric threshold raises ValueError."""
        manager = ThresholdManager()
        manager._thresholds["token"] = "invalid"

        with pytest.raises(ValueError, match="must be numeric"):
            manager.validate_thresholds()

    def test_validate_threshold_out_of_range(self):
        """Test that out-of-range threshold raises ValueError."""
        manager = ThresholdManager()
        manager._thresholds["token"] = 1.5

        with pytest.raises(ValueError, match="must be in \\[0.0, 1.0\\]"):
            manager.validate_thresholds()

    def test_validate_weight_non_numeric(self):
        """Test that non-numeric weight raises ValueError."""
        manager = ThresholdManager()
        manager._weights["ast"] = "invalid"

        with pytest.raises(ValueError, match="must be numeric"):
            manager.validate_thresholds()

    def test_validate_weight_non_positive(self):
        """Test that non-positive weight raises ValueError."""
        manager = ThresholdManager()
        manager._weights["ast"] = -1.0

        with pytest.raises(ValueError, match="must be positive"):
            manager.validate_thresholds()

    def test_validate_confidence_weight_non_numeric(self):
        """Test that non-numeric confidence weight raises ValueError."""
        manager = ThresholdManager()
        manager._confidence_weights["hash"] = "invalid"

        with pytest.raises(ValueError, match="must be numeric"):
            manager.validate_thresholds()

    def test_validate_confidence_weight_out_of_range(self):
        """Test that out-of-range confidence weight raises ValueError."""
        manager = ThresholdManager()
        manager._confidence_weights["hash"] = 1.5

        with pytest.raises(ValueError, match="must be in \\[0.0, 1.0\\]"):
            manager.validate_thresholds()

    def test_validate_decision_threshold_non_numeric(self):
        """Test that non-numeric decision threshold raises ValueError."""
        manager = ThresholdManager()
        manager._decision_threshold = "invalid"

        with pytest.raises(ValueError, match="must be numeric"):
            manager.validate_thresholds()

    def test_validate_decision_threshold_out_of_range(self):
        """Test that out-of-range decision threshold raises ValueError."""
        manager = ThresholdManager()
        manager._decision_threshold = 1.5

        with pytest.raises(ValueError, match="must be in \\[0.0, 1.0\\]"):
            manager.validate_thresholds()


class TestLoadFromFile:
    """Test load_from_file method."""

    def test_load_complete_config(self, tmp_path):
        """Test loading complete configuration from file."""
        config_file = tmp_path / "complete_config.json"
        config_data = {
            "thresholds": {"token": 0.75, "ast": 0.85, "hash": 0.65},
            "weights": {"token": 1.5, "ast": 2.5, "hash": 2.0},
            "confidence_weights": {"token": 0.25, "ast": 0.5, "hash": 0.25},
            "decision_threshold": 0.60,
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()
        manager.load_from_file(str(config_file))

        assert manager.get_threshold("token") == 0.75
        assert manager.get_weight("ast") == 2.5
        assert manager.get_confidence_weight("hash") == 0.25
        assert manager.get_decision_threshold() == 0.60

    def test_load_partial_config(self, tmp_path):
        """Test loading partial configuration (only thresholds)."""
        config_file = tmp_path / "partial_config.json"
        config_data = {"thresholds": {"token": 0.75, "ast": 0.85, "hash": 0.65}}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()
        manager.load_from_file(str(config_file))

        # Thresholds should be updated
        assert manager.get_threshold("token") == 0.75

        # Weights should remain default
        assert manager.get_weight("token") == 1.0

    def test_load_with_unknown_detector(self, tmp_path):
        """Test loading config with unknown detector (should be ignored)."""
        config_file = tmp_path / "unknown_detector.json"
        config_data = {
            "thresholds": {
                "token": 0.75,
                "ast": 0.85,
                "hash": 0.65,
                "unknown": 0.50,  # Should be ignored
            }
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()
        # Should not raise error, just ignore unknown detector
        manager.load_from_file(str(config_file))

        assert manager.get_threshold("token") == 0.75

    def test_load_invalid_threshold_type(self, tmp_path):
        """Test loading config with invalid threshold type."""
        config_file = tmp_path / "invalid_threshold.json"
        config_data = {"thresholds": "not a dictionary"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be a dictionary"):
            manager.load_from_file(str(config_file))

    def test_load_invalid_weights_type(self, tmp_path):
        """Test loading config with invalid weights type."""
        config_file = tmp_path / "invalid_weights.json"
        config_data = {"weights": "not a dictionary"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be a dictionary"):
            manager.load_from_file(str(config_file))

    def test_load_invalid_confidence_weights_type(self, tmp_path):
        """Test loading config with invalid confidence_weights type."""
        config_file = tmp_path / "invalid_conf_weights.json"
        config_data = {"confidence_weights": "not a dictionary"}

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be a dictionary"):
            manager.load_from_file(str(config_file))

    def test_load_invalid_confidence_weight_value(self, tmp_path):
        """Test loading config with invalid confidence weight value."""
        config_file = tmp_path / "invalid_conf_value.json"
        config_data = {
            "confidence_weights": {"token": 1.5, "ast": 0.4, "hash": 0.3}  # Out of range
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()

        with pytest.raises(ValueError, match="must be in \\[0.0, 1.0\\]"):
            manager.load_from_file(str(config_file))


class TestSaveToFile:
    """Test save_to_file method."""

    def test_save_default_config(self, tmp_path):
        """Test saving default configuration to file."""
        config_file = tmp_path / "saved_config.json"

        manager = ThresholdManager()
        manager.save_to_file(str(config_file))

        # Verify file was created
        assert config_file.exists()

        # Load and verify contents
        with open(config_file, "r") as f:
            loaded_config = json.load(f)

        assert loaded_config["thresholds"]["token"] == 0.70
        assert loaded_config["weights"]["ast"] == 2.0
        assert loaded_config["decision_threshold"] == 0.50

    def test_save_modified_config(self, tmp_path):
        """Test saving modified configuration to file."""
        config_file = tmp_path / "modified_config.json"

        manager = ThresholdManager()
        manager.set_threshold("token", 0.75)
        manager.set_weight("ast", 2.5)
        manager.set_decision_threshold(0.60)

        manager.save_to_file(str(config_file))

        # Load and verify
        with open(config_file, "r") as f:
            loaded_config = json.load(f)

        assert loaded_config["thresholds"]["token"] == 0.75
        assert loaded_config["weights"]["ast"] == 2.5
        assert loaded_config["decision_threshold"] == 0.60

    def test_save_creates_parent_directory(self, tmp_path):
        """Test that save creates parent directories if they don't exist."""
        config_file = tmp_path / "subdir" / "config.json"

        manager = ThresholdManager()
        manager.save_to_file(str(config_file))

        # Verify file was created
        assert config_file.exists()

    def test_save_and_reload(self, tmp_path):
        """Test saving and reloading configuration."""
        config_file = tmp_path / "roundtrip.json"

        manager1 = ThresholdManager()
        manager1.set_threshold("token", 0.75)
        manager1.set_weight("ast", 2.5)
        manager1.save_to_file(str(config_file))

        # Create new manager from saved file
        manager2 = ThresholdManager(config_path=str(config_file))

        assert manager2.get_threshold("token") == 0.75
        assert manager2.get_weight("ast") == 2.5


class TestGetConfig:
    """Test get_config method."""

    def test_get_config_structure(self):
        """Test that get_config returns correct structure."""
        manager = ThresholdManager()
        config = manager.get_config()

        assert "thresholds" in config
        assert "weights" in config
        assert "confidence_weights" in config
        assert "decision_threshold" in config

    def test_get_config_values(self):
        """Test that get_config returns correct values."""
        manager = ThresholdManager()
        config = manager.get_config()

        assert config["thresholds"]["token"] == 0.70
        assert config["weights"]["ast"] == 2.0
        assert config["confidence_weights"]["hash"] == 0.3
        assert config["decision_threshold"] == 0.50

    def test_get_config_returns_copy(self):
        """Test that get_config returns a copy, not reference."""
        manager = ThresholdManager()
        config = manager.get_config()

        # Modify returned config
        config["thresholds"]["token"] = 0.99

        # Original should be unchanged
        assert manager.get_threshold("token") == 0.70


class TestResetToDefaults:
    """Test reset_to_defaults method."""

    def test_reset_after_modifications(self):
        """Test resetting to defaults after modifications."""
        manager = ThresholdManager()

        # Modify configuration
        manager.set_threshold("token", 0.75)
        manager.set_weight("ast", 2.5)
        manager.set_decision_threshold(0.60)

        # Reset to defaults
        manager.reset_to_defaults()

        # Verify defaults are restored
        assert manager.get_threshold("token") == 0.70
        assert manager.get_weight("ast") == 2.0
        assert manager.get_decision_threshold() == 0.50

    def test_reset_all_detectors(self):
        """Test that reset affects all detectors."""
        manager = ThresholdManager()

        # Modify all detectors
        manager.set_threshold("token", 0.75)
        manager.set_threshold("ast", 0.85)
        manager.set_threshold("hash", 0.65)

        # Reset
        manager.reset_to_defaults()

        # Verify all are reset
        assert manager.get_threshold("token") == 0.70
        assert manager.get_threshold("ast") == 0.80
        assert manager.get_threshold("hash") == 0.60


class TestStringRepresentation:
    """Test __repr__ method."""

    def test_repr_method(self):
        """Test that __repr__ returns valid string."""
        manager = ThresholdManager()
        repr_str = repr(manager)

        assert isinstance(repr_str, str)
        assert "ThresholdManager" in repr_str

    def test_repr_contains_thresholds(self):
        """Test that __repr__ contains threshold information."""
        manager = ThresholdManager()
        repr_str = repr(manager)

        assert "thresholds" in repr_str.lower() or "0.7" in repr_str

    def test_repr_contains_weights(self):
        """Test that __repr__ contains weight information."""
        manager = ThresholdManager()
        repr_str = repr(manager)

        assert "weights" in repr_str.lower() or "2.0" in repr_str

    def test_repr_contains_decision_threshold(self):
        """Test that __repr__ contains decision threshold."""
        manager = ThresholdManager()
        repr_str = repr(manager)

        assert "decision_threshold" in repr_str.lower() or "0.5" in repr_str


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_threshold_at_zero(self):
        """Test setting threshold to exact 0.0."""
        manager = ThresholdManager()

        manager.set_threshold("token", 0.0)
        assert manager.get_threshold("token") == 0.0

    def test_threshold_at_one(self):
        """Test setting threshold to exact 1.0."""
        manager = ThresholdManager()

        manager.set_threshold("token", 1.0)
        assert manager.get_threshold("token") == 1.0

    def test_very_small_weight(self):
        """Test setting very small positive weight."""
        manager = ThresholdManager()

        manager.set_weight("token", 0.0001)
        assert manager.get_weight("token") == 0.0001

    def test_very_large_weight(self):
        """Test setting very large weight."""
        manager = ThresholdManager()

        manager.set_weight("token", 1000.0)
        assert manager.get_weight("token") == 1000.0

    def test_all_detectors_case_variations(self):
        """Test that all detector names work with case variations."""
        manager = ThresholdManager()

        # Test all case variations
        for detector in ["token", "TOKEN", "Token", "ToKeN"]:
            manager.set_threshold(detector, 0.75)
            assert manager.get_threshold(detector) == 0.75

    def test_sequential_modifications(self):
        """Test multiple sequential modifications."""
        manager = ThresholdManager()

        # Multiple modifications
        for i in range(10):
            value = 0.5 + (i * 0.01)
            manager.set_threshold("token", value)
            assert pytest.approx(manager.get_threshold("token"), abs=1e-9) == value

    def test_empty_config_file(self, tmp_path):
        """Test loading empty JSON object."""
        config_file = tmp_path / "empty.json"
        with open(config_file, "w") as f:
            json.dump({}, f)

        manager = ThresholdManager()
        manager.load_from_file(str(config_file))

        # Should keep defaults since nothing to load
        assert manager.get_threshold("token") == 0.70

    def test_load_with_unknown_weight_detector(self, tmp_path):
        """Test loading config with unknown detector in weights (should be ignored)."""
        config_file = tmp_path / "unknown_weight.json"
        config_data = {
            "weights": {
                "token": 1.5,
                "ast": 2.5,
                "hash": 2.0,
                "unknown": 1.0,  # Should be ignored with warning
            }
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()
        # Should not raise error, just ignore unknown detector
        manager.load_from_file(str(config_file))

        assert manager.get_weight("token") == 1.5

    def test_load_with_unknown_confidence_weight_detector(self, tmp_path):
        """Test loading config with unknown detector in confidence_weights (should be ignored)."""
        config_file = tmp_path / "unknown_conf_weight.json"
        config_data = {
            "confidence_weights": {
                "token": 0.25,
                "ast": 0.5,
                "hash": 0.25,
                "unknown": 0.0,  # Should be ignored with warning
            }
        }

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        manager = ThresholdManager()
        # Should not raise error, just ignore unknown detector
        manager.load_from_file(str(config_file))

        assert manager.get_confidence_weight("token") == 0.25

    def test_save_file_io_error(self, tmp_path):
        """Test that IOError is raised when file cannot be written."""
        # Create a read-only directory
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        config_file = readonly_dir / "config.json"

        # Make directory read-only (this will prevent writing)
        import os

        readonly_dir.chmod(0o444)

        manager = ThresholdManager()

        try:
            with pytest.raises(IOError, match="Failed to write"):
                manager.save_to_file(str(config_file))
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)
