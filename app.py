import gradio as gr
import requests

# --- OpenRouter API Configuration ---
from config import (
    MODEL_KWARGS,
    OPENROUTER_API_KEY,
    OPENROUTER_API_URL,
    OPENROUTER_MODEL,
    PRIMARY_MODEL,
    BACKUP_MODELS,
)

# Load CSS from external file
def load_css():
    try:
        with open("style.css", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("⚠️  style.css not found, using no custom CSS")
        return ""

# Module-level variable to track current active model
current_model = OPENROUTER_MODEL

# Check OpenRouter API key at startup
def check_openrouter_key():
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY not set in environment variables.")
        return False
    return True

openrouter_available = check_openrouter_key()


def generate_openrouter_response(message, history):
    """
    Generate response using OpenRouter API with automatic fallback to backup models
    """
    global current_model
    
    # List of models to try (current active model first, then backups)
    models_to_try = [current_model] + [m for m in BACKUP_MODELS if m != current_model]
    first_model_failed = False  # Track if we need to inform user about issues
    
    for i, model in enumerate(models_to_try):
        try:
            # Patient education focused system prompt
            system_prompt = """You are a compassionate AI assistant specializing in patient education about theranostics and nuclear medicine. Help patients understand medical concepts in simple, reassuring terms.

**Communication Guidelines:**
1. **Keep answers concise** - Provide clear, focused responses (2-4 sentences for simple questions)
2. **Use simple language** - Avoid medical jargon, explain in everyday terms
3. **Be reassuring and empathetic** - Acknowledge concerns with understanding
4. **For complex topics** - Give a brief overview, then encourage: "Would you like me to explain any specific part in more detail?"
5. **End with engagement** - Ask "What specific aspect would you like to know more about?" or "Do you have questions about [specific part]?"
6. **Remind about medical team** - Always note they should discuss specifics with their healthcare providers

**Response Style:**
- Start with a direct, simple answer
- Add 1-2 key points if needed  
- For complex topics: briefly summarize, then invite follow-up questions
- Always end by encouraging further questions or discussion with their medical team

**Target Audience:** Patients, families, and caregivers seeking clear, digestible information about their treatment options."""

            # Prepare conversation context with enhanced message formatting
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            if history:
                # Include more context (last 5 exchanges instead of 3)
                recent_history = history[-10:] if len(history) > 10 else history  # Get last 10 messages (5 exchanges)
                for msg in recent_history:
                    if msg["role"] in ["user", "assistant"]:
                        messages.append(msg)
            
            # Enhance the user's question with context if it's too brief
            enhanced_message = message
            if len(message.split()) < 5:  # If question is very short
                enhanced_message = f"Please provide a comprehensive explanation about: {message}"
            
            messages.append({"role": "user", "content": enhanced_message})

            payload = {
                "model": model,
                "messages": messages,
                **MODEL_KWARGS
            }
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://openrouter.ai/",
                "X-Title": "Theranostics Chatbot"
            }
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                assistant_response = result["choices"][0]["message"]["content"].strip()
                if not assistant_response:
                    assistant_response = "I understand your question. Could you please provide more details so I can give you a more specific answer?"
                
                # If we're using a backup model, update the current model and inform user
                if i > 0 and model != current_model:
                    current_model = model
                    print(f"✅ Switched to backup model: {model}")
                    # Add a brief notice to the response for users
                    model_name = model.split('/')[-1].replace(':free', '').replace('-', ' ').title()
                    assistant_response = f"*I've switched to a backup model ({model_name}) to ensure I can help you.*\n\n{assistant_response}"
                
                return assistant_response
            else:
                # Enhanced error handling for specific error types
                try:
                    error_data = response.json() if response.text else {}
                    error_message = error_data.get('error', {}).get('message', '')
                    error_code = error_data.get('error', {}).get('code', response.status_code)
                    
                    # Check for specific error conditions that warrant fallback
                    should_fallback = False
                    error_reason = ""
                    
                    if response.status_code == 429:
                        should_fallback = True
                        error_reason = "rate-limited"
                    elif response.status_code == 503:
                        should_fallback = True
                        error_reason = "service unavailable"
                    elif "rate-limited" in error_message.lower():
                        should_fallback = True
                        error_reason = "rate-limited upstream"
                    elif "no instances available" in error_message.lower():
                        should_fallback = True
                        error_reason = "no instances available"
                    elif "provider returned error" in error_message.lower():
                        should_fallback = True
                        error_reason = "provider error"
                    elif response.status_code >= 500:
                        should_fallback = True
                        error_reason = "server error"
                    
                    print(f"❌ Model {model} error ({response.status_code}): {error_reason}")
                    if error_message:
                        print(f"   Details: {error_message[:200]}...")
                    
                    if should_fallback and i < len(models_to_try) - 1:
                        # Mark that we had issues with the primary model
                        if i == 0:
                            first_model_failed = True
                        print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                        continue
                    elif not should_fallback:
                        # For non-fallback errors, return specific message
                        return f"I encountered an issue with the language model. Please try again or contact support if this persists."
                    else:
                        # All models failed
                        if first_model_failed:
                            return "I'm experiencing technical difficulties with all available AI models. Please try again in a few moments, and I'll do my best to help you."
                        else:
                            return "All language models are currently experiencing issues. Please try again in a few moments."
                        
                except (ValueError, KeyError):
                    # If we can't parse the error response, treat as generic error
                    print(f"❌ Model {model} error: {response.status_code} (unparseable response)")
                    if i < len(models_to_try) - 1:
                        if i == 0:
                            first_model_failed = True
                        print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                        continue
                    else:
                        return "I'm having trouble connecting to the language model. Please try again in a few moments."
                    
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout with model {model}")
            if i < len(models_to_try) - 1:
                if i == 0:
                    first_model_failed = True
                print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                continue
            else:
                return "The request timed out. Please try asking your question again."
        except Exception as e:
            print(f"❌ Error with model {model}: {e}")
            if i < len(models_to_try) - 1:
                if i == 0:
                    first_model_failed = True
                print(f"🔄 Trying backup model: {models_to_try[i+1]}")
                continue
            else:
                return "I apologize, but I'm having trouble processing your request right now. Please try again."
    
    # If we get here, all models failed
    if first_model_failed:
        return "I'm currently experiencing technical difficulties with all available AI models. Please try again in a few moments, and I'll do my best to help you with your question."
    else:
        return "I'm unable to process your request at the moment. Please try again later."


