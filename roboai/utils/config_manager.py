"""Configuration Manager for ROBOAi"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            # Try to use example config
            example_config = Path("config.example.yaml")
            if example_config.exists():
                print(f"Warning: {self.config_path} not found. Creating from example...")
                import shutil
                shutil.copy(example_config, self.config_path)
            else:
                raise FileNotFoundError(
                    f"Configuration file not found: {self.config_path}\n"
                    "Please create config.yaml from config.example.yaml"
                )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        Example: get('trading.mode')
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        Example: set('trading.mode', 'paper')
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self) -> None:
        """Save configuration to YAML file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            raise IOError(f"Failed to save configuration: {e}")
    
    def validate_config(self) -> tuple[bool, list[str]]:
        """
        Validate configuration
        Returns: (is_valid, list of errors)
        """
        errors = []
        
        # Check required mStock fields
        required_mstock_fields = ['api_key', 'api_secret', 'totp_secret']
        for field in required_mstock_fields:
            value = self.get(f'mstock.{field}', '')
            if not value or value == '':
                errors.append(f"Missing mStock configuration: {field}")
        
        # Check trading mode
        trading_mode = self.get('trading.mode', 'paper')
        if trading_mode not in ['paper', 'live']:
            errors.append(f"Invalid trading mode: {trading_mode}. Must be 'paper' or 'live'")
        
        # Validate numeric values
        min_gain = self.get('trading.min_gain_target', 0)
        if not isinstance(min_gain, (int, float)) or min_gain <= 0:
            errors.append("trading.min_gain_target must be a positive number")
        
        max_positions = self.get('trading.max_positions', 0)
        if not isinstance(max_positions, int) or max_positions <= 0:
            errors.append("trading.max_positions must be a positive integer")
        
        return len(errors) == 0, errors
    
    def is_paper_trading(self) -> bool:
        """Check if in paper trading mode"""
        return self.get('trading.mode', 'paper') == 'paper'
    
    def is_live_trading(self) -> bool:
        """Check if in live trading mode"""
        return self.get('trading.mode', 'paper') == 'live'
    
    def get_market_hours(self) -> tuple[str, str]:
        """Get market opening and closing hours"""
        start = self.get('scanning.market_hours.start', '09:15')
        end = self.get('scanning.market_hours.end', '15:30')
        return start, end
    
    def get_indices(self) -> list[str]:
        """Get list of indices to monitor"""
        return self.get('markets.indices', [])
    
    def __repr__(self) -> str:
        return f"<ConfigManager: {self.config_path}>"


# Global config instance
_config: Optional[ConfigManager] = None


def get_config(config_path: str = "config.yaml") -> ConfigManager:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = ConfigManager(config_path)
    return _config
