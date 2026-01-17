"""Authentication Agent"""

import asyncio
from typing import Optional
from .base_agent import BaseAgent
from ..core import MStockClient, ReconnectionManager
from ..utils.config_manager import get_config


class AuthAgent(BaseAgent):
    """Handles mStock authentication and session management"""
    
    def __init__(self):
        super().__init__("AuthAgent")
        self.config = get_config()
        self.client: Optional[MStockClient] = None
        self.reconnection_manager: Optional[ReconnectionManager] = None
    
    async def initialize(self) -> bool:
        """Initialize authentication agent"""
        try:
            # Get credentials from config
            api_key = self.config.get('mstock.api_key')
            api_secret = self.config.get('mstock.api_secret')
            totp_secret = self.config.get('mstock.totp_secret')
            client_code = self.config.get('mstock.client_code', '')
            
            if not all([api_key, api_secret, totp_secret]):
                self.logger.error("Missing mStock credentials in config")
                return False
            
            # Initialize mStock client
            self.client = MStockClient(
                api_key=api_key,
                api_secret=api_secret,
                totp_secret=totp_secret,
                client_code=client_code
            )
            
            # Initial authentication
            if not await self.client.authenticate():
                self.logger.error("Initial authentication failed")
                return False
            
            # Setup reconnection manager
            reconnect_interval = self.config.get('network.reconnect_interval', 60)
            max_retries = self.config.get('network.max_retries', 5)
            retry_delay = self.config.get('network.retry_delay', 10)
            
            self.reconnection_manager = ReconnectionManager(
                reconnect_interval=reconnect_interval,
                max_retries=max_retries,
                retry_delay=retry_delay
            )
            
            # Set connection callback
            self.reconnection_manager.set_connection_callback(self._reconnect_callback)
            self.reconnection_manager.mark_connected()
            
            self.logger.info("AuthAgent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize AuthAgent: {e}")
            return False
    
    async def _reconnect_callback(self) -> None:
        """Callback for reconnection attempts"""
        if self.client:
            await self.client.authenticate()
    
    async def run(self) -> None:
        """Main agent loop"""
        self.update_status("running")
        
        # Start reconnection manager
        if self.reconnection_manager:
            self.reconnection_manager.start()
        
        try:
            while self.is_running:
                # Monitor connection health
                await asyncio.sleep(10)
                
                if self.client and not self.client.is_authenticated:
                    self.logger.warning("Connection lost, marking as disconnected")
                    if self.reconnection_manager:
                        self.reconnection_manager.mark_disconnected()
        
        except asyncio.CancelledError:
            self.logger.info("AuthAgent run loop cancelled")
        except Exception as e:
            self.logger.exception(f"Error in AuthAgent run loop: {e}")
        finally:
            self.update_status("stopped")
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info("Stopping AuthAgent")
        self.is_running = False
        
        if self.reconnection_manager:
            await self.reconnection_manager.stop()
        
        if self.client:
            await self.client.close()
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.update_status("stopped")
    
    def get_client(self) -> Optional[MStockClient]:
        """Get the mStock client instance"""
        return self.client
    
    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self.client is not None and self.client.is_authenticated