def chatbot_response(message, history):
    """
    Main chatbot function that uses OpenRouter or falls back to predefined responses
    """
    if openrouter_available:
        return generate_openrouter_response(message, history)
    else:
        fallback_responses = [
            "I'm currently running in fallback mode. Please ensure OPENROUTER_API_KEY is set in your environment.",
            "I understand you have questions about your treatment. Please feel free to ask about anything that concerns you.",
            "Theranostics can seem complex, but I'm here to explain it in simple terms. What would you like to know?",
            "Many patients have similar concerns about nuclear medicine treatments. What specific questions do you have?",
        ]
        import random
        return random.choice(fallback_responses)


# Create the Gradio interface with ChatGPT-style CSS
with gr.Blocks(
    title="Theranostics Chatbot", 
    theme=gr.themes.Soft(),
    css=load_css()
) as demo:
    # Modern header with logo space
    with gr.Row(elem_classes="header-container"):
        with gr.Column():
            with gr.Row(elem_classes="logo-section"):
                gr.HTML("""
                <div>
                    <h1 class="main-title">🧬 Theranostics Assistant</h1>
                    <p class="subtitle">AI-Powered Patient Education & Support</p>
                </div>
                <div class="welcome-message">
                    <h3 style="margin-top: 0; color: #1f2937; font-size: 1.2rem;">Welcome to Your Theranostics Guide</h3>
                    <p style="margin: 0.5rem 0; color: #4b5563; line-height: 1.6;">
                        I'm here to help you understand theranostics and nuclear medicine treatments in simple, clear terms. 
                        Feel free to ask about treatment options, what to expect, safety concerns, or any other questions you may have.
                    </p>
                    <p style="margin: 0.5rem 0 0 0; color: #6b7280; font-size: 0.9rem; font-style: italic;">
                        💡 Remember: This information is educational. Always discuss your specific situation with your healthcare team.
                    </p>
                </div>
                """)

    # Example questions with improved styling
    with gr.Accordion("💡 Common Questions", open=False, elem_classes="questions-accordion"):
        gr.HTML("""
        <p style="margin: 0 0 1rem 0; color: #6b7280; font-size: 0.95rem;">
            Click any question below to get started, or type your own question in the chat.
        </p>
        """)
        with gr.Row():
            with gr.Column(scale=1):
                q1_btn = gr.Button("🔬 What is theranostics?", size="sm", variant="secondary")
                q2_btn = gr.Button("🛡️ Is nuclear medicine safe?", size="sm", variant="secondary")
                q3_btn = gr.Button("📋 What to expect during treatment", size="sm", variant="secondary")
            with gr.Column(scale=1):
                q4_btn = gr.Button("⚕️ Side effects and recovery", size="sm", variant="secondary")
                q5_btn = gr.Button("📊 How effective is this treatment?", size="sm", variant="secondary")
                q6_btn = gr.Button("📝 How should I prepare?", size="sm", variant="secondary")
            with gr.Column(scale=1):
                q7_btn = gr.Button("☢️ Will I be radioactive?", size="sm", variant="secondary")

    # Show model status with improved styling
    with gr.Row():
        with gr.Column():
            if openrouter_available:
                gr.HTML(f"""
                <div class="status-indicator">
                    <span style="color: #059669; font-weight: 600;">🟢 AI Model Active:</span> 
                    <span style="color: #374151; font-family: monospace; font-size: 0.9rem;">{current_model.split('/')[-1]}</span>
                </div>
                """)
            else:
                gr.HTML("""
                <div class="status-indicator">
                    <span style="color: #d97706; font-weight: 600;">🟡 Fallback Mode:</span> 
                    <span style="color: #374151;">Limited functionality - API key required</span>
                </div>
                """)

    # Main content area with tabs for chatbot and forms
    with gr.Tabs(selected=0) as tabs:
        with gr.TabItem("💬 Chat Assistant", elem_id="chat-tab"):
            # Enhanced chatbot interface
            chatbot = gr.Chatbot(
                value=[],
                elem_id="chatbot",
                height=500,
                show_copy_button=True,
                show_share_button=False,
                placeholder="💬 Start a conversation about theranostics...",
                type="messages",
                avatar_images=("👤", "🤖")
            )

            # ChatGPT-style input area with enhanced design
            with gr.Row(elem_classes="input-row"):
                msg = gr.Textbox(
                    placeholder="💬 Ask anything...",
                    container=False,
                    scale=1,
                    lines=1,
                    show_label=False,
                    elem_classes="chat-input"
                )
                submit_btn = gr.Button("˄", size="sm", variant="primary", elem_classes="send-button", scale=0)

        with gr.TabItem("📋 Feedback Form", elem_id="form-tab"):
            # Instructions for the custom form
            gr.HTML("""
            <div style="background-color: #f8fafc; border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h3 style="margin: 0 0 0.5rem 0; color: #1e40af; font-size: 1.1rem;">📝 Patient Feedback & Evaluation</h3>
                <p style="margin: 0; color: #475569; line-height: 1.5;">
                    Please complete this form to help us improve our theranostics education and support services. 
                    The AI assistant will appear automatically to help you when needed.
                </p>
            </div>
            """)
            
            # Custom form sections with conditional chatbot visibility
            with gr.Column():
                # Section navigation
                with gr.Row():
                    section_nav_a = gr.Button("📝 Section A: Demographics", variant="primary", scale=1)
                    section_nav_b = gr.Button("🏥 Section B: Treatment Experience", variant="secondary", scale=1)
                    section_nav_c = gr.Button("💭 Section C: Feedback & Comments", variant="secondary", scale=1)
                
                # Current section indicator
                current_form_section = gr.State("a")
                
                # Section A: Demographics
                with gr.Column(visible=True) as section_a:
                    gr.HTML("""
                    <div style="background-color: #dbeafe; border-left: 4px solid #3b82f6; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #1e40af;">📝 Section A: Demographics & Medical History</h4>
                    </div>
                    """)
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            age = gr.Number(label="Age", minimum=0, maximum=120)
                            gender = gr.Radio(["Male", "Female", "Other", "Prefer not to say"], label="Gender")
                            diagnosis = gr.Textbox(label="Primary Diagnosis", placeholder="e.g., Neuroendocrine tumor, Prostate cancer...")
                            
                        with gr.Column(scale=1):
                            # Show chatbot for Section A when requested
                            show_help_a = gr.Button("🤖 Get Help with Demographics", variant="secondary")
                            help_chatbot_a = gr.Chatbot(
                                value=[],
                                height=300,
                                visible=False,
                                label="Demographics Help Assistant",
                                type="messages",
                                avatar_images=("👤", "🤖")
                            )
                            help_msg_a = gr.Textbox(
                                placeholder="Ask about filling out demographics...",
                                visible=False,
                                show_label=False
                            )
                
                # Section B: Treatment Experience  
                with gr.Column(visible=False) as section_b:
                    gr.HTML("""
                    <div style="background-color: #f0fdf4; border-left: 4px solid #22c55e; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #166534;">🏥 Section B: Treatment Experience</h4>
                    </div>
                    """)
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            treatment_date = gr.Textbox(label="Treatment Date", placeholder="MM/YYYY or approximate")
                            treatment_satisfaction = gr.Slider(1, 10, value=5, label="Overall Treatment Satisfaction (1-10)")
                            side_effects = gr.CheckboxGroup(
                                ["Fatigue", "Nausea", "Pain", "Anxiety", "Sleep issues", "Other"],
                                label="Side Effects Experienced"
                            )
                            side_effects_severity = gr.Slider(1, 10, value=1, label="Side Effects Severity (1-10)")
                            
                        with gr.Column(scale=1):
                            # Show chatbot for Section B when requested
                            show_help_b = gr.Button("🤖 Get Help with Treatment Questions", variant="secondary")
                            help_chatbot_b = gr.Chatbot(
                                value=[],
                                height=300,
                                visible=False,
                                label="Treatment Experience Assistant",
                                type="messages",
                                avatar_images=("👤", "🤖")
                            )
                            help_msg_b = gr.Textbox(
                                placeholder="Ask about treatment experience...",
                                visible=False,
                                show_label=False
                            )
                
                # Section C: Feedback & Comments
                with gr.Column(visible=False) as section_c:
                    gr.HTML("""
                    <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                        <h4 style="margin: 0 0 0.5rem 0; color: #92400e;">💭 Section C: Feedback & Comments</h4>
                        <p style="margin: 0; color: #78350f; font-size: 0.9rem;">This section automatically shows the AI assistant to help you provide detailed feedback.</p>
                    </div>
                    """)
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            overall_feedback = gr.Textbox(
                                label="Overall Feedback", 
                                lines=4,
                                placeholder="Please share your overall experience with theranostic treatment..."
                            )
                            improvements = gr.Textbox(
                                label="Suggestions for Improvement",
                                lines=3,
                                placeholder="What could we improve to better support patients?"
                            )
                            recommend = gr.Radio(
                                ["Definitely", "Probably", "Maybe", "Probably not", "Definitely not"],
                                label="Would you recommend this treatment to others?"
                            )
                            
                        with gr.Column(scale=1):
                            # Always show chatbot for Section C
                            gr.HTML("""
                            <div style="background-color: #f0f9ff; border: 1px solid #3b82f6; border-radius: 0.5rem; padding: 0.75rem; margin-bottom: 1rem;">
                                <p style="margin: 0; color: #1e40af; font-size: 0.9rem; font-weight: 500;">
                                    🤖 AI Assistant Active
                                </p>
                                <p style="margin: 0.25rem 0 0 0; color: #475569; font-size: 0.8rem;">
                                    I'm here to help you provide detailed feedback!
                                </p>
                            </div>
                            """)
                            help_chatbot_c = gr.Chatbot(
                                value=[],
                                height=350,
                                visible=True,
                                label="Feedback Assistant",
                                type="messages",
                                avatar_images=("👤", "🤖")
                            )
                            help_msg_c = gr.Textbox(
                                placeholder="Ask for help with providing feedback...",
                                visible=True,
                                show_label=False
                            )
                
                # Form submission
                with gr.Row():
                    submit_form = gr.Button("📤 Submit Form", variant="primary", size="lg")
                    form_status = gr.HTML("""""", visible=False)
            
            # Help section for form assistance
            with gr.Accordion("🤔 Need Help with the Form?", open=False):
                gr.HTML("""
                <div style="padding: 1rem;">
                    <p style="margin: 0 0 1rem 0; color: #374151;">
                        If you're unsure about any question in the form, here are some quick help options:
                    </p>
                </div>
                """)
                
                with gr.Row():
                    form_help_q1 = gr.Button("❓ What is treatment satisfaction?", size="sm", variant="secondary")
                    form_help_q2 = gr.Button("❓ How to rate side effects?", size="sm", variant="secondary")
                    form_help_q3 = gr.Button("❓ What information should I share?", size="sm", variant="secondary")
                
                # Quick response area for form help
                form_help_response = gr.Textbox(
                    label="Quick Help Response",
                    interactive=False,
                    visible=False,
                    elem_classes="form-help-response"
                )

        with gr.TabItem("📊 Combined View", elem_id="combined-tab"):
            gr.HTML("""
            <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 1rem; margin: 1rem 0; border-radius: 0.5rem;">
                <h3 style="margin: 0 0 0.5rem 0; color: #92400e; font-size: 1.1rem;">🔄 Interactive Experience</h3>
                <p style="margin: 0; color: #78350f; line-height: 1.5;">
                    Fill out the form with AI assistance. The chatbot appears automatically when you need help!
                </p>
            </div>
            """)
            
            with gr.Row(equal_height=True):
                with gr.Column(scale=3):
                    # Compact form sections
                    with gr.Row():
                        combined_section_a = gr.Button("📝 Demographics", variant="primary", scale=1)
                        combined_section_b = gr.Button("🏥 Treatment Experience", variant="secondary", scale=1)
                        combined_section_c = gr.Button("💭 Feedback", variant="secondary", scale=1)
                    
                    combined_current_section = gr.State("a")
                    
                    # Compact Demographics Section
                    with gr.Column(visible=True) as combined_demo_section:
                        gr.HTML("<h4 style='color: #1e40af; margin: 0.5rem 0;'>📝 Demographics</h4>")
                        with gr.Row():
                            combined_age = gr.Number(label="Age", scale=1)
                            combined_gender = gr.Radio(["Male", "Female", "Other"], label="Gender", scale=2)
                        combined_diagnosis = gr.Textbox(label="Diagnosis", placeholder="Primary diagnosis...")
                    
                    # Compact Treatment Section
                    with gr.Column(visible=False) as combined_treatment_section:
                        gr.HTML("<h4 style='color: #166534; margin: 0.5rem 0;'>🏥 Treatment Experience</h4>")
                        combined_treatment_date = gr.Textbox(label="Treatment Date", placeholder="MM/YYYY")
                        combined_satisfaction = gr.Slider(1, 10, value=5, label="Satisfaction (1-10)")
                        combined_side_effects = gr.CheckboxGroup(
                            ["Fatigue", "Nausea", "Pain", "Other"], 
                            label="Side Effects"
                        )
                    
                    # Compact Feedback Section
                    with gr.Column(visible=False) as combined_feedback_section:
                        gr.HTML("<h4 style='color: #92400e; margin: 0.5rem 0;'>💭 Feedback & Comments</h4>")
                        combined_overall_feedback = gr.Textbox(
                            label="Overall Feedback", 
                            lines=3,
                            placeholder="Share your experience..."
                        )
                        combined_recommend = gr.Radio(
                            ["Definitely", "Probably", "Maybe", "Probably not"],
                            label="Recommend to others?"
                        )
                
                with gr.Column(scale=2):
                    # Dynamic chatbot that appears based on section and user needs
                    chatbot_status = gr.HTML("""
                    <div style="background-color: #f3f4f6; border: 1px solid #d1d5db; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; text-align: center;">
                        <p style="margin: 0; color: #6b7280; font-style: italic;">
                            🤖 AI Assistant will appear when you need help
                        </p>
                    </div>
                    """)
                    
                    combined_chatbot = gr.Chatbot(
                        value=[],
                        elem_id="combined-chatbot",
                        height=400,
                        show_copy_button=True,
                        show_share_button=False,
                        placeholder="💬 Ask questions about the form...",
                        type="messages",
                        avatar_images=("👤", "🤖"),
                        visible=False
                    )
                    
                    combined_msg = gr.Textbox(
                        placeholder="💬 Ask for help with the form...",
                        container=False,
                        scale=1,
                        lines=1,
                        show_label=False,
                        elem_classes="chat-input",
                        visible=False
                    )
                    
                    combined_submit = gr.Button("˄", size="sm", variant="primary", elem_classes="send-button", visible=False)
                    
                    # Help buttons for each section
                    with gr.Column():
                        need_help_btn = gr.Button("🆘 I Need Help", variant="secondary", visible=True)
                        hide_help_btn = gr.Button("✖️ Hide Assistant", variant="secondary", visible=False)

    # Keep the original standalone chatbot elements for backward compatibility (but make them invisible)
    chatbot_hidden = gr.Chatbot(
        value=[],
        elem_id="chatbot-hidden",
        height=500,
        show_copy_button=True,
        show_share_button=False,
        placeholder="💬 Start a conversation about theranostics...",
        type="messages",
        avatar_images=("👤", "🤖"),
        visible=False
    )

    msg_hidden = gr.Textbox(
        placeholder="💬 Ask anything...",
        container=False,
        scale=1,
        lines=1,
        show_label=False,
        elem_classes="chat-input",
        visible=False
    )
    submit_btn_hidden = gr.Button("˄", size="sm", variant="primary", elem_classes="send-button", scale=0, visible=False)



    # Example question click handlers
    def set_question(question):
        return question
    
    # Function to handle example questions - directly adds to chat and gets response
    def handle_example_question(question, history):
        # Add the question directly to chat history without showing in input
        new_history = history + [{"role": "user", "content": question}]
        return "", new_history  # Empty string for input field, updated history for chat
    
    # Function to handle form help questions
    def handle_form_help(question):
        form_help_responses = {
            "treatment_satisfaction": """**Treatment Satisfaction** refers to how pleased you are with your overall theranostic treatment experience. Consider factors like:
            • How well your symptoms improved
            • Communication with your medical team
            • Comfort during procedures
            • Whether your expectations were met
            
            Rate this honestly - your feedback helps improve care for future patients.""",
            
            "side_effects": """**Rating Side Effects:** Consider both severity and impact on your daily life:
            • **Mild (1-3):** Barely noticeable, doesn't affect daily activities
            • **Moderate (4-6):** Noticeable but manageable, some impact on activities  
            • **Severe (7-10):** Significantly affects daily life, requires medical attention
            
            Include both physical effects (fatigue, nausea) and emotional impacts.""",
            
            "information_sharing": """**What Information to Share:** Be as detailed as comfortable:
            • Specific symptoms you experienced and when
            • How treatment affected your quality of life
            • Any concerns or fears you had
            • Suggestions for improving the patient experience
            
            Your honest feedback, both positive and negative, helps improve care for others."""
        }
        return form_help_responses.get(question, "I can help explain any part of the feedback form. What specific question would you like help with?")
    
    # Function to provide contextual chatbot responses for forms
    def form_contextual_response(message, history, section="none"):
        """Enhanced chatbot response that's aware of form context and current section"""
        
        # Base form context
        form_context = """You are helping a patient who is filling out a feedback form about their theranostic treatment experience."""
        
        # Add section-specific context
        if section == "a":
            form_context += """ They are currently working on Section A (Demographics), which asks about basic information, medical history, and diagnosis. Help them understand what information to provide and why it's important."""
        elif section == "b":
            form_context += """ They are currently working on Section B (Treatment Experience), which focuses on their actual treatment experience, side effects, recovery, and ratings. Help them understand how to rate their experience and what factors to consider."""
        elif section == "c":
            form_context += """ They are currently working on Section C (Feedback & Comments), which asks for detailed feedback and suggestions. Encourage them to be honest and specific about their experience to help improve care for future patients."""
        else:
            form_context += """ They may ask questions about any part of the form including demographics, treatment experience, or feedback sections."""
        
        form_context += """
        
        Provide helpful, encouraging guidance while maintaining your patient education focus. Be specific about what information would be helpful to share and why it matters for improving theranostic care."""
        
        # Enhance the message with section context if relevant
        if any(keyword in message.lower() for keyword in ['form', 'rating', 'satisfaction', 'feedback', 'questionnaire', 'survey', 'section']):
            if section != "none":
                enhanced_message = f"[Form Section {section.upper()} Help] {message}"
            else:
                enhanced_message = f"[Form Help Request] {message}"
        else:
            enhanced_message = message
            
        return chatbot_response(enhanced_message, history)
    
    # Function to update section help display
    def update_section_help(section):
        if section in section_help_content:
            content = section_help_content[section]
            tips_html = "".join([f"<li style='margin: 0.25rem 0; color: #374151;'>{tip}</li>" for tip in content["tips"]])
            
            html_content = f"""
            <div style="background-color: {content['color']}; border-left: 4px solid {content['border']}; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
                <h4 style="margin: 0 0 0.5rem 0; color: #1f2937; font-size: 1.1rem;">{content['title']}</h4>
                <p style="margin: 0 0 0.75rem 0; color: #4b5563; line-height: 1.5;">{content['description']}</p>
                <div style="margin: 0.5rem 0 0 0;">
                    <p style="margin: 0 0 0.5rem 0; color: #6b7280; font-weight: 600; font-size: 0.9rem;">💡 Tips for this section:</p>
                    <ul style="margin: 0; padding-left: 1.25rem; color: #374151;">
                        {tips_html}
                    </ul>
                </div>
            </div>
            """
            return html_content, section
        else:
            return """
            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 0.5rem; padding: 1rem; margin: 1rem 0;">
                <p style="margin: 0; color: #64748b; font-style: italic;">
                    👆 Select a section above to get specific help and enable targeted chatbot assistance.
                </p>
            </div>
            """, "none"
    
    # Define patient-focused questions
    questions = {
        "q1": "What are theranostics and how do they work in simple terms?",
        "q2": "Is nuclear medicine safe for patients? What are the risks?",
        "q3": "What should I expect during my theranostic treatment?",
        "q4": "What are the common side effects and how long does recovery take?",
        "q5": "How effective is theranostic treatment for my type of cancer?",
        "q6": "How should I prepare for my nuclear medicine treatment?",
        "q7": "Will I be radioactive after treatment? Is it safe for my family?"
    }

    # State variable to track current form section
    current_section = gr.State("none")
    
    # Section-specific help content
    section_help_content = {
        "a": {
            "title": "📝 Section A: Demographics",
            "description": "This section asks about your basic information like age, gender, diagnosis, and treatment history.",
            "tips": [
                "Be accurate with dates and medical history",
                "Include all relevant treatments you've received",
                "Don't worry if you don't remember exact dates - approximate is fine"
            ],
            "color": "#dbeafe",
            "border": "#3b82f6"
        },
        "b": {
            "title": "🏥 Section B: Treatment Experience", 
            "description": "This section focuses on your actual treatment experience, side effects, and recovery.",
            "tips": [
                "Rate based on your personal experience, not what you think is 'normal'",
                "Include both physical and emotional impacts",
                "Consider the entire treatment period, not just the procedure day"
            ],
            "color": "#f0fdf4",
            "border": "#22c55e"
        },
        "c": {
            "title": "💭 Section C: Feedback & Comments",
            "description": "This section asks for your detailed feedback and suggestions for improvement.",
            "tips": [
                "Be honest about both positive and negative experiences",
                "Share specific examples when possible",
                "Think about what would have helped you feel more prepared or comfortable"
            ],
            "color": "#fef3c7",
            "border": "#f59e0b"
        }
    }

    # Handle message submission for main chat tab
    def user_message(message, history):
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history

    def bot_message(history):
        if history and len(history) > 0:
            # Check if the last message is from user and needs a response
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                # Get previous messages for context (exclude the current user message)
                previous_history = history[:-1]
                bot_response = chatbot_response(user_msg, previous_history)
                return history + [{"role": "assistant", "content": bot_response}]
        return history

    # Handle message submission for combined view
    def combined_user_message(message, history):
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history

    def combined_bot_message(history, section):
        if history and len(history) > 0:
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                previous_history = history[:-1]
                bot_response = form_contextual_response(user_msg, previous_history, section)
                return history + [{"role": "assistant", "content": bot_response}]
        return history

    # Event handlers for main chat tab
    msg.submit(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_message, chatbot, chatbot
    )
    submit_btn.click(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_message, chatbot, chatbot
    )
    
    # Event handlers for combined view
    combined_msg.submit(combined_user_message, [combined_msg, combined_chatbot], [combined_msg, combined_chatbot], queue=False).then(
        combined_bot_message, [combined_chatbot, combined_current_section], combined_chatbot
    )
    combined_submit.click(combined_user_message, [combined_msg, combined_chatbot], [combined_msg, combined_chatbot], queue=False).then(
        combined_bot_message, [combined_chatbot, combined_current_section], combined_chatbot
    )
    
    # Event handlers for section-specific help chatbots
    def section_help_user_message(message, history):
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history
    
    def section_help_bot_message(history, section):
        if history and len(history) > 0:
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                previous_history = history[:-1]
                bot_response = form_contextual_response(user_msg, previous_history, section)
                return history + [{"role": "assistant", "content": bot_response}]
        return history
    
    # Help chatbot A (Demographics)
    help_msg_a.submit(section_help_user_message, [help_msg_a, help_chatbot_a], [help_msg_a, help_chatbot_a], queue=False).then(
        lambda history: section_help_bot_message(history, "a"), help_chatbot_a, help_chatbot_a
    )
    
    # Help chatbot B (Treatment Experience)
    help_msg_b.submit(section_help_user_message, [help_msg_b, help_chatbot_b], [help_msg_b, help_chatbot_b], queue=False).then(
        lambda history: section_help_bot_message(history, "b"), help_chatbot_b, help_chatbot_b
    )
    
    # Help chatbot C (Feedback) - Always visible
    help_msg_c.submit(section_help_user_message, [help_msg_c, help_chatbot_c], [help_msg_c, help_chatbot_c], queue=False).then(
        lambda history: section_help_bot_message(history, "c"), help_chatbot_c, help_chatbot_c
    )
    
    # Section button handlers for custom form
    def switch_form_section(target_section):
        """Switch between form sections in the main form tab"""
        return (
            gr.update(visible=(target_section == "a")),  # section_a
            gr.update(visible=(target_section == "b")),  # section_b  
            gr.update(visible=(target_section == "c")),  # section_c
            gr.update(variant="primary" if target_section == "a" else "secondary"),  # section_nav_a
            gr.update(variant="primary" if target_section == "b" else "secondary"),  # section_nav_b
            gr.update(variant="primary" if target_section == "c" else "secondary"),  # section_nav_c
            target_section  # current_form_section state
        )
    
    def switch_combined_section(target_section):
        """Switch between form sections in the combined view"""
        return (
            gr.update(visible=(target_section == "a")),  # combined_demo_section
            gr.update(visible=(target_section == "b")),  # combined_treatment_section
            gr.update(visible=(target_section == "c")),  # combined_feedback_section
            gr.update(variant="primary" if target_section == "a" else "secondary"),  # combined_section_a
            gr.update(variant="primary" if target_section == "b" else "secondary"),  # combined_section_b
            gr.update(variant="primary" if target_section == "c" else "secondary"),  # combined_section_c
            target_section  # combined_current_section state
        )
    
    def toggle_help_chatbot(show_help):
        """Show or hide the help chatbot in combined view"""
        if show_help:
            return (
                gr.update(value="<div style='background-color: #f0f9ff; border: 1px solid #3b82f6; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; text-align: center;'><p style='margin: 0; color: #1e40af; font-weight: 500;'>🤖 AI Assistant Active</p></div>"),
                gr.update(visible=True),   # chatbot
                gr.update(visible=True),   # message input
                gr.update(visible=True),   # submit button
                gr.update(visible=False),  # need help button
                gr.update(visible=True)    # hide help button
            )
        else:
            return (
                gr.update(value="<div style='background-color: #f3f4f6; border: 1px solid #d1d5db; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; text-align: center;'><p style='margin: 0; color: #6b7280; font-style: italic;'>🤖 AI Assistant will appear when you need help</p></div>"),
                gr.update(visible=False),  # chatbot
                gr.update(visible=False),  # message input
                gr.update(visible=False),  # submit button
                gr.update(visible=True),   # need help button
                gr.update(visible=False)   # hide help button
            )
    
    def show_section_help(section):
        """Show help chatbot for specific form sections"""
        return (
            gr.update(visible=True),  # help_chatbot
            gr.update(visible=True)   # help_msg
        )
        
    def submit_form_data(*args):
        """Handle form submission"""
        return gr.update(
            value="""
            <div style="background-color: #d1fae5; border: 1px solid #22c55e; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                <p style="margin: 0; color: #166534; font-weight: 600;">✅ Form submitted successfully!</p>
                <p style="margin: 0.25rem 0 0 0; color: #166534; font-size: 0.9rem;">Thank you for your feedback.</p>
            </div>
            """,
            visible=True
        )

    # Event handlers for main form tab section navigation
    section_nav_a.click(
        lambda: switch_form_section("a"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    section_nav_b.click(
        lambda: switch_form_section("b"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    section_nav_c.click(
        lambda: switch_form_section("c"),
        outputs=[section_a, section_b, section_c, section_nav_a, section_nav_b, section_nav_c, current_form_section]
    )
    
    # Event handlers for combined view section navigation
    combined_section_a.click(
        lambda: switch_combined_section("a"),
        outputs=[combined_demo_section, combined_treatment_section, combined_feedback_section, 
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    combined_section_b.click(
        lambda: switch_combined_section("b"),
        outputs=[combined_demo_section, combined_treatment_section, combined_feedback_section,
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    combined_section_c.click(
        lambda: switch_combined_section("c"),
        outputs=[combined_demo_section, combined_treatment_section, combined_feedback_section,
                combined_section_a, combined_section_b, combined_section_c, combined_current_section]
    )
    
    # Help chatbot controls for individual sections
    show_help_a.click(
        lambda: show_section_help("a"),
        outputs=[help_chatbot_a, help_msg_a]
    )
    show_help_b.click(
        lambda: show_section_help("b"),
        outputs=[help_chatbot_b, help_msg_b]
    )
    
    # Combined view help controls
    need_help_btn.click(
        lambda: toggle_help_chatbot(True),
        outputs=[chatbot_status, combined_chatbot, combined_msg, combined_submit, need_help_btn, hide_help_btn]
    )
    hide_help_btn.click(
        lambda: toggle_help_chatbot(False),
        outputs=[chatbot_status, combined_chatbot, combined_msg, combined_submit, need_help_btn, hide_help_btn]
    )
    
    # Form submission
    submit_form.click(
        submit_form_data,
        inputs=[age, gender, diagnosis, treatment_date, treatment_satisfaction, side_effects, side_effects_severity, overall_feedback, improvements, recommend],
        outputs=[form_status]
    )
    
    # Form help button handlers
    def show_form_help(help_type):
        response = handle_form_help(help_type)
        return gr.update(value=response, visible=True)
    
    form_help_q1.click(
        lambda: show_form_help("treatment_satisfaction"),
        outputs=[form_help_response]
    )
    form_help_q2.click(
        lambda: show_form_help("side_effects"),
        outputs=[form_help_response]
    )
    form_help_q3.click(
        lambda: show_form_help("information_sharing"),
        outputs=[form_help_response]
    )
    
    # Example question button handlers (work with main chat tab)
    q1_btn.click(
        lambda history: handle_example_question(questions["q1"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q2_btn.click(
        lambda history: handle_example_question(questions["q2"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q3_btn.click(
        lambda history: handle_example_question(questions["q3"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q4_btn.click(
        lambda history: handle_example_question(questions["q4"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q5_btn.click(
        lambda history: handle_example_question(questions["q5"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q6_btn.click(
        lambda history: handle_example_question(questions["q6"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)
    
    q7_btn.click(
        lambda history: handle_example_question(questions["q7"], history),
        inputs=[chatbot],
        outputs=[msg, chatbot]
    ).then(bot_message, chatbot, chatbot)

if __name__ == "__main__":
    # For Hugging Face Spaces: do not set server_name, server_port, or share
    demo.launch(debug=True)