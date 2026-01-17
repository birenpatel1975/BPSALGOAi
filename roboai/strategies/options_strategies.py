"""Options Trading Strategies"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd


class OptionsStrategies:
    """
    Options trading strategies including:
    - Iron Condor
    - Straddle
    - Strangle
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize options strategies
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.min_iv = config.get('min_iv', 15)
        self.max_iv = config.get('max_iv', 40)
        self.min_days_to_expiry = config.get('min_days_to_expiry', 7)
        self.max_days_to_expiry = config.get('max_days_to_expiry', 30)
    
    def analyze_iron_condor(self, underlying_price: float, options_chain: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze for Iron Condor opportunity
        Sell OTM call and put, buy further OTM call and put
        Best in low volatility, range-bound market
        
        Args:
            underlying_price: Current price of underlying
            options_chain: Options chain data
            
        Returns:
            Signal dictionary if opportunity found, None otherwise
        """
        try:
            # Iron Condor is profitable in range-bound markets
            # We need IV to be moderate and price to be stable
            
            iv = options_chain.get('implied_volatility', 0)
            
            # Check if IV is in acceptable range
            if not (self.min_iv <= iv <= self.max_iv):
                return None
            
            # Select strikes (example: ATM ± 5% for short, ± 10% for long)
            atm_call_strike = underlying_price * 1.05
            atm_put_strike = underlying_price * 0.95
            otm_call_strike = underlying_price * 1.10
            otm_put_strike = underlying_price * 0.90
            
            # Calculate potential profit and loss
            premium_collected = self._estimate_premium(underlying_price, atm_call_strike, 'call') + \
                              self._estimate_premium(underlying_price, atm_put_strike, 'put')
            premium_paid = self._estimate_premium(underlying_price, otm_call_strike, 'call') + \
                          self._estimate_premium(underlying_price, otm_put_strike, 'put')
            
            max_profit = premium_collected - premium_paid
            max_loss = (atm_call_strike - otm_call_strike) - max_profit
            
            # Only execute if risk-reward is favorable
            if max_profit / abs(max_loss) < 0.25:  # At least 25% return on risk
                return None
            
            return {
                'signal': 'IRON_CONDOR',
                'strategy': 'IronCondor',
                'underlying_price': underlying_price,
                'legs': [
                    {'action': 'SELL', 'strike': atm_call_strike, 'type': 'CALL'},
                    {'action': 'SELL', 'strike': atm_put_strike, 'type': 'PUT'},
                    {'action': 'BUY', 'strike': otm_call_strike, 'type': 'CALL'},
                    {'action': 'BUY', 'strike': otm_put_strike, 'type': 'PUT'}
                ],
                'max_profit': max_profit,
                'max_loss': max_loss,
                'risk_reward': max_profit / abs(max_loss),
                'iv': iv,
                'reason': f'Iron Condor setup in range-bound market with IV {iv:.1f}%',
                'confidence': self._calculate_condor_confidence(iv, underlying_price)
            }
            
        except Exception as e:
            return None
    
    def analyze_straddle(self, underlying_price: float, options_chain: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze for Long Straddle opportunity
        Buy ATM call and put
        Best when expecting high volatility but uncertain of direction
        
        Args:
            underlying_price: Current price of underlying
            options_chain: Options chain data
            
        Returns:
            Signal dictionary if opportunity found, None otherwise
        """
        try:
            iv = options_chain.get('implied_volatility', 0)
            historical_vol = options_chain.get('historical_volatility', 0)
            
            # Straddle is good when expecting volatility increase
            # Current IV should be low, expecting to increase
            if iv > 30:  # IV too high
                return None
            
            if historical_vol > iv * 1.2:  # Historical vol much higher than implied
                # Market expects low volatility but history suggests otherwise
                pass
            else:
                return None
            
            atm_strike = round(underlying_price / 50) * 50  # Round to nearest 50
            
            call_premium = self._estimate_premium(underlying_price, atm_strike, 'call')
            put_premium = self._estimate_premium(underlying_price, atm_strike, 'put')
            
            total_cost = call_premium + put_premium
            breakeven_upper = atm_strike + total_cost
            breakeven_lower = atm_strike - total_cost
            
            return {
                'signal': 'LONG_STRADDLE',
                'strategy': 'Straddle',
                'underlying_price': underlying_price,
                'legs': [
                    {'action': 'BUY', 'strike': atm_strike, 'type': 'CALL'},
                    {'action': 'BUY', 'strike': atm_strike, 'type': 'PUT'}
                ],
                'total_cost': total_cost,
                'breakeven_upper': breakeven_upper,
                'breakeven_lower': breakeven_lower,
                'required_move': (total_cost / underlying_price) * 100,
                'iv': iv,
                'historical_vol': historical_vol,
                'reason': f'Long Straddle: Low IV {iv:.1f}% vs Historical {historical_vol:.1f}%',
                'confidence': self._calculate_straddle_confidence(iv, historical_vol)
            }
            
        except Exception as e:
            return None
    
    def analyze_strangle(self, underlying_price: float, options_chain: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze for Long Strangle opportunity
        Buy OTM call and put
        Similar to straddle but cheaper, needs bigger move
        
        Args:
            underlying_price: Current price of underlying
            options_chain: Options chain data
            
        Returns:
            Signal dictionary if opportunity found, None otherwise
        """
        try:
            iv = options_chain.get('implied_volatility', 0)
            historical_vol = options_chain.get('historical_volatility', 0)
            
            # Similar conditions to straddle but cheaper entry
            if iv > 25:
                return None
            
            if historical_vol <= iv * 1.15:
                return None
            
            # OTM strikes (2-3% away from ATM)
            call_strike = underlying_price * 1.025
            put_strike = underlying_price * 0.975
            
            call_premium = self._estimate_premium(underlying_price, call_strike, 'call')
            put_premium = self._estimate_premium(underlying_price, put_strike, 'put')
            
            total_cost = call_premium + put_premium
            breakeven_upper = call_strike + total_cost
            breakeven_lower = put_strike - total_cost
            
            return {
                'signal': 'LONG_STRANGLE',
                'strategy': 'Strangle',
                'underlying_price': underlying_price,
                'legs': [
                    {'action': 'BUY', 'strike': call_strike, 'type': 'CALL'},
                    {'action': 'BUY', 'strike': put_strike, 'type': 'PUT'}
                ],
                'total_cost': total_cost,
                'breakeven_upper': breakeven_upper,
                'breakeven_lower': breakeven_lower,
                'required_move': (total_cost / underlying_price) * 100,
                'iv': iv,
                'historical_vol': historical_vol,
                'reason': f'Long Strangle: Low IV {iv:.1f}%, cheaper than straddle',
                'confidence': self._calculate_strangle_confidence(iv, historical_vol)
            }
            
        except Exception as e:
            return None
    
    def _estimate_premium(self, spot: float, strike: float, option_type: str) -> float:
        """
        Estimate option premium (simplified Black-Scholes approximation)
        In production, use actual market prices from options chain
        """
        # Simplified estimation for demonstration
        intrinsic_value = max(0, spot - strike) if option_type == 'call' else max(0, strike - spot)
        time_value = abs(spot - strike) * 0.05  # Rough approximation
        
        return intrinsic_value + time_value
    
    def _calculate_condor_confidence(self, iv: float, price: float) -> float:
        """Calculate Iron Condor confidence score"""
        confidence = 50.0
        
        # IV in sweet spot (20-30%)
        if 20 <= iv <= 30:
            confidence += 30
        elif 15 <= iv <= 35:
            confidence += 15
        
        # Additional factors could include:
        # - Price stability over last few days
        # - Volume profile
        # - Market regime
        
        return min(confidence, 100.0)
    
    def _calculate_straddle_confidence(self, iv: float, historical_vol: float) -> float:
        """Calculate Straddle confidence score"""
        confidence = 50.0
        
        # Large gap between historical and implied volatility
        vol_gap = (historical_vol - iv) / iv
        if vol_gap > 0.3:
            confidence += 30
        elif vol_gap > 0.2:
            confidence += 20
        
        # Low current IV
        if iv < 15:
            confidence += 20
        elif iv < 20:
            confidence += 10
        
        return min(confidence, 100.0)
    
    def _calculate_strangle_confidence(self, iv: float, historical_vol: float) -> float:
        """Calculate Strangle confidence score"""
        # Similar to straddle but slightly lower confidence due to wider strikes
        confidence = self._calculate_straddle_confidence(iv, historical_vol)
        return max(confidence - 10, 0)
