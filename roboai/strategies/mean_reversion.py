"""Mean Reversion Trading Strategy"""

from typing import Dict, Any, Optional
from datetime import datetime
import pandas as pd
import numpy as np


class MeanReversionStrategy:
    """
    Mean reversion strategy
    Identifies when price deviates significantly from mean and likely to revert
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize mean reversion strategy
        
        Args:
            config: Strategy configuration
        """
        self.config = config
        self.lookback_period = config.get('mean_reversion_period', 20)
        self.std_threshold = config.get('mean_reversion_std', 2.0)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.rsi_overbought = config.get('rsi_overbought', 70)
    
    def analyze(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        Analyze data for mean reversion opportunities
        
        Args:
            data: OHLCV data with columns: open, high, low, close, volume
            
        Returns:
            Signal dictionary if opportunity found, None otherwise
        """
        if len(data) < self.lookback_period + 14:  # Need extra for RSI
            return None
        
        try:
            # Calculate Bollinger Bands
            sma = data['close'].rolling(window=self.lookback_period).mean()
            std = data['close'].rolling(window=self.lookback_period).std()
            
            upper_band = sma + (std * self.std_threshold)
            lower_band = sma - (std * self.std_threshold)
            
            current_price = data['close'].iloc[-1]
            current_sma = sma.iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            
            # Calculate RSI
            rsi = self._calculate_rsi(data['close'])
            current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # Check for oversold condition (buy signal)
            if current_price < current_lower and current_rsi < self.rsi_oversold:
                distance_from_mean = ((current_sma - current_price) / current_price) * 100
                
                return {
                    'signal': 'BUY',
                    'strategy': 'MeanReversion',
                    'entry_price': current_price,
                    'stop_loss': current_price - (current_price - current_lower) * 0.5,
                    'target': current_sma,  # Mean price as target
                    'reason': f'Oversold condition: Price {distance_from_mean:.2f}% below mean, RSI {current_rsi:.1f}',
                    'rsi': current_rsi,
                    'bollinger_position': 'below_lower',
                    'mean_price': current_sma,
                    'distance_from_mean': distance_from_mean,
                    'confidence': self._calculate_confidence(current_price, current_lower, current_sma, current_rsi, 'oversold')
                }
            
            # Check for overbought condition (sell signal)
            elif current_price > current_upper and current_rsi > self.rsi_overbought:
                distance_from_mean = ((current_price - current_sma) / current_price) * 100
                
                return {
                    'signal': 'SELL',
                    'strategy': 'MeanReversion',
                    'entry_price': current_price,
                    'stop_loss': current_price + (current_upper - current_price) * 0.5,
                    'target': current_sma,  # Mean price as target
                    'reason': f'Overbought condition: Price {distance_from_mean:.2f}% above mean, RSI {current_rsi:.1f}',
                    'rsi': current_rsi,
                    'bollinger_position': 'above_upper',
                    'mean_price': current_sma,
                    'distance_from_mean': distance_from_mean,
                    'confidence': self._calculate_confidence(current_price, current_upper, current_sma, current_rsi, 'overbought')
                }
            
            return None
            
        except Exception as e:
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_confidence(self, current_price: float, band: float, mean: float, 
                             rsi: float, condition: str) -> float:
        """Calculate confidence score (0-100)"""
        confidence = 50.0
        
        # RSI strength
        if condition == 'oversold':
            if rsi < 20:
                confidence += 25
            elif rsi < 30:
                confidence += 15
            
            # Distance from mean
            distance_pct = abs((current_price - mean) / mean) * 100
            if distance_pct > 5:
                confidence += 20
            elif distance_pct > 3:
                confidence += 10
            
        elif condition == 'overbought':
            if rsi > 80:
                confidence += 25
            elif rsi > 70:
                confidence += 15
            
            # Distance from mean
            distance_pct = abs((current_price - mean) / mean) * 100
            if distance_pct > 5:
                confidence += 20
            elif distance_pct > 3:
                confidence += 10
        
        return min(confidence, 100.0)
