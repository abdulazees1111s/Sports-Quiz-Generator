import streamlit as st
from src.generator import compile_quiz_data
from src.database import setup_and_populate_db
import json

# 1. Warm-up and initialize the vector DB with our offline facts on startup
@st.cache_resource
def prepare_knowledge_base():
    setup_and_populate_db()

prepare_knowledge_base()

# 2. Set Page configurations
st.set_page_config(page_title="AI-Powered Sports Quiz Generator", page_icon="https://cdn-icons-png.flaticon.com/128/5677/5677910.png", layout="centered")

st.title("AI-Powered Sports Quiz Generator")
st.write("Challenge yourself or generate engaging social media content!")

# 3. Sidebar inputs
st.sidebar.header("Quiz Settings")
sport_choice = st.sidebar.selectbox("Select Sport", ["Cricket", "Football", "Badminton"])
difficulty = st.sidebar.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])

# 4. Initialize session state to remember quizzes across page interactions
if "quiz_output" not in st.session_state:
    st.session_state.quiz_output = None
    st.session_state.quiz_context = None

# Button to trigger compilation pipeline
if st.sidebar.button("Generate Fresh Quiz", use_container_width=True):
    with st.spinner("Fetching historical facts & scouring the live web..."):
        try:
            quiz_text, context_used = compile_quiz_data(sport_choice, difficulty)
            st.session_state.quiz_output = quiz_text
            st.session_state.quiz_context = context_used
            st.success("Quiz created successfully!")
        except Exception as e:
            st.error(f"Failed to generate quiz: {e}")

# 5. Display the generated quiz
if st.session_state.quiz_output:
    try:
        quiz_data = json.loads(st.session_state.quiz_output)
        questions = quiz_data.get("quiz", [])
    except Exception as e:
        st.error(f"Error parsing quiz JSON: {e}")
        questions = []

    if questions:
        # 5a. Inject Custom CSS for Responsive Typography, Dynamic Themes, Spacing & Animations
        st.markdown("""
            <style>
            /* Typography scaling - forces large text across light/dark themes */
            .quiz-question-text {
                font-size: 1.5rem !important;
                font-weight: 700 !important;
                margin-bottom: 25px !important;
                color: var(--text-color, inherit);
            }
            
            /* Choice Rows styling and padding gaps */
            .choice-container {
                margin-bottom: 5px !important;
                padding: 4px 0px;
            }
            
            /* Smooth fade-in animation for questions */
            .fade-in-container {
                animation: fadeIn 0.5s ease-in-out;
            }
            @keyframes fadeIn {
                0% { opacity: 0; transform: translateY(8px); }
                100% { opacity: 1; transform: translateY(0); }
            }
            
            /* Expand animation for the explanation box */
            .animated-explanation {
                animation: slideDown 0.4s ease-out-forward;
                background-color: rgba(0, 102, 204, 0.1);
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #0066cc;
                font-size: 1.1rem !important;
                margin-top: 25px;
                color: var(--text-color, inherit);
            }
            @keyframes slideDown {
                0% { opacity: 0; max-height: 0px; transform: scaleY(0); transform-origin: top; }
                100% { opacity: 1; max-height: 600px; transform: scaleY(1); transform-origin: top; }
            }
            </style>
        """, unsafe_allow_html=True)

        # 5b. Initialize session state components
        if "current_q_index" not in st.session_state:
            st.session_state.current_q_index = 0
        if "selected_choice" not in st.session_state:
            st.session_state.selected_choice = None # No default choice selected!

        current_idx = st.session_state.current_q_index

        if current_idx >= len(questions):
            st.session_state.current_q_index = 0
            current_idx = 0

        q = questions[current_idx]
        correct_letter = q["correct_answer"].strip().upper()
        
        # 5c. Start Animation Wrapper
        st.markdown("<div class='fade-in-container'>", unsafe_allow_html=True)
        
        st.subheader(f"{sport_choice} ({difficulty})")
        st.progress((current_idx + 1) / len(questions), text=f"Question {current_idx + 1} of {len(questions)}")
        
        # Large sized question text
        st.markdown(f"<p class='quiz-question-text'>Q: {q['question']}</p>", unsafe_allow_html=True)

        options_map = {
            "A": q["option_a"],
            "B": q["option_b"],
            "C": q["option_c"],
            "D": q["option_d"]
        }

        # 5d. Dynamically render separate option rows with structural spacing gaps
        for key, text_val in options_map.items():
            st.markdown("<div class='choice-container'>", unsafe_allow_html=True)
            
            # Determine dynamic button coloring state based on submission
            if st.session_state.selected_choice is not None:
                if key == correct_letter:
                    # Highlight correct option in Green
                    button_label = f"{key}) {text_val} — (Correct Answer)"
                    st.success(button_label)
                elif key == st.session_state.selected_choice and key != correct_letter:
                    # Highlight selected wrong option in Red
                    button_label = f"{key}) {text_val} — (Your Selection)"
                    st.error(button_label)
                else:
                    # Standard locked options
                    st.button(f"{key}) {text_val}", key=f"opt_{current_idx}_{key}", disabled=True, use_container_width=True)
            else:
                # Active clickable buttons before selection (No default option chosen)
                if st.button(f"{key}) {text_val}", key=f"opt_{current_idx}_{key}", use_container_width=True):
                    st.session_state.selected_choice = key
                    st.rerun()
                    
            st.markdown("</div>", unsafe_allow_html=True)

        # 5e. Post-Selection evaluation block and transitions
        if st.session_state.selected_choice is not None:
            # Drop down explanation with CSS animations
            st.markdown(f"""
                <div class='animated-explanation'>
                    <strong>Ground Truth Explanation:</strong><br><br>
                    {q['explanation']}
                </div>
                <br>
            """, unsafe_allow_html=True)

            # Next Question Transition Router
            if current_idx < len(questions) - 1:
                if st.button("Next Question", use_container_width=True, type="primary"):
                    st.session_state.current_q_index += 1
                    st.session_state.selected_choice = None
                    st.rerun()
            else:
                st.balloons()
                if st.button("Quiz Completed! Restart?", use_container_width=True, type="primary"):
                    st.session_state.current_q_index = 0
                    st.session_state.selected_choice = None
                    st.session_state.quiz_output = None
                    st.rerun()
                    
        st.markdown("</div>", unsafe_allow_html=True) # End Animation Wrapper

    # Expandable audit window showcasing the "ground truth context"
    st.write("---")
    with st.expander("Inspect Ground Truth (RAG Context Used)"):
        st.code(st.session_state.quiz_context, language="markdown")