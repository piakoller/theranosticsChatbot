"""
Form Handlers Module
Handles form-specific logic, help functions, and contextual responses for the Theranostics Chatbot
Now with MongoDB integration for form submissions
"""

import gradio as gr
from datetime import datetime
from chatbot import theranostics_bot
from logging_module import conversation_logger


class FormHandler:
    """Handles form-related functionality and contextual help"""
    
    def __init__(self):
        self.section_help_content = {
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
        
        self.form_help_responses = {
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
    
    def form_contextual_response(self, message, history, section="none"):
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
        
        # Use form_help context for logging
        return theranostics_bot.chatbot_response(enhanced_message, history, context="form_help", section=section)
    
    def update_section_help(self, section):
        """Update section help display"""
        if section in self.section_help_content:
            content = self.section_help_content[section]
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
    
    def handle_form_help(self, question):
        """Handle form help questions"""
        return self.form_help_responses.get(question, "I can help explain any part of the feedback form. What specific question would you like help with?")
    
    def switch_form_section(self, target_section):
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
    
    def switch_combined_section(self, target_section):
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
    
    def toggle_help_chatbot(self, show_help):
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
    
    def show_section_help(self, section):
        """Show help chatbot for specific form sections"""
        return (
            gr.update(visible=True),  # help_chatbot
            gr.update(visible=True)   # help_msg
        )
        
    def submit_form_data(self, *args):
        """Handle form submission with MongoDB integration"""
        try:
            # Map form fields to data structure
            form_data = {}
            if len(args) >= 10:  # Ensure we have all expected form fields
                form_data = {
                    "age": args[0],
                    "gender": args[1], 
                    "diagnosis": args[2],
                    "treatment_date": args[3],
                    "treatment_satisfaction": args[4],
                    "side_effects": args[5] if args[5] else [],
                    "side_effects_severity": args[6],
                    "overall_feedback": args[7],
                    "improvements": args[8],
                    "recommend": args[9],
                    "completion_time": datetime.now().isoformat(),
                    "form_version": "v1.0"
                }
                
                # Save to MongoDB through the conversation logger
                result_message = conversation_logger.save_form_submission(form_data)
                
                # Create success message with database confirmation
                return gr.update(
                    value=f"""
                    <div style="background-color: #d1fae5; border: 1px solid #22c55e; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                        <p style="margin: 0; color: #166534; font-weight: 600;">✅ Form submitted successfully!</p>
                        <p style="margin: 0.25rem 0 0 0; color: #166534; font-size: 0.9rem;">Thank you for your feedback.</p>
                        <p style="margin: 0.5rem 0 0 0; color: #059669; font-size: 0.8rem;">{result_message}</p>
                    </div>
                    """,
                    visible=True
                )
            else:
                return gr.update(
                    value="""
                    <div style="background-color: #fef2f2; border: 1px solid #f87171; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                        <p style="margin: 0; color: #dc2626; font-weight: 600;">❌ Form submission error!</p>
                        <p style="margin: 0.25rem 0 0 0; color: #dc2626; font-size: 0.9rem;">Please fill out all required fields and try again.</p>
                    </div>
                    """,
                    visible=True
                )
                
        except Exception as e:
            print(f"❌ Error in form submission: {e}")
            return gr.update(
                value=f"""
                <div style="background-color: #fef2f2; border: 1px solid #f87171; border-radius: 0.5rem; padding: 1rem; text-align: center;">
                    <p style="margin: 0; color: #dc2626; font-weight: 600;">❌ Form submission error!</p>
                    <p style="margin: 0.25rem 0 0 0; color: #dc2626; font-size: 0.9rem;">Technical error: {str(e)}</p>
                </div>
                """,
                visible=True
            )
    
    def show_form_help(self, help_type):
        """Show form help response"""
        response = self.handle_form_help(help_type)
        return gr.update(value=response, visible=True)


# Global form handler instance
form_handler = FormHandler()