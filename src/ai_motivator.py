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


def _facts_context(language: str, facts: Optional[List[str]]) -> str:
    if not facts:
        return ""
    fact_lines = "\n".join(f"- {fact}" for fact in facts)
    if language == 'de':
        return (
            "Das weißt du aus früheren Gesprächen über den Nutzer "
            "(nutze es, wo es passt, aber zähle es nicht auf):\n"
            f"{fact_lines}\n"
        )
    return (
        "This is what you know about the user from earlier conversations "
        "(use it where fitting, but don't recite it):\n"
        f"{fact_lines}\n"
    )


def _mood_context(language: str, mood_score: Optional[int]) -> str:
    if mood_score is None:
        return ""
    if language == 'de':
        return f"Die zuletzt erfasste Stimmung des Nutzers ist {mood_score}/10 (1=sehr schlecht, 10=sehr gut). "
    return f"The user's last logged mood is {mood_score}/10 (1=very low, 10=very good). "


async def generate_motivation(language: str, mood_score: Optional[int] = None,
                              first_name: Optional[str] = None,
                              facts: Optional[List[str]] = None) -> Optional[str]:
    """Generate a personalized motivational message."""
    context = (
        f"{_name_context(language, first_name)}"
        f"{_mood_context(language, mood_score)}"
        f"{_facts_context(language, facts)}"
    )
    if language == 'de':
        prompt = (
            f"{context}"
            "Schreibe eine kurze, persönliche Motivationsnachricht, die zur Stimmung passt."
        )
    else:
        prompt = (
            f"{context}"
            "Write a short, personal motivational message that fits the mood."
        )

    return await generate_response(prompt, instructions=_instructions(language))


def _chat_instructions(language: str, mood_score: Optional[int],
                       first_name: Optional[str],
                       facts: Optional[List[str]] = None,
                       summary: Optional[str] = None) -> str:
    """Instructions for conversational replies, including user context."""
    base = _instructions(language)
    if language == 'de':
        extra = (
            "\nDu führst ein fortlaufendes Gespräch mit dem Nutzer. "
            "Wenn ein Bot-Befehl besser helfen würde (/mood für Stimmungs-Tracking, "
            "/motivateMe für Motivation, /settings für Einstellungen), erwähne ihn kurz."
        )
        summary_part = (
            f"\nZusammenfassung des bisherigen Gesprächs:\n{summary}\n" if summary else ""
        )
    else:
        extra = (
            "\nYou are having an ongoing conversation with the user. "
            "If a bot command would help (/mood for mood tracking, /motivateMe "
            "for motivation, /settings for preferences), mention it briefly."
        )
        summary_part = (
            f"\nSummary of the conversation so far:\n{summary}\n" if summary else ""
        )
    context = (
        f"{_name_context(language, first_name)}"
        f"{_mood_context(language, mood_score)}"
        f"{_facts_context(language, facts)}"
        f"{summary_part}"
    )
    return f"{base}{extra}\n{context}" if context else f"{base}{extra}"


async def generate_chat_reply(language: str, user_message: str,
                              mood_score: Optional[int] = None,
                              history: Optional[List[Dict[str, str]]] = None,
                              first_name: Optional[str] = None,
                              facts: Optional[List[str]] = None,
                              summary: Optional[str] = None) -> Optional[str]:
    """
    Generate an empathetic reply to a free-text message from the user.

    history carries the recent verbatim turns ({'role', 'content'} dicts),
    summary the rolling summary of everything older, and facts the long-term
    knowledge about the user.
    """
    return await generate_response(
        user_message,
        instructions=_chat_instructions(language, mood_score, first_name, facts, summary),
        history=history,
    )


async def generate_mood_reaction(language: str, mood_score: int,
                                 first_name: Optional[str] = None,
                                 facts: Optional[List[str]] = None) -> Optional[str]:
    """Generate an individual reaction to a fresh mood entry."""
    if language == 'de':
        prompt = (
            f"{_name_context(language, first_name)}"
            f"{_facts_context(language, facts)}"
            f"Der Nutzer hat gerade seine Stimmung mit {mood_score}/10 erfasst "
            "(1=sehr schlecht, 10=sehr gut). Reagiere individuell darauf: "
            "Bei niedriger Stimmung tröstend und stabilisierend, bei mittlerer "
            "ermutigend, bei hoher freue dich mit und bestärke."
        )
    else:
        prompt = (
            f"{_name_context(language, first_name)}"
            f"{_facts_context(language, facts)}"
            f"The user just logged their mood as {mood_score}/10 "
            "(1=very low, 10=very good). React individually: comforting and "
            "grounding for low moods, encouraging for medium, celebrate and "
            "reinforce for high moods."
        )

    return await generate_response(prompt, instructions=_instructions(language))


