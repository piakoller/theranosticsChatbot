"""
Study Handlers Module
Contains event handlers for the Patient Education Chatbot Study
"""

import gradio as gr
from datetime import datetime
from core import conversation as logging_module
from core.chatbot import theranostics_bot  # Use existing global instance
from .config import MINIMUM_QUESTIONS, PREDEFINED_QUESTIONS, CONSENT_CHOICES
from .utils import get_question_counter_text

# Try to import RAG chatbot, with fallback if not available
try:
    from core.rag_engine import get_rag_chatbot
    rag_chatbot = get_rag_chatbot()
    RAG_AVAILABLE = rag_chatbot is not None
except Exception as e:
    print(f"⚠️ RAG chatbot not available: {e}")
    rag_chatbot = None
    RAG_AVAILABLE = False

# Global state for tracking asked questions
asked_questions = set()

def get_chatbot_response(message, history, chatbot_type, context="patient_education_study", section="interaction", lang="de"):
    """Get response from the appropriate chatbot based on type selection"""
    if chatbot_type == "expert" and RAG_AVAILABLE and rag_chatbot:
        try:
            # Use RAG chatbot for expert mode (doesn't use lang parameter)
            return rag_chatbot.chatbot_response(message, history, context, section, chatbot_type)
        except Exception as e:
            print(f"❌ RAG chatbot error, falling back to normal: {e}")
            # Fall back to normal chatbot if RAG fails
    
    # Use normal chatbot
    return theranostics_bot.chatbot_response(message, history, context, section, lang, chatbot_type)


def proceed_to_chatbot(age, gender, education, medical_background, chatbot_experience, session_id):
    """Handle transition from demographics to chatbot section"""
    # Validate required fields
    if not all([age, gender, education, medical_background, chatbot_experience]):
        gr.Warning("Bitte füllen Sie alle Felder aus, bevor Sie fortfahren.")
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


def save_chatbot_selection(chatbot_choice, session_id):
    """Save the chatbot selection and proceed to demographics"""
    # Set the logger's user ID to match the session ID
    logging_module.set_user_id(session_id)
    
    # Save chatbot selection data
    selection_data = {
        'user_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'chatbot_type': chatbot_choice
    }
    
    try:
        logging_module.save_form_submission(selection_data, user_id=session_id)
    except Exception as e:
        print(f"Warning: Failed to save chatbot selection: {e}")
    
    return (
        chatbot_choice,            # Update chatbot_type state
        gr.update(visible=False),  # Hide chatbot selection section
        gr.update(visible=True)    # Show demographics section
    )


def save_demographics(age, gender, education, medical_background, chatbot_experience, treatment_reason, session_id):
    """Save demographics data and proceed directly to the chatbot section (skip attitude)"""
    # Set the logger's user ID to match the session ID
    logging_module.set_user_id(session_id)
    
    demographics_data = {
        'user_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'age': age,
        'gender': gender,
        'education': education,
        'medical_background': medical_background,
        'chatbot_experience': chatbot_experience,
        'treatment_reason': treatment_reason
    }
    try:
        logging_module.log_demographics(demographics_data, user_id=session_id)
    except Exception:
        # Fallback to generic logging if specific function isn't available
        logging_module.save_form_submission(demographics_data, user_id=session_id)

    return (
        gr.update(visible=False),  # Hide demographics section
        gr.update(visible=True)    # Show chatbot section
    )


def save_consent(consent_value, session_id):
    """Validate consent radio and proceed to demographics if consent given"""
    # Set the logger's user ID to match the session ID early in the process
    logging_module.set_user_id(session_id)
    
    # If user did not consent, keep them on the consent page (no progression)
    if consent_value is None or consent_value != CONSENT_CHOICES[0]:
        # Return no-op updates: keep consent visible
        return (
            gr.update(visible=True),   # consent_section stays visible
            gr.update()                # chatbot_selection_section unchanged
        )

    # Log consent decision (anonymized)
    consent_data = {
        'user_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'consent': consent_value
    }
    try:
        logging_module.save_form_submission(consent_data)
    except Exception:
        logging_module.log_interaction({'type': 'consent', **consent_data})

    # Proceed to demographics
    return (
        gr.update(visible=False),  # Hide consent section
        gr.update(visible=True)    # Show chatbot selection section
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
    
    # Get chatbot response (using German language)
    response = theranostics_bot.chatbot_response(
        message, 
        conversation_history, 
        context="patient_education_study", 
        section="interaction",
        lang="de"
    )
    
    # Update history in messages format
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
    # Increment question counter
    question_count += 1
    
    # Log the interaction to forms collection
    interaction_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'user_message': message,
        'bot_response': response,
        'question_number': question_count
    }
    
    logging_module.log_interaction(interaction_data)
    
    # Also log the conversation to conversations collection
    logging_module.log_conversation(
        user_input=message,
        bot_response=response,
        context="patient_education_study",
        section="interaction",
        chatbot_type="normal",  # Default for this function
        user_id=session_id,
        metadata={"questiontype": "manual", "question_number": question_count}
    )
    
    # Show "next" button after minimum questions
    show_next = question_count >= MINIMUM_QUESTIONS
    
    return "", history, question_count, gr.update(visible=show_next)


