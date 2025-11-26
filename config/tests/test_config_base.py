"""Tests for ConfigBase."""

import os

import pytest

from my_config import ConfigBase


class SampleConfig(ConfigBase):
    """Sample config for testing."""

    host: str = "localhost"
    port: int = 8080
    debug: bool = False


class TestConfigBase:
    """Tests for ConfigBase class."""

    def test_default_values(self):
        """Test that default values are used when no env vars are set."""
        config = SampleConfig()

        assert config.host == "localhost"
        assert config.port == 8080
        assert config.debug is False

    def test_from_env_with_prefix(self, monkeypatch: pytest.MonkeyPatch):
        """Test loading config from environment variables with prefix."""
        monkeypatch.setenv("TEST_HOST", "example.com")
        monkeypatch.setenv("TEST_PORT", "9000")
        monkeypatch.setenv("TEST_DEBUG", "true")

        config = SampleConfig.from_env(prefix="TEST_")

        assert config.host == "example.com"
        assert config.port == 9000
        assert config.debug is True

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        config = SampleConfig(host="test", custom_field="value")

        assert config.host == "test"
        assert config.custom_field == "value"  # type: ignore[attr-defined]

    def test_get_extra_configs(self):
        """Test get_extra_configs returns only extra fields."""
        config = SampleConfig(host="test", extra1="a", extra2="b")

        extras = config.get_extra_configs()

        assert extras == {"extra1": "a", "extra2": "b"}
        assert "host" not in extras

    def test_get_printable_config_masks_sensitive_fields(self):
        """Test that sensitive fields are masked in printable config."""

        class ConfigWithSecrets(ConfigBase):
            api_key: str = "secret123"
            password: str = "mypassword"
            host: str = "localhost"

        config = ConfigWithSecrets()
        printable = config.get_printable_config()

        assert printable["host"] == "localhost"
        assert printable["api_key"] == "se...23"
        assert printable["password"] == "my...rd"
