"""
Styling module for the Theranostics Chatbot User Study Application
Contains all CSS styles and styling-related configurations
"""

# Main CSS styles for the application (accessible, simplified palette)
MAIN_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

:root {
    /* Simplified palette: high-contrast navy text, soft neutral surfaces, single accent */
    --accent-color: #006494; /* accessible blue - good contrast */
    --accent-weak: #89c2d9;
    --bg: #ffffff;
    --surface: #f7f9fb;
    --text: #0b2545; /* dark navy for best contrast */
    --muted: #4b5563; /* secondary text */
    --success: #0b8457; /* green for success */
    --focus: #ffb703; /* warm visible focus color */
    --font-family: 'Roboto', sans-serif;
    --radius: 6px;
}

body, .gradio-container {
    font-family: var(--font-family);
    background-color: var(--bg);
    color: var(--text);
}

.study-header { 
    text-align: center; 
    margin-bottom: 1.5rem; 
    color: var(--text);
}

.study-header h1 {
    font-weight: 700;
    font-size: 2rem;
}

.section-header { 
    background-color: var(--surface);
    color: var(--text);
    padding: 1rem; 
    margin: 1.5rem 0; 
    border-radius: var(--radius); 
    border-left: 6px solid var(--accent-color);
}

.task-instruction { 
    background-color: #ffffff; /* keep it neutral */
    padding: 1rem; 
    margin: 0.75rem 0; 
    border-radius: var(--radius); 
    border-left: 6px solid var(--accent-weak);
}

.question-counter { 
    background-color: var(--surface); 
    padding: 0.75rem; 
    margin: 0.75rem 0; 
    border-radius: var(--radius); 
    border: 1px solid #e6eef6;
    color: var(--accent-color);
    text-align: center;
    font-weight: 600;
}

.next-button { 
    margin-top: 1.5rem; 
}

/* Constrain navigation button widths so Back and Next appear side-by-side
   even when global button styles expand them to full width. */
.next-button, .back-button {
    max-width: 260px; /* reasonable desktop width */
    width: 100%;
    margin: 0.5rem auto 0 auto;
    display: inline-block;
}

.gradio-button.primary {
    background-color: var(--accent-color) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    box-shadow: none !important;
}

.gradio-button.primary:hover {
    filter: brightness(0.95) !important;
}

.disabled-section { 
    opacity: 0.6; 
    pointer-events: none; 
}

.gradio-textbox, .gradio-radio, .gradio-checkboxgroup {
    border-radius: var(--radius) !important;
    border: 1px solid #dfeaf4 !important;
    padding: 10px !important;
    background-color: #ffffff !important;
}

/* Improved focus outline for keyboard users */
button:focus, .gradio-textbox:focus, .gradio-radio:focus, .gradio-checkboxgroup:focus {
    outline: 3px solid var(--focus) !important;
    outline-offset: 2px !important;
}

.gradio-tab-item {
    color: var(--muted) !important;
}

.gradio-tab-item.selected {
    color: var(--accent-color) !important;
}
"""

# Chatbot specific styles for stronger visibility
MAIN_CSS += """
# Chatbot container
# Chat messages area: add subtle border and background for contrast
# Note: Gradio's Chatbot may render as a div; we target the elem_id set on the component
# and the input field
# Ensure these styles are appended to the main CSS
#
# chat area
# Note: keep background slightly off-white to separate from page white
# and use a clear border color
#
# The selectors assume Gradio will render elements with these IDs
# if not, adjust accordingly in the browser inspector
#
# Chatbot box
#
##chatbot_interface .chatbot-messages, #chatbot_interface {
    border: 1px solid #d0e6f3;
    background: #fbfdff;
    padding: 8px;
    border-radius: 8px;
}

#chatbot_input {
    border: 1px solid #cfe9fb !important;
    box-shadow: none !important;
}

