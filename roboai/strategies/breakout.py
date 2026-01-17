"""Breakout Trading Strategy"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd


class BreakoutStrategy:
    """
    Breakout trading strategy
    Identifies when price breaks above resistance or below support with volume
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize breakout strategy
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.lookback_period = config.get('breakout_lookback', 20)
        self.volume_threshold = config.get('breakout_volume_multiplier', 1.5)
        self.atr_multiplier = config.get('breakout_atr_multiplier', 1.5)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Analyze data for breakout opportunities
        
        Args:
            data: OHLCV data with columns: open, high, low, close, volume
            
        Returns:
            Signal dictionary if opportunity found, None otherwise
        """
        if len(data) < self.lookback_period:
            return None
        
        try:
            # Calculate resistance and support
            resistance = data['high'].rolling(window=self.lookback_period).max().iloc[-1]
            support = data['low'].rolling(window=self.lookback_period).min().iloc[-1]
            
            current_price = data['close'].iloc[-1]
            current_volume = data['volume'].iloc[-1]
            avg_volume = data['volume'].rolling(window=self.lookback_period).mean().iloc[-1]
            
            # Calculate ATR for stop loss
            atr = self._calculate_atr(data)
            
            # Check for bullish breakout
            if current_price > resistance and current_volume > (avg_volume * self.volume_threshold):
                return {
                    'signal': 'BUY',
                    'strategy': 'Breakout',
                    'entry_price': current_price,
                    'stop_loss': current_price - (atr * self.atr_multiplier),
                    'target': current_price + (atr * self.atr_multiplier * 2),
                    'reason': f'Bullish breakout above resistance {resistance:.2f} with high volume',
                    'resistance': resistance,
                    'support': support,
                    'volume_ratio': current_volume / avg_volume,
                    'confidence': self._calculate_confidence(data, 'bullish')
                }
            
            # Check for bearish breakout (for shorting or PE buying)
            elif current_price < support and current_volume > (avg_volume * self.volume_threshold):
                return {
                    'signal': 'SELL',
                    'strategy': 'Breakout',
                    'entry_price': current_price,
                    'stop_loss': current_price + (atr * self.atr_multiplier),
                    'target': current_price - (atr * self.atr_multiplier * 2),
                    'reason': f'Bearish breakdown below support {support:.2f} with high volume',
                    'resistance': resistance,
                    'support': support,
                    'volume_ratio': current_volume / avg_volume,
                    'confidence': self._calculate_confidence(data, 'bearish')
                }
            
            return None
            
        except Exception as e:
            return None
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr if pd.notna(atr) else 0
    
    def _calculate_confidence(self, data: pd.DataFrame, direction: str) -> float:
        """Calculate confidence score (0-100)"""
        confidence = 50.0
        
        # Volume confirmation
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        if current_volume > avg_volume * 2:
            confidence += 20
        elif current_volume > avg_volume * 1.5:
            confidence += 10
        
        # Trend confirmation
        sma_short = data['close'].rolling(window=10).mean().iloc[-1]
        sma_long = data['close'].rolling(window=20).mean().iloc[-1]
        
        if direction == 'bullish' and sma_short > sma_long:
            confidence += 15
        elif direction == 'bearish' and sma_short < sma_long:
            confidence += 15
        
        # Price action strength
        price_change = abs((data['close'].iloc[-1] - data['close'].iloc[-5]) / data['close'].iloc[-5])
        if price_change > 0.02:  # 2% move
            confidence += 15
        
        return min(confidence, 100.0)
