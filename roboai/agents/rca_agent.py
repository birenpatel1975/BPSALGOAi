"""RCA Agent - Root Cause Analysis Engine"""

import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from ..utils.database import get_database


class RCAAgent(BaseAgent):
    """Performs post-trade analysis and strategy refinement"""
    
    def __init__(self):
        super().__init__("RCAAgent")
        self.database = get_database()
        self.analysis_queue: List[str] = []  # Queue of trade_ids to analyze
    
    async def initialize(self) -> bool:
        """Initialize RCA agent"""
        try:
            self.logger.info("RCAAgent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize RCAAgent: {e}")
            return False
    
    def queue_trade_analysis(self, trade_id: str) -> None:
        """
        Queue a trade for analysis
        
        Args:
            trade_id: Trade ID to analyze
        """
        if trade_id not in self.analysis_queue:
            self.analysis_queue.append(trade_id)
            self.logger.info(f"Queued trade for RCA: {trade_id}")
    
    async def analyze_trade(self, trade_id: str) -> Dict[str, Any]:
        """
        Analyze a completed trade
        
        Args:
            trade_id: Trade ID to analyze
        
        Returns:
            Analysis results
        """
        try:
            # Get trade details from database
            trades = self.database.get_trades()
            trade = next((t for t in trades if t['trade_id'] == trade_id), None)
            
            if not trade:
                self.logger.error(f"Trade not found: {trade_id}")
                return {}
            
            # Perform analysis
            analysis = {
                "trade_id": trade_id,
                "symbol": trade['symbol'],
                "pnl": trade.get('pnl', 0),
                "analysis": {},
                "recommendations": [],
                "adjustments": []
            }
            
            # Analyze outcome
            pnl = trade.get('pnl', 0)
            
            if pnl > 0:
                analysis['analysis']['outcome'] = 'PROFIT'
                analysis['analysis']['success_factors'] = self._identify_success_factors(trade)
            else:
                analysis['analysis']['outcome'] = 'LOSS'
                analysis['analysis']['failure_factors'] = self._identify_failure_factors(trade)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(trade, analysis['analysis'])
            
            # Generate strategy adjustments
            analysis['adjustments'] = self._generate_adjustments(trade, analysis['analysis'])
            
            # Store analysis
            self.database.insert_rca_log(trade_id, analysis)
            
            self.logger.info(f"Completed RCA for trade {trade_id}: {analysis['analysis']['outcome']}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze trade {trade_id}: {e}")
            return {}
    
    def _identify_success_factors(self, trade: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to success"""
        factors = []
        
        # Example analysis - would be more sophisticated in production
        strategy = trade.get('strategy', '')
        
        if 'momentum' in strategy.lower():
            factors.append("Momentum strategy worked well")
        
        if trade.get('entry_price', 0) < trade.get('exit_price', 0):
            factors.append("Good entry timing")
        
        factors.append("Market conditions were favorable")
        
        return factors
    
    def _identify_failure_factors(self, trade: Dict[str, Any]) -> List[str]:
        """Identify factors that contributed to failure"""
        factors = []
        
        # Example analysis
        pnl = trade.get('pnl', 0)
        
        if pnl < -500:
            factors.append("Significant loss - stop loss may have been too wide")
        
        entry_price = trade.get('entry_price', 0)
        exit_price = trade.get('exit_price', 0)
        
        if exit_price < entry_price:
            factors.append("Adverse price movement - entry timing may have been premature")
        
        factors.append("Consider market conditions before entry")
        
        return factors
    
    def _generate_recommendations(self, trade: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        outcome = analysis.get('outcome')
        
        if outcome == 'LOSS':
            recommendations.append("Review entry conditions for this strategy")
            recommendations.append("Consider tighter stop loss levels")
            recommendations.append("Increase confirmation signals required before entry")
        else:
            recommendations.append("Continue using this strategy for similar setups")
            recommendations.append("Consider increasing position size for high-confidence setups")
        
        return recommendations
    
    def _generate_adjustments(self, trade: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate strategy parameter adjustments"""
        adjustments = []
        
        outcome = analysis.get('outcome')
        pnl = trade.get('pnl', 0)
        
        # Example adjustments
        if outcome == 'LOSS' and pnl < -300:
            adjustments.append({
                "parameter": "stop_loss_percent",
                "current_value": 2.0,
                "suggested_value": 1.5,
                "reason": "Reduce stop loss to limit downside"
            })
        
        if outcome == 'PROFIT' and pnl > 1000:
            adjustments.append({
                "parameter": "min_gain_target",
                "current_value": 1000,
                "suggested_value": 1200,
                "reason": "Increase target based on recent success"
            })
        
        return adjustments
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary
        
        Returns:
            Performance metrics
        """
        try:
            pnl_summary = self.database.get_pnl_summary()
            
            win_rate = 0
            if pnl_summary.get('total_trades', 0) > 0:
                win_rate = (pnl_summary.get('winning_trades', 0) / pnl_summary['total_trades']) * 100
            
            return {
                "total_trades": pnl_summary.get('total_trades', 0),
                "winning_trades": pnl_summary.get('winning_trades', 0),
                "losing_trades": pnl_summary.get('losing_trades', 0),
                "win_rate": round(win_rate, 2),
                "total_pnl": pnl_summary.get('total_pnl', 0),
                "avg_pnl": pnl_summary.get('avg_pnl', 0),
                "max_profit": pnl_summary.get('max_profit', 0),
                "max_loss": pnl_summary.get('max_loss', 0)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    async def run(self) -> None:
        """Main agent loop"""
        self.update_status("running")
        
        try:
            while self.is_running:
                # Process analysis queue
                if self.analysis_queue:
                    trade_id = self.analysis_queue.pop(0)
                    await self.analyze_trade(trade_id)
                
                await asyncio.sleep(30)  # Check queue every 30 seconds
        
        except asyncio.CancelledError:
            self.logger.info("RCAAgent run loop cancelled")
        except Exception as e:
            self.logger.exception(f"Error in RCAAgent run loop: {e}")
        finally:
            self.update_status("stopped")
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info("Stopping RCAAgent")
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.update_status("stopped")
