"""Network Manager for handling network connections"""

import asyncio
import platform
import socket
from typing import Optional, Dict, Any
from enum import Enum


class ConnectionType(Enum):
    """Network connection types"""
    WIFI = "wifi"
    ETHERNET = "ethernet"
    MOBILE_4G = "4g"
    MOBILE_5G = "5g"
    UNKNOWN = "unknown"


class NetworkManager:
    """Manages network connections and preferences"""
    
    def __init__(self, preferred_connection: str = "5g"):
        self.preferred_connection = preferred_connection.lower()
        self.current_connection: Optional[ConnectionType] = None
        self._network_info: Dict[str, Any] = {}
    
    def check_internet_connectivity(self, host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
        """
        Check if internet is accessible
        
        Args:
            host: Host to check (default: Google DNS)
            port: Port to check
            timeout: Timeout in seconds
        
        Returns:
            True if internet is accessible, False otherwise
        """
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False
    
    async def check_connectivity_async(self, host: str = "8.8.8.8", port: int = 53) -> bool:
        """Async version of connectivity check"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=3.0
            )
            writer.close()
            await writer.wait_closed()
            return True
        except (asyncio.TimeoutError, OSError):
            return False
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        Get current network information
        
        Returns:
            Dictionary with network information
        """
        info = {
            "hostname": socket.gethostname(),
            "platform": platform.system(),
            "connected": self.check_internet_connectivity(),
        }
        
        try:
            info["ip_address"] = socket.gethostbyname(socket.gethostname())
        except socket.error:
            info["ip_address"] = "Unknown"
        
        self._network_info = info
        return info
    
    def detect_connection_type(self) -> ConnectionType:
        """
        Detect current network connection type
        
        Note: This is a basic implementation. Full detection requires
        platform-specific APIs (Windows: netsh, Linux: nmcli, etc.)
        
        Returns:
            ConnectionType enum
        """
        # This is a simplified implementation
        # In production, you'd use platform-specific APIs
        
        if not self.check_internet_connectivity():
            return ConnectionType.UNKNOWN
        
        # Default to unknown - would need platform-specific detection
        self.current_connection = ConnectionType.UNKNOWN
        return self.current_connection
    
    def is_preferred_connection(self) -> bool:
        """
        Check if current connection matches preferred connection
        
        Returns:
            True if using preferred connection, False otherwise
        """
        if self.current_connection is None:
            self.detect_connection_type()
        
        if self.current_connection == ConnectionType.UNKNOWN:
            # If we can't detect, assume it's okay
            return True
        
        return self.current_connection.value == self.preferred_connection
    
    def get_connection_strength(self) -> int:
        """
        Get connection strength as percentage (0-100)
        
        Note: This would require platform-specific implementation
        
        Returns:
            Connection strength percentage
        """
        # Simplified implementation - would need platform-specific APIs
        if self.check_internet_connectivity():
            return 100  # Assume full strength if connected
        return 0
    
    async def wait_for_connection(self, timeout: int = 30, check_interval: int = 5) -> bool:
        """
        Wait for internet connection to be available
        
        Args:
            timeout: Maximum time to wait in seconds
            check_interval: Interval between checks in seconds
        
        Returns:
            True if connection is available, False if timeout
        """
        elapsed = 0
        while elapsed < timeout:
            if await self.check_connectivity_async():
                return True
            await asyncio.sleep(check_interval)
            elapsed += check_interval
        
        return False
    
    def __repr__(self) -> str:
        return f"<NetworkManager: preferred={self.preferred_connection}, current={self.current_connection}>"
