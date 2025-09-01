import random
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    LINK = "link"

class MoodCategory(Enum):
    ANXIETY = "anxiety"
    DEPRESSION = "depression" 
    STRESS = "stress"
    MOTIVATION = "motivation"
    SELF_CARE = "self_care"
    GENERAL = "general"

@dataclass
class MotivationalContent:
    id: int
    content: str
    content_type: ContentType
    language: str
    category: MoodCategory
    media_url: str = None
    tags: List[str] = None

class ContentManager:
    def __init__(self):
        self.content = self._load_content()
    
    def _load_content(self) -> Dict[str, List[MotivationalContent]]:
        """Load motivational content in different languages"""
        content = {
            'en': [],
            'de': []
        }
        
        # English content
        english_content = [
            # General Motivation
            MotivationalContent(1, "You are stronger than you think. Every challenge you've overcome has made you more resilient. 💪", ContentType.TEXT, 'en', MoodCategory.MOTIVATION),
            MotivationalContent(2, "Progress, not perfection. Small steps forward are still steps forward. 🌟", ContentType.TEXT, 'en', MoodCategory.MOTIVATION),
            MotivationalContent(3, "Your mental health is just as important as your physical health. Take care of both. 🧠❤️", ContentType.TEXT, 'en', MoodCategory.SELF_CARE),
            
            # Anxiety Support  
            MotivationalContent(4, "Breathe in for 4, hold for 4, breathe out for 4. This moment will pass. 🌬️", ContentType.TEXT, 'en', MoodCategory.ANXIETY),
            MotivationalContent(5, "Anxiety is temporary, but your strength is permanent. You've got this. 🌊", ContentType.TEXT, 'en', MoodCategory.ANXIETY),
            
            # Depression Support
            MotivationalContent(6, "Even on your darkest days, you matter. Your presence in this world makes a difference. ☀️", ContentType.TEXT, 'en', MoodCategory.DEPRESSION),
            MotivationalContent(7, "It's okay to not be okay. Healing isn't linear, and that's perfectly normal. 🌱", ContentType.TEXT, 'en', MoodCategory.DEPRESSION),
            
            # Stress Management
            MotivationalContent(8, "You can't control everything, and that's okay. Focus on what you can influence. 🎯", ContentType.TEXT, 'en', MoodCategory.STRESS),
            MotivationalContent(9, "Take a 5-minute break. Your tasks will wait, but your well-being shouldn't. ⏰", ContentType.TEXT, 'en', MoodCategory.STRESS),
            
            # Self-Care
            MotivationalContent(10, "Self-care isn't selfish. You can't pour from an empty cup. Fill yours first. ☕", ContentType.TEXT, 'en', MoodCategory.SELF_CARE),
            MotivationalContent(11, "Today's reminder: Drink water, get some sunlight, and be kind to yourself. 🌞", ContentType.TEXT, 'en', MoodCategory.SELF_CARE),
            
            # Media Content
            MotivationalContent(12, "5-minute meditation for anxiety relief", ContentType.VIDEO, 'en', MoodCategory.ANXIETY, "https://www.youtube.com/shorts/example1"),
            MotivationalContent(13, "Quick breathing exercise for stress", ContentType.VIDEO, 'en', MoodCategory.STRESS, "https://www.youtube.com/shorts/example2"),
            MotivationalContent(14, "Mental Health Resources", ContentType.LINK, 'en', MoodCategory.GENERAL, "https://www.mentalhealth.gov/"),
        ]
        
        # German content
        german_content = [
            # Allgemeine Motivation
            MotivationalContent(15, "Du bist stärker als du denkst. Jede Herausforderung, die du gemeistert hast, macht dich widerstandsfähiger. 💪", ContentType.TEXT, 'de', MoodCategory.MOTIVATION),
            MotivationalContent(16, "Fortschritt, nicht Perfektion. Kleine Schritte vorwärts sind immer noch Schritte vorwärts. 🌟", ContentType.TEXT, 'de', MoodCategory.MOTIVATION),
            MotivationalContent(17, "Deine psychische Gesundheit ist genauso wichtig wie deine körperliche. Sorge für beides. 🧠❤️", ContentType.TEXT, 'de', MoodCategory.SELF_CARE),


            MotivationalContent(29, „Kleine Schritte sind besser als keine Schritte.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(30, „Das Geheimnis des Erfolgs ist anzufangen.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(31, „Machen ist wie wollen – nur krasser.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(32, „Wenn du keine Lust hast, von vorne anzufangen, dann gib nicht auf.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(33, „Du kannst die Zukunft verändern mit dem, was du heute tust.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(34, „Ehrgeiz ist die Fähigkeit, die Träume real werden lässt.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),


            MotivationalContent(34, „Innen muss etwas brennen, damit außen etwas leuchten kann.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(35, „Scheitern ist nicht das Gegenteil von Erfolg. Es ist ein Teil davon.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(36, „Nicht wie groß der erste Schritt ist zählt, sondern die richtige Richtung.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(37, „Warte nicht auf Motivation. Sei du die Motivation für andere!“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(38, „Höre nicht auf, wenn es weh tut. Höre auf, wenn du fertig bist.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(39, „Sobald wir unseren Geist auf ein Ziel richten, kommt es uns entgegen.“, ContentType.TEXT, 'de', MoodCategory.SELF_CARE),


            # Angst-Unterstützung
            MotivationalContent(18, "Atme 4 Sekunden ein, halte 4 Sekunden, atme 4 Sekunden aus. Dieser Moment wird vorübergehen. 🌬️", ContentType.TEXT, 'de', MoodCategory.ANXIETY),
            MotivationalContent(19, "Angst ist vorübergehend, aber deine Stärke ist dauerhaft. Du schaffst das. 🌊", ContentType.TEXT, 'de', MoodCategory.ANXIETY),
            
            # Depression-Unterstützung
            MotivationalContent(20, "Auch an deinen dunkelsten Tagen bist du wichtig. Deine Anwesenheit in dieser Welt macht einen Unterschied. ☀️", ContentType.TEXT, 'de', MoodCategory.DEPRESSION),
            MotivationalContent(21, "Es ist okay, nicht okay zu sein. Heilung verläuft nicht linear, und das ist völlig normal. 🌱", ContentType.TEXT, 'de', MoodCategory.DEPRESSION),
            
            # Stress-Management
            MotivationalContent(22, "Du kannst nicht alles kontrollieren, und das ist okay. Konzentriere dich auf das, was du beeinflussen kannst. 🎯", ContentType.TEXT, 'de', MoodCategory.STRESS),
            MotivationalContent(23, "Mach eine 5-minütige Pause. Deine Aufgaben können warten, aber dein Wohlbefinden sollte es nicht. ⏰", ContentType.TEXT, 'de', MoodCategory.STRESS),
            
            # Selbstfürsorge
            MotivationalContent(24, "Selbstfürsorge ist nicht egoistisch. Du kannst nicht aus einem leeren Becher gießen. Fülle deinen zuerst. ☕", ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            MotivationalContent(25, "Heutige Erinnerung: Trinke Wasser, hole dir etwas Sonnenlicht und sei freundlich zu dir selbst. 🌞", ContentType.TEXT, 'de', MoodCategory.SELF_CARE),
            
            # Media-Inhalte
            MotivationalContent(26, "5-Minuten Meditation gegen Angst", ContentType.VIDEO, 'de', MoodCategory.ANXIETY, "https://www.youtube.com/shorts/example3"),
            MotivationalContent(27, "Schnelle Atemübung gegen Stress", ContentType.VIDEO, 'de', MoodCategory.STRESS, "https://www.youtube.com/shorts/example4"),
            MotivationalContent(28, "Ressourcen für psychische Gesundheit", ContentType.LINK, 'de', MoodCategory.GENERAL, "https://www.bundesgesundheitsministerium.de/themen/praevention/gesundheitsfoerderung/praevention-psychischer-erkrankungen.html"),
        ]
        
        content['en'] = english_content
        content['de'] = german_content
        
        return content
    
    def get_random_content(self, language: str = 'de', category: MoodCategory = None, exclude_recent: List[int] = None) -> MotivationalContent:
        """Get random motivational content based on criteria"""
        available_content = self.content.get(language, self.content['de'])
        
        if category:
            available_content = [c for c in available_content if c.category == category]
        
        if exclude_recent:
            available_content = [c for c in available_content if c.id not in exclude_recent]
        
        if not available_content:
            # Fallback to general content if no matches
            available_content = [c for c in self.content[language] if c.category == MoodCategory.GENERAL]
        
        return random.choice(available_content) if available_content else None
    
    def get_content_by_mood(self, mood_score: int, language: str = 'de', exclude_recent: List[int] = None) -> MotivationalContent:
        """Get content based on mood score (1-10, where 1 is very low, 10 is excellent)"""
        if mood_score <= 3:
            # Low mood - depression/anxiety support
            categories = [MoodCategory.DEPRESSION, MoodCategory.ANXIETY, MoodCategory.SELF_CARE]
        elif mood_score <= 6:
            # Medium mood - general support and stress relief
            categories = [MoodCategory.STRESS, MoodCategory.GENERAL, MoodCategory.SELF_CARE]
        else:
            # Good mood - motivation and positivity
            categories = [MoodCategory.MOTIVATION, MoodCategory.GENERAL]
        
        category = random.choice(categories)
        return self.get_random_content(language, category, exclude_recent)
    
    def get_all_content(self, language: str = None) -> List[MotivationalContent]:
        """Get all content, optionally filtered by language"""
        if language:
            return self.content.get(language, [])
        
        all_content = []
        for lang_content in self.content.values():
            all_content.extend(lang_content)
        return all_content
    
    def add_custom_content(self, content: MotivationalContent):
        """Add custom content (for external management)"""
        language = content.language
        if language not in self.content:
            self.content[language] = []
        
        # Assign new ID
        max_id = max([c.id for lang_content in self.content.values() for c in lang_content], default=0)
        content.id = max_id + 1
        
        self.content[language].append(content)
    
    def remove_content(self, content_id: int) -> bool:
        """Remove content by ID"""
        for language in self.content:
            self.content[language] = [c for c in self.content[language] if c.id != content_id]
        return True