def _format_transcript(messages: List[Dict[str, str]]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)


async def summarize_conversation(language: str, old_summary: Optional[str],
                                 messages: List[Dict[str, str]]) -> Optional[str]:
    """
    Fold older conversation turns into the rolling summary.

    Returns the new summary text, or None if the AI call failed (in that
    case the caller must keep the messages unsummarized and retry later).
    """
    transcript = _format_transcript(messages)
    if language == 'de':
        instructions = (
            "Du verdichtest den Gesprächsverlauf eines Mental-Health-Support-Bots "
            "zu einer Zusammenfassung für zukünftige Antworten. Erhalte unbedingt: "
            "die emotionale Lage des Nutzers und ihre Entwicklung, wichtige "
            "Lebensumstände und Ereignisse, was dem Nutzer hilft oder schadet, "
            "sowie jegliche Krisenhinweise (diese niemals wegkürzen). "
            "Schreibe sachlich und kompakt, maximal 250 Wörter, keine Aufzählung "
            "von Belanglosem."
        )
        old_part = f"Bisherige Zusammenfassung:\n{old_summary}\n\n" if old_summary else ""
        prompt = (
            f"{old_part}Neue Gesprächsabschnitte:\n{transcript}\n\n"
            "Erstelle die aktualisierte Gesamtzusammenfassung."
        )
    else:
        instructions = (
            "You condense the conversation history of a mental health support bot "
            "into a summary used for future replies. You must preserve: the user's "
            "emotional state and how it developed, important life circumstances and "
            "events, what helps or harms the user, and any crisis indicators "
            "(never compress those away). Write factually and compactly, at most "
            "250 words, no trivia."
        )
        old_part = f"Previous summary:\n{old_summary}\n\n" if old_summary else ""
        prompt = (
            f"{old_part}New conversation segments:\n{transcript}\n\n"
            "Produce the updated overall summary."
        )

    return await generate_response(prompt, instructions=instructions)


async def extract_user_facts(language: str, existing_facts: List[str],
                             messages: List[Dict[str, str]]) -> Optional[List[str]]:
    """
    Update the long-term fact list about the user from recent conversation.

    Returns the full updated fact list, or None if the AI call failed.
    """
    transcript = _format_transcript(messages)
    if language == 'de':
        instructions = (
            "Du pflegst eine Liste langlebiger Fakten über den Nutzer eines "
            "Mental-Health-Support-Bots (z. B. Beziehungen, Haustiere, Arbeit, "
            "was ihm hilft oder schadet, wiederkehrende Themen). "
            "Behalte bestehende Fakten, außer sie werden widerlegt oder "
            "aktualisiert. Nimm nur langfristig Relevantes auf, keine "
            "Tagesstimmungen. Maximal 15 Fakten. "
            "Antworte NUR mit der vollständigen Liste, ein Fakt pro Zeile, "
            "ohne Nummerierung oder Aufzählungszeichen."
        )
        facts_part = "\n".join(existing_facts) if existing_facts else "(noch keine)"
        prompt = (
            f"Bestehende Fakten:\n{facts_part}\n\n"
            f"Neue Gesprächsabschnitte:\n{transcript}\n\n"
            "Gib die aktualisierte Faktenliste aus."
        )
    else:
        instructions = (
            "You maintain a list of long-lived facts about the user of a mental "
            "health support bot (e.g. relationships, pets, work, what helps or "
            "harms them, recurring topics). Keep existing facts unless they are "
            "contradicted or updated. Only include long-term relevant information, "
            "no day-to-day moods. At most 15 facts. "
            "Reply ONLY with the complete list, one fact per line, "
            "without numbering or bullet points."
        )
        facts_part = "\n".join(existing_facts) if existing_facts else "(none yet)"
        prompt = (
            f"Existing facts:\n{facts_part}\n\n"
            f"New conversation segments:\n{transcript}\n\n"
            "Output the updated fact list."
        )

    response = await generate_response(prompt, instructions=instructions)
    if response is None:
        return None

    facts = [line.strip().lstrip('-•* ') for line in response.splitlines() if line.strip()]
    return facts[:15]
