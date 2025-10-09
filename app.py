"""
Simple Patient Education Chatbot User Study
A clean, focused application for testing chatbot effectiveness in patient education
"""

import gradio as gr
from study_config import APP_TITLE, MAX_WIDTH, APP_CSS
from study_sections import create_demographics_section, create_chatbot_section, create_feedback_section
from study_handlers import proceed_to_chatbot, handle_chatbot_message, proceed_to_feedback, submit_study, clear_chat
from study_utils import generate_session_id, get_question_counter_text

def create_simple_study_app():
    """Create the main study application"""
    
    with gr.Blocks(
        title=APP_TITLE,
        theme=gr.themes.Soft(),
        css=APP_CSS
    ) as app:
        
        # Session state
        session_id = gr.State(value=generate_session_id())
        current_section = gr.State(value="demographics")
        question_count = gr.State(value=0)
        
        # Create all sections
        demographics_section, age, gender, education, medical_background, chatbot_experience, demo_next = create_demographics_section()
        chatbot_section, chatbot, msg, send_btn, clear_btn, question_counter, chat_next = create_chatbot_section()
        feedback_section, usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, submit_btn, completion_message = create_feedback_section()
        
        # Wire up event handlers
        demo_next.click(
            proceed_to_chatbot,
            inputs=[age, gender, education, medical_background, chatbot_experience, session_id],
            outputs=[demographics_section, chatbot_section, feedback_section, session_id]
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
            outputs=[completion_message]
        )
        
    return app


if __name__ == "__main__":
    print("🔄 Patient Education Chatbot Study initialized")
    app = create_simple_study_app()
    app.launch(debug=True, share=False)