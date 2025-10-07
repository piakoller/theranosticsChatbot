"""
Theranostics Chatbot - Main Application
A modular Gradio application for patient education about theranostics and nuclear medicine
"""

import gradio as gr
from ui_components import ui_components
from form_handlers import form_handler
from logging_module import conversation_logger
from chatbot import theranostics_bot


def setup_event_handlers(components):
    """Set up all event handlers for the application"""
    
    # Unpack components
    (chatbot, msg, submit_btn, export_btn, export_status,
     section_nav_a, section_nav_b, section_nav_c, current_form_section,
     section_a, section_b, section_c, submit_form, form_status,
     form_components, help_components,
     combined_section_a, combined_section_b, combined_section_c, combined_current_section,
     combined_sections, chatbot_status, combined_chatbot, combined_msg, combined_submit,
     need_help_btn, hide_help_btn,
     question_buttons) = components
    
    # Main chat tab event handlers
    msg.submit(ui_components.user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        ui_components.bot_message, chatbot, chatbot
    )
    submit_btn.click(ui_components.user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        ui_components.bot_message, chatbot, chatbot
    )
    
    # Export conversation logs
    export_btn.click(conversation_logger.export_conversations_to_csv, outputs=export_status)
    
    # Combined view event handlers
    combined_msg.submit(ui_components.combined_user_message, [combined_msg, combined_chatbot], [combined_msg, combined_chatbot], queue=False).then(
        ui_components.combined_bot_message, [combined_chatbot, combined_current_section], combined_chatbot
    )
    combined_submit.click(ui_components.combined_user_message, [combined_msg, combined_chatbot], [combined_msg, combined_chatbot], queue=False).then(
        ui_components.combined_bot_message, [combined_chatbot, combined_current_section], combined_chatbot
    )
    
    # Section-specific help chatbots
    form_components['help_msg_a'].submit(ui_components.section_help_user_message, [form_components['help_msg_a'], form_components['help_chatbot_a']], [form_components['help_msg_a'], form_components['help_chatbot_a']], queue=False).then(
        lambda history: ui_components.section_help_bot_message(history, "a"), form_components['help_chatbot_a'], form_components['help_chatbot_a']
    )
    
    form_components['help_msg_b'].submit(ui_components.section_help_user_message, [form_components['help_msg_b'], form_components['help_chatbot_b']], [form_components['help_msg_b'], form_components['help_chatbot_b']], queue=False).then(
        lambda history: ui_components.section_help_bot_message(history, "b"), form_components['help_chatbot_b'], form_components['help_chatbot_b']
    )
    
    form_components['help_msg_c'].submit(ui_components.section_help_user_message, [form_components['help_msg_c'], form_components['help_chatbot_c']], [form_components['help_msg_c'], form_components['help_chatbot_c']], queue=False).then(
        lambda history: ui_components.section_help_bot_message(history, "c"), form_components['help_chatbot_c'], form_components['help_chatbot_c']
    )
    
    # Main form tab section navigation
    section_nav_a.click(
        lambda: form_handler.switch_form_section("a"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    section_nav_b.click(
        lambda: form_handler.switch_form_section("b"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    section_nav_c.click(
        lambda: form_handler.switch_form_section("c"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    
    # Combined view section navigation
    combined_section_a.click(
        lambda: form_handler.switch_combined_section("a"),
        outputs=[combined_sections['combined_demo_section'], combined_sections['combined_treatment_section'], combined_sections['combined_feedback_section'], 
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    combined_section_b.click(
        lambda: form_handler.switch_combined_section("b"),
        outputs=[combined_sections['combined_demo_section'], combined_sections['combined_treatment_section'], combined_sections['combined_feedback_section'],
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    combined_section_c.click(
        lambda: form_handler.switch_combined_section("c"),
        outputs=[combined_sections['combined_demo_section'], combined_sections['combined_treatment_section'], combined_sections['combined_feedback_section'],
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    
    # Help chatbot controls for individual sections
    form_components['show_help_a'].click(
        lambda: form_handler.show_section_help("a"),
        outputs=[form_components['help_chatbot_a'], form_components['help_msg_a']]
    )
    form_components['show_help_b'].click(
        lambda: form_handler.show_section_help("b"),
        outputs=[form_components['help_chatbot_b'], form_components['help_msg_b']]
    )
    
    # Combined view help controls
    need_help_btn.click(
        lambda: form_handler.toggle_help_chatbot(True),
        outputs=[chatbot_status, combined_chatbot, combined_msg, combined_submit, need_help_btn, hide_help_btn]
    )
    hide_help_btn.click(
        lambda: form_handler.toggle_help_chatbot(False),
        outputs=[chatbot_status, combined_chatbot, combined_msg, combined_submit, need_help_btn, hide_help_btn]
    )
    
    # Form submission
    submit_form.click(
        form_handler.submit_form_data,
        inputs=[form_components['age'], form_components['gender'], form_components['diagnosis'], 
                form_components['treatment_date'], form_components['treatment_satisfaction'], 
                form_components['side_effects'], form_components['side_effects_severity'], 
                form_components['overall_feedback'], form_components['improvements'], form_components['recommend']],
        outputs=[form_status]
    )
    
    # Form help button handlers
    help_components['form_help_q1'].click(
        lambda: form_handler.show_form_help("treatment_satisfaction"),
        outputs=[help_components['form_help_response']]
    )
    help_components['form_help_q2'].click(
        lambda: form_handler.show_form_help("side_effects"),
        outputs=[help_components['form_help_response']]
    )
    help_components['form_help_q3'].click(
        lambda: form_handler.show_form_help("information_sharing"),
        outputs=[help_components['form_help_response']]
    )
    
    # Example question button handlers
    question_buttons[0].click(  # q1_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q1"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[1].click(  # q2_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q2"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[2].click(  # q3_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q3"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[3].click(  # q4_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q4"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[4].click(  # q5_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q5"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[5].click(  # q6_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q6"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)
    
    question_buttons[6].click(  # q7_btn
        lambda history: ui_components.handle_example_question(ui_components.questions["q7"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(ui_components.bot_message, chatbot, chatbot)


def create_app():
    """Create and configure the main Gradio application"""
    
    # Create the Gradio interface with custom CSS
    with gr.Blocks(
        title="Theranostics Chatbot", 
        theme=gr.themes.Soft(),
        css=ui_components.load_css()
    ) as demo:
        
        # Create header
        ui_components.create_header()
        
        # Create example questions
        question_buttons = ui_components.create_example_questions()
        
        # Show model status
        ui_components.create_model_status()
        
        # Main content area with tabs
        with gr.Tabs(selected=0) as tabs:
            # Chat Assistant Tab
            chatbot, msg, submit_btn, export_btn, export_status = ui_components.create_chat_tab()
            
            # Feedback Form Tab
            (section_nav_a, section_nav_b, section_nav_c, current_form_section,
             section_a, section_b, section_c, submit_form, form_status,
             form_components, help_components) = ui_components.create_form_tab()
            
            # Combined View Tab
            (combined_section_a, combined_section_b, combined_section_c, combined_current_section,
             combined_sections, chatbot_status, combined_chatbot, combined_msg, combined_submit,
             need_help_btn, hide_help_btn) = ui_components.create_combined_tab()
        
        # Set up all event handlers
        components = (
            chatbot, msg, submit_btn, export_btn, export_status,
            section_nav_a, section_nav_b, section_nav_c, current_form_section,
            section_a, section_b, section_c, submit_form, form_status,
            form_components, help_components,
            combined_section_a, combined_section_b, combined_section_c, combined_current_section,
            combined_sections, chatbot_status, combined_chatbot, combined_msg, combined_submit,
            need_help_btn, hide_help_btn,
            question_buttons
        )
        
        setup_event_handlers(components)
        
        return demo


def main():
    """Main entry point of the application"""
    # Initialize conversation logging
    print("🔄 Conversation logging system initialized")
    
    # Create and launch the app
    demo = create_app()
    
    # For Hugging Face Spaces: do not set server_name, server_port, or share
    demo.launch(debug=True)


if __name__ == "__main__":
    main()