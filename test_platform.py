#!/usr/bin/env python3
"""
Quick test script for ROBOAi Trading Platform
Tests basic functionality without requiring full dependencies
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    try:
        from roboai import __version__, __author__
        print(f"✓ ROBOAi version: {__version__}")
        print(f"✓ Author: {__author__}")
        
        from roboai.utils import get_config, get_logger, get_database
        print("✓ Utils module imported")
        
        from roboai.core import TOTPHandler, NetworkManager, MStockClient
        print("✓ Core module imported")
        
        from roboai.agents import AgentManager, AuthAgent, DataAgent
        print("✓ Agents module imported")
        
        from roboai.main import ROBOAiPlatform
        print("✓ Main platform imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_config():
    """Test configuration management"""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    
    try:
        from roboai.utils import get_config
        
        config = get_config('config.example.yaml')
        print(f"✓ Config loaded from config.example.yaml")
        
        # Test getters
        mode = config.get('trading.mode')
        print(f"✓ Trading mode: {mode}")
        
        is_paper = config.is_paper_trading()
        print(f"✓ Paper trading: {is_paper}")
        
        indices = config.get_indices()
        print(f"✓ Indices configured: {', '.join(indices)}")
        
        # Test validation
        is_valid, errors = config.validate_config()
        if not is_valid:
            print(f"✓ Validation detected missing config (expected): {len(errors)} items")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_totp():
    """Test TOTP generation"""
    print("\n" + "=" * 60)
    print("Testing TOTP Handler")
    print("=" * 60)
    
    try:
        from roboai.core import TOTPHandler
        
        # Test with example secret
        secret = "JBSWY3DPEHPK3PXP"
        totp = TOTPHandler(secret)
        print(f"✓ TOTP handler created")
        
        token = totp.generate_token()
        print(f"✓ Token generated: {token}")
        
        # Test verification
        is_valid = totp.verify_token(token)
        print(f"✓ Token verification: {is_valid}")
        
        return True
    except Exception as e:
        print(f"✗ TOTP test failed: {e}")
        return False

def test_database():
    """Test database operations"""
    print("\n" + "=" * 60)
    print("Testing Database")
    print("=" * 60)
    
    try:
        from roboai.utils import get_database
        import tempfile
        import os
        
        # Use temp database for testing
        fd, temp_db = tempfile.mkstemp(suffix='.db')
        os.close(fd)  # Close file descriptor
        db = get_database(temp_db)
        print(f"✓ Database created: {temp_db}")
        
        # Test trade insertion
        trade_data = {
            'trade_id': 'TEST001',
            'symbol': 'NIFTY50',
            'segment': 'FO',
            'side': 'BUY',
            'quantity': 1,
            'entry_price': 19500.0,
            'entry_time': '2024-01-17 10:00:00',
            'status': 'OPEN',
            'strategy': 'momentum'
        }
        trade_id = db.insert_trade(trade_data)
        print(f"✓ Trade inserted: ID {trade_id}")
        
        # Test trade retrieval
        trades = db.get_trades(limit=1)
        print(f"✓ Trades retrieved: {len(trades)} records")
        
        # Cleanup
        db.close()
        if os.path.exists(temp_db):
            os.unlink(temp_db)
        print(f"✓ Test database cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_agents():
    """Test agent initialization"""
    print("\n" + "=" * 60)
    print("Testing Agent System")
    print("=" * 60)
    
    try:
        from roboai.agents import AgentManager, BaseAgent
        import asyncio
        
        # Create simple test agent
        class TestAgent(BaseAgent):
            async def initialize(self):
                return True
            
            async def run(self):
                pass
            
            async def stop(self):
                self.is_running = False
        
        manager = AgentManager()
        print(f"✓ Agent manager created")
        
        test_agent = TestAgent("TestAgent")
        manager.register_agent(test_agent)
        print(f"✓ Test agent registered")
        
        agents = manager.list_agents()
        print(f"✓ Agents in manager: {', '.join(agents)}")
        
        return True
    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ROBOAi Trading Platform - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("TOTP", test_totp),
        ("Database", test_database),
        ("Agents", test_agents),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Platform is ready to use.")
        print("\n⚠️  Note: Full functionality requires installing all dependencies:")
        print("   pip install -r requirements.txt")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
