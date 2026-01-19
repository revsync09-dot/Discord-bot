"""
Repository pattern for database access.
No raw SQL in business logic.
"""

from typing import Optional, List
from datetime import datetime
import json

from .database import Database
from .models import Guild, GitHubRepository, Subscription, EventLog
from ..core.logger import get_logger

logger = get_logger(__name__)


class GuildRepository:
    """Repository for guild operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, guild: Guild) -> Guild:
        """Create a new guild."""
        await self.db.execute(
            """
            INSERT INTO guilds (guild_id, name, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
                name = excluded.name,
                updated_at = CURRENT_TIMESTAMP
            """,
            (guild.guild_id, guild.name, guild.created_at)
        )
        logger.info(f"Created/updated guild: {guild.guild_id}")
        return guild
    
    async def get_by_id(self, guild_id: int) -> Optional[Guild]:
        """Get guild by ID."""
        row = await self.db.fetch_one(
            "SELECT * FROM guilds WHERE guild_id = ?",
            (guild_id,)
        )
        
        if row:
            return Guild(
                guild_id=row['guild_id'],
                name=row['name'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
        return None
    
    async def get_all(self) -> List[Guild]:
        """Get all guilds."""
        rows = await self.db.fetch_all("SELECT * FROM guilds ORDER BY created_at DESC")
        
        return [
            Guild(
                guild_id=row['guild_id'],
                name=row['name'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
            )
            for row in rows
        ]


class RepositoryRepository:
    """Repository for GitHub repository operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, repo: GitHubRepository) -> GitHubRepository:
        """Create a new repository."""
        await self.db.execute(
            """
            INSERT INTO repositories (owner, name, url, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner, name) DO NOTHING
            """,
            (repo.owner, repo.name, repo.url, repo.created_at)
        )
        
        # Get the ID
        row = await self.db.fetch_one(
            "SELECT id FROM repositories WHERE owner = ? AND name = ?",
            (repo.owner, repo.name)
        )
        
        repo.id = row['id'] if row else None
        logger.info(f"Created repository: {repo.full_name}")
        return repo
    
    async def get_by_full_name(self, owner: str, name: str) -> Optional[GitHubRepository]:
        """Get repository by owner/name."""
        row = await self.db.fetch_one(
            "SELECT * FROM repositories WHERE owner = ? AND name = ?",
            (owner, name)
        )
        
        if row:
            return GitHubRepository(
                id=row['id'],
                owner=row['owner'],
                name=row['name'],
                url=row['url'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None
    
    async def get_by_id(self, repo_id: int) -> Optional[GitHubRepository]:
        """Get repository by ID."""
        row = await self.db.fetch_one(
            "SELECT * FROM repositories WHERE id = ?",
            (repo_id,)
        )
        
        if row:
            return GitHubRepository(
                id=row['id'],
                owner=row['owner'],
                name=row['name'],
                url=row['url'],
                created_at=datetime.fromisoformat(row['created_at'])
            )
        return None


class SubscriptionRepository:
    """Repository for subscription operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, subscription: Subscription) -> Subscription:
        """Create a new subscription."""
        await self.db.execute(
            """
            INSERT INTO subscriptions 
            (guild_id, repository_id, channel_id, enabled_events, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                subscription.guild_id,
                subscription.repository_id,
                subscription.channel_id,
                subscription.enabled_events,
                subscription.created_at,
                subscription.is_active
            )
        )
        
        subscription.id = await self.db.get_last_insert_id()
        logger.info(f"Created subscription: {subscription.id}")
        return subscription
    
    async def get_by_guild_and_repo(
        self,
        guild_id: int,
        repository_id: int
    ) -> List[Subscription]:
        """Get subscriptions for a guild and repository."""
        rows = await self.db.fetch_all(
            """
            SELECT * FROM subscriptions 
            WHERE guild_id = ? AND repository_id = ? AND is_active = 1
            """,
            (guild_id, repository_id)
        )
        
        return [
            Subscription(
                id=row['id'],
                guild_id=row['guild_id'],
                repository_id=row['repository_id'],
                channel_id=row['channel_id'],
                enabled_events=row['enabled_events'],
                created_at=datetime.fromisoformat(row['created_at']),
                is_active=bool(row['is_active'])
            )
            for row in rows
        ]
    
    async def get_by_guild(self, guild_id: int) -> List[Subscription]:
        """Get all subscriptions for a guild."""
        rows = await self.db.fetch_all(
            "SELECT * FROM subscriptions WHERE guild_id = ? AND is_active = 1",
            (guild_id,)
        )
        
        return [
            Subscription(
                id=row['id'],
                guild_id=row['guild_id'],
                repository_id=row['repository_id'],
                channel_id=row['channel_id'],
                enabled_events=row['enabled_events'],
                created_at=datetime.fromisoformat(row['created_at']),
                is_active=bool(row['is_active'])
            )
            for row in rows
        ]
    
    async def delete(self, subscription_id: int):
        """Soft delete a subscription."""
        await self.db.execute(
            "UPDATE subscriptions SET is_active = 0 WHERE id = ?",
            (subscription_id,)
        )
        logger.info(f"Deleted subscription: {subscription_id}")
    
    async def get_by_repository(self, repository_id: int) -> List[Subscription]:
        """Get all active subscriptions for a repository."""
        rows = await self.db.fetch_all(
            "SELECT * FROM subscriptions WHERE repository_id = ? AND is_active = 1",
            (repository_id,)
        )
        
        return [
            Subscription(
                id=row['id'],
                guild_id=row['guild_id'],
                repository_id=row['repository_id'],
                channel_id=row['channel_id'],
                enabled_events=row['enabled_events'],
                created_at=datetime.fromisoformat(row['created_at']),
                is_active=bool(row['is_active'])
            )
            for row in rows
        ]


class EventLogRepository:
    """Repository for event log operations."""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def create(self, event_log: EventLog) -> EventLog:
        """Create a new event log."""
        await self.db.execute(
            """
            INSERT INTO event_logs 
            (event_type, repository_id, guild_id, channel_id, delivered_at, 
             payload_hash, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_log.event_type,
                event_log.repository_id,
                event_log.guild_id,
                event_log.channel_id,
                event_log.delivered_at,
                event_log.payload_hash,
                event_log.success,
                event_log.error_message
            )
        )
        
        event_log.event_id = await self.db.get_last_insert_id()
        return event_log
    
    async def get_recent(self, limit: int = 100) -> List[EventLog]:
        """Get recent event logs."""
        rows = await self.db.fetch_all(
            "SELECT * FROM event_logs ORDER BY delivered_at DESC LIMIT ?",
            (limit,)
        )
        
        return [
            EventLog(
                event_id=row['event_id'],
                event_type=row['event_type'],
                repository_id=row['repository_id'],
                guild_id=row['guild_id'],
                channel_id=row['channel_id'],
                delivered_at=datetime.fromisoformat(row['delivered_at']),
                payload_hash=row['payload_hash'],
                success=bool(row['success']),
                error_message=row['error_message']
            )
            for row in rows
        ]
