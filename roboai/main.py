"""Main entry point for ROBOAi Trading Platform"""

import asyncio
import sys
import signal
from typing import Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from roboai.utils import get_logger, get_config, get_database
from roboai.agents import (
    AgentManager,
    AuthAgent,
    DataAgent,
    MarketScannerAgent,
    SentimentAgent,
    StrategyAgent,
    ExecutionAgent,
    RCAAgent,
    PromptAgent
)


class ROBOAiPlatform:
    """Main ROBOAi Trading Platform"""
    
    def __init__(self):
        self.logger = get_logger("ROBOAi")
        self.config = get_config()
        self.database = get_database()
        self.agent_manager = AgentManager()
        
        self.auth_agent: Optional[AuthAgent] = None
        self.data_agent: Optional[DataAgent] = None
        self.market_scanner: Optional[MarketScannerAgent] = None
        self.sentiment_agent: Optional[SentimentAgent] = None
        self.strategy_agent: Optional[StrategyAgent] = None
        self.execution_agent: Optional[ExecutionAgent] = None
        self.rca_agent: Optional[RCAAgent] = None
        self.prompt_agent: Optional[PromptAgent] = None
        
        self._shutdown = False
    
    def display_banner(self) -> None:
        """Display startup banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              ROBOAi Trading Platform v1.0.0                  ║
║         AI-Powered Algorithmic Trading for NSE F&O           ║
║                                                              ║
║                   ⚠️  IMPORTANT NOTICE ⚠️                     ║
║                                                              ║
║  • This platform is currently in PAPER TRADING mode          ║
║  • No real trades will be executed                           ║
║  • Test thoroughly before enabling live trading              ║
║  • Trading involves substantial risk of loss                 ║
║  • Past performance is not indicative of future results      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def display_config_info(self) -> None:
        """Display configuration information"""
        mode = "PAPER TRADING" if self.config.is_paper_trading() else "LIVE TRADING"
        auto_trade = "ENABLED" if self.config.get('trading.auto_trade', False) else "DISABLED"
        
        print(f"\n📊 Configuration:")
        print(f"   Mode: {mode}")
        print(f"   Auto-Trade: {auto_trade}")
        print(f"   Max Positions: {self.config.get('trading.max_positions', 5)}")
        print(f"   Min Gain Target: ₹{self.config.get('trading.min_gain_target', 1000)}")
        print(f"   Scan Interval: {self.config.get('scanning.scan_interval', 60)}s")
        print(f"   Indices: {', '.join(self.config.get_indices())}")
        print()
    
    async def initialize_agents(self) -> bool:
        """Initialize all agents"""
        try:
            self.logger.info("Initializing agents...")
            
            # Validate config
            is_valid, errors = self.config.validate_config()
            if not is_valid:
                self.logger.error("Configuration validation failed:")
                for error in errors:
                    self.logger.error(f"  - {error}")
                
                # Allow continuing in paper trading mode even with missing API keys
                if not self.config.is_paper_trading():
                    return False
                else:
                    self.logger.warning("Continuing in paper trading mode without API credentials")
            
            # Initialize agents
            self.auth_agent = AuthAgent()
            self.agent_manager.register_agent(self.auth_agent)
            
            # Get mStock client (may be None in paper trading)
            mstock_client = None
            if not self.config.is_paper_trading():
                if await self.auth_agent.initialize():
                    mstock_client = self.auth_agent.get_client()
                else:
                    self.logger.error("Failed to initialize authentication")
                    return False
            
            self.data_agent = DataAgent(mstock_client)
            self.agent_manager.register_agent(self.data_agent)
            
            self.market_scanner = MarketScannerAgent(self.data_agent)
            self.agent_manager.register_agent(self.market_scanner)
            
            self.sentiment_agent = SentimentAgent()
            self.agent_manager.register_agent(self.sentiment_agent)
            
            self.strategy_agent = StrategyAgent()
            self.agent_manager.register_agent(self.strategy_agent)
            
            self.execution_agent = ExecutionAgent(mstock_client)
            self.agent_manager.register_agent(self.execution_agent)
            
            self.rca_agent = RCAAgent()
            self.agent_manager.register_agent(self.rca_agent)
            
            self.prompt_agent = PromptAgent()
            self.agent_manager.register_agent(self.prompt_agent)
            
            self.logger.info("All agents initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize agents: {e}")
            return False
    
    async def start(self) -> None:
        """Start the platform"""
        try:
            self.display_banner()
            self.display_config_info()
            
            self.logger.info("Starting ROBOAi Trading Platform...")
            
            # Initialize agents
            if not await self.initialize_agents():
                self.logger.error("Agent initialization failed. Exiting.")
                return
            
            # Start all agents
            await self.agent_manager.start_all()
            
            self.logger.info("✅ ROBOAi Platform is now running")
            self.logger.info("Press Ctrl+C to stop")
            
            # Main loop
            while not self._shutdown:
                await asyncio.sleep(1)
                
                # Display status periodically
                await self.display_status()
                await asyncio.sleep(30)
        
        except KeyboardInterrupt:
            self.logger.info("Shutdown signal received")
        except Exception as e:
            self.logger.exception(f"Error in main loop: {e}")
        finally:
            await self.shutdown()
    
    async def display_status(self) -> None:
        """Display platform status"""
        try:
            # Get agent statuses
            statuses = await self.agent_manager.get_all_status()
            
            # Display summary
            running = sum(1 for s in statuses.values() if s.get('is_running', False))
            total = len(statuses)
            
            self.logger.info(f"Status: {running}/{total} agents running")
            
            # Display PnL if available
            if self.execution_agent:
                pnl = self.execution_agent.get_pnl()
                self.logger.info(f"PnL: ₹{pnl.get('total_pnl', 0):.2f} (Daily: ₹{pnl.get('daily_pnl', 0):.2f})")
        
        except Exception as e:
            self.logger.error(f"Error displaying status: {e}")
    
    async def shutdown(self) -> None:
        """Shutdown the platform"""
        self.logger.info("Shutting down ROBOAi Platform...")
        self._shutdown = True
        
        try:
            # Stop all agents
            await self.agent_manager.stop_all()
            
            # Close database
            self.database.close()
            
            self.logger.info("✅ Shutdown complete")
        
        except Exception as e:
            self.logger.exception(f"Error during shutdown: {e}")
    
    def setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            self.logger.info(f"Signal {sig} received")
            self._shutdown = True
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)


async def async_main():
    """Async main function"""
    platform = ROBOAiPlatform()
    platform.setup_signal_handlers()
    await platform.start()


def main():
    """Main entry point"""
    try:
        # Run async main
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nShutdown complete. Goodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
