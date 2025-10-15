"""
Study Configuration Module
Contains constants and settings for the Patient Education Chatbot Study
"""

# Study configuration
STUDY_SECTIONS = ['demographics', 'chatbot_interaction', 'feedback']

# UI Configuration
MAX_WIDTH = "800px"
CHATBOT_HEIGHT = 400
MINIMUM_QUESTIONS = 3

# Demographics choices
AGE_GROUPS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

GENDER_OPTIONS = ["Männlich", "Weiblich", "Andere", "Keine Angabe"]

EDUCATION_LEVELS = [
    "Hauptschule oder weniger",
    "Weiterführende Schule", 
    "Bachelor-Abschluss",
    "Master-Abschluss",
    "Doktorat",
    "Andere"
]

MEDICAL_BACKGROUND_OPTIONS = ["Ja", "Nein"]

CHATBOT_EXPERIENCE_OPTIONS = ["Nie", "Selten", "Manchmal", "Oft", "Sehr oft"]

# Feedback scale options
RATING_SCALE = {
    'min': 1,
    'max': 10,
    'default': 5,
    'step': 1
}

WOULD_USE_OPTIONS = [
    "Auf jeden Fall ja", 
    "Wahrscheinlich ja", 
    "Nicht sicher", 
    "Wahrscheinlich nein", 
    "Auf keinen Fall"
]

# Study instructions
STUDY_INSTRUCTIONS = """
**Anweisungen:** Sie werden nun mit einem Chatbot interagieren, der zur Patientenaufklärung über Dosimetrie und Patientensicherheit bei nuklearmedizinischen Behandlungen entwickelt wurde.

Wählen Sie mindestens 3-5 Fragen aus den vordefinierten Fragen unten aus. Die Fragen fokussieren auf Strahlendosimetrie, Sicherheitsmaßnahmen und Schutzmaßnahmen. Nach jeder Antwort des Chatbots können Sie **Nachfragen** stellen, um weitere Details zu erhalten.

**Tipp:** Klicken Sie auf eine Frage, um sie dem Chatbot zu stellen. Nach der Antwort können Sie das Textfeld für Nachfragen so oft verwenden, wie Sie möchten.
"""

# Predefined questions for the chatbot interaction
PREDEFINED_QUESTIONS = [
    "Was ist Dosimetrie und warum ist sie wichtig?",
    "Wie wird die Strahlendosis bei der Behandlung berechnet?",
    "Welche Sicherheitsmaßnahmen gibt es zum Schutz vor Strahlung?",
    "Wie lange bin ich nach der Behandlung radioaktiv?",
    "Welche Vorsichtsmaßnahmen muss ich zu Hause beachten?",
    "Ist die Strahlenbelastung für meine Familie gefährlich?",
    "Wie wird meine Strahlendosis überwacht?",
    "Welche Grenzwerte gibt es für die Strahlenexposition?",
    "Wie schützt sich das medizinische Personal vor Strahlung?",
    "Was passiert, wenn ich zu viel Strahlung abbekomme?"
]


# Attitude & Expectations choices and text
PRIOR_USE_CHOICES = ["Nie verwendet", "Einmal verwendet", "Gelegentlich", "Häufig"]

TRUST_LIKERT_MIN = 1
TRUST_LIKERT_MAX = 7
TRUST_LIKERT_DEFAULT = 4

PREFERRED_CHANNELS_CHOICES = [
    "Arztgespräch",
    "Flyer/Informationsblatt",
    "Krankenhaus-Website",
    "Chatbot",
    "Patientenforum",
    "Video",
    "Telefonanruf",
    "Andere"
]

PRIMARY_EXPECTATIONS_CHOICES = [
    "Klare Erklärungen",
    "Vorbereitungsschritte",
    "Nebenwirkungsberatung",
    "Terminerinnerungen",
    "Emotionale Beruhigung",
    "Links zu weiteren Informationen",
    "Kontakt zum Arzt",
    "Andere"
]

CONCERNS_CHOICES = [
    "Genauigkeit",
    "Datenschutz",
    "Missverständnis meiner Situation",
    "Mangel an Empathie",
    "Nicht individualisiert",
    "Technische Probleme",
    "Keine",
    "Andere"
]

ATTITUDE_TITLE = "## Einstellung & Erwartungen"
ATTITUDE_SUBTEXT = "Bitte teilen Sie uns Ihre Einstellung zu Chatbots und Ihre Erwartungen mit:"

