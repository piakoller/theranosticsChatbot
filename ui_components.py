"""
UI Components module for the Theranostics Chatbot User Study Application
Contains reusable UI components and section layouts
"""

import gradio as gr
from styles import get_question_counter_html, get_task_instructions_html, get_section_header_html, get_study_header_html, get_progress_html
from forms import StudyForms

class UIComponents:
    """Contains reusable UI components for the study application"""
    
    @staticmethod
    def create_header(lang='en'):
        """Create the main application header (language-aware)"""
        return gr.HTML(get_study_header_html(lang=lang))
        
    @staticmethod
    def create_question_counter(lang='en', prefix=''):
        """Create the question counter component for Section C (language/prefix aware)"""
        elem = f"question_counter_display_{prefix}" if prefix else "question_counter_display"
        return gr.HTML(
            value=get_question_counter_html(0, lang=lang),
            elem_id=elem
        )

class StudySections:
    """Contains the complete section layouts for the study"""
    
    @staticmethod
    def create_study_layout(lang='en', prefix='en', initially_visible=False):
        """Create the full study layout for a given language.

        lang: 'en' or 'de'
        prefix: string appended to elem_ids to avoid collisions when creating multiple layouts
        initially_visible: whether the first section should be visible
        """
        
        all_forms = {}
        section_groups = {}

        # Use individual visible sections (columns) rather than tabs so only the
        # current section is shown. Each section container is stored in
        # `section_groups` and visibility can be toggled by the event handler.
        with gr.Column(elem_id=f"study_sections_{prefix}"):
            vis_a = True if initially_visible else False
            with gr.Column(visible=vis_a, elem_id=f"section_A_{prefix}") as tab_a:
                section_groups['A'] = tab_a
                gr.HTML(get_section_header_html('A', lang=lang))
                forms_a = StudyForms.create_section_a_forms(lang=lang)
                all_forms['A'] = forms_a

                forms_a["consent"]
                forms_a["participant_role"]
                forms_a["role_other"]
                forms_a["age_range"]
                forms_a["gender"]
                forms_a["education"]
                forms_a["experience"]
                forms_a["digital_comfort"]
                from utils.ui import render_navigation_row
                render_navigation_row(forms_a["back_button"], forms_a["next_button"])
                forms_a["status"]

            with gr.Column(visible=False, elem_id=f"section_B_{prefix}") as tab_b:
                section_groups['B'] = tab_b
                gr.HTML(get_section_header_html('B', lang=lang))
                forms_b = StudyForms.create_section_b_forms(lang=lang)
                all_forms['B'] = forms_b

                forms_b["baseline_knowledge"]
                forms_b["chatbot_use"]
                forms_b["trust_automated"]
                forms_b["info_channels"]
                forms_b["chatbot_expectations"]
                forms_b["chatbot_concerns"]
                from utils.ui import render_navigation_row
                render_navigation_row(forms_b["back_button"], forms_b["next_button"])
                forms_b["status"]

            with gr.Column(visible=False, elem_id=f"section_C_{prefix}") as tab_c:
                section_groups['C'] = tab_c
                gr.HTML(get_section_header_html('C', lang=lang))
                # Show task instructions and question counter immediately
                # above the chatbot interface.
                gr.HTML(get_task_instructions_html(lang=lang))
                question_counter_display = UIComponents.create_question_counter(lang=lang, prefix=prefix)

                # Progress display for the whole study (per-language)
                progress_display = gr.HTML(get_progress_html(0, total=6, lang=lang), elem_id=f"study_progress_{prefix}")

                # Hidden placeholder used to inject small HTML scripts that update
                # the browser location.hash. We update this element when advancing
                # sections so the browser history contains a hash for each step.
                history_display = gr.HTML(value="", elem_id=f"study_history_{prefix}")

                # Now create the Section C form components so they are placed
                # beneath the instructions in the layout order.
                forms_c = StudyForms.create_section_c_forms(lang=lang)
                all_forms['C'] = forms_c

                with gr.Row():
                    with gr.Column(scale=1):
                        forms_c["chatbot_interface"]
                        forms_c["user_input"]
                        forms_c["send_btn"]

                from utils.ui import render_navigation_row
                render_navigation_row(forms_c["back_button"], forms_c["next_button"])
                forms_c["status"]

            with gr.Column(visible=False, elem_id=f"section_D_{prefix}") as tab_d:
                section_groups['D'] = tab_d
                gr.HTML(get_section_header_html('D', lang=lang))
                forms_d = StudyForms.create_section_d_forms(lang=lang)
                all_forms['D'] = forms_d

                forms_d["prototype_opened"]
                forms_d["interaction_time"]
                forms_d["perceived_accuracy"]
                forms_d["perceived_usefulness"]
                forms_d["act_on_advice"]
                forms_d["anxiety_change"]
                forms_d["perceived_limitations"]
                gr.HTML('<h4>System Usability</h4>')
                forms_d["sus1"]
                forms_d["sus2"]
                from utils.ui import render_navigation_row
                render_navigation_row(forms_d["back_button"], forms_d["next_button"])
                forms_d["status"]

            with gr.Column(visible=False, elem_id=f"section_E_{prefix}") as tab_e:
                section_groups['E'] = tab_e
                gr.HTML(get_section_header_html('E', lang=lang))
                forms_e = StudyForms.create_section_e_forms(lang=lang)
                all_forms['E'] = forms_e

                gr.HTML('<h4>Scenario 1: Mild Expected Side Effect</h4>')
                gr.HTML('<p><em>"What over-the-counter medicine can I take?" (after radionuclide therapy)</em></p>')
                forms_e["scenario1_trust"]
                forms_e["scenario1_reason"]
                
                gr.HTML('<h4>Scenario 2: Preparation Instructions</h4>')
                gr.HTML('<p><em>"How should I prepare for my therapy session?"</em></p>')
                forms_e["scenario2_trust"]
                forms_e["scenario2_reason"]

                gr.HTML('<h4>Scenario 3: Serious Side Effects</h4>')
                gr.HTML('<p><em>"I\'m experiencing severe nausea after treatment - what should I do?"</em></p>')
                forms_e["scenario3_trust"]
                forms_e["scenario3_reason"]

                from utils.ui import render_navigation_row
                render_navigation_row(forms_e["back_button"], forms_e["next_button"])
                forms_e["status"]

            with gr.Column(visible=False, elem_id=f"section_F_{prefix}") as tab_f:
                section_groups['F'] = tab_f
                gr.HTML(get_section_header_html('F', lang=lang))
                forms_f = StudyForms.create_section_f_forms(lang=lang)
                all_forms['F'] = forms_f

                forms_f["overall_satisfaction"]
                forms_f["improvements"]
                forms_f["recommend_tool"]
                forms_f["additional_feedback"]
                from utils.ui import render_navigation_row
                render_navigation_row(forms_f["back_button"], forms_f["complete_button"])
                forms_f["status"]
                forms_f["completion_message"]

        # Return the mapping of section containers so callers can update
        # visibility per-section, the forms dict, the question counter, the progress display,
        # and the hidden history display which is used to push URL hash updates.
        return section_groups, all_forms, question_counter_display, progress_display, history_display

