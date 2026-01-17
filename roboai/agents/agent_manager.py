"""Agent Manager - Orchestrates all agents"""

import asyncio
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from ..utils.logger import get_logger


class AgentManager:
    """Manages and orchestrates all trading agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = get_logger()
        self.is_running = False
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the manager
        
        Args:
            agent: Agent to register
        """
        if agent.name in self.agents:
            self.logger.warning(f"Agent {agent.name} already registered, overwriting")
        
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Get agent by name
        
        Args:
            name: Agent name
        
        Returns:
            Agent instance or None
        """
        return self.agents.get(name)
    
    async def start_all(self) -> None:
        """Start all registered agents"""
        self.logger.info("Starting all agents...")
        self.is_running = True
        
        for name, agent in self.agents.items():
            try:
                await agent.start()
            except Exception as e:
                self.logger.error(f"Failed to start agent {name}: {e}")
    
    async def stop_all(self) -> None:
        """Stop all registered agents"""
        self.logger.info("Stopping all agents...")
        self.is_running = False
        
        for name, agent in self.agents.items():
            try:
                await agent.stop()
            except Exception as e:
                self.logger.error(f"Failed to stop agent {name}: {e}")
    
    async def start_agent(self, name: str) -> bool:
        """
        Start a specific agent
        
        Args:
            name: Agent name
        
        Returns:
            True if started successfully, False otherwise
        """
        agent = self.get_agent(name)
        if agent is None:
            self.logger.error(f"Agent not found: {name}")
            return False
        
        try:
            await agent.start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to start agent {name}: {e}")
            return False
    
    async def stop_agent(self, name: str) -> bool:
        """
        Stop a specific agent
        
        Args:
            name: Agent name
        
        Returns:
            True if stopped successfully, False otherwise
        """
        agent = self.get_agent(name)
        if agent is None:
            self.logger.error(f"Agent not found: {name}")
            return False
        
        try:
            await agent.stop()
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop agent {name}: {e}")
            return False
    
    async def get_all_status(self) -> Dict[str, Any]:
        """
        Get status of all agents
        
        Returns:
            Dictionary with agent statuses
        """
        statuses = {}
        for name, agent in self.agents.items():
            try:
                statuses[name] = await agent.health_check()
            except Exception as e:
                statuses[name] = {"error": str(e)}
        
        return statuses
    
    def list_agents(self) -> List[str]:
        """
        List all registered agents
        
        Returns:
            List of agent names
        """
        return list(self.agents.keys())
    
    async def send_message(self, from_agent: str, to_agent: str, message: Any) -> bool:
        """
        Send message between agents (for future inter-agent communication)
        
        Args:
            from_agent: Source agent name
            to_agent: Destination agent name
            message: Message to send
        
        Returns:
            True if successful, False otherwise
        """
        target = self.get_agent(to_agent)
        if target is None:
            self.logger.error(f"Target agent not found: {to_agent}")
            return False
        
        self.logger.debug(f"Message from {from_agent} to {to_agent}: {message}")
        # Implement message passing logic here
        return True
    
    def __repr__(self) -> str:
        agent_list = ", ".join(self.agents.keys())
        return f"<AgentManager: {len(self.agents)} agents [{agent_list}]>"
