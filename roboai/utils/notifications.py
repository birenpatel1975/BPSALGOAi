"""Desktop Notifications Module"""

import platform
import logging
from typing import Optional


class NotificationManager:
    """
    Handle desktop notifications across platforms
    Windows: Uses Windows Toast notifications
    Linux: Uses notify-send
    macOS: Uses osascript
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ROBOAi")
        self.system = platform.system()
        self.enabled = True
        
        # Check if notifications are available
        self._check_availability()
    
    def _check_availability(self) -> None:
        """Check if notification system is available"""
        try:
            if self.system == "Windows":
                # Try importing win10toast for Windows
                try:
                    from win10toast import ToastNotifier
                    self.toaster = ToastNotifier()
                except ImportError:
                    self.logger.warning("win10toast not installed. Install with: pip install win10toast")
                    self.enabled = False
            elif self.system == "Linux":
                # Check if notify-send is available
                import subprocess
                result = subprocess.run(['which', 'notify-send'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning("notify-send not available on Linux")
                    self.enabled = False
            elif self.system == "Darwin":  # macOS
                # osascript is built-in on macOS
                pass
            else:
                self.logger.warning(f"Notifications not supported on {self.system}")
                self.enabled = False
                
        except Exception as e:
            self.logger.error(f"Error checking notification availability: {e}")
            self.enabled = False
    
    def send_notification(self, title: str, message: str, 
                         icon: Optional[str] = None,
                         duration: int = 5) -> bool:
        """
        Send desktop notification
        
        Args:
            title: Notification title
            message: Notification message
            icon: Path to icon file (optional)
            duration: Duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            self.logger.debug(f"Notification (disabled): {title} - {message}")
            return False
        
        try:
            if self.system == "Windows":
                return self._send_windows(title, message, icon, duration)
            elif self.system == "Linux":
                return self._send_linux(title, message, icon, duration)
            elif self.system == "Darwin":
                return self._send_macos(title, message, duration)
            return False
            
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")
            return False
    
    def _send_windows(self, title: str, message: str, 
                     icon: Optional[str], duration: int) -> bool:
        """Send Windows toast notification"""
        try:
            # Use threaded=True to avoid blocking
            self.toaster.show_toast(
                title=title,
                msg=message,
                icon_path=icon,
                duration=duration,
                threaded=True
            )
            return True
        except Exception as e:
            self.logger.error(f"Windows notification error: {e}")
            return False
    
    def _send_linux(self, title: str, message: str, 
                   icon: Optional[str], duration: int) -> bool:
        """Send Linux notification using notify-send"""
        try:
            import subprocess
            
            cmd = ['notify-send', title, message, '-t', str(duration * 1000)]
            if icon:
                cmd.extend(['-i', icon])
            
            subprocess.run(cmd, check=True)
            return True
            
        except Exception as e:
            self.logger.error(f"Linux notification error: {e}")
            return False
    
    def _send_macos(self, title: str, message: str, duration: int) -> bool:
        """Send macOS notification using osascript"""
        try:
            import subprocess
            
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=True)
            return True
            
        except Exception as e:
            self.logger.error(f"macOS notification error: {e}")
            return False
    
    def notify_trade_signal(self, symbol: str, signal: str, 
                           price: float, reason: str) -> bool:
        """
        Send trade signal notification
        
        Args:
            symbol: Trading symbol
            signal: BUY/SELL
            price: Entry price
            reason: Trade reason
            
        Returns:
            True if successful
        """
        title = f"🔔 Trade Signal: {signal} {symbol}"
        message = f"Price: ₹{price:.2f}\n{reason}"
        return self.send_notification(title, message, duration=10)
    
    def notify_order_filled(self, symbol: str, order_type: str, 
                           quantity: int, price: float) -> bool:
        """
        Send order filled notification
        
        Args:
            symbol: Trading symbol
            order_type: BUY/SELL
            quantity: Order quantity
            price: Fill price
            
        Returns:
            True if successful
        """
        title = f"✅ Order Filled: {order_type} {symbol}"
        message = f"Quantity: {quantity}\nPrice: ₹{price:.2f}"
        return self.send_notification(title, message, duration=8)
    
    def notify_stop_loss_hit(self, symbol: str, loss_amount: float) -> bool:
        """
        Send stop loss notification
        
        Args:
            symbol: Trading symbol
            loss_amount: Loss amount
            
        Returns:
            True if successful
        """
        title = f"🛑 Stop Loss Hit: {symbol}"
        message = f"Loss: ₹{loss_amount:.2f}\nPosition closed"
        return self.send_notification(title, message, duration=10)
    
    def notify_target_reached(self, symbol: str, profit_amount: float) -> bool:
        """
        Send target reached notification
        
        Args:
            symbol: Trading symbol
            profit_amount: Profit amount
            
        Returns:
            True if successful
        """
        title = f"🎯 Target Reached: {symbol}"
        message = f"Profit: ₹{profit_amount:.2f}\nPosition closed"
        return self.send_notification(title, message, duration=10)
    
    def notify_daily_pnl(self, pnl: float, trades: int) -> bool:
        """
        Send daily P&L summary notification
        
        Args:
            pnl: Daily profit/loss
            trades: Number of trades
            
        Returns:
            True if successful
        """
        emoji = "📈" if pnl >= 0 else "📉"
        title = f"{emoji} Daily P&L Summary"
        message = f"P&L: ₹{pnl:.2f}\nTrades: {trades}"
        return self.send_notification(title, message, duration=15)
    
    def notify_circuit_breaker(self, reason: str) -> bool:
        """
        Send circuit breaker notification
        
        Args:
            reason: Circuit breaker trigger reason
            
        Returns:
            True if successful
        """
        title = "⚠️ Circuit Breaker Activated"
        message = f"Trading stopped!\n{reason}"
        return self.send_notification(title, message, duration=15)
    
    def notify_error(self, error_type: str, message: str) -> bool:
        """
        Send error notification
        
        Args:
            error_type: Type of error
            message: Error message
            
        Returns:
            True if successful
        """
        title = f"❌ Error: {error_type}"
        return self.send_notification(title, message, duration=10)
    
    def enable(self) -> None:
        """Enable notifications"""
        self.enabled = True
        self.logger.info("Notifications enabled")
    
    def disable(self) -> None:
        """Disable notifications"""
        self.enabled = False
        self.logger.info("Notifications disabled")


# Global notification manager instance
_notification_manager: Optional[NotificationManager] = None


def get_notification_manager() -> NotificationManager:
    """
    Get or create notification manager singleton
    
    Returns:
        NotificationManager instance
    """
    global _notification_manager
    if _notification_manager is None:
        _notification_manager = NotificationManager()
    return _notification_manager
