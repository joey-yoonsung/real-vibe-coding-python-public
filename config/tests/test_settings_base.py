"""Tests for SettingsBase."""

from functools import cached_property

import pytest

from my_config import ConfigBase, SettingsBase


class RedisConfig(ConfigBase):
    """Sample Redis config for testing."""

    host: str = "localhost"
    port: int = 6379


class TestSettingsBase:
    """Tests for SettingsBase class."""

    def test_default_model_config(self):
        """Test that SettingsBase has default model_config."""

        class Settings(SettingsBase):
            app_name: str = "test"

        settings = Settings()

        assert settings.model_config.get("env_file") == ".env"
        assert settings.model_config.get("case_sensitive") is False
        assert settings.model_config.get("extra") == "ignore"

    def test_load_config_helper(self, monkeypatch: pytest.MonkeyPatch):
        """Test _load_config helper method."""
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("REDIS_PORT", "6380")

        class Settings(SettingsBase):
            @cached_property
            def redis(self) -> RedisConfig:
                return self._load_config(RedisConfig, prefix="REDIS_")

        settings = Settings()

        assert settings.redis.host == "redis.example.com"
        assert settings.redis.port == 6380

    def test_load_config_uses_defaults(self):
        """Test _load_config uses ConfigBase defaults when env vars not set."""

        class Settings(SettingsBase):
            @cached_property
            def redis(self) -> RedisConfig:
                return self._load_config(RedisConfig, prefix="REDIS_")

        settings = Settings()

        assert settings.redis.host == "localhost"
        assert settings.redis.port == 6379