class EventHandlers:
    """Contains event handling logic for the study application"""
    
    @staticmethod
    def create_chatbot_handler(study_manager):
        """Create chatbot interaction handler (language-aware)"""
        def handle_chatbot_interaction(message, history, session_id_val, count, lang='en'):
            """Handle chatbot interaction and update question count"""
            if not message.strip():
                return history, "", count, gr.update(), gr.update()

            # Determine language (default 'en') and forward to study manager
            lang_code = 'de' if str(lang).lower().startswith('d') else 'en'
            response, new_count = study_manager.get_chatbot_response(message, session_id_val, lang=lang_code)

            # Normalize incoming history to Gradio 'messages' format:
            # [{'role': 'user'|'assistant', 'content': '...'}, ...]
            normalized = []
            if history:
                # If history is a list of dicts already, keep it.
                if isinstance(history, list) and len(history) > 0 and isinstance(history[0], dict) and 'role' in history[0]:
                    normalized = history.copy()
                else:
                    # Handle legacy pair-format [[user, assistant], ...]
                    try:
                        for pair in history:
                            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                                normalized.append({'role': 'user', 'content': pair[0]})
                                normalized.append({'role': 'assistant', 'content': pair[1]})
                    except Exception:
                        normalized = []

            # Append new messages in messages format
            normalized.append({'role': 'user', 'content': message})
            normalized.append({'role': 'assistant', 'content': response})

            # Update counter display
            counter_html = get_question_counter_html(new_count, lang=lang_code)

            # Show next button if enough questions asked
            show_next = new_count >= 3

            return normalized, "", new_count, gr.update(value=counter_html), gr.update(visible=show_next)
        
        return handle_chatbot_interaction
    
    @staticmethod
    def create_section_advance_handler(study_manager):
        """Create section advancement handler"""
        def advance_section(current, session_id_val, from_section, to_section, *form_data):
            """Advance to next section after saving current section data"""
            
            # Save current section data
            data_dict = {f"field_{i}": value for i, value in enumerate(form_data) if value is not None}
            study_manager.save_section_data(session_id_val, from_section, data_dict)
            
            # Status message
            from styles import get_section_completed_html, get_progress_html
            # Determine language for this session (saved when the user started the study)
            session_info = study_manager.user_sessions.get(session_id_val, {})
            lang = session_info.get('lang', 'en')
            status_html = get_section_completed_html(from_section, lang=lang)

            # Compute progress (how many sections completed)
            completed = len(session_info.get('completed_sections', []))
            progress_html = get_progress_html(completed, total=6, lang=lang)

            # Build visibility updates for sections A-F. The `to_section` is
            # made visible and all others hidden.
            sections = ['A', 'B', 'C', 'D', 'E', 'F']
            visibility_updates = []
            for s in sections:
                visible = (s == to_section)
                visibility_updates.append(gr.update(visible=visible))

            # Also create a small HTML snippet that, when applied, will set the
            # browser's location.hash so the browser creates a history entry.
            # Gradio will insert this HTML into the DOM; the inline script will
            # update location.hash to the destination section (e.g., '#C').
            history_html = f"""
            <div style="display:none;">
              <script>try{{ location.hash = '#{to_section}'; }}catch(e){{/* ignore */}}</script>
            </div>
            """

            # Update session current_section and log to terminal for debugging/traceability
            try:
                if session_id_val in study_manager.user_sessions:
                    study_manager.user_sessions[session_id_val]['current_section'] = to_section
            except Exception:
                pass

            try:
                from datetime import datetime
                print(f"[{datetime.now().isoformat()}] Session '{session_id_val}' advanced to section {to_section}")
            except Exception:
                print(f"Session '{session_id_val}' advanced to section {to_section}")

            # Return visibility updates for A..F followed by the status HTML, progress HTML, and the history script HTML.
            return (*visibility_updates, gr.update(value=status_html), gr.update(value=progress_html), gr.update(value=history_html))
        
        return advance_section
    
    @staticmethod
    def create_completion_handler(study_manager):
        """Create study completion handler"""
        def complete_study_handler(session_id_val, *form_data):
            """Complete the study"""
            data_dict = {f"field_{i}": value for i, value in enumerate(form_data) if value is not None}
            study_manager.save_section_data(session_id_val, "F", data_dict)
            
            from styles import get_completion_html
            completion_html = get_completion_html(session_id_val)
            
            return gr.update(visible=True, value=completion_html)
        
        return complete_study_handler

    @staticmethod
    def create_section_back_handler(study_manager):
        """Create handler to move back to a previous section"""
        def back_section(current, session_id_val, from_section, to_section, *form_data):
            # Save current section data
            data_dict = {f"field_{i}": value for i, value in enumerate(form_data) if value is not None}
            study_manager.save_section_data(session_id_val, from_section, data_dict)

            from styles import get_section_completed_html, get_progress_html
            session_info = study_manager.user_sessions.get(session_id_val, {})
            lang = session_info.get('lang', 'en')
            # Note: for backward navigation we can also show a short status
            status_html = get_section_completed_html(from_section, lang=lang)

            completed = len(session_info.get('completed_sections', []))
            progress_html = get_progress_html(completed, total=6, lang=lang)

            sections = ['A', 'B', 'C', 'D', 'E', 'F']
            visibility_updates = []
            for s in sections:
                visible = (s == to_section)
                visibility_updates.append(gr.update(visible=visible))

            history_html = f"""
            <div style="display:none;">
              <script>try{{ location.hash = '#{to_section}'; }}catch(e){{/* ignore */}}</script>
            </div>
            """

            # Update session current_section and log to terminal
            try:
                if session_id_val in study_manager.user_sessions:
                    study_manager.user_sessions[session_id_val]['current_section'] = to_section
            except Exception:
                pass

            try:
                from datetime import datetime
                print(f"[{datetime.now().isoformat()}] Session '{session_id_val}' moved back to section {to_section}")
            except Exception:
                print(f"Session '{session_id_val}' moved back to section {to_section}")

            return (*visibility_updates, gr.update(value=status_html), gr.update(value=progress_html), gr.update(value=history_html))

        return back_section