# CSS styling
APP_CSS = """
.gradio-container {
    max-width: 800px !important;
    margin: auto !important;
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-size: 16px !important; /* Increased base font size */
}

* {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-size: inherit !important; /* Inherit the larger base size */
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-weight: 600 !important;
}

h1 { font-size: 2rem !important; }
h2 { font-size: 1.75rem !important; }
h3 { font-size: 1.5rem !important; }
h4 { font-size: 1.25rem !important; }

.gr-button {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-weight: 500 !important;
    font-size: 16px !important; /* Larger button text */
    padding: 12px 24px !important; /* Larger button padding */
}

/* Larger text for form elements */
.gr-textbox label,
.gr-dropdown label,
.gr-radio label,
.gr-slider label {
    font-size: 18px !important;
    font-weight: 500 !important;
}

/* Larger text for chatbot messages */
.gr-chatbot .message {
    font-size: 16px !important;
    line-height: 1.5 !important;
}

/* Style the actual input containers */
.gr-form > div,
.gr-radio > div,
.gr-dropdown > div,
.gr-textbox > div {
    border: 2px solid #e5e7eb !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 12px !important; /* Increased padding */
    background: white !important;
    font-size: 16px !important;
}

/* Style the label of our custom dropdowns */
.demographic-dropdown .label-wrap {
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important;
    color: white !important;
    padding: 12px !important;
    border-top-left-radius: 6px !important;
    border-top-right-radius: 6px !important;
    font-size: 18px !important;
}

/* Style the input area of the dropdown */
.demographic-dropdown .svelte-1gfkn6j {
    background-color: #e0e7ff !important;
    color: #e0e7ff !important;
    padding: 12px !important;
    width: 100% !important;
    font-size: 16px !important;
}
.label-wrap .svelte-g2oxp3 {
    width: 100% !important;
    background-color: #e0e7ff !important;
}

/* Style the dropdown items on hover */
.demographic-dropdown ul li:hover {
    background-color: #a855f7 !important;
    color: white !important;
}

/* Style the dropdown arrow */
.demographic-dropdown .arrow-down {
    color: #7c3aed !important;
}

/* App header styling */
.app-header {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: min(12px, 2vw) !important;
    padding: min(12px, 2vw) 0 !important;
}

/* Responsive icon sizing */
.app-header .icon {
    display: inline-block !important;
}

.responsive-icon {
    width: clamp(24px, 4vw, 48px) !important;
    height: clamp(24px, 4vw, 48px) !important;
    display: inline-block !important;
    max-width: 100% !important;
}

.app-header h1 {
    margin: 0 !important;
    font-size: clamp(1.2rem, 3vw, 1.8rem) !important; /* Increased header font size */
    font-weight: 700 !important;
}

/* Media queries for fine-tuned responsive behavior */
@media (max-width: 480px) {
    .responsive-icon {
        width: 28px !important;
        height: 28px !important;
    }
    .app-header h1 {
        font-size: 1.3rem !important;
    }
    .app-header {
        gap: 8px !important;
        padding: 8px 0 !important;
    }
    .gradio-container {
        font-size: 14px !important;
    }
}

@media (min-width: 481px) and (max-width: 768px) {
    .responsive-icon {
        width: 32px !important;
        height: 32px !important;
    }
    .app-header h1 {
        font-size: 1.4rem !important;
    }
    .gradio-container {
        font-size: 15px !important;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .responsive-icon {
        width: 36px !important;
        height: 36px !important;
    }
    .app-header h1 {
        font-size: 1.5rem !important;
    }
}

@media (min-width: 1025px) {
    .responsive-icon {
        width: 42px !important;
        height: 42px !important;
    }
    .app-header h1 {
        font-size: 1.6rem !important;
    }
}

/* Chatbot type indicator styling */
.chatbot-type-indicator {
    display: inline-block !important;
    margin: 10px auto !important;
    padding: 8px 16px !important;
    border-radius: 5px !important;
    font-size: 12px !important;
    text-align: center !important;
}

.chatbot-type-indicator.normal {
    background: white !important;
}

.chatbot-type-indicator.expert {
    background: white !important;
}
"""

# Study data configuration
STUDY_TYPE = 'patient_education_chatbot'
CHATBOT_CONTEXT = "patient_education_study"
CHATBOT_SECTION = "interaction"

# Consent / intro text
CONSENT_TITLE = "# Einverständniserklärung"
CONSENT_TEXT = (
    "Diese Studie wird einen Chatbot bewerten, der zur Patientenaufklärung über Dosimetrie und Patientensicherheit bei nuklearmedizinischen Behandlungen entwickelt wurde. "
    "Der Fokus liegt auf Strahlenschutz, Dosisberechnungen und Sicherheitsmaßnahmen. "
    "Ihre Teilnahme ist freiwillig. Wir werden Ihre Antworten und die Chat-Interaktion für Forschungszwecke sammeln. "
    "Alle Daten werden anonymisiert und sicher gespeichert. Es werden keine persönlichen Identifikatoren gesammelt.\n\n"
    "Wenn Sie der Teilnahme und der Verwendung Ihrer anonymisierten Daten für die Forschung zustimmen, wählen Sie bitte 'Ich stimme zu' unten aus, um fortzufahren."
)

CONSENT_CHOICES = ["Ich stimme zu", "Ich stimme nicht zu"]