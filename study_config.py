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
"""

# Study data configuration
STUDY_TYPE = 'patient_education_chatbot'
CHATBOT_CONTEXT = "patient_education_study"
CHATBOT_SECTION = "interaction"