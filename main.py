"""
IAEA Theranostics Chatbot - Main Application
============================================

A comprehensive patient education chatbot for theranostics and nuclear medicine,
featuring both normal and expert chatbot modes with study functionality.
"""

import gradio as gr
import base64
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import study components
from src.study.config import MAX_WIDTH, APP_CSS, PREDEFINED_QUESTIONS
from src.study.sections import (
    create_demographics_section, 
    create_chatbot_section, 
    create_feedback_section, 
    create_thank_you_section, 
    create_consent_section, 
    create_chatbot_selection_section
)
from src.study.handlers import (
    proceed_to_chatbot, 
    save_demographics, 
    handle_chatbot_message, 
    proceed_to_feedback, 
    submit_study, 
    clear_chat, 
    save_consent, 
    handle_predefined_question, 
    handle_follow_up_question, 
    save_chatbot_selection
)
from src.study.utils import generate_user_id

# Load app icon
try:
    with open('assets/TheranosticChatbotIcon.svg', 'rb') as f:
        svg_data = base64.b64encode(f.read()).decode()
except FileNotFoundError:
    print("⚠️ Warning: App icon not found")
    svg_data = ""

def update_chatbot_type_display(chatbot_type_value):
    """Update the chatbot type indicator"""
    if chatbot_type_value == "expert":
        return gr.update(value='<div class="chatbot-type-indicator expert">Experten Chatbot</div>', visible=True)
    elif chatbot_type_value == "normal":
        return gr.update(value='<div class="chatbot-type-indicator normal">Normaler Chatbot</div>', visible=True)
    else:
        return gr.update(value='', visible=False)

def create_study_app():
    """Create the main study application"""
    
    with gr.Blocks(
        theme="soft",
        css=APP_CSS
    ) as app:
        # Session state
        session_id = gr.State(value=generate_user_id())
        question_count = gr.State(value=0)
        chatbot_type = gr.State(value="normal")  # Default to normal chatbot

        # Static header
        if svg_data:
            gr.HTML(f"""
            <div class='app-header'>
            <span class='icon'>
                <img src='data:image/svg+xml;base64,{svg_data}' style='width:5em;height:5em;display:inline-block' />
            </span>
            <h1>Theranostik Chatbot</h1>
            </div>
            """)
        else:
            gr.HTML("""
            <div class='app-header'>
            <h1>Theranostik Chatbot</h1>
            </div>
            """)
        
        # Dynamic chatbot type indicator (separate from header)
        chatbot_type_display = gr.HTML("", visible=False)

        # Create all sections (consent shown first)
        consent_section, consent_agreed, consent_proceed_btn = create_consent_section()
        chatbot_selection_section, chatbot_type_radio, selection_proceed_btn = create_chatbot_selection_section()
        demographics_section, age, gender, education, medical_background, chatbot_experience, treatment_reason, demographics_submit_btn = create_demographics_section()
        chatbot_section, conversation_history, question_buttons, question_texts, follow_up_section, follow_up_input, send_btn, clear_btn, question_counter, feedback_btn = create_chatbot_section()
        feedback_section, usefulness_rating, accuracy_rating, ease_of_use_rating, trust_rating, would_use_rating, improvements_text, overall_feedback_text, feedback_submit_btn = create_feedback_section()
        thank_you_section = create_thank_you_section()

        # Event handlers
        consent_proceed_btn.click(
            save_consent,
            inputs=[session_id, consent_agreed],
            outputs=[
                consent_section, 
                chatbot_selection_section
            ]
        )

        selection_proceed_btn.click(
            save_chatbot_selection,
            inputs=[session_id, chatbot_type_radio],
            outputs=[
                chatbot_type,
                chatbot_selection_section, 
                demographics_section
            ]
        )

        chatbot_type.change(
            update_chatbot_type_display,
            inputs=[chatbot_type],
            outputs=[chatbot_type_display]
        )

        demographics_submit_btn.click(
            save_demographics,
            inputs=[
                session_id,
                age,
                gender,
                education,
                medical_background,
                chatbot_experience
            ],
            outputs=[
                demographics_section,
                chatbot_section
            ]
        )

        feedback_btn.click(
            proceed_to_chatbot,
            outputs=[
                feedback_btn,
                question_buttons,
                follow_up_input,
                send_btn,
                clear_btn
            ]
        )

        # Predefined question handlers
        for i, question in enumerate(PREDEFINED_QUESTIONS):
            question_buttons.select(
                lambda evt, q_num=i: handle_predefined_question(evt, q_num) if evt.index == q_num else (gr.update(), gr.update(), gr.update()),
                inputs=[],
                outputs=[
                    conversation_history,
                    question_count,
                    session_id
                ]
            )

        # Follow-up question handler
        def handle_follow_up_wrapper(text, history, q_count, user_id, bot_type):
            return handle_follow_up_question(text, history, q_count, user_id, bot_type)

        send_btn.click(
            handle_follow_up_wrapper,
            inputs=[
                follow_up_input,
                conversation_history,
                question_count,
                session_id,
                chatbot_type
            ],
            outputs=[
                conversation_history,
                follow_up_input,
                question_count
            ]
        )

        follow_up_input.submit(
            handle_follow_up_wrapper,
            inputs=[
                follow_up_input,
                conversation_history,
                question_count,
                session_id,
                chatbot_type
            ],
            outputs=[
                conversation_history,
                follow_up_input,
                question_count
            ]
        )

        clear_btn.click(
            clear_chat,
            outputs=[conversation_history]
        )

        feedback_btn.click(
            proceed_to_feedback,
            outputs=[
                chatbot_section,
                feedback_section
            ]
        )

        feedback_submit_btn.click(
            submit_study,
            inputs=[
                session_id,
                usefulness_rating,
                accuracy_rating,
                ease_of_use_rating,
                trust_rating,
                would_use_rating,
                improvements_text,
                overall_feedback_text,
                chatbot_type
            ],
            outputs=[
                feedback_section,
                thank_you_section
            ]
        )

    return app

def main():
    """Main application entry point"""
    print("🚀 Starting IAEA Theranostics Chatbot...")
    
    # Create and launch the app
    app = create_study_app()
    
    # Launch configuration
    try:
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            favicon_path="assets/TheranosticFavicon.ico" if os.path.exists("assets/TheranosticFavicon.ico") else None
        )
    except Exception as e:
        print(f"❌ Failed to launch application: {e}")
        print("💡 Make sure port 7860 is available and try again")

if __name__ == "__main__":
    main()