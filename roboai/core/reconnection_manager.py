"""Reconnection Manager for mStock API"""

import asyncio
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from ..utils.logger import get_logger


class ReconnectionManager:
    """Manages automatic reconnection to mStock API"""
    
    def __init__(
        self,
        reconnect_interval: int = 60,
        max_retries: int = 5,
        retry_delay: int = 10
    ):
        """
        Initialize reconnection manager
        
        Args:
            reconnect_interval: Interval between reconnection checks in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retry attempts in seconds
        """
        self.reconnect_interval = reconnect_interval
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.is_connected = False
        self.last_connection_time: Optional[datetime] = None
        self.connection_callback: Optional[Callable] = None
        self.reconnection_task: Optional[asyncio.Task] = None
        
        self.logger = get_logger()
        self._running = False
        self._retry_count = 0
    
    def set_connection_callback(self, callback: Callable) -> None:
        """
        Set callback function for reconnection
        
        Args:
            callback: Async function to call for reconnection
        """
        self.connection_callback = callback
    
    def mark_connected(self) -> None:
        """Mark connection as established"""
        self.is_connected = True
        self.last_connection_time = datetime.now()
        self._retry_count = 0
        self.logger.info("Connection established")
    
    def mark_disconnected(self) -> None:
        """Mark connection as lost"""
        was_connected = self.is_connected
        self.is_connected = False
        
        if was_connected:
            self.logger.warning("Connection lost")
    
    async def attempt_reconnect(self) -> bool:
        """
        Attempt to reconnect
        
        Returns:
            True if reconnection successful, False otherwise
        """
        if self.connection_callback is None:
            self.logger.error("No connection callback set")
            return False
        
        self._retry_count += 1
        self.logger.info(f"Attempting reconnection (attempt {self._retry_count}/{self.max_retries})")
        
        try:
            await self.connection_callback()
            self.mark_connected()
            return True
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
            return False
    
    async def reconnection_loop(self) -> None:
        """Main reconnection loop"""
        self.logger.info("Reconnection manager started")
        self._running = True
        
        while self._running:
            try:
                await asyncio.sleep(self.reconnect_interval)
                
                if not self.is_connected:
                    self.logger.info("Connection lost, attempting to reconnect...")
                    
                    # Try to reconnect with retries
                    for attempt in range(self.max_retries):
                        if await self.attempt_reconnect():
                            break
                        
                        if attempt < self.max_retries - 1:
                            self.logger.info(f"Waiting {self.retry_delay}s before next attempt...")
                            await asyncio.sleep(self.retry_delay)
                    else:
                        self.logger.error(f"Failed to reconnect after {self.max_retries} attempts")
                        # Reset retry count for next cycle
                        self._retry_count = 0
                
                else:
                    # Check connection health
                    time_since_connection = datetime.now() - self.last_connection_time
                    
                    # Proactive reconnection every reconnect_interval
                    if time_since_connection >= timedelta(seconds=self.reconnect_interval):
                        self.logger.info("Performing proactive reconnection...")
                        await self.attempt_reconnect()
            
            except asyncio.CancelledError:
                self.logger.info("Reconnection loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in reconnection loop: {e}")
                await asyncio.sleep(self.retry_delay)
        
        self.logger.info("Reconnection manager stopped")
    
    def start(self) -> None:
        """Start the reconnection manager"""
        if self.reconnection_task is None or self.reconnection_task.done():
            self.reconnection_task = asyncio.create_task(self.reconnection_loop())
            self.logger.info("Reconnection manager task created")
    
    async def stop(self) -> None:
        """Stop the reconnection manager"""
        self._running = False
        
        if self.reconnection_task and not self.reconnection_task.done():
            self.reconnection_task.cancel()
            try:
                await self.reconnection_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Reconnection manager stopped")
    
    def get_status(self) -> dict:
        """
        Get current status
        
        Returns:
            Dictionary with status information
        """
        return {
            'is_connected': self.is_connected,
            'last_connection_time': self.last_connection_time.isoformat() if self.last_connection_time else None,
            'retry_count': self._retry_count,
            'is_running': self._running,
        }
