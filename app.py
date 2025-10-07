"""
Theranostics Chatbot - User Study Application
A comprehensive user study interface for evaluating the theranostics chatbot prototype
"""

import gradio as gr
import uuid
import json
from datetime import datetime
from logging_module import conversation_logger
from chatbot import theranostics_bot
from styles import MAIN_CSS
from ui_components import UIComponents, StudySections, EventHandlers


class UserStudy:
    """Manages the user study data collection and interface"""
    
    def __init__(self):
        self.user_sessions = {}
        
    def generate_user_id(self):
        """Generate a unique user ID for each participant"""
        user_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"study_{user_id}_{timestamp}"
        
        self.user_sessions[session_id] = {
            "start_time": datetime.now().isoformat(),
            "responses": {},
            "current_section": "A",
            "completed_sections": [],
            "question_count": 0
        }
        
        return session_id
    
    def save_section_data(self, session_id, section, data):
        """Save data for a specific section and mark as completed"""
        if session_id in self.user_sessions:
            self.user_sessions[session_id]["responses"][section] = data
            self.user_sessions[session_id]["last_updated"] = datetime.now().isoformat()
            
            # Mark section as completed
            if section not in self.user_sessions[session_id]["completed_sections"]:
                self.user_sessions[session_id]["completed_sections"].append(section)
            
            # Also save to MongoDB
            study_data = {
                "session_id": session_id,
                "section": section,
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "study_type": "theranostics_chatbot_evaluation"
            }
            conversation_logger.save_form_submission(study_data)
    
    def advance_to_next_section(self, session_id):
        """Advance user to the next section"""
        if session_id in self.user_sessions:
            current = self.user_sessions[session_id]["current_section"]
            section_order = ["A", "B", "C", "D", "E", "F"]
            
            try:
                current_index = section_order.index(current)
                if current_index < len(section_order) - 1:
                    next_section = section_order[current_index + 1]
                    self.user_sessions[session_id]["current_section"] = next_section
                    return next_section
            except ValueError:
                pass
        return None
    
    def can_access_section(self, session_id, section):
        """Check if user can access a specific section"""
        if session_id not in self.user_sessions:
            return False
        
        current_section = self.user_sessions[session_id]["current_section"]
        section_order = ["A", "B", "C", "D", "E", "F"]
        
        try:
            current_index = section_order.index(current_section)
            target_index = section_order.index(section)
            return target_index <= current_index
        except ValueError:
            return False
    
    def increment_question_count(self, session_id):
        """Increment question count for Section C"""
        if session_id in self.user_sessions:
            self.user_sessions[session_id]["question_count"] += 1
            return self.user_sessions[session_id]["question_count"]
        return 0
    
    def get_question_count(self, session_id):
        """Get current question count"""
        if session_id in self.user_sessions:
            return self.user_sessions[session_id]["question_count"]
        return 0
    
    def get_chatbot_response(self, message, session_id, lang='en'):
        """Get response from chatbot and increment question counter

        lang: 'en' or 'de' to control system prompt language
        """
        response = theranostics_bot.chatbot_response(message, [], context="user_study", section="C", lang=lang)

        # Increment question count
        count = self.increment_question_count(session_id)

        # Log the interaction
        conversation_logger.log_conversation(
            user_input=message,
            bot_response=response,
            context="user_study",
            model_used=theranostics_bot.get_current_model(),
            metadata={"session_id": session_id, "question_number": count, "lang": lang}
        )

        return response, count


# Global study manager
study_manager = UserStudy()


