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
}
"""

# Study data configuration
STUDY_TYPE = 'patient_education_chatbot'
CHATBOT_CONTEXT = "patient_education_study"
CHATBOT_SECTION = "interaction"