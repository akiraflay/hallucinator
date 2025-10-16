"""
Hallucinator - Legal Benchmark Generator & Evaluator
A Streamlit app for generating and evaluating legal multiple-choice questions using OpenRouter API
"""

import streamlit as st
import json
import os
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables - force reload and show status
load_dotenv(override=True)
print(f"[DEBUG] .env loaded. OPENROUTER_API_KEY present: {bool(os.getenv('OPENROUTER_API_KEY'))}")
if os.getenv('OPENROUTER_API_KEY'):
    key = os.getenv('OPENROUTER_API_KEY')
    print(f"[DEBUG] API key preview: {key[:10]}...{key[-4:]}")

# Configure page
st.set_page_config(
    page_title="Hallucinator",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Model mapping - Display names to OpenRouter API IDs
MODELS = {
    "Sonnet 4.5": "anthropic/claude-sonnet-4.5",
    "Opus 4.1": "anthropic/claude-opus-4.1",
    "Haiku 4.5": "anthropic/claude-haiku-4.5",
    "GPT 4.5 Thinking": "openai/gpt-4.5-thinking",
    "GPT 4.5": "openai/gpt-4.5",
    "GPT 4.1": "openai/gpt-4.1",
    "GPT 4o Mini": "openai/gpt-4o-mini",
    "Gemini 2.5 Pro": "google/gemini-2.5-pro",
    "Gemini 2.5 Flash": "google/gemini-2.5-flash"
}

# Legal topics
TOPICS = [
    "Criminal Procedure",
    "Evidence",
    "Professional Ethics",
    "Sentencing",
    "Bail & Pretrial",
    "Constitutional Criminal Law"
]

# File paths
QUESTIONS_FILE = "questions.json"
RESULTS_FILE = "eval_results.json"

# Custom CSS for dark mode aesthetics
def load_custom_css():
    st.markdown("""
        <style>
        /* Main app styling */
        .stApp {
            background-color: #0E1117;
        }

        /* Gradient buttons */
        .stButton>button {
            background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0, 217, 255, 0.2);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 217, 255, 0.4);
        }

        /* Question card styling */
        .question-card {
            background: linear-gradient(135deg, #1E2130 0%, #252838 100%);
            border-radius: 16px;
            padding: 2.5rem;
            margin: 2rem auto;
            max-width: 900px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(0, 217, 255, 0.15);
            border: 1px solid rgba(0, 217, 255, 0.2);
            position: relative;
        }

        /* Question metadata section */
        .question-metadata {
            display: flex;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }

        .metadata-badge {
            display: inline-block;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.3px;
        }

        .topic-badge {
            background: linear-gradient(90deg, rgba(0, 217, 255, 0.2) 0%, rgba(123, 47, 255, 0.2) 100%);
            border: 1px solid rgba(0, 217, 255, 0.4);
            color: #00D9FF;
        }

        .model-badge {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #AAAAAA;
        }

        /* Question text styling */
        .question-text {
            font-size: 1.15rem;
            font-weight: 500;
            line-height: 1.7;
            color: #FFFFFF;
            margin: 1.5rem 0 2rem 0;
            padding: 0 0.5rem;
        }

        .options-header {
            font-size: 0.85rem;
            font-weight: 600;
            color: #888;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Option boxes */
        .option-box {
            background: #1E2130;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 3px solid #00D9FF;
            transition: all 0.2s ease;
        }

        .option-box:hover {
            background: #252838;
            border-left-color: #7B2FFF;
        }

        .correct-answer {
            background: linear-gradient(90deg, rgba(0, 217, 100, 0.25) 0%, rgba(0, 217, 100, 0.15) 100%);
            border-left: 5px solid #00D964;
            font-weight: 600;
            box-shadow: 0 0 15px rgba(0, 217, 100, 0.3);
        }

        /* Progress bars */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
        }

        /* Status indicators */
        .status-success {
            background: linear-gradient(90deg, rgba(0, 217, 100, 0.2) 0%, rgba(0, 217, 100, 0.1) 100%);
            border-left: 4px solid #00D964;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .status-error {
            background: linear-gradient(90deg, rgba(255, 75, 75, 0.2) 0%, rgba(255, 75, 75, 0.1) 100%);
            border-left: 4px solid #FF4B4B;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .status-info {
            background: linear-gradient(90deg, rgba(0, 217, 255, 0.2) 0%, rgba(0, 217, 255, 0.1) 100%);
            border-left: 4px solid #00D9FF;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        /* Table styling */
        .dataframe {
            border-radius: 8px;
            overflow: hidden;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
            background-color: transparent;
            border-radius: 8px;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, rgba(0, 217, 255, 0.2) 0%, rgba(123, 47, 255, 0.2) 100%);
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: #00D9FF !important;
        }

        /* Headers */
        h1, h2, h3 {
            font-weight: 700;
        }

        /* Expander */
        .streamlit-expanderHeader {
            background: #1E2130;
            border-radius: 8px;
            font-weight: 600;
        }

        /* Selectbox and input styling */
        .stSelectbox > div > div {
            background-color: #1E2130;
            border-radius: 8px;
        }

        .stNumberInput > div > div {
            background-color: #1E2130;
            border-radius: 8px;
        }

        /* Checkbox styling */
        .stCheckbox {
            padding: 0.5rem;
            border-radius: 8px;
            transition: all 0.2s ease;
        }

        .stCheckbox:hover {
            background: rgba(0, 217, 255, 0.05);
        }

        /* JSON streaming container */
        .json-stream-box {
            background: #1E2130;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            overflow-x: auto;
            word-wrap: break-word;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            border: 1px solid rgba(0, 217, 255, 0.2);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .json-stream-box::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        .json-stream-box::-webkit-scrollbar-track {
            background: #0E1117;
            border-radius: 4px;
        }

        .json-stream-box::-webkit-scrollbar-thumb {
            background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
            border-radius: 4px;
        }

        .json-stream-box::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(90deg, #00D9FF 30%, #7B2FFF 70%);
        }

        /* Minimalist action buttons for question review */
        .review-button>button {
            background: rgba(255, 255, 255, 0.05) !important;
            color: #AAAAAA !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 0.6rem 1.5rem !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }

        .review-button>button:hover {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            transform: none !important;
            box-shadow: none !important;
        }

        /* Primary action (Approve) gets subtle green accent */
        .review-button-primary>button {
            background: rgba(0, 217, 100, 0.1) !important;
            border-color: rgba(0, 217, 100, 0.3) !important;
            color: #00D964 !important;
        }

        .review-button-primary>button:hover {
            background: rgba(0, 217, 100, 0.15) !important;
            border-color: rgba(0, 217, 100, 0.4) !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize OpenRouter client
@st.cache_resource
def get_openrouter_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error("⚠️ OPENROUTER_API_KEY not found in .env file")
        st.stop()

    # Debug: Show first/last 4 chars of API key (safe to display)
    masked_key = f"{api_key[:7]}...{api_key[-4:]}" if len(api_key) > 11 else "***"
    print(f"[DEBUG] Using API key: {masked_key}")

    # Create client with explicit Authorization header
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        default_headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Hallucinator - Legal Benchmark Generator",
        }
    )

    print(f"[DEBUG] Client created with base_url: {client.base_url}")
    print(f"[DEBUG] Default headers: {list(client.default_headers.keys())}")

    return client

# Data management functions
def load_questions():
    """Load questions from JSON file"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_question(question_data):
    """Save a new question to JSON file"""
    questions = load_questions()

    # Generate new ID
    new_id = max([q.get('id', 0) for q in questions], default=0) + 1
    question_data['id'] = new_id
    question_data['created_at'] = datetime.now().isoformat()

    questions.append(question_data)

    with open(QUESTIONS_FILE, 'w') as f:
        json.dump(questions, f, indent=2)

    return new_id

def load_results():
    """Load evaluation results from JSON file"""
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_results(results):
    """Save evaluation results to JSON file"""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)

# Question generation function with streaming
def generate_question_stream(client, topic, model):
    """Generate a legal question using OpenRouter API with streaming"""

    prompt = f"""Generate a legal multiple-choice question on the topic of {topic}.

Requirements:
- Create a moderately difficult to difficult question (no easy questions)
- Focus on federal law and broadly applicable legal principles relevant to public defenders
- Provide exactly 4 answer options labeled A, B, C, D
- Make the wrong answers adversarial - they should be plausible and require legal reasoning to rule out
- One answer must be clearly correct
- Include a detailed reasoning trace explaining why the correct answer is right and why the wrong answers are incorrect

Output format (valid JSON only):
{{
    "question": "The question text here",
    "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
    "correct_answer": "C",
    "reasoning": "Detailed explanation of why C is correct and why A, B, D are incorrect"
}}

Respond only with valid JSON, no additional text."""

    try:
        print(f"[DEBUG] Attempting API call with model: {MODELS[model]}")
        response = client.chat.completions.create(
            model=MODELS[model],
            messages=[
                {"role": "system", "content": "You are an expert in criminal law and legal education. Generate high-quality legal exam questions."},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.8
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        # Parse the final JSON
        try:
            # Strip markdown code fences if present
            json_text = re.sub(r'^```json\s*', '', full_response.strip())
            json_text = re.sub(r'\s*```$', '', json_text)

            print(f"[DEBUG] Attempting to parse JSON (length: {len(json_text)} chars)")
            question_data = json.loads(json_text)
            print(f"[DEBUG] JSON parsed successfully!")
            yield {"parsed": question_data}
        except json.JSONDecodeError as e:
            print(f"[DEBUG] JSON parsing failed: {str(e)}")
            print(f"[DEBUG] Raw response: {full_response[:200]}...")
            yield {"error": f"Failed to parse JSON: {str(e)}"}

    except Exception as e:
        error_msg = f"API Error: {str(e)}"
        print(f"[DEBUG] {error_msg}")
        print(f"[DEBUG] Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            print(f"[DEBUG] Response: {e.response}")
        yield {"error": error_msg}

# Evaluation function
def evaluate_question(client, question_data, model_name):
    """Evaluate a single question with a specific model"""

    options_text = "\n".join(question_data['options'])
    prompt = f"""Answer this multiple choice question. Respond with ONLY the letter (A, B, C, or D) of your answer, nothing else.

Question: {question_data['question']}

{options_text}

Your answer (A, B, C, or D only):"""

    try:
        response = client.chat.completions.create(
            model=MODELS[model_name],
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )

        answer = response.choices[0].message.content.strip().upper()

        # Extract just the letter
        for char in answer:
            if char in ['A', 'B', 'C', 'D']:
                selected = char
                break
        else:
            selected = answer[0] if answer else "?"

        is_correct = selected == question_data['correct_answer']

        return {
            "question_id": question_data['id'],
            "model": model_name,
            "selected": selected,
            "correct": is_correct,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "question_id": question_data['id'],
            "model": model_name,
            "selected": "ERROR",
            "correct": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

# Initialize session state
def init_session_state():
    if 'generated_questions' not in st.session_state:
        st.session_state.generated_questions = []
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = "idle"  # "idle" | "generating" | "reviewing" | "complete"
    if 'evaluating' not in st.session_state:
        st.session_state.evaluating = False

# Main app
def main():
    load_custom_css()
    init_session_state()

    # Get OpenRouter client
    client = get_openrouter_client()

    # Impressive header
    st.markdown("""
        <h1 style='text-align: center; background: linear-gradient(90deg, #00D9FF 0%, #7B2FFF 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem;
        font-weight: 800; margin-bottom: 0;'>
        🎭 Hallucinator
        </h1>
        <p style='text-align: center; color: #888; font-size: 1.2rem; margin-top: 0; margin-bottom: 2rem;'>
        Legal Benchmark Generator & Evaluator
        </p>
    """, unsafe_allow_html=True)

    # Create tabs
    tab1, tab2 = st.tabs(["✨ Generate Questions", "📊 Evaluate"])

    # ==================== TAB 1: GENERATE QUESTIONS ====================
    with tab1:
        st.markdown("### 🎯 Generate Legal Questions")

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            topic = st.selectbox("📚 Select Topic", TOPICS, key="gen_topic")

        with col2:
            model = st.selectbox("🤖 Select Model", list(MODELS.keys()), key="gen_model")

        with col3:
            quantity = st.number_input("📝 Quantity", min_value=1, max_value=20, value=5, key="gen_quantity")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚀 Generate Questions", use_container_width=True):
            st.session_state.generated_questions = []
            st.session_state.current_question_idx = 0
            st.session_state.workflow_state = "generating"

            # Generate questions
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(quantity):
                status_text.markdown(f"<div class='status-info'>🎯 Generating question {i+1} of {quantity}...</div>", unsafe_allow_html=True)

                # Streaming container
                stream_container = st.empty()

                full_text = ""
                question_data = None

                for chunk in generate_question_stream(client, topic, model):
                    if isinstance(chunk, dict):
                        if "parsed" in chunk:
                            question_data = chunk["parsed"]
                            question_data['topic'] = topic
                            question_data['generated_by'] = model
                        elif "error" in chunk:
                            # Show all errors to user
                            st.error(f"❌ {chunk['error']}")
                            break
                    else:
                        full_text += chunk
                        stream_container.markdown(f"<div class='json-stream-box'>{full_text}</div>", unsafe_allow_html=True)

                if question_data:
                    st.session_state.generated_questions.append(question_data)
                    print(f"[DEBUG] Appended question {i+1}, total questions now: {len(st.session_state.generated_questions)}")
                    # Show success message briefly
                    stream_container.markdown("<div class='status-success'>✅ Question generated successfully!</div>", unsafe_allow_html=True)
                    stream_container.empty()
                else:
                    print(f"[DEBUG] Question {i+1} failed to generate (question_data is None)")

                progress_bar.progress((i + 1) / quantity)

            # Clear generation UI elements
            status_text.empty()
            progress_bar.empty()

            # Transition to review mode with validation
            print(f"[DEBUG] Generation complete. Total questions generated: {len(st.session_state.generated_questions)}")
            print(f"[DEBUG] Session state generated_questions: {st.session_state.generated_questions}")

            if len(st.session_state.generated_questions) > 0:
                st.session_state.current_question_idx = 0
                st.session_state.workflow_state = "reviewing"
                print(f"[DEBUG] Transitioning to 'reviewing' state")
                st.rerun()
            else:
                st.error("❌ No questions were generated successfully. Please try again.")
                st.session_state.workflow_state = "idle"
                print(f"[DEBUG] No questions generated, staying in 'idle' state")

        # Display generated questions for review
        if st.session_state.workflow_state == "reviewing":
            # Defensive checks: ensure questions exist and index is valid
            print(f"[DEBUG] In reviewing state. Questions count: {len(st.session_state.generated_questions)}, Current idx: {st.session_state.current_question_idx}")
            if not st.session_state.generated_questions:
                print(f"[DEBUG] ERROR: In reviewing state but generated_questions is empty! Resetting to idle.")
                st.session_state.workflow_state = "idle"
                st.rerun()
            elif st.session_state.current_question_idx >= len(st.session_state.generated_questions):
                print(f"[DEBUG] Current index >= questions length, transitioning to complete")
                st.session_state.workflow_state = "complete"
                st.rerun()

            idx = st.session_state.current_question_idx
            q = st.session_state.generated_questions[idx]

            total = len(st.session_state.generated_questions)
            st.markdown(f"### Question {idx + 1} of {total}")
            st.progress((idx + 1) / total)

            # Question card
            st.markdown("<div class='question-card'>", unsafe_allow_html=True)

            st.markdown(f"**📝 {q.get('question', 'N/A')}**")
            st.markdown("<br>", unsafe_allow_html=True)

            # Display options
            for i, option in enumerate(q.get('options', [])):
                letter = option[0] if option else "?"
                is_correct = letter == q.get('correct_answer', '')

                if is_correct:
                    st.markdown(f"<div class='option-box correct-answer'><strong>✅ CORRECT ANSWER:</strong> {option}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='option-box'>{option}</div>", unsafe_allow_html=True)

            # Reasoning expander
            with st.expander("🧠 View Reasoning"):
                st.write(q.get('reasoning', 'No reasoning provided'))

            st.markdown("</div>", unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns([2, 1, 1, 3])

            with col1:
                st.markdown('<div class="review-button review-button-primary">', unsafe_allow_html=True)
                if st.button("Approve & Save", use_container_width=True, key="approve_btn"):
                    question_id = save_question(q)
                    st.success(f"🎉 Question saved with ID #{question_id}")
                    st.session_state.current_question_idx += 1
                    # Mark as complete if this was the last question
                    if st.session_state.current_question_idx >= len(st.session_state.generated_questions):
                        st.session_state.workflow_state = "complete"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="review-button">', unsafe_allow_html=True)
                if st.button("Skip", use_container_width=True, key="skip_btn"):
                    st.session_state.current_question_idx += 1
                    # Mark as complete if this was the last question
                    if st.session_state.current_question_idx >= len(st.session_state.generated_questions):
                        st.session_state.workflow_state = "complete"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            with col3:
                if idx > 0:
                    st.markdown('<div class="review-button">', unsafe_allow_html=True)
                    if st.button("Back", use_container_width=True, key="back_btn"):
                        st.session_state.current_question_idx -= 1
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        elif st.session_state.workflow_state == "complete":
            st.markdown("<div class='status-success'>✨ All questions reviewed!</div>", unsafe_allow_html=True)
            if st.button("🔄 Generate More"):
                st.session_state.generated_questions = []
                st.session_state.current_question_idx = 0
                st.session_state.workflow_state = "idle"
                st.rerun()

        else:
            st.markdown("<div class='status-info'>💡 Configure settings above and click 'Generate Questions' to begin</div>", unsafe_allow_html=True)

    # ==================== TAB 2: EVALUATE ====================
    with tab2:
        st.markdown("### 📊 Model Evaluation")

        # Load approved questions
        all_questions = load_questions()

        # Topic filter
        st.markdown("#### Filter Questions")
        selected_topic = st.selectbox("📚 Filter by Topic", ["All Topics"] + TOPICS, key="eval_topic")

        # Filter questions by topic
        if selected_topic != "All Topics":
            questions = [q for q in all_questions if q.get('topic') == selected_topic]
        else:
            questions = all_questions

        # Show question counts
        if selected_topic != "All Topics":
            st.markdown(f"<div class='status-info'>📚 {len(questions)} questions in '{selected_topic}' ({len(all_questions)} total)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='status-info'>📚 {len(questions)} questions ready for evaluation</div>", unsafe_allow_html=True)

        if len(questions) == 0:
            st.warning("⚠️ No approved questions yet. Generate and approve some questions first!")
        else:
            st.markdown("#### Select Models to Evaluate")

            # Model selection in columns
            cols = st.columns(3)
            selected_models = []

            for idx, (model_name, _) in enumerate(MODELS.items()):
                with cols[idx % 3]:
                    if st.checkbox(f"☑ {model_name}", key=f"eval_{model_name}"):
                        selected_models.append(model_name)

            st.markdown("<br>", unsafe_allow_html=True)

            if len(selected_models) == 0:
                st.warning("⚠️ Please select at least one model to evaluate")
            else:
                st.markdown(f"<div class='status-info'>🎯 {len(selected_models)} models selected</div>", unsafe_allow_html=True)

                if st.button("🚀 Run Evaluation", use_container_width=True):
                    # Run evaluation
                    progress_bar = st.progress(0)
                    status_container = st.empty()

                    all_results = load_results()

                    total_evaluations = len(questions) * len(selected_models)
                    current_eval = 0

                    for q_idx, question in enumerate(questions):
                        for m_idx, model_name in enumerate(selected_models):
                            current_eval += 1

                            status_container.markdown(
                                f"<div class='status-info'>🔍 Evaluating Question {q_idx + 1}/{len(questions)} "
                                f"with {model_name}... ({current_eval}/{total_evaluations})</div>",
                                unsafe_allow_html=True
                            )

                            result = evaluate_question(client, question, model_name)
                            all_results.append(result)

                            # Show result
                            emoji = "✅" if result['correct'] else "❌"
                            st.write(f"{emoji} {model_name} → Selected: {result['selected']}")

                            progress_bar.progress(current_eval / total_evaluations)

                    # Save results
                    save_results(all_results)

                    status_container.markdown("<div class='status-success'>✅ Evaluation complete!</div>", unsafe_allow_html=True)
                    status_container.empty()
                    progress_bar.empty()
                    st.rerun()

            # Display results
            st.markdown("---")
            st.markdown("### 🏆 Results")

            results = load_results()

            if len(results) > 0:
                # Calculate accuracy per model
                model_stats = {}

                for result in results:
                    model = result['model']
                    if model not in model_stats:
                        model_stats[model] = {'correct': 0, 'total': 0}

                    model_stats[model]['total'] += 1
                    if result['correct']:
                        model_stats[model]['correct'] += 1

                # Create results table
                results_data = []
                for model, stats in model_stats.items():
                    accuracy = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    results_data.append({
                        "Model": model,
                        "Correct": stats['correct'],
                        "Total": stats['total'],
                        "Accuracy": f"{accuracy:.1f}%"
                    })

                # Sort by accuracy
                results_data.sort(key=lambda x: float(x['Accuracy'].rstrip('%')), reverse=True)

                # Add rank medals
                for idx, row in enumerate(results_data):
                    if idx == 0:
                        row['Rank'] = "🥇"
                    elif idx == 1:
                        row['Rank'] = "🥈"
                    elif idx == 2:
                        row['Rank'] = "🥉"
                    else:
                        row['Rank'] = f"{idx + 1}"

                # Reorder columns
                results_data = [{k: row[k] for k in ['Rank', 'Model', 'Correct', 'Total', 'Accuracy']} for row in results_data]

                st.table(results_data)

                # Download button
                if st.button("📥 Download Results", use_container_width=True):
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(results, indent=2),
                        file_name=f"eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            else:
                st.markdown("<div class='status-info'>💡 No evaluation results yet. Run an evaluation to see results here.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