"""

# HTML templates for common UI elements
HTML_TEMPLATES_LANG = {
    "de": {
        "study_header": (
            """
    <div class="study-header">
        <h1>Theranostics Chatbot Benutzerstudie</h1>
        <p><strong>Evaluation KI-gestützter Patienteninformation in der Nuklearmedizin</strong></p>
        <p>Danke für Ihre Teilnahme an dieser Studie. Bitte bearbeiten Sie die Abschnitte der Reihe nach.</p>
    </div>
    """
        ),
        "question_counter": (
            """
    <div class="question-counter">
        <h4>Gestellte Fragen: {count} / 3-5 erforderlich</h4>
    </div>
    """
        ),
        "completion_success": (
            """
    <div class="section-header" style="background: #d4edda; border: 2px solid #28a745;">
        <h2>🎉 Studie abgeschlossen!</h2>
        <p>Vielen Dank für Ihre Teilnahme! Ihre Antworten wurden gespeichert.</p>
        <p><strong>Teilnehmer-ID:</strong> {session_id}</p>
        <p>Ihr Feedback hilft, KI-Tools zur Patienteninformation in der Nuklearmedizin zu verbessern.</p>
    </div>
    """
        ),
        "section_completed": (
            """
    <div style="color: green;">✅ Abschnitt {section} erfolgreich abgeschlossen</div>
    """
        )
    },
    "en": {
        "study_header": (
            """
    <div class="study-header">
        <h1>Theranostics Chatbot User Study</h1>
        <p><strong>Evaluating AI-assisted patient information in nuclear medicine</strong></p>
        <p>Thank you for participating. Please complete the sections in order.</p>
    </div>
    """
        ),
        "question_counter": (
            """
    <div class="question-counter">
        <h4>Questions asked: {count} / 3-5 required</h4>
    </div>
    """
        ),
        "completion_success": (
            """
    <div class="section-header" style="background: #d4edda; border: 2px solid #28a745;">
        <h2>🎉 Study completed!</h2>
        <p>Thank you for your participation. Your responses have been saved.</p>
        <p><strong>Participant ID:</strong> {session_id}</p>
    </div>
    """
        ),
        "section_completed": (
            """
    <div style="color: green;">✅ Section {section} completed</div>
    """
        )
    }
}

# Language-aware task instructions (keep the existing German html as 'de' and add English 'en')
TASK_INSTRUCTIONS = {
    "de": (
        """
    <div class="task-instruction">
        <h3>Aufgabenanweisungen zum Prototyp</h3>
        <p><strong>Stellen Sie 3–5 Fragen Ihrer Wahl zur Theranostik, Nuklearmedizin oder verwandten Themen.</strong></p>
        <p>Vorschläge (Sie können natürlich auch andere Fragen stellen):</p>
        <ul>
            <li>„Was ist Theranostik?“</li>
            <li>„Wie soll ich mich auf meinen PET-Scan vorbereiten?“</li>
            <li>„Welche Nebenwirkungen hat die Radionuklidtherapie?“</li>
            <li>„Ich habe Diabetes und eine Therapie geplant – was sollte ich meinem Arzt sagen?“</li>
            <li>„Wie lange dauert die Behandlung?“</li>
        </ul>
    </div>
    """
    ),
    "en": (
        """
    <div class="task-instruction">
        <h3>Prototype Task Instructions</h3>
        <p><strong>Ask 3–5 questions of your choice about theranostics, nuclear medicine or related topics.</strong></p>
        <p>Suggestions (you may ask other questions):</p>
        <ul>
            <li>"What is theranostics?"</li>
            <li>"How should I prepare for my PET scan?"</li>
            <li>"What side effects can radionuclide therapy cause?"</li>
            <li>"I have diabetes and therapy is planned — what should I tell my doctor?"</li>
            <li>"How long does the treatment take?"</li>
        </ul>
    </div>
    """
    )
}


# Section metadata localized per language
SECTION_INFO = {
    "en": {
        "A": {"name": "Consent & Demographics", "description": "Please complete each section to proceed."},
        "B": {"name": "Pre-prototype Attitudes", "description": "Your expectations and prior experience."},
        "C": {"name": "Prototype Interaction", "description": "Interact with the chatbot prototype."},
        "D": {"name": "Post-prototype Evaluation", "description": "Rate your experience with the prototype."},
        "E": {"name": "Scenario Trust", "description": "Assess trust across example scenarios."},
        "F": {"name": "Final Feedback", "description": "Provide final feedback and suggestions."}
    },
    "de": {
        "A": {"name": "Einwilligung & Demographie", "description": "Bitte füllen Sie jeden Abschnitt aus, um zum nächsten zu gelangen."},
        "B": {"name": "Einstellungen vor dem Prototyp", "description": "Ihre Erwartungen und Vorerfahrungen."},
        "C": {"name": "Prototyp-Interaktion", "description": "Interagieren Sie mit dem Chatbot-Prototyp."},
        "D": {"name": "Bewertung nach dem Prototyp", "description": "Bewerten Sie Ihre Erfahrung mit dem Prototyp."},
        "E": {"name": "Szenario-Vertrauen", "description": "Beurteilen Sie das Vertrauen in verschiedene Szenarien."},
        "F": {"name": "Abschließendes Feedback", "description": "Geben Sie abschließendes Feedback und Vorschläge."}
    }
}


def get_task_instructions_html(lang='en'):
    """Return HTML for the task instructions in the requested language."""
    return TASK_INSTRUCTIONS.get(lang, TASK_INSTRUCTIONS['en'])


def get_study_header_html(lang='en'):
    """Return the language-specific study header HTML."""
    return HTML_TEMPLATES_LANG.get(lang, HTML_TEMPLATES_LANG['en'])['study_header']


def get_section_header_html(section, lang='en'):
    """Return a localized section header HTML block for a given section key (A..F)."""
    info = SECTION_INFO.get(lang, SECTION_INFO['en']).get(section, {})
    name = info.get('name', f'Section {section}')
    desc = info.get('description', '')
    html = f'<div class="section-header"><h2>{name}</h2>'
    if desc:
        html += f'<p>{desc}</p>'
    html += '</div>'
    return html



def get_question_counter_html(count, lang='en'):
    """Generate question counter HTML for the requested language"""
    template = HTML_TEMPLATES_LANG.get(lang, HTML_TEMPLATES_LANG['en'])['question_counter']
    return template.format(count=count)

def get_completion_html(session_id, lang='en'):
    """Generate completion success HTML for the requested language"""
    template = HTML_TEMPLATES_LANG.get(lang, HTML_TEMPLATES_LANG['en'])['completion_success']
    return template.format(session_id=session_id)

def get_section_completed_html(section, lang='en'):
    """Generate section completed status HTML for the requested language"""
    template = HTML_TEMPLATES_LANG.get(lang, HTML_TEMPLATES_LANG['en'])['section_completed']
    return template.format(section=section)


def get_progress_html(completed, total=6, lang='en'):
    """Return a small progress HTML fragment showing completed/total sections.

    completed: number of sections completed
    total: total number of sections in the study (default 6)
    """
    pct = 0
    try:
        pct = int((completed / float(total)) * 100)
    except Exception:
        pct = 0

    # Localized label
    if lang.startswith('de'):
        label = f"Fortschritt: {completed} / {total} abgeschlossen"
    else:
        label = f"Progress: {completed} / {total} completed"

    html = f"""
    <div class="question-counter" style="text-align:left;">
      <div style="font-weight:600;margin-bottom:6px;">{label}</div>
      <div style="background:#e9f4fb;border-radius:6px;height:10px;width:100%;">
        <div style="background:var(--accent-color);width:{pct}%;height:10px;border-radius:6px;"></div>
      </div>
    </div>
    """
    return html