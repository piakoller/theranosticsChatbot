"""
Section A forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_a_forms(lang='en'):
    # localized labels
    if lang == 'de':
        consent_label = "Zustimmung zur Teilnahme"
        participant_role_label = "Teilnehmerrolle"
        role_other_label = "Wenn 'Andere', bitte angeben:"
        age_range_label = "Altersgruppe"
        gender_label = "Geschlecht"
        education_label = "Höchster Bildungsabschluss"
        experience_label = "Frühere Erfahrung mit Theranostik/Nuklearmedizin"
        digital_comfort_label = "Komfort mit digitalen Werkzeugen"
    else:
        consent_label = "Consent to Participate"
        participant_role_label = "Participant Role"
        role_other_label = "If Other, please specify:"
        age_range_label = "Age Range"
        gender_label = "Gender"
        education_label = "Highest Education Level"
        experience_label = "Previous Experience with Theranostics/Nuclear Medicine"
        digital_comfort_label = "Comfort with Digital Tools"
    consent = gr.Radio(
        label=consent_label,
        choices=["I consent to participate in this study and agree that anonymized responses and prototype usage logs may be used for research."] if lang=='en' else ["Ich stimme der Teilnahme an dieser Studie zu und bin damit einverstanden, dass anonymisierte Antworten und Prototyp-Nutzungsprotokolle für Forschungszwecke verwendet werden dürfen."],
        info="Your participation is voluntary and data will be anonymized." if lang=='en' else "Ihre Teilnahme ist freiwillig und die Daten werden anonymisiert."
    )
    
    participant_role = gr.Radio(
        label=participant_role_label,
        choices=["Patient", "Caregiver/Family", "Physician", "Pharma/Industry", "Other"] if lang=='en' else ["Patient", "Betreuer/Familie", "Arzt", "Pharma/Industrie", "Andere"],
        info="Select the option that best describes your relationship to healthcare." if lang=='en' else "Wählen Sie die Option, die Ihre Beziehung zum Gesundheitswesen am besten beschreibt."
    )
    
    role_other = gr.Textbox(
        label=role_other_label,
        visible=False
    )
    
    age_range = gr.Radio(
        label=age_range_label,
        choices=["Under 18", "18–30", "31–50", "51–70", "Over 70"] if lang=='en' else ["Unter 18", "18–30", "31–50", "51–70", "Über 70"]
    )
    
    gender = gr.Radio(
        label=gender_label,
        choices=["Female", "Male", "Non-binary", "Prefer not to say", "Other"] if lang=='en' else ["Weiblich", "Männlich", "Nicht-binär", "Möchte ich nicht angeben", "Andere"]
    )
    
    education = gr.Radio(
        label=education_label,
        choices=["Primary", "Secondary", "Vocational", "Bachelor", "Master/PhD", "Prefer not to say"] if lang=='en' else ["Grundschule", "Sekundarstufe", "Berufsausbildung", "Bachelor", "Master/PhD", "Möchte ich nicht angeben"]
    )
    
    experience = gr.Radio(
        label=experience_label,
        choices=["None", "Observed a family member", "Received a procedure", "Work in field"] if lang=='en' else ["Keine", "Hatte Familienmitglied beobachtet", "Behandlung erhalten", "Arbeite in diesem Bereich"]
    )
    
    digital_comfort = gr.Radio(
        label=digital_comfort_label,
        choices=["1 - Not at all comfortable", "2", "3", "4", "5 - Very comfortable"] if lang=='en' else ["1 - Überhaupt nicht komfortabel", "2", "3", "4", "5 - Sehr komfortabel"]
    )
    
    # create shared navigation buttons using the utils.navigation_row helper
    back_button, next_button = navigation_row(lang=lang, show_back=True)
    section_a_status = gr.HTML()
    
    return {
        "consent": consent,
        "participant_role": participant_role,
        "role_other": role_other,
        "age_range": age_range,
        "gender": gender,
        "education": education,
        "experience": experience,
        "digital_comfort": digital_comfort,
    "back_button": back_button,
    "next_button": next_button,
        "status": section_a_status
    }
