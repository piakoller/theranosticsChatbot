"""
Study Sections Module
Contains UI section creation functions for the Patient Education Chatbot Study
"""

import gradio as gr
import random
from study_config import (
    AGE_GROUPS, GENDER_OPTIONS, EDUCATION_LEVELS, 
    MEDICAL_BACKGROUND_OPTIONS, CHATBOT_EXPERIENCE_OPTIONS,
    RATING_SCALE, WOULD_USE_OPTIONS, STUDY_INSTRUCTIONS,
    CHATBOT_HEIGHT, APP_TITLE, PREDEFINED_QUESTIONS
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
        gr.Markdown("## Angaben zur Person")
        gr.Markdown("Bitte geben Sie einige grundlegende Informationen über sich an:")
        
        age = gr.Dropdown(
            label="Altersgruppe",
            choices=AGE_GROUPS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        gender = gr.Radio(
            label="Geschlecht",
            choices=GENDER_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        education = gr.Dropdown(
            label="Bildungsgrad",
            choices=EDUCATION_LEVELS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        medical_background = gr.Radio(
            label="Haben Sie einen medizinischen Hintergrund?",
            choices=MEDICAL_BACKGROUND_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        chatbot_experience = gr.Radio(
            label="Wie oft verwenden Sie Chatbots?",
            choices=CHATBOT_EXPERIENCE_OPTIONS,
            value=None,
            elem_classes=["label-wrap"]
        )
        
        treatment_reason = gr.Textbox(
            label="Weshalb befinden Sie sich für eine nuklearmedizinische Untersuchung im Spital?",
            lines=2,
            placeholder="z.B. PET-CT, Szintigraphie, Radiojodtherapie...",
            elem_classes=["label-wrap"]
        )
        
        next_btn = gr.Button("Weiter", variant="primary")
        
    return demographics_section, age, gender, education, medical_background, chatbot_experience, treatment_reason, next_btn


def create_consent_section():
    """Create an introductory consent section shown before demographics"""
    with gr.Column(visible=True) as consent_section:
        gr.Markdown(CONSENT_TITLE)
        gr.Markdown(CONSENT_TEXT)

        consent_radio = gr.Radio(
            label="Stimmen Sie der Teilnahme und der Verwendung anonymisierter Daten für die Forschung zu?",
            choices=CONSENT_CHOICES,
            value=None,
            elem_classes=["label-wrap"]
        )

        consent_next = gr.Button("Weiter", variant="primary")

    return consent_section, consent_radio, consent_next


def create_attitude_section():
    """Create a section to collect attitude towards chatbots and expectations"""
    with gr.Column(visible=False) as attitude_section:
        gr.Markdown(ATTITUDE_TITLE)
        gr.Markdown(ATTITUDE_SUBTEXT)

        # 1. Prior use of health chatbots (required)
        prior_use = gr.Radio(
            label="Haben Sie schon Chatbots verwendet um Informationen zu Gesundheitsthemen zu erhalten?",
            choices=PRIOR_USE_CHOICES,
            value=None,
            elem_classes=["label-wrap"]
        )

        # 2. Trust in automated health information (Likert 1-7, required)
        trust_likert = gr.Slider(
            label="Vertrauen Sie Gesundheitsinformationen, die KI-generiert sind?",
            minimum=TRUST_LIKERT_MIN,
            maximum=TRUST_LIKERT_MAX,
            value=TRUST_LIKERT_DEFAULT,
            step=1,
            info="1 = Nicht vertrauenswürdig; 7 = Völlig vertrauenswürdig",
            elem_classes=["label-wrap"]
        )

        # 3. Preferred channels for health information (multiple choice, required)
        preferred_channels = gr.CheckboxGroup(
            label="Welcher ist Ihr bevorzugter Kanal, um Gesundheitsinformationen zu erhalten?",
            choices=PREFERRED_CHANNELS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        preferred_other = gr.Textbox(
            label="Falls Andere (bevorzugte Kanäle), bitte spezifizieren",
            lines=1,
            placeholder="Anderer Kanal...",
            elem_classes=["label-wrap"]
        )

        # 4. Primary expectations from a chatbot (multiple choice with Other, required)
        primary_expectations = gr.CheckboxGroup(
            label="Welche Erwartungen haben Sie an einen Gesundheits-Chatbot?",
            choices=PRIMARY_EXPECTATIONS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        expectations_other = gr.Textbox(
            label="Falls Andere (Erwartungen), bitte spezifizieren",
            lines=1,
            placeholder="Andere Erwartung...",
            elem_classes=["label-wrap"]
        )

        # 5. Biggest concerns about chatbots (checkboxes)
        concerns = gr.CheckboxGroup(
            label="Welche Bedenken haben Sie gegenüber Gesundheits-Chatbots?",
            choices=CONCERNS_CHOICES,
            value=[],
            elem_classes=["label-wrap"]
        )
        concerns_other = gr.Textbox(
            label="Falls Andere (Bedenken), bitte spezifizieren",
            lines=1,
            placeholder="Andere Bedenken...",
            elem_classes=["label-wrap"]
        )

        attitude_next = gr.Button("Weiter", variant="primary")

    return attitude_section, prior_use, trust_likert, preferred_channels, preferred_other, primary_expectations, expectations_other, concerns, concerns_other, attitude_next


def create_chatbot_section():
    """Create the chatbot interaction section"""
    with gr.Column(visible=False) as chatbot_section:
        gr.Markdown("## Chatbot-Interaktion")
        gr.Markdown(STUDY_INSTRUCTIONS)

        # Randomize the order of questions for display
        randomized_questions = random.sample(PREDEFINED_QUESTIONS, len(PREDEFINED_QUESTIONS))
        
        # Create predefined question buttons
        gr.Markdown("**Wählen Sie eine Frage aus:**")
        question_buttons = []
        with gr.Row():
            with gr.Column():
                for i, question in enumerate(randomized_questions[:5]):
                    btn = gr.Button(question, variant="secondary", size="sm")
                    question_buttons.append(btn)
            with gr.Column():
                for i, question in enumerate(randomized_questions[5:]):
                    btn = gr.Button(question, variant="secondary", size="sm")
                    question_buttons.append(btn)
        
        chatbot = gr.Chatbot(
            label="Chatbot",
            height=CHATBOT_HEIGHT,
            show_label=True,
            type="messages",
            elem_classes=["label-wrap"]
        )
        
        # Follow-up question input (initially hidden)
        follow_up_section = gr.Column(visible=False)
        with follow_up_section:
            gr.Markdown("Bitte besprechen Sie individuelle Fragen auch mit Ihrem behandelnden Arzt.")
            gr.Markdown("**Nachfragen stellen (beliebig viele):**")
            msg = gr.Textbox(
                label="Ihre Nachfrage",
                placeholder="Stellen Sie hier Nachfragen zur letzten Antwort... Sie können mehrere Nachfragen stellen.",
                lines=1,
                max_lines=3,
                elem_classes=["label-wrap"]
            )
            send_btn = gr.Button("Nachfrage senden", variant="primary")
        
        clear_btn = gr.Button("Chat löschen", variant="secondary")
        
        question_counter = gr.Markdown("**Gestellte Fragen: 0**")
        
        next_btn = gr.Button("Interaktion beenden & Feedback geben", variant="primary", visible=False)
        
    return chatbot_section, chatbot, question_buttons, follow_up_section, msg, send_btn, clear_btn, question_counter, next_btn


def create_feedback_section():
    """Create the feedback collection section"""
    with gr.Column(visible=False) as feedback_section:
        gr.Markdown("## Feedback")
        gr.Markdown("Bitte geben Sie Ihr Feedback zur Chatbot-Interaktion:")
        
        usefulness = gr.Slider(
            label="Wie nützlich war der Chatbot für die Patientenaufklärung?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Überhaupt nicht nützlich, 10 = Äußerst nützlich"
        )
        
        accuracy = gr.Slider(
            label="Wie genau schienen die Informationen?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Sehr ungenau, 10 = Sehr genau"
        )
        
        ease_of_use = gr.Slider(
            label="Wie einfach war die Verwendung des Chatbots?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Sehr schwierig, 10 = Sehr einfach"
        )
        
        trust = gr.Slider(
            label="Wie sehr würden Sie diesem Chatbot für Gesundheitsinformationen vertrauen?",
            minimum=RATING_SCALE['min'],
            maximum=RATING_SCALE['max'],
            value=RATING_SCALE['default'],
            step=RATING_SCALE['step'],
            info="1 = Überhaupt kein Vertrauen, 10 = Vollständiges Vertrauen"
        )
        
        would_use = gr.Radio(
            label="Würden Sie diesen Chatbot in einer echten Gesundheitsumgebung verwenden?",
            choices=WOULD_USE_OPTIONS,
            value=None
        )
        
        improvements = gr.Textbox(
            label="Welche Verbesserungen würden Sie vorschlagen?",
            lines=3,
            placeholder="Bitte beschreiben Sie Verbesserungen oder zusätzliche Funktionen..."
        )
        
        overall_feedback = gr.Textbox(
            label="Weitere Kommentare oder Feedback?",
            lines=3,
            placeholder="Teilen Sie gerne weitere Gedanken mit..."
        )
        
        submit_btn = gr.Button("Studie abschicken", variant="primary")
        
    return feedback_section, usefulness, accuracy, ease_of_use, trust, would_use, improvements, overall_feedback, submit_btn


def create_thank_you_section():
    """Create the thank you completion section"""
    with gr.Column(visible=False) as thank_you_section:
        gr.Markdown("## Vielen Dank für Ihre Teilnahme!")
        gr.Markdown("""
        Ihre Antworten wurden aufgezeichnet und werden zur Verbesserung von Chatbot-basierten Patientenaufklärungstools beitragen.
        
        Ihr Feedback ist wertvoll für die Weiterentwicklung der Gesundheitstechnologie.
        
        Sie können dieses Fenster jetzt schließen.
        """)
        
    return thank_you_section