def create_app():
    """Create the user study application"""
    
    with gr.Blocks(
        title="Theranostics Chatbot User Study",
        theme=gr.themes.Soft(),
        css=MAIN_CSS
    ) as demo:
        
        # Initialize session
        session_id = gr.State(value=study_manager.generate_user_id())
        current_section = gr.State(value="A")
        question_count = gr.State(value=0)
        
        # Language state (created early so header can use it)
        chosen_lang = gr.State(value='en')

        # Header
        with gr.Row():
            UIComponents.create_header(lang=chosen_lang)
        
        # Participant ID is generated and stored in session state but not shown
        # in the UI to participants.
        
        # Language selection: let participant choose English or German
        lang_choice = gr.Radio(label="Select language / Sprache wählen:", choices=["English", "Deutsch"], value="English")
        lang_sel_btn = gr.Button("Start / Starten")

        # Create both English and German layouts (hidden by default)
        en_section_groups, en_forms, en_question_counter, en_progress_display, en_history_display = StudySections.create_study_layout(lang='en', prefix='en', initially_visible=False)
        de_section_groups, de_forms, de_question_counter, de_progress_display, de_history_display = StudySections.create_study_layout(lang='de', prefix='de', initially_visible=False)

        # Helper to toggle visibility of the two language layouts when Start is pressed
        def setup_language(lang_radio_value, session_id_val=None):
            """Show the chosen language layout and persist the choice for the session.

            This function no longer hides the language controls so participants
            can change language mid-study.
            """
            lang = 'de' if lang_radio_value and lang_radio_value.lower().startswith('d') else 'en'
            chosen_lang.value = lang

            # Persist language choice in the session record if available
            try:
                if session_id_val and session_id_val in study_manager.user_sessions:
                    study_manager.user_sessions[session_id_val]['lang'] = lang
            except Exception:
                pass

            # Build visibility updates for en and de sections (A..F)
            sections = ['A', 'B', 'C', 'D', 'E', 'F']
            outputs = []
            for s in sections:
                # English sections visible if lang == 'en'
                outputs.append(gr.update(visible=(lang == 'en')))
            for s in sections:
                # German sections visible if lang == 'de'
                outputs.append(gr.update(visible=(lang == 'de')))

            # Return only section visibility updates (do NOT hide the language controls)
            return tuple(outputs)

        # Wire start button to show the chosen language layout (outputs: en A..F, de A..F, hide lang_choice, hide lang_sel_btn)
        lang_sel_btn.click(
            fn=setup_language,
            inputs=[lang_choice, session_id],
            outputs=[
                en_section_groups['A'], en_section_groups['B'], en_section_groups['C'], en_section_groups['D'], en_section_groups['E'], en_section_groups['F'],
                de_section_groups['A'], de_section_groups['B'], de_section_groups['C'], de_section_groups['D'], de_section_groups['E'], de_section_groups['F'],
            ]
        )

        # Allow participants to change language at any time by listening to
        # changes on the language selector. This uses the same handler and
        # persists the choice for the session.
        lang_choice.change(
            fn=setup_language,
            inputs=[lang_choice, session_id],
            outputs=[
                en_section_groups['A'], en_section_groups['B'], en_section_groups['C'], en_section_groups['D'], en_section_groups['E'], en_section_groups['F'],
                de_section_groups['A'], de_section_groups['B'], de_section_groups['C'], de_section_groups['D'], de_section_groups['E'], de_section_groups['F'],
            ]
        )
        
        # Create event handlers
        chatbot_handler = EventHandlers.create_chatbot_handler(study_manager)
        section_advance_handler = EventHandlers.create_section_advance_handler(study_manager)
        section_back_handler = EventHandlers.create_section_back_handler(study_manager)
        completion_handler = EventHandlers.create_completion_handler(study_manager)

        # Helper to wire handlers for a given language set (loop-driven to avoid repetition)
        def wire_language_handlers(section_groups, forms, question_counter, progress_display, history_display):
            # Chatbot handlers (Section C)
            forms['C']["send_btn"].click(
                chatbot_handler,
                inputs=[forms['C']["user_input"], forms['C']["chatbot_interface"], session_id, question_count, chosen_lang],
                outputs=[forms['C']["chatbot_interface"], forms['C']["user_input"], question_count, question_counter, forms['C']["next_button"]]
            )

            forms['C']["user_input"].submit(
                chatbot_handler,
                inputs=[forms['C']["user_input"], forms['C']["chatbot_interface"], session_id, question_count, chosen_lang],
                outputs=[forms['C']["chatbot_interface"], forms['C']["user_input"], question_count, question_counter, forms['C']["next_button"]]
            )

            # Define section order and the fields to collect for each section when advancing
            section_order = ['A', 'B', 'C', 'D', 'E', 'F']
            fields_map = {
                'A': ["consent", "participant_role", "age_range", "gender", "education", "experience", "digital_comfort"],
                'B': ["baseline_knowledge", "chatbot_use", "trust_automated", "info_channels", "chatbot_expectations", "chatbot_concerns"],
                'C': [],  # handled specially (uses question_count)
                'D': ["prototype_opened", "perceived_accuracy", "perceived_usefulness", "act_on_advice", "anxiety_change", "perceived_limitations", "sus1", "sus2"],
                'E': ["scenario1_trust", "scenario1_reason", "scenario2_trust", "scenario2_reason", "scenario3_trust", "scenario3_reason"],
                'F': ["overall_satisfaction", "improvements", "recommend_tool", "additional_feedback"]
            }

            # Helper to produce the common visibility outputs (A..F)
            def visibility_outputs():
                return [section_groups[s] for s in section_order]

            # Create advance (Next) handlers programmatically
            def make_advance_handler(from_s, to_s):
                def _handler(*args):
                    # args order: session_id, current_section, *form_fields
                    return section_advance_handler(args[1], args[0], from_s, to_s, *args[2:])
                return _handler

            # Create back handlers programmatically
            def make_back_handler(from_s, to_s):
                def _handler(*args):
                    return section_back_handler(args[1], args[0], from_s, to_s, *args[2:])
                return _handler

            for idx, sec in enumerate(section_order):
                # Next / Advance (for all except F)
                if sec != 'F' and 'next_button' in forms.get(sec, {}):
                    next_sec = section_order[idx + 1]
                    if sec == 'C':
                        inputs = [session_id, current_section, question_count]
                    else:
                        inputs = [session_id, current_section] + [forms[sec][k] for k in fields_map.get(sec, [])]

                    outputs = visibility_outputs() + [forms[sec]["status"], progress_display, history_display]
                    forms[sec]["next_button"].click(make_advance_handler(sec, next_sec), inputs=inputs, outputs=outputs)

                # Back (for all except A)
                if sec != 'A' and 'back_button' in forms.get(sec, {}):
                    prev_sec = section_order[idx - 1]
                    inputs = [session_id, current_section]
                    outputs = visibility_outputs() + [forms[sec]["status"], progress_display, history_display]
                    forms[sec]["back_button"].click(make_back_handler(sec, prev_sec), inputs=inputs, outputs=outputs)

            # Completion handler for F
            if 'complete_button' in forms.get('F', {}):
                forms['F']["complete_button"].click(
                    completion_handler,
                    inputs=[session_id] + [forms['F'][key] for key in fields_map['F']],
                    outputs=[forms['F']["completion_message"]]
                )

        # Wire handlers for both English and German layouts (include progress and history displays)
        wire_language_handlers(en_section_groups, en_forms, en_question_counter, en_progress_display, en_history_display)
        wire_language_handlers(de_section_groups, de_forms, de_question_counter, de_progress_display, de_history_display)
        
        return demo


def main():
    """Main entry point of the application"""
    print("🔄 Theranostics Chatbot User Study initialized")
    
    # Create and launch the app
    demo = create_app()
    demo.launch(debug=True)


if __name__ == "__main__":
    main()