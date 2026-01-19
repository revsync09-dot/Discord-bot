"""
Database models. 
All models are versionable and use proper relationships.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Guild:
    """Discord guild (server) model."""
    
    guild_id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    def __repr__(self):
        return f"<Guild {self.guild_id} ({self.name})>"


@dataclass
class GitHubRepository:
    """GitHub repository model."""
    
    id: Optional[int]
    owner: str
    name: str
    url: str
    created_at: datetime
    
    @property
    def full_name(self) -> str:
        """Get full repository name (owner/repo)."""
        return f"{self.owner}/{self.name}"
    
    def __repr__(self):
        return f"<GitHubRepository {self.full_name}>"


@dataclass
class Subscription:
    """Subscription linking guilds to repositories."""
    
    id: Optional[int]
    guild_id: int
    repository_id: int
    channel_id: int
    enabled_events: str  # JSON array stored as string
    created_at: datetime
    is_active: bool = True
    
    def __repr__(self):
        return f"<Subscription guild={self.guild_id} repo={self.repository_id} channel={self.channel_id}>"


@dataclass
class EventLog:
    """Log of delivered GitHub events."""
    
    event_id: Optional[int]
    event_type: str
    repository_id: int
    guild_id: int
    channel_id: int
    delivered_at: datetime
    payload_hash: Optional[str] = None  # For deduplication
    success: bool = True
    error_message: Optional[str] = None
    
    def __repr__(self):
        return f"<EventLog {self.event_type} repo={self.repository_id}>"