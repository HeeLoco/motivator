#!/usr/bin/env python3
"""
Test script to verify settings persistence
"""

from database import Database

def test_persistence():
    """Test that user settings persist after add_user calls"""
    
    db = Database()
    user_id = 1153831100
    
    print("=== Testing Settings Persistence ===")
    
    # Check current settings
    settings_before = db.get_user_settings(user_id)
    print(f"Settings before add_user: {settings_before}")
    
    # Simulate what happens when user restarts bot (/start command)
    result = db.add_user(user_id, "HeeLoco", "Edgard")
    print(f"add_user result: {result}")
    
    # Check settings after
    settings_after = db.get_user_settings(user_id)
    print(f"Settings after add_user: {settings_after}")
    
    # Compare
    if settings_before and settings_after:
        if settings_before['message_frequency'] == settings_after['message_frequency']:
            print("✅ SUCCESS: Settings persisted!")
        else:
            print("❌ FAILURE: Settings were reset!")
    else:
        print("❌ ERROR: Could not retrieve settings")

if __name__ == '__main__':
    test_persistence()