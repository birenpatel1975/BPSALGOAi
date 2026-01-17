"""Prompt Injection Agent - Dynamic command interface"""

import asyncio
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from ..utils.logger import get_logger
from ..utils.config_manager import get_config
from ..utils.database import get_database


class PromptAgent(BaseAgent):
    """
    Agent for handling dynamic user prompts and commands
    Analyzes user input and creates actionable items
    """
    
    def __init__(self):
        super().__init__("PromptAgent")
        self.config = get_config()
        self.db = get_database()
        self.pending_prompts: List[Dict[str, Any]] = []
        self.processed_prompts: List[Dict[str, Any]] = []
        
        # Command patterns
        self.command_patterns = {
            'position_size': r'(?:increase|decrease|change|adjust|set)\s+position\s+size\s+(?:by\s+)?(\d+)%?',
            'add_filter': r'add\s+(\w+)\s*([<>=!]+)\s*(\d+)\s+filter',
            'avoid_sector': r'avoid\s+(\w+)\s+(?:stocks?|sector)',
            'strategy_param': r'set\s+(\w+)\s+(?:to\s+)?(\d+\.?\d*)',
            'enable_feature': r'enable\s+(\w+)',
            'disable_feature': r'disable\s+(\w+)',
            'max_loss': r'(?:set|change)\s+max\s+(?:daily\s+)?loss\s+(?:to\s+)?₹?(\d+)',
            'target_gain': r'(?:set|change)\s+(?:min\s+)?(?:gain\s+)?target\s+(?:to\s+)?₹?(\d+)'
        }
    
    async def initialize(self) -> bool:
        """Initialize the Prompt Agent"""
        self.logger.info(f"{self.name} initialized")
        await self._create_prompt_table()
        return True
    
    async def run(self) -> None:
        """Main agent loop"""
        self.logger.info(f"{self.name} started")
        
        while self.is_running:
            try:
                # Process pending prompts
                if self.pending_prompts:
                    await self._process_prompts()
                
                # Check database for new prompts from web UI
                await self._check_database_prompts()
                
                self.update_status("running")
                await asyncio.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Error in {self.name}: {e}")
                await asyncio.sleep(10)
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info(f"{self.name} stopping")
        self.is_running = False
    
    async def inject_prompt(self, prompt: str, source: str = "console") -> Dict[str, Any]:
        """
        Inject a new prompt for processing
        
        Args:
            prompt: User prompt/command
            source: Source of the prompt (console, web, api)
            
        Returns:
            Analysis result with action items
        """
        self.logger.info(f"New prompt from {source}: {prompt}")
        
        # Analyze the prompt
        analysis = await self._analyze_prompt(prompt)
        
        # Store in database
        await self._store_prompt(prompt, source, analysis)
        
        # Add to pending queue
        self.pending_prompts.append({
            'prompt': prompt,
            'source': source,
            'analysis': analysis,
            'timestamp': datetime.now()
        })
        
        return analysis
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze prompt and extract intent and parameters
        
        Args:
            prompt: User prompt
            
        Returns:
            Analysis result with action items
        """
        prompt_lower = prompt.lower()
        
        # Check for each command pattern
        for command_type, pattern in self.command_patterns.items():
            match = re.search(pattern, prompt_lower)
            if match:
                return await self._create_action_item(command_type, match, prompt)
        
        # If no pattern matches, create a general analysis
        return {
            'command_type': 'unknown',
            'action': 'ignore',
            'reason': 'Could not parse command. Please use specific command format.',
            'original_prompt': prompt,
            'suggestions': self._get_command_suggestions()
        }
    
    async def _create_action_item(self, command_type: str, match: re.Match, prompt: str) -> Dict[str, Any]:
        """
        Create action item from parsed command
        
        Args:
            command_type: Type of command
            match: Regex match object
            prompt: Original prompt
            
        Returns:
            Action item dictionary
        """
        action_item = {
            'command_type': command_type,
            'action': 'apply',
            'original_prompt': prompt,
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract parameters based on command type
        if command_type == 'position_size':
            action_item['parameters'] = {
                'adjustment': int(match.group(1)),
                'current_size': self.config.get('risk.max_position_size', 10000)
            }
            action_item['description'] = f"Adjust position size by {match.group(1)}%"
            
        elif command_type == 'add_filter':
            action_item['parameters'] = {
                'indicator': match.group(1).upper(),
                'operator': match.group(2),
                'threshold': float(match.group(3))
            }
            action_item['description'] = f"Add filter: {match.group(1)} {match.group(2)} {match.group(3)}"
            
        elif command_type == 'avoid_sector':
            action_item['parameters'] = {
                'sector': match.group(1).upper()
            }
            action_item['description'] = f"Avoid {match.group(1)} sector"
            
        elif command_type == 'strategy_param':
            action_item['parameters'] = {
                'param_name': match.group(1),
                'param_value': float(match.group(2))
            }
            action_item['description'] = f"Set {match.group(1)} to {match.group(2)}"
            
        elif command_type == 'enable_feature':
            action_item['parameters'] = {
                'feature': match.group(1)
            }
            action_item['description'] = f"Enable {match.group(1)} feature"
            
        elif command_type == 'disable_feature':
            action_item['parameters'] = {
                'feature': match.group(1)
            }
            action_item['description'] = f"Disable {match.group(1)} feature"
            
        elif command_type == 'max_loss':
            action_item['parameters'] = {
                'max_daily_loss': int(match.group(1))
            }
            action_item['description'] = f"Set max daily loss to ₹{match.group(1)}"
            
        elif command_type == 'target_gain':
            action_item['parameters'] = {
                'min_gain_target': int(match.group(1))
            }
            action_item['description'] = f"Set min gain target to ₹{match.group(1)}"
        
        # Add impact assessment
        action_item['impact'] = await self._assess_impact(action_item)
        
        return action_item
    
    async def _assess_impact(self, action_item: Dict[str, Any]) -> str:
        """
        Assess the impact of applying this command
        
        Args:
            action_item: Action item to assess
            
        Returns:
            Impact description
        """
        command_type = action_item.get('command_type')
        
        impact_map = {
            'position_size': 'This will affect risk per trade. Larger positions = higher risk/reward.',
            'add_filter': 'This will filter out trades that don\'t meet the condition.',
            'avoid_sector': 'This will skip all trades in this sector.',
            'max_loss': 'This will change the daily loss limit threshold.',
            'target_gain': 'This will filter trades below the minimum gain target.',
            'enable_feature': 'This will enable the specified feature.',
            'disable_feature': 'This will disable the specified feature.',
            'strategy_param': 'This will adjust strategy parameters.'
        }
        
        return impact_map.get(command_type, 'Impact unknown')
    
    async def _process_prompts(self) -> None:
        """Process pending prompts"""
        while self.pending_prompts:
            prompt_data = self.pending_prompts.pop(0)
            analysis = prompt_data['analysis']
            
            if analysis.get('action') == 'apply':
                # Apply the command
                applied = await self._apply_command(analysis)
                
                if applied:
                    self.logger.info(f"Applied command: {analysis.get('description')}")
                    prompt_data['status'] = 'applied'
                else:
                    self.logger.warning(f"Failed to apply command: {analysis.get('description')}")
                    prompt_data['status'] = 'failed'
            else:
                self.logger.info(f"Ignored command: {prompt_data['prompt']}")
                prompt_data['status'] = 'ignored'
            
            self.processed_prompts.append(prompt_data)
            
            # Keep only last 100 processed prompts
            if len(self.processed_prompts) > 100:
                self.processed_prompts.pop(0)
    
    async def _apply_command(self, action_item: Dict[str, Any]) -> bool:
        """
        Apply the command by updating configuration
        
        Args:
            action_item: Action item to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            command_type = action_item.get('command_type')
            parameters = action_item.get('parameters', {})
            
            if command_type == 'position_size':
                adjustment = parameters['adjustment']
                current = parameters['current_size']
                new_size = current * (1 + adjustment / 100)
                self.config.set('risk.max_position_size', int(new_size))
                
            elif command_type == 'add_filter':
                # Store filter in database for strategy agent to use
                await self._store_filter(parameters)
                
            elif command_type == 'avoid_sector':
                # Add to excluded sectors list
                await self._add_excluded_sector(parameters['sector'])
                
            elif command_type == 'max_loss':
                self.config.set('risk.max_daily_loss', parameters['max_daily_loss'])
                
            elif command_type == 'target_gain':
                self.config.set('trading.min_gain_target', parameters['min_gain_target'])
                
            elif command_type == 'enable_feature' or command_type == 'disable_feature':
                feature = parameters['feature']
                enabled = command_type == 'enable_feature'
                await self._toggle_feature(feature, enabled)
                
            elif command_type == 'strategy_param':
                param_name = parameters['param_name']
                param_value = parameters['param_value']
                self.config.set(f'strategy.{param_name}', param_value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying command: {e}")
            return False
    
    async def _store_filter(self, filter_params: Dict[str, Any]) -> None:
        """Store filter in database"""
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO prompt_filters (indicator, operator, threshold, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    filter_params['indicator'],
                    filter_params['operator'],
                    filter_params['threshold'],
                    datetime.now().isoformat()
                )
            )
            await conn.commit()
    
    async def _add_excluded_sector(self, sector: str) -> None:
        """Add sector to exclusion list"""
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO excluded_sectors (sector, created_at)
                VALUES (?, ?)
                """,
                (sector, datetime.now().isoformat())
            )
            await conn.commit()
    
    async def _toggle_feature(self, feature: str, enabled: bool) -> None:
        """Toggle feature on/off"""
        # Map feature names to config keys
        feature_map = {
            'auto_trade': 'trading.auto_trade',
            'sentiment': 'sentiment.enabled',
            'rca': 'rca.enabled',
            'alerts': 'alerts.enabled'
        }
        
        config_key = feature_map.get(feature)
        if config_key:
            self.config.set(config_key, enabled)
    
    async def _check_database_prompts(self) -> None:
        """Check database for new prompts from web UI"""
        try:
            async with self.db.get_connection() as conn:
                cursor = await conn.execute(
                    """
                    SELECT id, prompt, source, created_at
                    FROM user_prompts
                    WHERE status = 'pending'
                    ORDER BY created_at ASC
                    LIMIT 10
                    """
                )
                rows = await cursor.fetchall()
                
                for row in rows:
                    prompt_id, prompt, source, created_at = row
                    await self.inject_prompt(prompt, source)
                    
                    # Mark as processing
                    await conn.execute(
                        "UPDATE user_prompts SET status = 'processing' WHERE id = ?",
                        (prompt_id,)
                    )
                    await conn.commit()
                    
        except Exception as e:
            self.logger.debug(f"Could not check database prompts: {e}")
    
    async def _store_prompt(self, prompt: str, source: str, analysis: Dict[str, Any]) -> None:
        """Store prompt and analysis in database"""
        try:
            async with self.db.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO prompt_history 
                    (prompt, source, command_type, action, description, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        prompt,
                        source,
                        analysis.get('command_type', 'unknown'),
                        analysis.get('action', 'ignore'),
                        analysis.get('description', ''),
                        datetime.now().isoformat()
                    )
                )
                await conn.commit()
        except Exception as e:
            self.logger.debug(f"Could not store prompt: {e}")
    
    async def _create_prompt_table(self) -> None:
        """Create tables for prompt management"""
        try:
            async with self.db.get_connection() as conn:
                # Prompt history table
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prompt_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt TEXT NOT NULL,
                        source TEXT NOT NULL,
                        command_type TEXT,
                        action TEXT,
                        description TEXT,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                
                # User prompts (from web UI)
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt TEXT NOT NULL,
                        source TEXT NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at TEXT NOT NULL
                    )
                    """
                )
                
                # Filters table
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS prompt_filters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        indicator TEXT NOT NULL,
                        operator TEXT NOT NULL,
                        threshold REAL NOT NULL,
                        active INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                
                # Excluded sectors table
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS excluded_sectors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sector TEXT NOT NULL UNIQUE,
                        active INTEGER DEFAULT 1,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                
                await conn.commit()
        except Exception as e:
            self.logger.debug(f"Could not create prompt tables: {e}")
    
    def _get_command_suggestions(self) -> List[str]:
        """Get list of supported commands"""
        return [
            "Increase position size by 20%",
            "Add RSI > 70 filter",
            "Avoid banking stocks",
            "Set max daily loss to 5000",
            "Set min gain target to 1000",
            "Enable auto_trade",
            "Disable sentiment",
            "Set stop_loss_percent to 2"
        ]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'name': self.name,
            'status': self.status,
            'is_running': self.is_running,
            'pending_prompts': len(self.pending_prompts),
            'processed_prompts': len(self.processed_prompts),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
