"""
Goals Management System for Motivator Bot

Provides goal categories, templates, and management functionality
for mental health and personal development goals.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import random

class GoalCategory(Enum):
    HEALTH_FITNESS = "health_fitness"
    MENTAL_WELLBEING = "mental_wellbeing" 
    PERSONAL_DEVELOPMENT = "personal_development"
    HABIT_BUILDING = "habit_building"
    SOCIAL_CONNECTIONS = "social_connections"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class GoalTemplate:
    id: str
    title: str
    description: str
    category: GoalCategory
    difficulty: DifficultyLevel
    is_daily: bool
    duration_days: int
    tips: List[str]
    
class GoalManager:
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict[str, List[GoalTemplate]]]:
        """Load goal templates organized by language and category"""
        templates = {
            'de': {},
            'en': {}
        }
        
        # German templates
        de_templates = [
            # Mental Wellbeing
            GoalTemplate(
                'de_meditation_beginner', '10 Minuten täglich meditieren',
                'Täglich 10 Minuten der Achtsamkeit und Entspannung widmen',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 21,
                ['Nutze eine Meditations-App', 'Beginne mit 5 Minuten', 'Finde einen ruhigen Ort']
            ),
            GoalTemplate(
                'de_gratitude_beginner', 'Dankbarkeits-Tagebuch führen',
                'Täglich 3 Dinge aufschreiben, für die ich dankbar bin',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 21,
                ['Schreibe jeden Abend', 'Sei spezifisch', 'Denke an kleine Dinge']
            ),
            GoalTemplate(
                'de_breathing_beginner', 'Atemübungen praktizieren',
                'Täglich 5 Minuten bewusste Atemübungen machen',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 14,
                ['4-7-8 Atemtechnik versuchen', 'Bei Stress anwenden', 'Ruhig und langsam atmen']
            ),
            
            # Health & Fitness
            GoalTemplate(
                'de_walk_beginner', '30 Minuten täglich spazieren',
                'Jeden Tag einen 30-minütigen Spaziergang machen',
                GoalCategory.HEALTH_FITNESS, DifficultyLevel.BEGINNER, True, 30,
                ['Beginne mit 15 Minuten', 'Höre Musik oder Podcasts', 'Gehe zur gleichen Zeit']
            ),
            GoalTemplate(
                'de_water_beginner', '2 Liter Wasser täglich trinken',
                'Jeden Tag ausreichend Wasser trinken für bessere Gesundheit',
                GoalCategory.HEALTH_FITNESS, DifficultyLevel.BEGINNER, True, 21,
                ['Stelle eine Wasserflasche bereit', 'Trinke vor jeder Mahlzeit', 'Nutze eine App zur Erinnerung']
            ),
            GoalTemplate(
                'de_sleep_beginner', 'Um 22 Uhr ins Bett gehen',
                'Regelmäßigen Schlafrhythmus für bessere Erholung entwickeln',
                GoalCategory.HABIT_BUILDING, DifficultyLevel.BEGINNER, True, 21,
                ['1 Stunde vor dem Schlafen kein Handy', 'Schlafzimmer abdunkeln', 'Entspannungsroutine entwickeln']
            ),
            
            # Personal Development
            GoalTemplate(
                'de_reading_beginner', '20 Minuten täglich lesen',
                'Jeden Tag 20 Minuten in einem Buch lesen',
                GoalCategory.PERSONAL_DEVELOPMENT, DifficultyLevel.BEGINNER, True, 30,
                ['Wähle interessante Bücher', 'Lese zur gleichen Zeit', 'Beginne mit weniger Minuten']
            ),
            GoalTemplate(
                'de_journal_intermediate', 'Reflexions-Tagebuch führen',
                'Täglich über Gedanken, Gefühle und Erfahrungen schreiben',
                GoalCategory.PERSONAL_DEVELOPMENT, DifficultyLevel.INTERMEDIATE, True, 30,
                ['Schreibe morgens oder abends', 'Sei ehrlich zu dir selbst', 'Keine Rechtschreibung-Sorgen']
            ),
            
            # Social Connections
            GoalTemplate(
                'de_friends_beginner', 'Jeden Tag jemanden kontaktieren',
                'Täglich mit einem Freund oder Familienmitglied Kontakt aufnehmen',
                GoalCategory.SOCIAL_CONNECTIONS, DifficultyLevel.BEGINNER, True, 14,
                ['Schicke eine kurze Nachricht', 'Rufe jemanden an', 'Plane gemeinsame Aktivitäten']
            ),
        ]
        
        # English templates
        en_templates = [
            # Mental Wellbeing
            GoalTemplate(
                'en_meditation_beginner', 'Meditate 10 minutes daily',
                'Dedicate 10 minutes each day to mindfulness and relaxation',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 21,
                ['Use a meditation app', 'Start with 5 minutes', 'Find a quiet place']
            ),
            GoalTemplate(
                'en_gratitude_beginner', 'Keep a gratitude journal',
                'Write down 3 things I\'m grateful for every day',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 21,
                ['Write every evening', 'Be specific', 'Think of small things']
            ),
            GoalTemplate(
                'en_breathing_beginner', 'Practice breathing exercises',
                'Do 5 minutes of conscious breathing exercises daily',
                GoalCategory.MENTAL_WELLBEING, DifficultyLevel.BEGINNER, True, 14,
                ['Try 4-7-8 breathing technique', 'Use when stressed', 'Breathe calmly and slowly']
            ),
            
            # Health & Fitness
            GoalTemplate(
                'en_walk_beginner', 'Walk 30 minutes daily',
                'Take a 30-minute walk every day',
                GoalCategory.HEALTH_FITNESS, DifficultyLevel.BEGINNER, True, 30,
                ['Start with 15 minutes', 'Listen to music or podcasts', 'Walk at the same time']
            ),
            GoalTemplate(
                'en_water_beginner', 'Drink 2 liters of water daily',
                'Drink enough water every day for better health',
                GoalCategory.HEALTH_FITNESS, DifficultyLevel.BEGINNER, True, 21,
                ['Keep a water bottle ready', 'Drink before each meal', 'Use a reminder app']
            ),
            GoalTemplate(
                'en_sleep_beginner', 'Go to bed at 10 PM',
                'Develop a regular sleep rhythm for better rest',
                GoalCategory.HABIT_BUILDING, DifficultyLevel.BEGINNER, True, 21,
                ['No phone 1 hour before bed', 'Darken bedroom', 'Develop relaxation routine']
            ),
            
            # Personal Development
            GoalTemplate(
                'en_reading_beginner', 'Read 20 minutes daily',
                'Read in a book for 20 minutes every day',
                GoalCategory.PERSONAL_DEVELOPMENT, DifficultyLevel.BEGINNER, True, 30,
                ['Choose interesting books', 'Read at the same time', 'Start with fewer minutes']
            ),
            GoalTemplate(
                'en_journal_intermediate', 'Keep a reflection journal',
                'Write daily about thoughts, feelings and experiences',
                GoalCategory.PERSONAL_DEVELOPMENT, DifficultyLevel.INTERMEDIATE, True, 30,
                ['Write in morning or evening', 'Be honest with yourself', 'Don\'t worry about spelling']
            ),
            
            # Social Connections
            GoalTemplate(
                'en_friends_beginner', 'Contact someone every day',
                'Reach out to a friend or family member daily',
                GoalCategory.SOCIAL_CONNECTIONS, DifficultyLevel.BEGINNER, True, 14,
                ['Send a short message', 'Call someone', 'Plan activities together']
            ),
        ]
        
        # Organize templates by language and category
        for lang, template_list in [('de', de_templates), ('en', en_templates)]:
            for template in template_list:
                category_key = template.category.value
                if category_key not in templates[lang]:
                    templates[lang][category_key] = []
                templates[lang][category_key].append(template)
        
        return templates
    
    def get_categories(self, language: str = 'de') -> Dict[str, str]:
        """Get goal categories with display names"""
        if language == 'de':
            return {
                'health_fitness': '🏃‍♂️ Gesundheit & Fitness',
                'mental_wellbeing': '🧠 Mentales Wohlbefinden',
                'personal_development': '📚 Persönliche Entwicklung',
                'habit_building': '🎯 Gewohnheiten',
                'social_connections': '👥 Soziale Kontakte'
            }
        else:
            return {
                'health_fitness': '🏃‍♂️ Health & Fitness',
                'mental_wellbeing': '🧠 Mental Wellbeing',
                'personal_development': '📚 Personal Development',
                'habit_building': '🎯 Habit Building',
                'social_connections': '👥 Social Connections'
            }
    
    def get_templates_by_category(self, category: str, language: str = 'de') -> List[GoalTemplate]:
        """Get goal templates for a specific category"""
        return self.templates.get(language, {}).get(category, [])
    
    def get_template_by_id(self, template_id: str, language: str = 'de') -> Optional[GoalTemplate]:
        """Get a specific template by ID"""
        for category in self.templates.get(language, {}).values():
            for template in category:
                if template.id == template_id:
                    return template
        return None
    
    def get_random_template(self, language: str = 'de', difficulty: DifficultyLevel = None) -> Optional[GoalTemplate]:
        """Get a random goal template"""
        all_templates = []
        for category in self.templates.get(language, {}).values():
            for template in category:
                if difficulty is None or template.difficulty == difficulty:
                    all_templates.append(template)
        
        return random.choice(all_templates) if all_templates else None
    
    def format_goal_display(self, goal: Dict, language: str = 'de') -> str:
        """Format goal for display in bot interface"""
        streak_emoji = "🔥" if goal['streak_days'] > 0 else "⭐"
        category_emojis = {
            'health_fitness': '🏃‍♂️',
            'mental_wellbeing': '🧠',
            'personal_development': '📚', 
            'habit_building': '🎯',
            'social_connections': '👥'
        }
        
        category_emoji = category_emojis.get(goal['category'], '🎯')
        
        if language == 'de':
            status = f"{streak_emoji} {goal['streak_days']} Tage Streak" if goal['streak_days'] > 0 else "🆕 Neu"
            return f"{category_emoji} *{goal['text']}*\n💪 Status: {status}"
        else:
            status = f"{streak_emoji} {goal['streak_days']} day streak" if goal['streak_days'] > 0 else "🆕 New"
            return f"{category_emoji} *{goal['text']}*\n💪 Status: {status}"