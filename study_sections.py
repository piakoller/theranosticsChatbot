"""
Study Sections Module
Contains UI section creation functions for the Patient Education Chatbot Study
"""

import gradio as gr
from study_config import (
    AGE_GROUPS, GENDER_OPTIONS, EDUCATION_LEVELS, 
    MEDICAL_BACKGROUND_OPTIONS, CHATBOT_EXPERIENCE_OPTIONS,
    RATING_SCALE, WOULD_USE_OPTIONS, STUDY_INSTRUCTIONS,
    CHATBOT_HEIGHT, APP_TITLE
)


def create_demographics_section():
    """Create the demographics collection section"""
    with gr.Column(visible=True) as demographics_section:
        gr.Markdown(f"# {APP_TITLE}")
        gr.Markdown("## Demographics Information")
        gr.Markdown("Please provide some basic information about yourself:")
        
        age = gr.Dropdown(
            label="Age Group",
            choices=AGE_GROUPS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        gender = gr.Radio(
            label="Gender",
            choices=GENDER_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        education = gr.Dropdown(
            label="Education Level",
            choices=EDUCATION_LEVELS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        medical_background = gr.Radio(
            label="Do you have a medical background?",
            choices=MEDICAL_BACKGROUND_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        chatbot_experience = gr.Radio(
            label="Have you used chatbots before?",
            choices=CHATBOT_EXPERIENCE_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        next_btn = gr.Button("Next", variant="primary")
        
    return demographics_section, age, gender, education, medical_background, chatbot_experience, next_btn


def create_attitude_section():
    """Create a section to collect attitude towards chatbots and expectations"""
    with gr.Column(visible=False) as attitude_section:
        gr.Markdown("## Attitude & Expectations")
        gr.Markdown("Please tell us about your attitude towards chatbots and what you expect from them:")

        attitude = gr.Radio(
            label="Overall attitude towards chatbots",
            choices=["Very positive", "Somewhat positive", "Neutral", "Somewhat negative", "Very negative"],
            value=None,
            elem_classes=["label-wrap"]
        )

        trust_sources = gr.CheckboxGroup(
            label="Which sources would make you trust a chatbot? (choose all that apply)",
            choices=["Hospital/Clinic endorsement", "Physician recommendation", "Cited sources/references", "Accurate answers consistently", "Data privacy assurances"],
            value=[],
            elem_classes=["label-wrap"]
        )

        expectations = gr.Textbox(
            label="What do you expect from a healthcare chatbot?",
            lines=3,
            placeholder="E.g., clear explanations, references, empathy, referral to specialists...",
            elem_classes=["label-wrap"]
        )

        attitude_next = gr.Button("Next", variant="primary")

    return attitude_section, attitude, trust_sources, expectations, attitude_next


def create_chatbot_section():
    """Create the chatbot interaction section"""
    with gr.Column(visible=False) as chatbot_section:
        gr.Markdown("## Chatbot Interaction")
        gr.Markdown(STUDY_INSTRUCTIONS)
        
        chatbot = gr.Chatbot(
            label="Patient Education Chatbot",
            height=CHATBOT_HEIGHT,
            show_label=True,
            type="messages"
        )
        
        msg = gr.Textbox(
            label="Your message",
            placeholder="Type your question here and press Enter to send...",
            lines=1,
            max_lines=3,
            autofocus=True,
            elem_classes=["label-wrap"]
        )
        
        send_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear Chat", variant="secondary")
        
        question_counter = gr.Markdown("**Questions asked: 0**")
        
        next_btn = gr.Button("Complete Interaction & Give Feedback", variant="primary", visible=False)
        
    return chatbot_section, chatbot, msg, send_btn, clear_btn, question_counter, next_btn


def create_feedback_section():
    """Create the feedback collection section"""
    with gr.Column(visible=False) as feedback_section:
        gr.Markdown("## Feedback")
        gr.Markdown("Please provide your feedback about the chatbot interaction:")
        
        usefulness = gr.Slider(
            label="How useful was the chatbot for patient education?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Not useful at all, 10 = Extremely useful"
        )
        
        accuracy = gr.Slider(
            label="How accurate did the information seem?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Very inaccurate, 10 = Very accurate"
        )
        
        ease_of_use = gr.Slider(
            label="How easy was it to use the chatbot?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Very difficult, 10 = Very easy"
        )
        
        trust = gr.Slider(
            label="How much would you trust this chatbot for health information?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = No trust at all, 10 = Complete trust"
        )
        
        would_use = gr.Radio(
            label="Would you use this chatbot in a real healthcare setting?",
            choices=WOULD_USE_OPTIONS,
            value=None
        )
        
        improvements = gr.Textbox(
            label="What improvements would you suggest?",
            lines=3,
            placeholder="Please describe any improvements or additional features..."
        )
        
        overall_feedback = gr.Textbox(
            label="Any other comments or feedback?",
            lines=3,
            placeholder="Feel free to share any additional thoughts..."
        )
        
        submit_btn = gr.Button("Submit Study", variant="primary")
        
    return feedback_section, usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, submit_btn


def create_thank_you_section():
    """Create the thank you completion section"""
    with gr.Column(visible=False) as thank_you_section:
        gr.Markdown("## Thank you for participating!")
        gr.Markdown("""
        Your responses have been recorded and will help improve chatbot-based patient education tools.
        
        Your feedback is valuable for advancing healthcare technology.
        
        You can now close this window.
        """)
        
    return thank_you_section