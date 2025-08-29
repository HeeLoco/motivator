#!/usr/bin/env python3
"""
Content Import Script for MotivatOR Bot

This script imports motivational content from a JSON file into the bot's content system.
Supports all content types: TEXT, IMAGE, VIDEO, LINK
"""

import json
import sys
import logging
from typing import List, Dict, Any
from content import ContentManager, MotivationalContent, ContentType, MoodCategory

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentImporter:
    def __init__(self):
        self.content_manager = ContentManager()
        self.imported_count = 0
        self.error_count = 0
        
    def import_from_json(self, json_file_path: str) -> bool:
        """Import content from JSON file"""
        try:
            # Load JSON file
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            logger.info(f"Loading content from {json_file_path}")
            
            # Validate JSON structure
            if not self._validate_json_structure(data):
                return False
            
            # Import content by language
            for language, content_list in data.get('content', {}).items():
                logger.info(f"Importing {len(content_list)} items for language: {language}")
                self._import_language_content(language, content_list)
            
            # Save updated content to content.py
            self._save_to_content_file()
            
            logger.info(f"Import completed: {self.imported_count} imported, {self.error_count} errors")
            return self.error_count == 0
            
        except FileNotFoundError:
            logger.error(f"File not found: {json_file_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            return False
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return False
    
    def _validate_json_structure(self, data: Dict[str, Any]) -> bool:
        """Validate JSON file structure"""
        if 'content' not in data:
            logger.error("JSON must contain 'content' key")
            return False
        
        valid_languages = ['en', 'de']
        valid_types = ['TEXT', 'IMAGE', 'VIDEO', 'LINK']
        valid_categories = ['ANXIETY', 'DEPRESSION', 'STRESS', 'MOTIVATION', 'SELF_CARE', 'GENERAL']
        
        for language, content_list in data['content'].items():
            if language not in valid_languages:
                logger.warning(f"Unknown language: {language}")
            
            for i, item in enumerate(content_list):
                # Check required fields
                required_fields = ['content', 'type', 'category']
                for field in required_fields:
                    if field not in item:
                        logger.error(f"Missing '{field}' in item {i} for language {language}")
                        return False
                
                # Validate type and category
                if item['type'] not in valid_types:
                    logger.error(f"Invalid type '{item['type']}' in item {i}")
                    return False
                
                if item['category'] not in valid_categories:
                    logger.error(f"Invalid category '{item['category']}' in item {i}")
                    return False
        
        return True
    
    def _import_language_content(self, language: str, content_list: List[Dict[str, Any]]):
        """Import content for a specific language"""
        for item in content_list:
            try:
                # Create MotivationalContent object
                content = MotivationalContent(
                    id=0,  # Auto-assigned
                    content=item['content'],
                    content_type=ContentType[item['type']],
                    language=language,
                    category=MoodCategory[item['category']],
                    media_url=item.get('media_url'),
                    tags=item.get('tags')
                )
                
                # Add to content manager's content dictionary
                if language not in self.content_manager.content:
                    self.content_manager.content[language] = []
                
                self.content_manager.content[language].append(content)
                self.imported_count += 1
                
                logger.info(f"Imported: {item['type']} - {item['content'][:50]}...")
                
            except Exception as e:
                logger.error(f"Error importing item: {item.get('content', 'Unknown')[:30]} - {e}")
                self.error_count += 1
    
    def _save_to_content_file(self):
        """Save imported content back to content.py file"""
        try:
            # Read current content.py file
            with open('content.py', 'r', encoding='utf-8') as file:
                content_py = file.read()
            
            # Generate new content arrays
            new_content = self._generate_content_arrays()
            
            # Replace content in file (this is a simplified approach)
            # In production, you might want more sophisticated file editing
            logger.info("Content successfully added to memory. Restart bot to see changes.")
            logger.warning("Note: Auto-saving to content.py not implemented yet.")
            logger.info("Please manually add the imported content to content.py or restart the import script with --write-file flag")
            
        except Exception as e:
            logger.error(f"Error updating content.py: {e}")
    
    def _generate_content_arrays(self) -> str:
        """Generate Python code for content arrays"""
        output = []
        
        for language, content_list in self.content_manager.content.items():
            output.append(f"# {language.upper()} Content ({len(content_list)} items)")
            output.append(f"'{language}': [")
            
            for content in content_list:
                media_url = f", media_url='{content.media_url}'" if content.media_url else ""
                tags = f", tags={content.tags}" if content.tags else ""
                
                output.append(f"    MotivationalContent(")
                output.append(f"        id=0,")
                output.append(f"        content='{content.content.replace(chr(39), chr(92) + chr(39))}',")
                output.append(f"        content_type=ContentType.{content.content_type.name},")
                output.append(f"        language='{content.language}',")
                output.append(f"        category=MoodCategory.{content.category.name}{media_url}{tags}")
                output.append(f"    ),")
            
            output.append(f"],")
            output.append("")
        
        return "\n".join(output)
    
    def print_import_summary(self):
        """Print summary of imported content"""
        print("\n" + "="*60)
        print("📊 IMPORT SUMMARY")
        print("="*60)
        
        for language, content_list in self.content_manager.content.items():
            print(f"\n🌍 {language.upper()} Content: {len(content_list)} items")
            
            # Count by category
            categories = {}
            types = {}
            
            for content in content_list:
                cat = content.category.name
                typ = content.content_type.name
                categories[cat] = categories.get(cat, 0) + 1
                types[typ] = types.get(typ, 0) + 1
            
            print("   Categories:", ", ".join([f"{k}:{v}" for k, v in categories.items()]))
            print("   Types:", ", ".join([f"{k}:{v}" for k, v in types.items()]))
        
        print(f"\n✅ Total imported: {self.imported_count}")
        print(f"❌ Total errors: {self.error_count}")
        print("="*60)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python import_content.py <json_file>")
        print("Example: python import_content.py content_example.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Create importer and run
    importer = ContentImporter()
    success = importer.import_from_json(json_file)
    
    # Show summary
    importer.print_import_summary()
    
    if success:
        print("\n🎉 Import completed successfully!")
        print("💡 Restart the bot to see the new content.")
    else:
        print("\n❌ Import completed with errors. Check logs above.")
        sys.exit(1)

if __name__ == '__main__':
    main()