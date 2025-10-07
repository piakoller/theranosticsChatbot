"""
Section F forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_f_forms(lang='en'):
    overall_satisfaction = gr.Radio(
        label=("Overall Satisfaction" if lang=='en' else "Gesamtzufriedenheit"),
        choices=["1 - Very dissatisfied", "2", "3", "4", "5", "6", "7 - Very satisfied"] if lang=='en' else ["1 - Sehr unzufrieden", "2", "3", "4", "5", "6", "7 - Sehr zufrieden"]
    )
    
    improvements = gr.Textbox(
        label=("Top Three Improvements You Want" if lang=='en' else "Die drei wichtigsten Verbesserungen, die Sie wünschen"),
        placeholder=("What are the three most important improvements you would like to see?" if lang=='en' else "Welche drei Verbesserungen sind Ihnen am wichtigsten?"),
        lines=4
    )
    
    recommend_tool = gr.Radio(
        label=("Would You Recommend This Tool to Others?" if lang=='en' else "Würden Sie dieses Tool anderen empfehlen?"),
        choices=["Yes", "No", "Maybe"] if lang=='en' else ["Ja", "Nein", "Vielleicht"]
    )
    
    additional_feedback = gr.Textbox(
        label=("Additional Comments" if lang=='en' else "Weitere Kommentare"),
        placeholder=("Any other feedback about your experience..." if lang=='en' else "Weitere Rückmeldungen zu Ihrer Erfahrung..."),
        lines=4
    )
    back_button, complete_button = navigation_row(lang=lang, show_back=True, next_label=("Complete Study" if lang=='en' else "Studie abschließen"))
    section_f_status = gr.HTML()
    completion_message = gr.HTML(visible=False)

    return {
        "overall_satisfaction": overall_satisfaction,
        "improvements": improvements,
        "recommend_tool": recommend_tool,
        "additional_feedback": additional_feedback,
    "back_button": back_button,
    "complete_button": complete_button,
        "status": section_f_status,
        "completion_message": completion_message
    }
