#!/usr/bin/env python3
"""
Migration Script: Hardcoded Content → Database

This script migrates motivational content from hardcoded Python lists in content.py
to the new motivational_content database table.

SAFETY: This script only INSERTS data, never deletes or modifies existing content.
"""

import sys
import os
import logging

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import Database
from src.content import ContentManager, ContentType, MoodCategory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_content_to_database(db_path: str = "motivator.db"):
    """
    Migrate hardcoded content from content.py to database

    Args:
        db_path: Path to database file

    Returns:
        Tuple of (success_count, error_count)
    """
    logger.info("="*60)
    logger.info("Starting Content Migration to Database")
    logger.info("="*60)

    # Initialize database and content manager
    db = Database(db_path)
    content_manager = ContentManager()

    success_count = 0
    error_count = 0
    skipped_count = 0

    # Check if content already exists in database
    existing_content = db.get_all_content()
    if existing_content:
        logger.warning(f"Database already contains {len(existing_content)} content items")
        response = input("Do you want to add more content anyway? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Migration cancelled by user")
            return 0, 0

    # Migrate content for each language
    for language, content_list in content_manager.content.items():
        logger.info(f"\n📝 Processing {language.upper()} content ({len(content_list)} items)...")

        for content_obj in content_list:
            try:
                # Convert enum values to strings for database
                content_type_str = content_obj.content_type.value
                category_str = content_obj.category.value

                # Convert tags list to JSON string if present
                tags_str = None
                if content_obj.tags:
                    import json
                    tags_str = json.dumps(content_obj.tags)

                # Insert into database
                content_id = db.add_content(
                    content=content_obj.content,
                    content_type=content_type_str,
                    language=content_obj.language,
                    category=category_str,
                    media_url=content_obj.media_url,
                    tags=tags_str
                )

                if content_id:
                    success_count += 1
                    logger.debug(f"  ✓ Migrated: {content_obj.content[:50]}...")
                else:
                    error_count += 1
                    logger.error(f"  ✗ Failed: {content_obj.content[:50]}...")

            except Exception as e:
                error_count += 1
                logger.error(f"  ✗ Error migrating content: {e}")
                logger.error(f"     Content: {content_obj.content[:50]}...")

    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 MIGRATION SUMMARY")
    logger.info("="*60)
    logger.info(f"✅ Successfully migrated: {success_count} items")
    logger.info(f"❌ Errors: {error_count} items")

    if success_count > 0:
        # Get and display database stats
        stats = db.get_content_stats()
        logger.info(f"\n📈 Database Content Statistics:")
        logger.info(f"   Total active content: {stats.get('total', 0)}")
        logger.info(f"   By language: {stats.get('by_language', {})}")
        logger.info(f"   By category: {stats.get('by_category', {})}")
        logger.info(f"   By type: {stats.get('by_type', {})}")

    logger.info("="*60)

    return success_count, error_count


def verify_migration(db_path: str = "motivator.db"):
    """Verify that migration was successful"""
    logger.info("\n🔍 Verifying migration...")

    db = Database(db_path)
    content_manager = ContentManager()

    # Count hardcoded content
    hardcoded_total = sum(len(items) for items in content_manager.content.values())

    # Count database content
    db_content = db.get_all_content()
    db_total = len(db_content)

    logger.info(f"Hardcoded content items: {hardcoded_total}")
    logger.info(f"Database content items: {db_total}")

    if db_total >= hardcoded_total:
        logger.info("✅ Verification PASSED - All content migrated successfully")
        return True
    else:
        logger.warning(f"⚠️  Verification INCOMPLETE - Missing {hardcoded_total - db_total} items")
        return False


def main():
    """Main migration function"""
    logger.info("🚀 Content Migration Script")
    logger.info("This script migrates hardcoded content to database")
    logger.info("SAFE: Only adds content, never deletes or modifies existing data\n")

    # Get database path
    db_path = "motivator.db"
    if len(sys.argv) > 1:
        db_path = sys.argv[1]

    logger.info(f"Database: {db_path}\n")

    # Run migration
    success, errors = migrate_content_to_database(db_path)

    # Verify migration
    if success > 0:
        verify_migration(db_path)

    # Exit status
    if errors > 0:
        logger.error("\n❌ Migration completed with errors")
        sys.exit(1)
    elif success == 0:
        logger.warning("\n⚠️  No content was migrated")
        sys.exit(0)
    else:
        logger.info("\n✅ Migration completed successfully!")
        logger.info("💡 Next steps:")
        logger.info("   1. Update ContentManager to load from database")
        logger.info("   2. Restart the bot")
        logger.info("   3. Test content delivery")
        sys.exit(0)


if __name__ == '__main__':
    main()
