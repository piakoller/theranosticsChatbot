"""
Study Configuration Module
Contains constants and settings for the Patient Education Chatbot Study
"""

# Study configuration
STUDY_SECTIONS = ['demographics', 'chatbot_interaction', 'feedback']

# UI Configuration
APP_TITLE = "Patient Education Chatbot Study"
MAX_WIDTH = "800px"
CHATBOT_HEIGHT = 400
MINIMUM_QUESTIONS = 3

# Demographics choices
AGE_GROUPS = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

GENDER_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]

EDUCATION_LEVELS = [
    "High school or less",
    "Some college",
    "Bachelor's degree", 
    "Master's degree",
    "Doctoral degree",
    "Other"
]

MEDICAL_BACKGROUND_OPTIONS = ["Yes", "No"]

CHATBOT_EXPERIENCE_OPTIONS = ["Never", "Rarely", "Sometimes", "Often", "Very often"]

# Feedback scale options
RATING_SCALE = {
    'min': 1,
    'max': 10,
    'default': 5,
    'step': 1
}

WOULD_USE_OPTIONS = [
    "Definitely yes", 
    "Probably yes", 
    "Not sure", 
    "Probably no", 
    "Definitely no"
]

# Study instructions
STUDY_INSTRUCTIONS = """
**Instructions:** You will now interact with a chatbot designed to provide patient education about theranostics treatments. 

Please ask at least 3-5 questions about:
- What is theranostics?
- Treatment procedures
- Side effects and management
- Pre/post-treatment care
- Any other questions you might have

**Tip:** Type your question and press **Enter** to send, or click the Send button.

Take your time and ask questions as if you were a real patient seeking information.
"""


# Attitude & Expectations choices and text
PRIOR_USE_CHOICES = ["Never used", "Used once", "Occasionally", "Frequently"]

TRUST_LIKERT_MIN = 1
TRUST_LIKERT_MAX = 7
TRUST_LIKERT_DEFAULT = 4

PREFERRED_CHANNELS_CHOICES = [
    "Physician consultation",
    "Printed leaflet",
    "Hospital website",
    "Chatbot",
    "Patient forum",
    "Video",
    "Phone call",
    "Other"
]

PRIMARY_EXPECTATIONS_CHOICES = [
    "Clear explanations",
    "Preparation steps",
    "Side-effect guidance",
    "Appointment reminders",
    "Emotional reassurance",
    "Links to further reading",
    "Contact clinician option",
    "Other"
]

CONCERNS_CHOICES = [
    "Accuracy",
    "Privacy",
    "Misunderstanding my situation",
    "Lack of empathy",
    "Not tailored",
    "Technical issues",
    "None",
    "Other"
]

ATTITUDE_TITLE = "## Attitude & Expectations"
ATTITUDE_SUBTEXT = "Please tell us about your attitude towards chatbots and what you expect from them:"

# CSS styling
APP_CSS = """
.gradio-container {
    max-width: 800px !important;
    margin: auto !important;
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
}

* {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-weight: 600 !important;
}

.gr-button {
    font-family: 'Segoe UI', 'Arial', sans-serif !important;
    font-weight: 500 !important;
}

/* Style the actual input containers */
.gr-form > div,
.gr-radio > div,
.gr-dropdown > div,
.gr-textbox > div {
    border: 2px solid #e5e7eb !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 8px !important;
    background: white !important;
}

/* Style the label of our custom dropdowns */
.demographic-dropdown .label-wrap {
    background: linear-gradient(90deg, #7c3aed, #a855f7) !important;
    color: white !important;
    padding: 10px !important;
    border-top-left-radius: 6px !important;
    border-top-right-radius: 6px !important;
}

/* Style the input area of the dropdown */
.demographic-dropdown .svelte-1gfkn6j {
    background-color: #e0e7ff !important;
    color: #e0e7ff !important;
    padding: 10px !important;
    width: 100% !important;
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
    font-size: clamp(1rem, 3vw, 1.5rem) !important;
    font-weight: 700 !important;
}

/* Media queries for fine-tuned responsive behavior */
@media (max-width: 480px) {
    .responsive-icon {
        width: 28px !important;
        height: 28px !important;
    }
    .app-header h1 {
        font-size: 1.1rem !important;
    }
    .app-header {
        gap: 8px !important;
        padding: 8px 0 !important;
    }
}

@media (min-width: 481px) and (max-width: 768px) {
    .responsive-icon {
        width: 32px !important;
        height: 32px !important;
    }
    .app-header h1 {
        font-size: 1.2rem !important;
    }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .responsive-icon {
        width: 36px !important;
        height: 36px !important;
    }
    .app-header h1 {
        font-size: 1.3rem !important;
    }
}

@media (min-width: 1025px) {
    .responsive-icon {
        width: 42px !important;
        height: 42px !important;
    }
    .app-header h1 {
        font-size: 1.4rem !important;
    }
}
"""

# Study data configuration
STUDY_TYPE = 'patient_education_chatbot'
CHATBOT_CONTEXT = "patient_education_study"
CHATBOT_SECTION = "interaction"

# Consent / intro text
CONSENT_TITLE = "# Participant Information & Consent"
CONSENT_TEXT = (
    "This study will evaluate a chatbot designed to provide patient education about theranostics treatments. "
    "Your participation is voluntary. We will collect your responses and the chat interaction for research purposes. "
    "All data will be anonymized and stored securely. No personal identifiers will be collected.\n\n"
    "If you consent to participate and for your anonymized data to be used for research, please select 'I consent' below to continue."
)

CONSENT_CHOICES = ["I consent", "I do not consent"]