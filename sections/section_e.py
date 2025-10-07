"""
Section E forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_e_forms(lang='en'):
    scenario1_trust = gr.Radio(
        label=("Would you trust the chatbot's answer enough to act without clinician input?" if lang=='en' else "Würden Sie der Antwort des Chatbots vertrauen, um ohne Rücksprache mit einem Kliniker zu handeln?"),
        choices=["Yes", "No", "Maybe"] if lang=='en' else ["Ja", "Nein", "Vielleicht"]
    )
    
    scenario1_reason = gr.Textbox(
        label=("Why or why not?" if lang=='en' else "Warum (oder warum nicht)?"),
        lines=2
    )
    
    scenario2_trust = gr.Radio(
        label=("Scenario 2: Would you trust the chatbot for preparation instructions?" if lang=='en' else "Szenario 2: Würden Sie dem Chatbot bei Vorbereitungsanweisungen vertrauen?"),
        choices=["Yes", "No", "Maybe"] if lang=='en' else ["Ja", "Nein", "Vielleicht"]
    )
    
    scenario2_reason = gr.Textbox(
        label=("Why or why not?" if lang=='en' else "Warum (oder warum nicht)?"),
        lines=2
    )
    
    scenario3_trust = gr.Radio(
        label=("Scenario 3: Would you trust the chatbot for serious side effects?" if lang=='en' else "Szenario 3: Würden Sie dem Chatbot bei schweren Nebenwirkungen vertrauen?"),
        choices=["Yes", "No", "Maybe"] if lang=='en' else ["Ja", "Nein", "Vielleicht"]
    )
    
    scenario3_reason = gr.Textbox(
        label=("Why or why not?" if lang=='en' else "Warum (oder warum nicht)?"),
        lines=2
    )
    back_button, next_button = navigation_row(lang=lang, show_back=True, next_label=("Complete Scenarios & Continue to Final Feedback" if lang=='en' else "Szenarien abschließen & zum Abschlussfeedback"))
    section_e_status = gr.HTML()

    return {
        "scenario1_trust": scenario1_trust,
        "scenario1_reason": scenario1_reason,
        "scenario2_trust": scenario2_trust,
        "scenario2_reason": scenario2_reason,
        "scenario3_trust": scenario3_trust,
        "scenario3_reason": scenario3_reason,
    "back_button": back_button,
    "next_button": next_button,
        "status": section_e_status
    }
