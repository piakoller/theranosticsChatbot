"""
Section B forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_b_forms(lang='en'):
    if lang == 'de':
        baseline_label = "Grundkenntnisse"
        baseline_placeholder = "Beschreiben Sie in einem Satz, was 'Theranostik' für Sie bedeutet."
        chatbot_use_label = "Frühere Verwendung von Gesundheits-Chatbots"
        trust_label = "Vertrauen in automatisierte Gesundheitsinformationen"
    else:
        baseline_label = "Baseline Knowledge Check"
        baseline_placeholder = "In one sentence, describe what 'theranostics' means to you."
        chatbot_use_label = "Prior Use of Health Chatbots"
        trust_label = "Trust in Automated Health Information"
    baseline_knowledge = gr.Textbox(
        label=baseline_label,
        placeholder=baseline_placeholder,
        lines=3
    )
    
    chatbot_use = gr.Radio(
        label=chatbot_use_label,
        choices=["Never used", "Used once", "Occasionally", "Frequently"] if lang=='en' else ["Nie benutzt", "Einmal benutzt", "Gelegentlich", "Häufig"]
    )
    
    trust_automated = gr.Radio(
        label=trust_label,
        choices=["1 - Not trustworthy", "2", "3", "4", "5", "6", "7 - Completely trustworthy"] if lang=='en' else ["1 - Nicht vertrauenswürdig", "2", "3", "4", "5", "6", "7 - Vollständig vertrauenswürdig"]
    )
    
    info_channels = gr.CheckboxGroup(
        label="Bevorzugte Kanäle für Gesundheitsinformationen" if lang=='de' else "Preferred Channels for Health Information",
        choices=["Physician consultation", "Printed leaflet", "Hospital website", "Chatbot", "Patient forum", "Video", "Phone call", "Other"] if lang=='en' else ["Arztgespräch", "Gedrucktes Merkblatt", "Krankenhaus-Website", "Chatbot", "Patientenforum", "Video", "Telefonanruf", "Andere"]
    )
    
    chatbot_expectations = gr.CheckboxGroup(
        label="Haupt-Erwartungen an einen Chatbot" if lang=='de' else "Primary Expectations from a Chatbot",
        choices=["Clear explanations", "Preparation steps", "Side-effect guidance", "Appointment reminders", "Emotional reassurance", "Links to further reading", "Contact clinician option", "Other"] if lang=='en' else ["Klare Erklärungen", "Vorbereitungs-Schritte", "Hinweise zu Nebenwirkungen", "Terminerinnerungen", "Emotionale Unterstützung", "Links zur Vertiefung", "Kontakt zum Arzt", "Andere"]
    )
    
    chatbot_concerns = gr.CheckboxGroup(
        label="Größte Bedenken gegenüber Chatbots" if lang=='de' else "Biggest Concerns about Chatbots",
        choices=["Accuracy", "Privacy", "Misunderstanding my situation", "Lack of empathy", "Not tailored", "Technical issues", "None", "Other"] if lang=='en' else ["Genauigkeit", "Datenschutz", "Missverständnis meiner Situation", "Mangel an Empathie", "Nicht individuell", "Technische Probleme", "Keine", "Andere"]
    )
    
    back_button, next_button = navigation_row(lang=lang, show_back=True)
    section_b_status = gr.HTML()
    
    return {
        "baseline_knowledge": baseline_knowledge,
        "chatbot_use": chatbot_use,
        "trust_automated": trust_automated,
        "info_channels": info_channels,
        "chatbot_expectations": chatbot_expectations,
        "chatbot_concerns": chatbot_concerns,
    "back_button": back_button,
    "next_button": next_button,
        "status": section_b_status
    }