def handle_predefined_question(question_text, history, session_id, question_count, chatbot_type="normal"):
    """Handle predefined question button clicks"""
    global asked_questions
    
    # Track that this question has been asked
    asked_questions.add(question_text)
    
    # Get bot response for the predefined question
    conversation_history = history.copy() if history else []
    conversation_history.append({"role": "user", "content": question_text})
    
    response = get_chatbot_response(
        question_text,
        conversation_history,
        chatbot_type,
        context="patient_education_study",
        section="interaction"
    )
    
    # Update history
    history = history or []
    history.append({"role": "user", "content": question_text})
    history.append({"role": "assistant", "content": response})
    
    # Increment question counter
    question_count += 1
    
    # Log the interaction to forms collection
    interaction_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'user_message': question_text,
        'bot_response': response,
        'question_number': question_count,
        'question_type': 'predefined',
        'chatbot_type': chatbot_type
    }
    
    logging_module.log_interaction(interaction_data)
    
    # Also log the conversation to conversations collection
    logging_module.log_conversation(
        user_input=question_text,
        bot_response=response,
        context="patient_education_study",
        section="interaction",
        chatbot_type=chatbot_type,
        user_id=session_id,
        metadata={"questiontype": "predefined", "question_number": question_count}
    )
    
    # Show follow-up section and check if next button should be visible
    show_next = question_count >= MINIMUM_QUESTIONS
    show_follow_up = True
    
    return history, question_count, get_question_counter_text(question_count), gr.update(visible=show_follow_up), gr.update(visible=show_next)


def handle_follow_up_question(message, history, session_id, question_count, chatbot_type="normal"):
    """Handle follow-up questions after predefined questions"""
    if not message.strip():
        return "", history, question_count, get_question_counter_text(question_count), gr.update(), gr.update()
    
    # Get bot response for the follow-up question
    conversation_history = history.copy() if history else []
    conversation_history.append({"role": "user", "content": message})
    
    response = get_chatbot_response(
        message,
        conversation_history,
        chatbot_type,
        context="patient_education_study",
        section="interaction"
    )
    
    # Update history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    
    # Increment question counter for follow-up questions too
    question_count += 1
    
    # Log the interaction to forms collection
    interaction_data = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'user_message': message,
        'bot_response': response,
        'question_number': question_count,
        'question_type': 'follow_up',
        'chatbot_type': chatbot_type
    }
    
    logging_module.log_interaction(interaction_data)
    
    # Also log the conversation to conversations collection
    logging_module.log_conversation(
        user_input=message,
        bot_response=response,
        context="patient_education_study",
        section="interaction",
        chatbot_type=chatbot_type,
        user_id=session_id,
        metadata={"questiontype": "follow_up", "question_number": question_count}
    )
    
    # Show next button if minimum questions reached, keep follow-up section visible
    show_next = question_count >= MINIMUM_QUESTIONS
    
    return "", history, question_count, get_question_counter_text(question_count), gr.update(visible=True), gr.update(visible=show_next)


def proceed_to_feedback(session_id):
    """Handle transition from chatbot to feedback section"""
    return (
        gr.update(visible=False),  # Hide demographics
        gr.update(visible=False),  # Hide chatbot
        gr.update(visible=True),   # Show feedback
        session_id
    )


def clear_chat():
    """Clear the chat history and reset question tracking"""
    global asked_questions
    asked_questions.clear()
    
    # Clear conversation memory for both chatbots
    if hasattr(theranostics_bot, "clear_conversation_memory"):
        getattr(theranostics_bot, "clear_conversation_memory")()
    elif hasattr(theranostics_bot, "clear_conversation_history"):
        getattr(theranostics_bot, "clear_conversation_history")()
    
    # Clear RAG chatbot memory if available
    try:
        # Use the module-level rag_chatbot if it was initialized earlier; avoid fragile import paths
        if RAG_AVAILABLE and rag_chatbot:
            # Prefer known method names, call via getattr to avoid static attribute access
            for method_name in ("clear_conversation_history", "clear_conversation_memory", "clear_conversation", "clear_memory"):
                if hasattr(rag_chatbot, method_name):
                    getattr(rag_chatbot, method_name)()
                    break
    except Exception:
        # Ignore any errors when attempting to clear RAG chatbot state
        pass
    
    return [], 0, get_question_counter_text(0), gr.update(visible=False), gr.update(visible=False)


def submit_study(usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, session_id, chatbot_type="normal"):
    """Handle study submission"""
    # Validate required feedback fields
    if would_use is None:
        gr.Warning("Bitte beantworten Sie, ob Sie diesen Chatbot verwenden würden.")
        return (
            gr.update(),  # demographics_section
            gr.update(),  # chatbot_section  
            gr.update(),  # feedback_section
            gr.update(),  # thank_you_section (unchanged)
            session_id    # session_id (unchanged)
        )
    
    # Save feedback data
    feedback_data = {
        'user_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'usefulness': usefulness,
        'accuracy': accuracy,
        'ease_of_use': ease_of_use,
        'trust': trust,
        'would_use': would_use,
        'improvements': improvements,
        'overall_feedback': overall_feedback,
        'chatbot_type': chatbot_type
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