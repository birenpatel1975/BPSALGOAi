"""Base Agent class for all agents"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime
from ..utils.logger import get_logger


class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str):
        """
        Initialize base agent
        
        Args:
            name: Agent name
        """
        self.name = name
        self.logger = get_logger()
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        self.status = "initialized"
        self.last_update: Optional[datetime] = None
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the agent
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def run(self) -> None:
        """Main agent loop"""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the agent"""
        pass
    
    async def start(self) -> None:
        """Start the agent"""
        if self.is_running:
            self.logger.warning(f"{self.name} is already running")
            return
        
        self.logger.info(f"Starting {self.name}")
        
        # Initialize agent
        if not await self.initialize():
            self.logger.error(f"Failed to initialize {self.name}")
            return
        
        self.is_running = True
        self.status = "running"
        self.task = asyncio.create_task(self.run())
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check agent health
        
        Returns:
            Health status dictionary
        """
        return {
            "name": self.name,
            "status": self.status,
            "is_running": self.is_running,
            "last_update": self.last_update.isoformat() if self.last_update else None
        }
    
    def update_status(self, status: str) -> None:
        """Update agent status"""
        self.status = status
        self.last_update = datetime.now()
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.name}, status={self.status}>"
