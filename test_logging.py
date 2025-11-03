#!/usr/bin/env python3
"""
Test script for the logging system.

Tests both JSON and text formatters, correlation IDs, and structured logging.
"""

import os
import sys
import logging

# Add src directory to path to import logging_config directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import logging_config
from logging_config import (
    setup_logging,
    get_logger,
    log_with_context,
    set_correlation_id,
    clear_correlation_id
)


def test_text_logging():
    """Test text-based logging (development mode)"""
    print("\n" + "="*60)
    print("Testing TEXT Logging Format (Development Mode)")
    print("="*60 + "\n")

    # Force text format
    os.environ['LOG_FORMAT'] = 'text'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    os.environ['LOG_FILE'] = ''  # Disable file logging for test

    setup_logging()
    logger = get_logger(__name__)

    # Test basic logging levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")

    # Test logging with user context
    print("\n--- With User Context ---")
    log_with_context(
        logger, logging.INFO,
        "User performed action",
        user_id=12345
    )

    # Test logging with correlation ID
    print("\n--- With Correlation ID ---")
    set_correlation_id("test_corr_123")
    logger.info("Operation started")
    logger.info("Operation in progress")
    logger.info("Operation completed")
    clear_correlation_id()

    # Test logging with extra fields
    print("\n--- With Extra Fields ---")
    log_with_context(
        logger, logging.INFO,
        "Message sent",
        user_id=12345,
        mood_category="MOTIVATION",
        message_frequency=3,
        success=True
    )


def test_json_logging():
    """Test JSON-based logging (container mode)"""
    print("\n" + "="*60)
    print("Testing JSON Logging Format (Container Mode)")
    print("="*60 + "\n")

    # Force JSON format
    os.environ['LOG_FORMAT'] = 'json'
    os.environ['LOG_LEVEL'] = 'INFO'
    os.environ['CONTAINER_ENV'] = 'true'

    setup_logging()
    logger = get_logger(__name__)

    # Test basic logging levels
    logger.info("This is an INFO message in JSON format")
    logger.warning("This is a WARNING message in JSON format")
    logger.error("This is an ERROR message in JSON format")

    # Test logging with user context
    print("\n--- With User Context (JSON) ---")
    log_with_context(
        logger, logging.INFO,
        "User performed action",
        user_id=67890
    )

    # Test logging with correlation ID
    print("\n--- With Correlation ID (JSON) ---")
    set_correlation_id("json_corr_456")
    logger.info("JSON operation started")
    logger.info("JSON operation in progress")
    logger.info("JSON operation completed")
    clear_correlation_id()

    # Test logging with extra fields
    print("\n--- With Extra Fields (JSON) ---")
    log_with_context(
        logger, logging.INFO,
        "Scheduled message sent",
        user_id=67890,
        scheduled_time="2025-11-03T14:30:00Z",
        actual_send_time="2025-11-03T14:30:05Z",
        message_type="motivational",
        delay_seconds=5
    )


def test_auto_detection():
    """Test auto-detection of container environment"""
    print("\n" + "="*60)
    print("Testing Auto-Detection")
    print("="*60 + "\n")

    # Clear environment to test defaults
    os.environ.pop('LOG_FORMAT', None)
    os.environ.pop('CONTAINER_ENV', None)
    os.environ['LOG_LEVEL'] = 'INFO'

    setup_logging()
    logger = get_logger(__name__)

    logger.info("Auto-detected logging format (should be TEXT in development)")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("LOGGING SYSTEM TEST SUITE")
    print("="*60)

    try:
        # Test text logging
        test_text_logging()

        # Test JSON logging
        test_json_logging()

        # Test auto-detection
        test_auto_detection()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
