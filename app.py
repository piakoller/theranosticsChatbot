"""
Simple Patient Education Chatbot User Study
A clean, focused application for testing chatbot effectiveness in patient education
"""

import gradio as gr
from study_config import APP_TITLE, MAX_WIDTH, APP_CSS
from study_sections import create_demographics_section, create_attitude_section, create_chatbot_section, create_feedback_section, create_thank_you_section, create_consent_section
from study_handlers import proceed_to_chatbot, save_demographics, save_attitude, handle_chatbot_message, proceed_to_feedback, submit_study, clear_chat, save_consent
from study_utils import generate_session_id

import base64
with open('assets/TheranosticChatbotIcon.svg', 'rb') as f:
    svg_data = base64.b64encode(f.read()).decode()

def create_study_app():
    """Create the main study application"""
    
    with gr.Blocks(
        title=APP_TITLE,
        theme=gr.themes.Soft(),
        css=APP_CSS
    ) as app:
        # Session state
        session_id = gr.State(value=generate_session_id())
        question_count = gr.State(value=0)

        gr.HTML(f"""
        <div class='app-header'>
        <span class='icon'>
            <img src='data:image/svg+xml;base64,{svg_data}' style='width:5em;height:5em;display:inline-block' />
        </span>
        <h1>Theranostik-Chatbot</h1>
        </div>
        """)

        # Create all sections (consent shown first)
        consent_section, consent_radio, consent_next = create_consent_section()
        demographics_section, age, gender, education, medical_background, chatbot_experience, demo_next = create_demographics_section()
        attitude_section, prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, attitude_next = create_attitude_section()
        chatbot_section, chatbot, msg, send_btn, clear_btn, question_counter, chat_next = create_chatbot_section()
        feedback_section, usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, submit_btn = create_feedback_section()
        thank_you_section = create_thank_you_section()

        # Wire up event handlers
        # After demographics, save and go to attitude section
        demo_next.click(
            save_demographics,
            inputs=[age, gender, education, medical_background, chatbot_experience, session_id],
            outputs=[demographics_section, attitude_section, session_id]
        )

        # Consent flow: proceed to demographics only if consent given
        consent_next.click(
            save_consent,
            inputs=[consent_radio, session_id],
            outputs=[consent_section, demographics_section, session_id]
        )

        # Attitude section continues to chatbot
        attitude_next.click(
            save_attitude,
            inputs=[prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, session_id],
            outputs=[attitude_section, chatbot_section, session_id]
        )

        send_btn.click(
            handle_chatbot_message,
            inputs=[msg, chatbot, session_id, question_count],
            outputs=[msg, chatbot, question_count, chat_next]
        )

        msg.submit(
            handle_chatbot_message,
            inputs=[msg, chatbot, session_id, question_count],
            outputs=[msg, chatbot, question_count, chat_next]
        )

        clear_btn.click(
            clear_chat,
            outputs=[chatbot, question_count, chat_next]
        )

        chat_next.click(
            proceed_to_feedback,
            inputs=[session_id],
            outputs=[demographics_section, chatbot_section, feedback_section, session_id]
        )

        submit_btn.click(
            submit_study,
            inputs=[usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, session_id],
            outputs=[demographics_section, chatbot_section, feedback_section, thank_you_section, session_id]
        )

        return app


if __name__ == "__main__":
    print("🔄 Patient Education Chatbot Study initialized")
    app = create_study_app()
    app.launch(debug=True, share=False, favicon_path="assets/TheranosticFavicon.ico")