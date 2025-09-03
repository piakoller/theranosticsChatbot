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
            system_prompt = """You are a compassionate and knowledgeable AI assistant specializing in patient education about theranostics, nuclear medicine, and cancer treatments. Your role is to help patients and their families understand complex medical concepts in simple, reassuring terms.

**Your Expertise Areas:**
- Theranostic treatments (diagnosis + therapy combined)
- Nuclear medicine procedures and imaging
- Radiopharmaceuticals and how they work
- Treatment processes and what to expect
- Side effects, safety, and preparation instructions
- Benefits and risks of different treatments

**Communication Guidelines:**
1. **Use simple, everyday language** - avoid complex medical jargon
2. **Be reassuring and empathetic** - acknowledge patient concerns and fears
3. **Explain step-by-step** - break down complex processes into easy steps
4. **Use analogies and comparisons** - relate to familiar concepts when helpful
5. **Focus on practical information** - what patients will experience, feel, or need to do
6. **Address common concerns** - safety, effectiveness, side effects, recovery
7. **Encourage questions** - remind patients to discuss with their medical team
8. **Be supportive** - offer hope while being realistic about treatments

**Target Audience:** Patients, families, and caregivers who want to understand their treatment options and what to expect.

**Important:** Always remind patients that this information is educational and they should discuss specific medical decisions with their healthcare team. Provide clear, caring explanations that help reduce anxiety and improve understanding."""

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


# Create the Gradio interface
with gr.Blocks(title="Theranostics Chatbot", theme=gr.themes.Soft()) as demo:
    # Custom CSS for ChatGPT-like look
    gr.HTML("""
    <style>
    body { background: #343541 !important; }
    #chatbot { background: #444654 !important; border-radius: 16px; }
    .message.user { background: #40414f !important; color: #fff !important; border-radius: 12px 12px 0 12px; margin: 8px 0; }
    .message.assistant { background: #343541 !important; color: #fff !important; border-radius: 12px 12px 12px 0; margin: 8px 0; }
    .gradio-container { max-width: 700px !important; margin: 0 auto !important; }
    .gr-button { border-radius: 50% !important; min-width: 40px !important; min-height: 40px !important; padding: 0 !important; }
    .gr-button svg { margin: 0 auto; }
    .gr-textbox { border-radius: 16px !important; }
    </style>
    """)
    # Header
    gr.Markdown("""
    <div style='text-align:center; color:#fff; font-size:2em; font-weight:bold; margin-top:10px;'>Theranostics Chatbot</div>
    <div style='text-align:center; color:#bdbdbd; font-size:1.1em; margin-bottom:10px;'>Your AI Assistant for Theranostics Research and Applications</div>
    <div style='text-align:center; color:#bdbdbd; font-size:1em; margin-bottom:20px;'>Welcome! This chatbot is here to help you understand theranostics and nuclear medicine treatments.<br>Ask questions about your treatment options, what to expect, or how these therapies work.<br><b>Always discuss your specific situation with your medical team.</b></div>
    """)

    # Example questions for patients
    with gr.Accordion("💡 Common Questions", open=False):
        with gr.Row():
            with gr.Column(scale=1):
                q1_btn = gr.Button("What is theranostics?", size="sm", variant="secondary")
                q2_btn = gr.Button("Is nuclear medicine safe?", size="sm", variant="secondary")
                q3_btn = gr.Button("What to expect during treatment", size="sm", variant="secondary")
            with gr.Column(scale=1):
                q4_btn = gr.Button("Side effects and recovery", size="sm", variant="secondary")
                q5_btn = gr.Button("How effective is this treatment?", size="sm", variant="secondary")
                q6_btn = gr.Button("How should I prepare?", size="sm", variant="secondary")
            with gr.Column(scale=1):
                q7_btn = gr.Button("Will I be radioactive?", size="sm", variant="secondary")

    # Show model status with improved styling
    if openrouter_available:
        gr.Markdown(f"🟢 **AI Model:** {current_model}")
    else:
        gr.Markdown("🟡 **Status:** Running in fallback mode (set OPENROUTER_API_KEY for full functionality)")

    # Enhanced chatbot interface
    chatbot = gr.Chatbot(
        value=[],
        elem_id="chatbot",
        height=500,
        show_copy_button=True,
        show_share_button=False,
        placeholder="Start a conversation about theranostics...",
        type="messages"  # Use OpenAI-style format instead of deprecated tuples
    )

    # Input area with improved styling
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Message Theranostics Chatbot...",
            container=False,
            scale=7,
            lines=1,
            show_label=False
        )
        submit_btn = gr.Button("", scale=1, variant="primary", size="sm", icon="🚀", elem_id="send-btn")
    
    with gr.Row():
        clear_btn = gr.Button("🗑️ Clear Chat", scale=1, variant="secondary")

    # Example question click handlers
    def set_question(question):
        return question
    
    # Function to handle example questions - directly adds to chat and gets response
    def handle_example_question(question, history):
        # Add the question directly to chat history without showing in input
        new_history = history + [{"role": "user", "content": question}]
        return "", new_history  # Empty string for input field, updated history for chat
    
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

    # Handle message submission
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

    # Event handlers
    msg.submit(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_message, chatbot, chatbot
    )
    submit_btn.click(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot_message, chatbot, chatbot
    )
    clear_btn.click(lambda: ([], ""), outputs=[chatbot, msg], queue=False)
    
    # Example question button handlers
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