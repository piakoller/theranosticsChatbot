"""
Study Handlers Module
Contains event handlers for the Patient Education Chatbot Study
"""

import gradio as gr
from datetime import datetime
import logging_module
from chatbot import TheranosticsBot
from study_config import MINIMUM_QUESTIONS

# Initialize chatbot
theranostics_bot = TheranosticsBot()


def proceed_to_chatbot(age, gender, education, medical_background, chatbot_experience, session_id):
    """Handle transition from demographics to chatbot section"""
    # Validate required fields
    if not all([age, gender, education, medical_background, chatbot_experience]):
        gr.Warning("Please fill in all fields before continuing.")
        return (
            gr.update(),  # demographics_section
            gr.update(),  # chatbot_section  
            gr.update(),  # feedback_section
            session_id    # session_id (unchanged)
        )
    
    # Save demographics data
    demographics_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'age': age,
        'gender': gender,
        'education': education,
        'medical_background': medical_background,
        'chatbot_experience': chatbot_experience
    }
    
    logging_module.log_demographics(demographics_data)
    
    return (
        gr.update(visible=False),  # Hide demographics
        gr.update(visible=True),   # Show chatbot
        gr.update(visible=False),  # Keep feedback hidden
        session_id
    )


def handle_chatbot_message(message, history, session_id, question_count):
    """Handle chatbot message interaction"""
    if not message.strip():
        return "", history, question_count, gr.update(visible=False)
    
    # Convert Gradio history format to chatbot expected format
    conversation_history = []
    if history:
        for user_msg, bot_msg in history:
            if user_msg:
                conversation_history.append({"role": "user", "content": user_msg})
            if bot_msg:
                conversation_history.append({"role": "assistant", "content": bot_msg})
    
    # Add current message
    conversation_history.append({"role": "user", "content": message})
    
    # Get chatbot response
    response = theranostics_bot.chatbot_response(
        message, 
        conversation_history, 
        context="patient_education_study", 
        section="interaction"
    )
    
    # Update history in Gradio format
    history = history or []
    history.append([message, response])
    
    # Increment question counter
    question_count += 1
    
    # Log the interaction
    interaction_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'user_message': message,
        'bot_response': response,
        'question_number': question_count
    }
    
    logging_module.log_interaction(interaction_data)
    
    # Show "next" button after minimum questions
    show_next = question_count >= MINIMUM_QUESTIONS
    
    return "", history, question_count, gr.update(visible=show_next)


def proceed_to_feedback(session_id):
    """Handle transition from chatbot to feedback section"""
    return (
        gr.update(visible=False),  # Hide demographics
        gr.update(visible=False),  # Hide chatbot
        gr.update(visible=True),   # Show feedback
        session_id
    )


def clear_chat():
    """Clear the chat history"""
    return [], 0, gr.update(visible=False)


def submit_study(usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, session_id):
    """Handle study submission"""
    # Validate required feedback fields
    if would_use is None:
        gr.Warning("Please answer whether you would use this chatbot.")
        return gr.update()
    
    # Save feedback data
    feedback_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'usefulness': usefulness,
        'accuracy': accuracy,
        'ease_of_use': ease_of_use,
        'trust': trust,
        'would_use': would_use,
        'improvements': improvements,
        'overall_feedback': overall_feedback
    }
    
    logging_module.log_feedback(feedback_data)
    
    # Show completion message
    completion_text = f"""
    ## Thank you for participating!
    
    Your responses have been recorded (Session ID: {session_id}).
    Your feedback will help improve chatbot-based patient education tools.
    
    You can now close this window.
    """
    
    return gr.update(value=completion_text, visible=True)