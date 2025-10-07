"""
Section D forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_d_forms(lang='en'):
    prototype_opened = gr.Radio(
        label=("Did you interact with the prototype?" if lang=='en' else "Haben Sie mit dem Prototyp interagiert?"),
        choices=["Yes" if lang=='en' else "Ja", "No" if lang=='en' else "Nein"]
    )
    
    interaction_time = gr.Radio(
        label=("How long did you interact with the prototype?" if lang=='en' else "Wie lange haben Sie mit dem Prototyp interagiert?"),
        choices=["<5 min", "5–10 min", "10–20 min", ">20 min"]
    )
    
    perceived_accuracy = gr.Radio(
        label=("Perceived Accuracy" if lang=='en' else "Wahrgenommene Genauigkeit"),
        choices=[
            ("1 - Inaccurate" if lang=='en' else "1 - Ungenau"),
            "2", "3", "4", "5", "6",
            ("7 - Accurate" if lang=='en' else "7 - Genau")
        ]
    )
    
    perceived_usefulness = gr.Radio(
        label=("Perceived Usefulness for My Situation" if lang=='en' else "Wahrgenommene Nützlichkeit für meine Situation"),
        choices=[
            ("1 - Not useful" if lang=='en' else "1 - Nicht nützlich"),
            "2", "3", "4", "5", "6",
            ("7 - Very useful" if lang=='en' else "7 - Sehr nützlich")
        ]
    )
    
    act_on_advice = gr.Radio(
        label=("Would you act on the chatbot's advice without contacting a clinician?" if lang=='en' else "Würden Sie den Rat des Chatbots befolgen, ohne einen Kliniker zu kontaktieren?"),
        choices=[
            ("Yes" if lang=='en' else "Ja"),
            ("No" if lang=='en' else "Nein"),
            ("Maybe" if lang=='en' else "Vielleicht"),
            ("I would check with clinician first but use chatbot as reference" if lang=='en' else "Ich würde zuerst einen Kliniker konsultieren, aber den Chatbot als Referenz verwenden")
        ]
    )
    
    anxiety_change = gr.Radio(
        label=("After using the chatbot my anxiety changed:" if lang=='en' else "Nach der Nutzung des Chatbots hat sich meine Angst verändert:"),
        choices=[
            ("1 - Much worse" if lang=='en' else "1 - Viel schlechter"),
            "2", "3", "4", "5", "6",
            ("7 - Much better" if lang=='en' else "7 - Viel besser")
        ]
    )
    
    perceived_limitations = gr.Textbox(
        label=("Perceived Limitations" if lang=='en' else "Wahrgenommene Einschränkungen"),
        placeholder=("Describe anything the chatbot missed or answered poorly." if lang=='en' else "Beschreiben Sie alles, was der Chatbot verpasst oder schlecht beantwortet hat."),
        lines=4
    )
    
    # SUS Usability Scale
    sus1 = gr.Radio(
        label=("I think I would like to use this system frequently." if lang=='en' else "Ich denke, ich würde dieses System häufig nutzen."),
        choices=[
            ("Strongly disagree" if lang=='en' else "Stimme überhaupt nicht zu"),
            ("Disagree" if lang=='en' else "Stimme nicht zu"),
            ("Neutral" if lang=='en' else "Neutral"),
            ("Agree" if lang=='en' else "Stimme zu"),
            ("Strongly agree" if lang=='en' else "Stimme voll und ganz zu")
        ]
    )
    
    sus2 = gr.Radio(
        label=("I found the system unnecessarily complex." if lang=='en' else "Ich fand das System unnötig komplex."),
        choices=[
            ("Strongly disagree" if lang=='en' else "Stimme überhaupt nicht zu"),
            ("Disagree" if lang=='en' else "Stimme nicht zu"),
            ("Neutral" if lang=='en' else "Neutral"),
            ("Agree" if lang=='en' else "Stimme zu"),
            ("Strongly agree" if lang=='en' else "Stimme voll und ganz zu")
        ]
    )
    back_button, next_button = navigation_row(lang=lang, show_back=True, next_label=("Complete Assessment & Continue to Scenarios" if lang=='en' else "Bewertung abschließen & zu den Szenarien"))
    section_d_status = gr.HTML()

    return {
    "back_button": back_button,
        "prototype_opened": prototype_opened,
        "interaction_time": interaction_time,
        "perceived_accuracy": perceived_accuracy,
        "perceived_usefulness": perceived_usefulness,
        "act_on_advice": act_on_advice,
        "anxiety_change": anxiety_change,
        "perceived_limitations": perceived_limitations,
        "sus1": sus1,
        "sus2": sus2,
    "next_button": next_button,
        "status": section_d_status
    }
