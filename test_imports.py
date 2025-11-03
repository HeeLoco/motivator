#!/usr/bin/env python3
"""
Test script to verify all modules can be imported correctly.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing imports...")

try:
    print("1. Testing logging_config import...")
    from src.logging_config import setup_logging, get_logger
    print("   ✓ logging_config imported successfully")

    print("\n2. Setting up logging...")
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['LOG_FORMAT'] = 'text'
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Logging system initialized")
    print("   ✓ Logging setup successful")

    print("\n3. Testing database module import...")
    from src.database import Database
    print("   ✓ database module imported successfully")

    print("\n4. Testing content module import...")
    from src.content import ContentManager
    print("   ✓ content module imported successfully")

    print("\n5. Testing smart_scheduler module import...")
    from src.smart_scheduler import SmartMessageScheduler
    print("   ✓ smart_scheduler module imported successfully")

    print("\n6. Testing bot module import...")
    from src.bot import MotivatorBot
    print("   ✓ bot module imported successfully")

    print("\n" + "="*60)
    print("ALL IMPORTS SUCCESSFUL!")
    print("="*60)

except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
