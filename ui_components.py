"""
UI Components Module
Handles Gradio interface components and layouts for the Theranostics Chatbot
"""

import gradio as gr
from chatbot import theranostics_bot
from form_handlers import form_handler
from logging_module import conversation_logger


class UIComponents:
    """Manages all UI components and layouts"""
    
    def __init__(self):
        self.questions = {
            "q1": "What are theranostics and how do they work in simple terms?",
            "q2": "Is nuclear medicine safe for patients? What are the risks?",
            "q3": "What should I expect during my theranostic treatment?",
            "q4": "What are the common side effects and how long does recovery take?",
            "q5": "How effective is theranostic treatment for my type of cancer?",
            "q6": "How should I prepare for my nuclear medicine treatment?",
            "q7": "Will I be radioactive after treatment? Is it safe for my family?"
        }
    
    def load_css(self):
        """Load CSS from external file"""
        try:
            with open("style.css", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("⚠️  style.css not found, using no custom CSS")
            return ""
    
    def create_header(self):
        """Create the main header section"""
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
    
    def create_example_questions(self):
        """Create the example questions accordion"""
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
        
        return [q1_btn, q2_btn, q3_btn, q4_btn, q5_btn, q6_btn, q7_btn]
    
    def create_model_status(self):
        """Create the model status display"""
        with gr.Row():
            with gr.Column():
                if theranostics_bot.is_api_available():
                    gr.HTML(f"""
                    <div class="status-indicator">
                        <span style="color: #059669; font-weight: 600;">🟢 AI Model Active:</span> 
                        <span style="color: #374151; font-family: monospace; font-size: 0.9rem;">{theranostics_bot.get_current_model().split('/')[-1]}</span>
                    </div>
                    """)
                else:
                    gr.HTML("""
                    <div class="status-indicator">
                        <span style="color: #d97706; font-weight: 600;">🟡 Fallback Mode:</span> 
                        <span style="color: #374151;">Limited functionality - API key required</span>
                    </div>
                    """)
    
    def create_chat_tab(self):
        """Create the main chat tab"""
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
            
            # Admin controls for conversation data
            with gr.Row():
                with gr.Column():
                    export_btn = gr.Button("📥 Export Conversations", variant="secondary", size="sm")
                    export_status = gr.Textbox(
                        label="Export Status",
                        placeholder="Click 'Export Conversations' to download logged conversations as CSV",
                        interactive=False,
                        lines=1
                    )
        
        return chatbot, msg, submit_btn, export_btn, export_status
    
    def create_form_tab(self):
        """Create the feedback form tab"""
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
                
                # Create form sections
                section_a, section_b, section_c, form_components = self._create_form_sections()
                
                # Form submission
                with gr.Row():
                    submit_form = gr.Button("📤 Submit Form", variant="primary", size="lg")
                    form_status = gr.HTML("""""", visible=False)
            
            # Help section for form assistance
            help_components = self._create_form_help_section()
        
        return (section_nav_a, section_nav_b, section_nav_c, current_form_section, 
                section_a, section_b, section_c, submit_form, form_status, 
                form_components, help_components)
    
    def _create_form_sections(self):
        """Create the individual form sections"""
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
        
        form_components = {
            'age': age, 'gender': gender, 'diagnosis': diagnosis,
            'treatment_date': treatment_date, 'treatment_satisfaction': treatment_satisfaction,
            'side_effects': side_effects, 'side_effects_severity': side_effects_severity,
            'overall_feedback': overall_feedback, 'improvements': improvements, 'recommend': recommend,
            'show_help_a': show_help_a, 'help_chatbot_a': help_chatbot_a, 'help_msg_a': help_msg_a,
            'show_help_b': show_help_b, 'help_chatbot_b': help_chatbot_b, 'help_msg_b': help_msg_b,
            'help_chatbot_c': help_chatbot_c, 'help_msg_c': help_msg_c
        }
        
        return section_a, section_b, section_c, form_components
    
    def _create_form_help_section(self):
        """Create the form help section"""
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
        
        return {
            'form_help_q1': form_help_q1,
            'form_help_q2': form_help_q2,
            'form_help_q3': form_help_q3,
            'form_help_response': form_help_response
        }
    
    def create_combined_tab(self):
        """Create the combined view tab"""
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
                    
                    # Create compact form sections
                    combined_sections = self._create_combined_form_sections()
                
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
        
        return (combined_section_a, combined_section_b, combined_section_c, combined_current_section,
                combined_sections, chatbot_status, combined_chatbot, combined_msg, combined_submit,
                need_help_btn, hide_help_btn)
    
    def _create_combined_form_sections(self):
        """Create compact form sections for combined view"""
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
        
        return {
            'combined_demo_section': combined_demo_section,
            'combined_treatment_section': combined_treatment_section,
            'combined_feedback_section': combined_feedback_section,
            'combined_age': combined_age,
            'combined_gender': combined_gender,
            'combined_diagnosis': combined_diagnosis,
            'combined_treatment_date': combined_treatment_date,
            'combined_satisfaction': combined_satisfaction,
            'combined_side_effects': combined_side_effects,
            'combined_overall_feedback': combined_overall_feedback,
            'combined_recommend': combined_recommend
        }
    
    # Message handling functions
    def user_message(self, message, history):
        """Handle user message submission"""
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history

    def bot_message(self, history):
        """Handle bot response generation"""
        if history and len(history) > 0:
            # Check if the last message is from user and needs a response
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                # Get previous messages for context (exclude the current user message)
                previous_history = history[:-1]
                bot_response = theranostics_bot.chatbot_response(user_msg, previous_history, context="main_chat")
                
                return history + [{"role": "assistant", "content": bot_response}]
        return history

    def combined_user_message(self, message, history):
        """Handle message submission for combined view"""
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history

    def combined_bot_message(self, history, section):
        """Handle bot response for combined view"""
        if history and len(history) > 0:
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                previous_history = history[:-1]
                bot_response = form_handler.form_contextual_response(user_msg, previous_history, section)
                return history + [{"role": "assistant", "content": bot_response}]
        return history

    def section_help_user_message(self, message, history):
        """Handle user message for section help"""
        if message.strip():
            return "", history + [{"role": "user", "content": message}]
        return message, history

    def section_help_bot_message(self, history, section):
        """Handle bot response for section help"""
        if history and len(history) > 0:
            last_message = history[-1]
            if last_message["role"] == "user":
                user_msg = last_message["content"]
                previous_history = history[:-1]
                bot_response = form_handler.form_contextual_response(user_msg, previous_history, section)
                return history + [{"role": "assistant", "content": bot_response}]
        return history

    def handle_example_question(self, question, history):
        """Handle example question clicks"""
        # Add the question directly to chat history without showing in input
        new_history = history + [{"role": "user", "content": question}]
        return "", new_history  # Empty string for input field, updated history for chat


# Global UI components instance
ui_components = UIComponents()