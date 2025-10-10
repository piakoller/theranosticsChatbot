"""
Study Handlers Module
Contains event handlers for the Patient Education Chatbot Study
"""

import gradio as gr
from datetime import datetime
import logging_module
from chatbot import TheranosticsBot
from study_config import MINIMUM_QUESTIONS

from study_config import CONSENT_CHOICES

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


def save_demographics(age, gender, education, medical_background, chatbot_experience, session_id):
    """Save demographics data and proceed to the attitude section"""
    demographics_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'age': age,
        'gender': gender,
        'education': education,
        'medical_background': medical_background,
        'chatbot_experience': chatbot_experience
    }
    try:
        logging_module.log_demographics(demographics_data, session_id)
    except Exception:
        # Fallback to generic logging if specific function isn't available
        logging_module.save_form_submission(demographics_data, session_id)

    return (
        gr.update(visible=False),  # Hide demographics
        gr.update(visible=True),   # Show attitude
        session_id
    )


def save_consent(consent_value, session_id):
    """Validate consent radio and proceed to demographics if consent given"""
    # If user did not consent, keep them on the consent page (no progression)
    if consent_value is None or consent_value != CONSENT_CHOICES[0]:
        # Return no-op updates: keep consent visible
        return (
            gr.update(visible=True),   # consent_section stays visible
            gr.update(),                # demographics_section unchanged
            session_id
        )

    # Log consent decision (anonymized)
    consent_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'consent': consent_value
    }
    try:
        logging_module.save_form_submission(consent_data)
    except Exception:
        logging_module.log_interaction({'type': 'consent', **consent_data})

    # Proceed to demographics
    return (
        gr.update(visible=False),  # Hide consent
        gr.update(visible=True),   # Show demographics
        session_id
    )


def save_attitude(prior_use_val, trust_likert_val, preferred_channels_val, preferred_other_val, primary_expectations_val, expectations_other_val, concerns_val, concerns_other_val, session_id):
    """Save detailed attitude & expectations data and proceed to chatbot interaction"""
    attitude_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'prior_use': prior_use_val,
        'trust_likert': trust_likert_val,
        'preferred_channels': preferred_channels_val,
        'preferred_other': preferred_other_val,
        'primary_expectations': primary_expectations_val,
        'expectations_other': expectations_other_val,
        'concerns': concerns_val,
        'concerns_other': concerns_other_val
    }
    # Log under a dedicated type for easier querying
    logging_module.log_interaction({'type': 'attitude', **attitude_data}, session_id)

    return (
        gr.update(visible=False),  # Hide attitude
        gr.update(visible=True),   # Show chatbot
        session_id
    )


def handle_chatbot_message(message, history, session_id, question_count):
    """Handle chatbot message interaction"""
    if not message.strip():
        return "", history, question_count, gr.update(visible=False)
    
    # Convert Gradio messages format to chatbot expected format
    conversation_history = []
    if history:
        # With type="messages", history is already in the correct format
        conversation_history = history.copy()
    
    # Add current message
    conversation_history.append({"role": "user", "content": message})
    
    # Get chatbot response
    response = theranostics_bot.chatbot_response(
        message, 
        conversation_history, 
        context="patient_education_study", 
        section="interaction"
    )
    
    # Update history in messages format
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
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
        return (
            gr.update(),  # demographics_section
            gr.update(),  # chatbot_section  
            gr.update(),  # feedback_section
            gr.update(),  # thank_you_section (unchanged)
            session_id    # session_id (unchanged)
        )
    
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
    
    logging_module.log_feedback(feedback_data, session_id)
    
    # Show thank you section and hide others
    return (
        gr.update(visible=False),  # Hide demographics
        gr.update(visible=False),  # Hide chatbot
        gr.update(visible=False),  # Hide feedback
        gr.update(visible=True),   # Show thank you
        session_id
    )