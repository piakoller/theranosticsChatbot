"""
Forms module for the Theranostics Chatbot User Study Application
Contains all form definitions and form field configurations
"""

import gradio as gr

from sections.section_a import create_section_a_forms
from sections.section_b import create_section_b_forms
from sections.section_c import create_section_c_forms
from sections.section_d import create_section_d_forms
from sections.section_e import create_section_e_forms
from sections.section_f import create_section_f_forms


class StudyForms:
    """Facade that delegates section form creation to modules in `sections/`"""

    @staticmethod
    def create_section_a_forms(lang='en'):
        return create_section_a_forms(lang=lang)

    @staticmethod
    def create_section_b_forms(lang='en'):
        return create_section_b_forms(lang=lang)

    @staticmethod
    def create_section_c_forms(lang='en'):
        return create_section_c_forms(lang=lang)

    @staticmethod
    def create_section_d_forms(lang='en'):
        return create_section_d_forms(lang=lang)

    @staticmethod
    def create_section_e_forms(lang='en'):
        return create_section_e_forms(lang=lang)

    @staticmethod
    def create_section_f_forms(lang='en'):
        return create_section_f_forms(lang=lang)