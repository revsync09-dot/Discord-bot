"""
Core configuration module.
Loads environment variables and provides type-safe configuration access.
No secrets are hardcoded.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BotConfig:
    """Bot configuration container."""
    
    # Discord
    token: str
    application_id: str
    
    # GitHub Webhook
    webhook_secret: str
    webhook_host: str
    webhook_port: int
    
    # Database
    database_url: str
    
    # Logging
    log_level: str
    log_format: str
    
    # Feature Flags
    debug_mode: bool
    sync_commands_on_ready: bool
    
    @classmethod
    def from_env(cls) -> "BotConfig":
        """
        Load configuration from environment variables.
        Raises ValueError if required variables are missing.
        """
        
        # Required variables
        token = os.getenv("DISCORD_BOT_TOKEN")
        application_id = os.getenv("DISCORD_APPLICATION_ID")
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET")
        
        if not token:
            raise ValueError("DISCORD_BOT_TOKEN is required")
        if not application_id:
            raise ValueError("DISCORD_APPLICATION_ID is required")
        if not webhook_secret:
            raise ValueError("GITHUB_WEBHOOK_SECRET is required")
        
        return cls(
            # Discord
            token=token,
            application_id=application_id,
            
            # GitHub Webhook
            webhook_secret=webhook_secret,
            webhook_host=os.getenv("WEBHOOK_HOST", "0.0.0.0"),
            webhook_port=int(os.getenv("WEBHOOK_PORT", "8000")),
            
            # Database
            database_url=os.getenv("DATABASE_URL", "sqlite:///data/bot.db"),
            
            # Logging
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_format=os.getenv(
                "LOG_FORMAT",
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            ),
            
            # Feature Flags
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            sync_commands_on_ready=os.getenv("SYNC_COMMANDS_ON_READY", "true").lower() == "true",
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if self.webhook_port < 1 or self.webhook_port > 65535:
            raise ValueError(f"Invalid webhook port: {self.webhook_port}")
        
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid log level: {self.log_level}")


# Global config instance (loaded once)
_config: Optional[BotConfig] = None


def get_config() -> BotConfig:
    """
    Get the global configuration instance.
    Loads from environment on first call.
    """
    global _config
    
    if _config is None:
        _config = BotConfig.from_env()
        _config.validate()
    
    return _config


def reload_config() -> BotConfig:
    """Force reload configuration from environment."""
    global _config
    _config = BotConfig.from_env()
    _config.validate()
    return _config
