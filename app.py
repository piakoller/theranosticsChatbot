"""
Simple Patient Education Chatbot User Study
A clean, focused application for testing chatbot effectiveness in patient education
"""

import gradio as gr
from study_config import MAX_WIDTH, APP_CSS, PREDEFINED_QUESTIONS
from study_sections import create_demographics_section, create_chatbot_section, create_feedback_section, create_thank_you_section, create_consent_section, create_chatbot_selection_section
from study_handlers import proceed_to_chatbot, save_demographics, handle_chatbot_message, proceed_to_feedback, submit_study, clear_chat, save_consent, handle_predefined_question, handle_follow_up_question
from study_utils import generate_session_id

import base64
with open('assets/TheranosticChatbotIcon.svg', 'rb') as f:
    svg_data = base64.b64encode(f.read()).decode()

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
        session_id = gr.State(value=generate_session_id())
        question_count = gr.State(value=0)
        chatbot_type = gr.State(value="normal")  # Default to normal chatbot

        # Static header
        gr.HTML(f"""
        <div class='app-header'>
        <span class='icon'>
            <img src='data:image/svg+xml;base64,{svg_data}' style='width:5em;height:5em;display:inline-block' />
        </span>
        <h1>Theranostik Chatbot</h1>
        </div>
        """)
        
        # Dynamic chatbot type indicator (separate from header)
        chatbot_type_display = gr.HTML("", visible=False)

        # Create all sections (consent shown first)
        consent_section, consent_radio, consent_next = create_consent_section()
        chatbot_selection_section, chatbot_type_radio, selection_next = create_chatbot_selection_section()
        demographics_section, age, gender, education, medical_background, chatbot_experience, treatment_reason, demo_next = create_demographics_section()
        # attitude_section, prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, attitude_next = create_attitude_section()
        chatbot_section, chatbot, question_buttons, question_texts, follow_up_section, msg, send_btn, clear_btn, question_counter, chat_next = create_chatbot_section()
        feedback_section, usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, submit_btn = create_feedback_section()
        thank_you_section = create_thank_you_section()

        # Wire up event handlers
        # After demographics, go directly to chatbot section (skip attitude)
        demo_next.click(
            lambda age_val, gender_val, edu_val, med_bg_val, chat_exp_val, treat_reason_val, sid: (
                save_demographics(age_val, gender_val, edu_val, med_bg_val, chat_exp_val, treat_reason_val, sid),
                gr.update(visible=False), 
                gr.update(visible=True)
            )[1:], # Return from the 2nd element onwards
            inputs=[age, gender, education, medical_background, chatbot_experience, treatment_reason, session_id],
            outputs=[demographics_section, chatbot_section]
        )

        # Consent flow: proceed to chatbot selection only if consent given
        consent_next.click(
            lambda consent_val, sid: (
                save_consent(consent_val, sid),
                gr.update(visible=False),
                gr.update(visible=True)
            )[1:], # Return from the 2nd element onwards
            inputs=[consent_radio, session_id],
            outputs=[consent_section, chatbot_selection_section]
        )

        # Chatbot selection: proceed to demographics after selection
        selection_next.click(
            lambda chatbot_choice, sid: (
                gr.update(visible=False),
                gr.update(visible=True),
                chatbot_choice,
                update_chatbot_type_display(chatbot_choice)
            ),
            inputs=[chatbot_type_radio, session_id],
            outputs=[chatbot_selection_section, demographics_section, chatbot_type, chatbot_type_display]
        )

        # Attitude section commented out - skip directly to chatbot
        # attitude_next.click(
        #     save_attitude,
        #     inputs=[prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, session_id],
        #     outputs=[attitude_section, chatbot_section, session_id]
        # )

        send_btn.click(
            handle_follow_up_question,
            inputs=[msg, chatbot, session_id, question_count, chatbot_type],
            outputs=[msg, chatbot, question_count, question_counter, follow_up_section, chat_next]
        )

        msg.submit(
            handle_follow_up_question,
            inputs=[msg, chatbot, session_id, question_count, chatbot_type],
            outputs=[msg, chatbot, question_count, question_counter, follow_up_section, chat_next]
        )

        # Wire up predefined question buttons
        # Each button gets its corresponding question text passed as a hidden input
        for i, (btn, question_text) in enumerate(zip(question_buttons, question_texts)):
            # Create a hidden component to store the question text
            question_text_state = gr.State(value=question_text)
            btn.click(
                handle_predefined_question,
                inputs=[question_text_state, chatbot, session_id, question_count, chatbot_type],
                outputs=[chatbot, question_count, question_counter, follow_up_section, chat_next]
            )

        clear_btn.click(
            clear_chat,
            outputs=[chatbot, question_count, question_counter, follow_up_section, chat_next]
        )

        chat_next.click(
            lambda sid: (
                proceed_to_feedback(sid),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True)
            )[1:], # Return from the 2nd element onwards
            inputs=[session_id],
            outputs=[demographics_section, chatbot_section, feedback_section]
        )

        submit_btn.click(
            lambda usefulness_val, accuracy_val, ease_val, trust_val, use_again_val, improve_val, overall_val, sid: (
                submit_study(usefulness_val, accuracy_val, ease_val, trust_val, use_again_val, improve_val, overall_val, sid),
                gr.update(visible=False),
                gr.update(visible=True)
            )[1:], # Return from the 2nd element onwards
            inputs=[usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, session_id],
            outputs=[feedback_section, thank_you_section]
        )

    return app


if __name__ == "__main__":
    print("🔄 Patient Education Chatbot Study initialized")
    app = create_study_app()
    app.launch(debug=True, share=False, favicon_path="assets/TheranosticFavicon.ico")