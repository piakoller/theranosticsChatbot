"""
Minimal Form Handlers Module

This file provides a small, focused FormHandler used by the UI to:
- expose per-section help content
- provide a contextual helper for the chatbot when the user asks about the form
- save form submissions via the existing `conversation_logger` adapter

The goal is to remove unused/duplicated code while preserving the public
interface (`form_handler`) consumed by other modules.
"""

from datetime import datetime
from core.chatbot import theranostics_bot
from core.conversation import conversation_logger
from typing import Optional


class FormHandler:
    """Compact form handler used by the UI.

    Methods kept small and well-defined so other modules can call them.
    """

    def __init__(self):
        self.section_help_content = {
            "a": {
                "title": "Section A: Demographics",
                "description": "This section asks about your basic information like age, gender, diagnosis, and treatment history.",
                "tips": [
                    "Be accurate with dates and medical history",
                    "Include all relevant treatments you've received",
                    "Approximate dates are fine if unsure"
                ],
                "color": "#dbeafe",
                "border": "#3b82f6"
            },
            "b": {
                "title": "Section B: Treatment Experience",
                "description": "This section focuses on your actual treatment experience, side effects, and recovery.",
                "tips": [
                    "Rate based on your personal experience",
                    "Include physical and emotional impacts",
                    "Consider the entire treatment period"
                ],
                "color": "#f0fdf4",
                "border": "#22c55e"
            },
            "c": {
                "title": "Section C: Feedback & Comments",
                "description": "This section asks for your detailed feedback and suggestions for improvement.",
                "tips": [
                    "Be honest about both positive and negative experiences",
                    "Share specific examples when possible",
                    "Think about what would have helped you feel more prepared"
                ],
                "color": "#fef3c7",
                "border": "#f59e0b"
            }
        }

    def get_section_help(self, section_key: str) -> dict:
        """Return the help content for the given section (a, b, c)."""
        return self.section_help_content.get(section_key.lower(), {})

    def form_contextual_response(self, message: str, history: list, section: str = "none") -> str:
        """Return a model response targeted to form-related questions.

        This simply forwards to the existing chatbot helper with an adjusted
        message when the user explicitly asks about the form.
        """
        if not message:
            return ""

        prefix = ""
        if section and section.lower() in self.section_help_content:
            prefix = f"[Section {section.upper()} Form Help] "
        elif any(k in message.lower() for k in ("form", "survey", "section", "rating", "feedback")):
            prefix = "[Form Help] "

        enhanced = prefix + message
        return theranostics_bot.chatbot_response(enhanced, history, context="form_help", section=section)

    def submit_form_data(self, form_data: dict, session_id: Optional[str] = None) -> str:
        """Save the form submission via conversation_logger and return a message."""
        try:
            payload = form_data.copy()
            payload.setdefault("submission_timestamp", datetime.now().isoformat())
            payload.setdefault("form_version", "v1.0")
            # conversation_logger handles MongoDB vs file backup based on env flags
            result = conversation_logger.save_form_submission(payload, user_id=session_id)
            return result
        except Exception as e:
            print(f"❌ Error saving form submission: {e}")
            return f"Error: {str(e)}"


# Global form handler instance (kept for compatibility)
form_handler = FormHandler()