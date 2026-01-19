"""
Database abstraction layer.
Uses SQLite with async support via aiosqlite.
"""

import aiosqlite
from typing import Optional, List
from pathlib import Path

from ..core.logger import get_logger

logger = get_logger(__name__)


class Database:
    """
    Async database manager. 
    Handles connection pooling and schema initialization.
    """
    
    def __init__(self, database_url: str):
        # Extract path from URL (sqlite:///path/to/db.db)
        self.db_path = database_url.replace("sqlite:///, ")
        self.connection: Optional[aiosqlite.Connection] = None
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    async def connect(self):
        """Establish database connection."""
        logger.info(f"Connecting to database: {self.db_path}")
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row
        await self.initialize_schema()
        logger.info("Database connected")
    
    async def disconnect(self):
        """Close database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database disconnected")
    
    async def initialize_schema(self):
        """Create tables if they don't exist."""
        logger.info("Initializing database schema...")
        
        async with self.connection.cursor() as cursor:
            # Guilds table
            await cursor.execute("
                CREATE TABLE IF NOT EXISTS guilds (
                    guild_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP
                )
            ")
            
            # Repositories table
            await cursor.execute("
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    owner TEXT NOT NULL,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    UNIQUE(owner, name)
                )
            ")
            
            # Subscriptions table
            await cursor.execute("
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    repository_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    enabled_events TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id),
                    FOREIGN KEY (repository_id) REFERENCES repositories(id),
                    UNIQUE(guild_id, repository_id, channel_id)
                )
            ")
            
            # Event logs table
            await cursor.execute("
                CREATE TABLE IF NOT EXISTS event_logs (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    repository_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    delivered_at TIMESTAMP NOT NULL,
                    payload_hash TEXT,
                    success BOOLEAN DEFAULT 1,
                    error_message TEXT,
                    FOREIGN KEY (repository_id) REFERENCES repositories(id),
                    FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
                )
            ")
            
            # Indexes
            await cursor.execute("
                CREATE INDEX IF NOT EXISTS idx_subscriptions_guild 
                ON subscriptions(guild_id)
            ")
            
            await cursor.execute("
                CREATE INDEX IF NOT EXISTS idx_subscriptions_repo 
                ON subscriptions(repository_id)
            ")
            
            await cursor.execute("
                CREATE INDEX IF NOT EXISTS idx_event_logs_delivered 
                ON event_logs(delivered_at)
            ")
            
            await self.connection.commit()
        
        logger.info("Database schema initialized")
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query without returning results."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            await self.connection.commit()
    
    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows."""
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            return await cursor.fetchall()
    
    async def get_last_insert_id(self) -> int:
        """Get the last inserted row ID."""
        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT last_insert_rowid()")
            row = await cursor.fetchone()
            return row[0] if row else None
