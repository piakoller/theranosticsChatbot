"""
Section C forms
"""
import gradio as gr
from utils.i18n import t
from utils.ui import navigation_row


def create_section_c_forms(lang='en'):
    chatbot_interface = gr.Chatbot(
        label="Theranostics Information Assistant" if lang=='en' else "Theranostik Informationsassistent",
        height=420,
        show_copy_button=True,
        type="messages",
        elem_id="chatbot_interface"
    )
    
    user_input = gr.Textbox(
        label="Ask your questions about theranostics:" if lang=='en' else "Stellen Sie Ihre Fragen zur Theranostik:",
        placeholder="Type your question here..." if lang=='en' else "Geben Sie hier Ihre Frage ein...",
        lines=1,
        elem_id="chatbot_input"
    )
    
    send_btn = gr.Button("Send Question" if lang=='en' else "Frage senden", variant="primary", elem_id="chatbot_send")
    back_button, next_button = navigation_row(lang=lang, show_back=True, next_label=("Complete Prototype Section & Continue to Assessment" if lang=='en' else "Prototyp-Abschnitt abschließen & zur Bewertung"))
    section_c_status = gr.HTML()
    
    return {
        "chatbot_interface": chatbot_interface,
        "user_input": user_input,
    "send_btn": send_btn,
    "back_button": back_button,
    "next_button": next_button,
        "status": section_c_status
    }
