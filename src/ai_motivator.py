"""
AI-powered content generation for Motivator Bot.

Domain layer on top of ai_client: builds mental-health-aware prompts for
motivational messages, chat replies, and mood reactions. All functions
return None when the AI is unavailable so callers can fall back to the
static content from ContentManager.
"""

from typing import Dict, List, Optional

from src.ai_client import generate_response
from src.logging_config import get_logger

logger = get_logger(__name__)

_BASE_INSTRUCTIONS = {
    'de': (
        "Du bist der Motivator Bot, ein einfühlsamer Telegram-Bot für mentale "
        "Gesundheit und Motivation. Deine Nutzer können mit Ängsten, Depressionen "
        "oder Stress zu kämpfen haben.\n"
        "Regeln:\n"
        "- Antworte auf Deutsch, warm, unterstützend und ohne Floskeln.\n"
        "- Verwende nicht-triggernde, wertschätzende Sprache. Keine Diagnosen, "
        "keine medizinischen Ratschläge.\n"
        "- Du bist eine Unterstützung, kein Ersatz für professionelle Hilfe. "
        "Bei Anzeichen einer akuten Krise (Suizidgedanken, Selbstverletzung) "
        "weise behutsam auf die Telefonseelsorge hin: 0800 111 0 111 (kostenlos, 24/7).\n"
        "- Halte dich kurz: 2-4 Sätze, passende Emojis sind willkommen.\n"
        "- Kein Markdown, nur einfacher Text."
    ),
    'en': (
        "You are the Motivator Bot, an empathetic Telegram bot for mental health "
        "and motivation. Your users may struggle with anxiety, depression, or stress.\n"
        "Rules:\n"
        "- Reply in English, warm, supportive, and without platitudes.\n"
        "- Use non-triggering, appreciative language. No diagnoses, no medical advice.\n"
        "- You are a support tool, not a replacement for professional care. "
        "If there are signs of an acute crisis (suicidal thoughts, self-harm), "
        "gently point to a crisis line such as 988 (US) or find help at findahelpline.com.\n"
        "- Keep it short: 2-4 sentences, fitting emojis are welcome.\n"
        "- No markdown, plain text only."
    ),
}


def _instructions(language: str) -> str:
    return _BASE_INSTRUCTIONS.get(language, _BASE_INSTRUCTIONS['de'])


def _name_context(language: str, first_name: Optional[str]) -> str:
    if not first_name:
        return ""
    if language == 'de':
        return (
            f"Der Nutzer heißt {first_name}. Sprich ihn gelegentlich persönlich "
            "mit seinem Namen an, aber nicht zwanghaft in jeder Nachricht. "
        )
    return (
        f"The user's name is {first_name}. Address them personally by name "
        "occasionally, but not forcedly in every message. "
    )


def _mood_context(language: str, mood_score: Optional[int]) -> str:
    if mood_score is None:
        return ""
    if language == 'de':
        return f"Die zuletzt erfasste Stimmung des Nutzers ist {mood_score}/10 (1=sehr schlecht, 10=sehr gut). "
    return f"The user's last logged mood is {mood_score}/10 (1=very low, 10=very good). "


async def generate_motivation(language: str, mood_score: Optional[int] = None,
                              first_name: Optional[str] = None) -> Optional[str]:
    """Generate a personalized motivational message."""
    if language == 'de':
        prompt = (
            f"{_name_context(language, first_name)}{_mood_context(language, mood_score)}"
            "Schreibe eine kurze, persönliche Motivationsnachricht, die zur Stimmung passt."
        )
    else:
        prompt = (
            f"{_name_context(language, first_name)}{_mood_context(language, mood_score)}"
            "Write a short, personal motivational message that fits the mood."
        )

    return await generate_response(prompt, instructions=_instructions(language))


def _chat_instructions(language: str, mood_score: Optional[int],
                       first_name: Optional[str]) -> str:
    """Instructions for conversational replies, including user context."""
    base = _instructions(language)
    if language == 'de':
        extra = (
            "\nDu führst ein fortlaufendes Gespräch mit dem Nutzer. "
            "Wenn ein Bot-Befehl besser helfen würde (/mood für Stimmungs-Tracking, "
            "/motivateMe für Motivation, /settings für Einstellungen), erwähne ihn kurz."
        )
    else:
        extra = (
            "\nYou are having an ongoing conversation with the user. "
            "If a bot command would help (/mood for mood tracking, /motivateMe "
            "for motivation, /settings for preferences), mention it briefly."
        )
    context = f"{_name_context(language, first_name)}{_mood_context(language, mood_score)}"
    return f"{base}{extra}\n{context}" if context else f"{base}{extra}"


async def generate_chat_reply(language: str, user_message: str,
                              mood_score: Optional[int] = None,
                              history: Optional[List[Dict[str, str]]] = None,
                              first_name: Optional[str] = None) -> Optional[str]:
    """
    Generate an empathetic reply to a free-text message from the user.

    history carries prior conversation turns ({'role', 'content'} dicts)
    so the AI can refer back to what was said earlier.
    """
    return await generate_response(
        user_message,
        instructions=_chat_instructions(language, mood_score, first_name),
        history=history,
    )


async def generate_mood_reaction(language: str, mood_score: int,
                                 first_name: Optional[str] = None) -> Optional[str]:
    """Generate an individual reaction to a fresh mood entry."""
    if language == 'de':
        prompt = (
            f"{_name_context(language, first_name)}"
            f"Der Nutzer hat gerade seine Stimmung mit {mood_score}/10 erfasst "
            "(1=sehr schlecht, 10=sehr gut). Reagiere individuell darauf: "
            "Bei niedriger Stimmung tröstend und stabilisierend, bei mittlerer "
            "ermutigend, bei hoher freue dich mit und bestärke."
        )
    else:
        prompt = (
            f"{_name_context(language, first_name)}"
            f"The user just logged their mood as {mood_score}/10 "
            "(1=very low, 10=very good). React individually: comforting and "
            "grounding for low moods, encouraging for medium, celebrate and "
            "reinforce for high moods."
        )

    return await generate_response(prompt, instructions=_instructions(language))
