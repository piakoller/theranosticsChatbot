"""
Study Utils Module
Contains utility functions for the Patient Education Chatbot Study
"""

import uuid
import logging_module
from datetime import datetime


def generate_session_id():
    """Generate a unique session ID for the study participant"""
    return str(uuid.uuid4())


def save_study_data(session_id, data_type, data):
    """Save study data with consistent formatting"""
    formatted_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'data_type': data_type,
        **data
    }
    
    if data_type == 'demographics':
        logging_module.log_demographics(formatted_data)
    elif data_type == 'interaction':
        logging_module.log_interaction(formatted_data)
    elif data_type == 'feedback':
        logging_module.log_feedback(formatted_data)
    else:
        # Generic logging for any other data types
        logging_module.log_interaction(formatted_data)


def validate_demographics(age, gender, education, medical_background, chatbot_experience):
    """Validate that all required demographics fields are filled"""
    required_fields = [age, gender, education, medical_background, chatbot_experience]
    return all(field is not None and field != "" for field in required_fields)


def validate_feedback(would_use):
    """Validate that required feedback fields are filled"""
    return would_use is not None


def format_completion_message(session_id):
    """Format the study completion message"""
    return f"""
    ## Thank you for participating!
    
    Your responses have been recorded (Session ID: {session_id}).
    Your feedback will help improve chatbot-based patient education tools.
    
    You can now close this window.
    """


def get_question_counter_text(count):
    """Get formatted question counter text"""
    return f"**Questions asked: {count}**"