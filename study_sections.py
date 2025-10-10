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
from study_config import (
    PRIOR_USE_CHOICES, TRUST_LIKERT_MIN, TRUST_LIKERT_MAX, TRUST_LIKERT_DEFAULT,
    PREFERRED_CHANNELS_CHOICES, PRIMARY_EXPECTATIONS_CHOICES, CONCERNS_CHOICES,
    ATTITUDE_TITLE, ATTITUDE_SUBTEXT
)
from study_config import (
    CONSENT_TITLE, CONSENT_TEXT, CONSENT_CHOICES
)


def create_demographics_section():
    """Create the demographics collection section"""
    with gr.Column(visible=False) as demographics_section:
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


def create_consent_section():
    """Create an introductory consent section shown before demographics"""
    with gr.Column(visible=True) as consent_section:
        gr.Markdown(CONSENT_TITLE)
        gr.Markdown(CONSENT_TEXT)

        consent_radio = gr.Radio(
            label="Do you consent to participate and for anonymized data to be used for research?",
            choices=CONSENT_CHOICES,
            value=None,
            elem_classes=["label-wrap"]
        )

        consent_next = gr.Button("Next", variant="primary")

    return consent_section, consent_radio, consent_next


def create_attitude_section():
    """Create a section to collect attitude towards chatbots and expectations"""
    with gr.Column(visible=False) as attitude_section:
        gr.Markdown(ATTITUDE_TITLE)
        gr.Markdown(ATTITUDE_SUBTEXT)

        # 1. Prior use of health chatbots (required)
        prior_use = gr.Radio(
            label="Prior use of health chatbots",
            choices=PRIOR_USE_CHOICES,
            value=None,
            elem_classes=["label-wrap"]
        )

        # 2. Trust in automated health information (Likert 1-7, required)
        trust_likert = gr.Slider(
            label="Trust in automated health information",
            minimum=TRUST_LIKERT_MIN,
            maximum=TRUST_LIKERT_MAX,
            value=TRUST_LIKERT_DEFAULT,
            step=1,
            info="1 = Not trustworthy; 7 = Completely trustworthy",
            elem_classes=["label-wrap"]
        )

        # 3. Preferred channels for health information (multiple choice, required)
        preferred_channels = gr.CheckboxGroup(
            label="Preferred channels for health information",
            choices=PREFERRED_CHANNELS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        preferred_other = gr.Textbox(
            label="If Other (preferred channels), please specify",
            lines=1,
            placeholder="Other channel...",
            elem_classes=["label-wrap"]
        )

        # 4. Primary expectations from a chatbot (multiple choice with Other, required)
        primary_expectations = gr.CheckboxGroup(
            label="Primary expectations from a chatbot",
            choices=PRIMARY_EXPECTATIONS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        expectations_other = gr.Textbox(
            label="If Other (expectations), please specify",
            lines=1,
            placeholder="Other expectation...",
            elem_classes=["label-wrap"]
        )

        # 5. Biggest concerns about chatbots (checkboxes)
        concerns = gr.CheckboxGroup(
            label="Biggest concerns about chatbots",
            choices=CONCERNS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        concerns_other = gr.Textbox(
            label="If Other (concerns), please specify",
            lines=1,
            placeholder="Other concern...",
            elem_classes=["label-wrap"]
        )

        attitude_next = gr.Button("Next", variant="primary")

    return attitude_section, prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, attitude_next


def create_chatbot_section():
    """Create the chatbot interaction section"""
    with gr.Column(visible=False) as chatbot_section:
        gr.Markdown("## Chatbot Interaction")
        gr.Markdown(STUDY_INSTRUCTIONS)
        
        chatbot = gr.Chatbot(
            label="Patient Education Chatbot",
            height=CHATBOT_HEIGHT,
            show_label=True,
            type="messages",
            elem_classes=["label-wrap"]
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