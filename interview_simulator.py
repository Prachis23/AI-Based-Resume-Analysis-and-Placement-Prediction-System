import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pydantic')
warnings.filterwarnings("ignore", category=UserWarning, module='sqlalchemy')

import os
os.environ["GEMINI_API_KEY"] = "AIzaSyD-B7F_NMwL4mKSyc0E-6ezJlF3rRIkj0o"
import time
import json
from datetime import datetime

# Third-party libraries
import streamlit as st
from pypdf import PdfReader
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Corrected import

# Real-time A/V and Audio Processing
from streamlit_webrtc import webrtc_streamer, WebRtcMode
import av # To handle audio/video frames

# --- 2.5. SPEECH-TO-TEXT FUNCTION ---
import speech_recognition as sr

# NOTE: For a real A/V setup, you would use:
# from streamlit_webrtc import webrtc_streamer, WebRtcMode
# from streamlit_audiorecorder import audiorecorder
# from vosk import Model, KaldiRecognizer # For local VAD/Transcription
# For this script, we SIMULATE these functions.

# Gemini API
from google import genai
from google.genai import types

# --- 0. PROFESSIONAL CSS STYLING (Light Theme with Blue Buttons) ---

def set_custom_styles():
    """Injects professional, modern CSS for a polished, light-colored, user-friendly look."""
    st.markdown("""
        <style>
        /* General Page Layout and Font (Light Theme) */
        .stApp {
            background-color: #ffffff; /* White background */
            color: #333333; /* Dark text */
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        /* Titles and Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #004A99; /* Dark Blue highlight for headers */
            font-weight: 600;
            border-bottom: 2px solid #EEEEEE;
            padding-bottom: 5px;
            margin-top: 20px;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #F8F8F8; /* Light gray sidebar */
            color: #333333;
            border-right: 1px solid #007BFF; /* Blue border */
        }

        /* Buttons - Primary (Action) - BLUE */
        .stButton button {
            background-color: #007BFF; /* Bright Blue primary button */
            color: white !important;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.2s;
        }
        .stButton button:hover {
            background-color: #0056b3; /* Darker blue on hover */
            transform: scale(1.02);
        }

        /* Input Fields (Light theme compatible) */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea, 
        .stSelectbox > div > div {
            background-color: #f9f9f9; /* Off-white input background */
            color: #333333;
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 10px;
        }
        
        /* Chat Messages (Lighter, user-friendly bubble style) */
        .stChatMessage [data-testid="stChatMessageContent"] {
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .stChatMessage [data-testid="stChatMessageContent"]:first-child {
            background-color: #E0E0E0; /* Interviewer background - Light Gray */
            color: #333333;
        }
        .stChatMessage [data-testid="stChatMessageContent"]:not(:first-child) {
            background-color: #BBDEFB; /* Student answer background - Light Blue */
            color: #333333;
            align-self: flex-end; 
        }

        /* Progress Bar Styling */
        .stProgress > div > div > div > div {
            background-color: #007BFF; /* Blue progress bar */
        }
        .stProgress > div > div > div {
            background-color: #E0E0E0;
        }

        </style>
        """, unsafe_allow_html=True)

# --- 1. CONFIGURATION AND INITIALIZATION ---

# Check for API Key
if "GEMINI_API_KEY" not in os.environ:
    st.error("FATAL ERROR: Please set the GEMINI_API_KEY environment variable.")
    st.stop()

# Initialize Gemini Client
try:
    client = genai.Client()
except Exception as e:
    st.error(f"Error initializing Gemini Client: {e}")
    st.stop()

# Set up Database (SQLite is embedded in the app folder)
ENGINE = create_engine('sqlite:///interviews.db')
Base = declarative_base() 

# Define the Interview Session Table
class InterviewSession(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    interview_type = Column(String)
    domain = Column(String)
    date = Column(DateTime, default=datetime.now)
    score = Column(Integer)
    feedback_summary = Column(Text)
    full_feedback = Column(Text)

# Create the database and table if they don't exist
Base.metadata.create_all(ENGINE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

# --- 2. RESUME PARSING FUNCTION ---

@st.cache_data
def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- 3. CORE PROMPT ENGINEERING AND SIMULATION ---

INTERVIEWER_SYSTEM_INSTRUCTION = """
You are a highly professional, polite, and dynamic AI Interviewer. Your goal is to conduct a structured, real-time interview.

CRITICAL RULES:
1. Speak only as the interviewer.
2. Generate only ONE question at a time.
3. Your tone must be formal and encouraging.
4. Dynamically mix generic (HR/Domain) and resume-specific questions.
5. Do NOT generate the full list of questions upfront. Generate the next question only when requested.
6. When asked for the NEXT question, ensure it follows the stated flow (HR/Domain -> Resume -> HR/Domain -> Resume...).
"""
# --- 3.5. HARDCODED QUESTION BANK new  ---

QUESTION_BANK = {
    # General HR Questions
    "HR": [
        "Tell me about yourself.",
          "Walk me through your resume.",
          "What are your strengths?",
          "What are your weaknesses?",
          "Why are you interested in this role?",
          "Why should we hire you?",
          "Where do you see yourself in 5 years?",
          "Describe a challenging situation you faced and how you handled it.",
          "Tell me about a failure and what you learned from it.",
          "How do you handle stress and pressure?",
          "Describe a time you worked in a team and your role in it.",
          "Give an example of a conflict you faced at work and how you resolved it.",
          "What motivates you to perform well?",
          "How do you prioritize tasks when you have multiple deadlines?",
          "Tell me about a time you showed leadership skills.",
          "How do you handle constructive criticism?",
          "What is your expected salary?",
          "Why do you want to leave your current job?",
          "What do you know about our company?",
          "Do you have any questions for us?",


    ],
    
    # Domain-Specific Questions (General Technical)
    "Python Development": [
        "Explain the difference between a list and a tuple in Python.",
        "How does Python manage memory?",
        "Describe the purpose of decorators in Python.",
        "Explain the concept of GIL (Global Interpreter Lock).",
    ],
    "Data Science": [
        "Explain the difference between supervised and unsupervised learning.",
        "What is overfitting, and how do you prevent it?",
        "Describe a method for handling missing data.",
        "What are the assumptions of linear regression?",
    ],
    "Cloud Engineering (AWS/Azure)": [
        "What is the difference between IaaS, PaaS, and SaaS?",
        "Explain the concept of serverless computing.",
        "How do you ensure high availability in a cloud deployment?",
        "What are Security Groups/Network Security Groups (NSGs)?",
    ],
    "Frontend Web Development": [
        "Explain the concept of event bubbling and capturing in JavaScript.",
        "What is the difference between var, let, and const?",
        "How does the browser render a webpage after receiving HTML/CSS?",
        "Describe the purpose of a virtual DOM in React/Vue.",
    ],
    "General Software Engineering": [
        "Explain object-oriented programming (OOP) principles.",
        "What are the benefits of using version control (Git)?",
        "Describe the stages of the Software Development Life Cycle (SDLC).",
        "Explain polymorphism with a real-world example.",
    ],
}






# JSON Schema for the Detailed Feedback Report (Enhanced to match new requirements)
FEEDBACK_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    properties={
        "performance_score": types.Schema(type=types.Type.INTEGER, description="Overall score out of 100."),
        "star_rating": types.Schema(type=types.Type.INTEGER, description="Visual feedback score from 1 to 5 stars."),
        "summary": types.Schema(type=types.Type.STRING, description="A 1-2 line summary of the performance."),
        "strengths": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="List of strong points."),
        "areas_of_improvement": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="List of weak areas such as hesitation, filler words, or unclear answers."),
        "confidence_communication_tips": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="Suggestions for maintaining tone, body language, and positive attitude."),
        "technical_recommendations": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="Resources or topics to improve specific skill gaps (if applicable)."),
        "numeric_breakdown": types.Schema(
            type=types.Type.OBJECT,
            properties={
                "content_correctness": types.Schema(type=types.Type.INTEGER, description="Score out of 10 for the accuracy and relevance of answers."),
                "language_fluency": types.Schema(type=types.Type.INTEGER, description="Score out of 10 for grammar, pronunciation, and coherence."),
                "confidence_tone": types.Schema(type=types.Type.INTEGER, description="Score out of 10 for pitch, tone, and steady voice."),
                "body_language": types.Schema(type=types.Type.INTEGER, description="Score out of 10 for simulated eye contact and facial expressions (if A/V used)."),
                "structure_conciseness": types.Schema(type=types.Type.INTEGER, description="Score out of 10 for the organization and length of the response."),
            }
        ),
        "action_plan": types.Schema(
            type=types.Type.OBJECT,
            properties={
                "30_days": types.Schema(type=types.Type.STRING, description="Specific goal for the next 30 days."),
                "60_days": types.Schema(type=types.Type.STRING, description="Specific goal for the next 60 days."),
                "90_days": types.Schema(type=types.Type.STRING, description="Specific goal for the next 90 days."),
            }
        ),
    },
    required=[
        "performance_score", "star_rating", "summary", "strengths",
        "areas_of_improvement", "confidence_communication_tips",
        "numeric_breakdown", "action_plan"
    ]
)

# --- 4. STREAMLIT APP LOGIC ---

st.set_page_config(
    page_title="AI-Driven Interview Simulator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Variables
if 'stage' not in st.session_state:
    st.session_state.stage = 'setup'  # setup, interview, feedback
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'gemini_chat' not in st.session_state:
    st.session_state.gemini_chat = None
if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'interview_log' not in st.session_state:
    st.session_state.interview_log = "" # Full log for final feedback analysis
if 'next_question_type' not in st.session_state:
    st.session_state.next_question_type = 'initial' # initial, hr/domain, resume

# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---
# --- 4.1. SETUP STAGE ---

# --- 4.1. SETUP STAGE ---

def setup_form():
    """Form to collect user data and settings."""
    st.header("👤 Interview Setup")
    st.markdown("An innovative feature designed to help students practice and improve their interview skills through real-time AI-based simulations.")
    
    # Use a single form to ensure all fields are captured when the button is pressed
    with st.form("setup_form"):
        # 1. Name Input
        name = st.text_input("Your Name", placeholder="e.g., Alex Johnson", value=st.session_state.get('name', ''))
        
        # 2. Interview Type
        # Using selectbox to reduce re-run complexity
        interview_type = st.selectbox(
            "Select Interview Type",
            ('Technical Interview', 'HR Interview'),
            key='interview_type_selectbox'
        )

        domain = ""
        # 3. Interest Domain Selector (Conditional)
        if interview_type == 'Technical Interview':
            domain = st.selectbox(
                "Select Interest Domain",
                ['Python Development', 'Data Science', 'Cloud Engineering (AWS/Azure)', 'Frontend Web Development', 'General Software Engineering'],
                key='domain_selectbox'
            )
        
        st.subheader("Document Upload")
        uploaded_resume = st.file_uploader("Upload Resume (PDF only)", type=["pdf"])
        
        # Mandatory camera/mic reminder
        st.info("💡 **Mandatory A/V Recording:** The system will record your entire session (video and audio) securely for detailed analysis. Please ensure your camera and microphone are ready.")
        
        # 4. Start Button - CRITICAL FIX: REMOVE 'disabled' ARGUMENT
        # The button will now always be visible and clickable.
        start_button = st.form_submit_button(
            "🚀 Start Interview", 
            type="primary"
        )

    # --- EXECUTION LOGIC (MUST BE OUTSIDE THE 'with st.form' block) ---
    if start_button:
        # Check for both missing fields explicitly here
        if not name:
             st.error("❌ Please fill in your name to start.")
             return
        if uploaded_resume is None:
             st.error("❌ Please upload your resume (PDF only) to start.")
             return

        # 1. Parse Resume
        resume_text = extract_text_from_pdf(uploaded_resume)
        if not resume_text:
            st.error("❌ Could not extract text from resume. Please try a different PDF.")
            return

        # 2. Store Setup Data in Session State
        st.session_state.name = name
        st.session_state.resume_text = resume_text
        st.session_state.interview_type = interview_type
        st.session_state.domain = domain if interview_type == 'Technical Interview' else 'N/A'
        st.session_state.next_question_type = 'hr/domain' 
        
        # 3. Initialize Chat Session
        question_flow_type = 'HR' if st.session_state.interview_type == 'HR Interview' else f'Technical questions in the {st.session_state.domain} domain'
        
        context_prompt = f"""
        USER PROFILE:
        Name: {name}
        Interview Type: {interview_type}
        Domain (if technical): {st.session_state.domain}
        RESUME CONTENT:
        {resume_text}

        INTERVIEW FLOW LOGIC:
        - The first 1-2 questions must be {question_flow_type} based.
        - The next 1-2 questions must be SPECIFICALLY based on the RESUME content.
        - Continue strictly alternating between {question_flow_type} and RESUME-based questions until the interview is stopped.
        - IMPORTANT: For {question_flow_type} questions, focus on conceptual, problem-solving, or scenario-based questions.
        - IMPORTANT: For RESUME questions, focus on projects, internships, and technical skills listed in the resume.
        """
        
        # st.session_state.gemini_chat = client.chats.create(
        #     model="gemini-2.5-flash",
        #     config=types.GenerateContentConfig(
        #         system_instruction=INTERVIEWER_SYSTEM_INSTRUCTION + "\n\n" + context_prompt,
        #     )
        # )
        # 3. Use one-off API call to extract and store Keywords
        resume_keywords = extract_resume_keywords(resume_text)
        st.session_state.keywords = resume_keywords
        
        # 4. Initialize a dummy chat state (no live connection needed for questions)
        st.session_state.gemini_chat = "READY" # Use a string flag instead of a live object
        # 4. Move to Interview Stage
        st.session_state.stage = 'interview'
        st.rerun()
# --- 4.2. INTERVIEW STAGE ---

# --- 4.2. INTERVIEW STAGE (LOCAL QUESTION GENERATION) ---

# --- 4.2. INTERVIEW STAGE (LOCAL QUESTION GENERATION) ---

def get_next_question():
    """Generates the next interview question using a local bank and resume keywords."""
    
    # 1. Determine the category type (HR/Domain vs. Resume)
    current_flow_type = st.session_state.next_question_type
    interview_type = st.session_state.interview_type
    domain = st.session_state.domain
    
    question = ""
    
    # --- Logic to Select the Question ---
    if current_flow_type == 'hr/domain' or current_flow_type == 'initial':
        # Select an HR or Domain-Specific question
        
        # Decide the source key: 'HR' for HR Interview, else the selected domain
        source_key = 'HR' if interview_type == 'HR Interview' or current_flow_type == 'initial' else domain
        
        # Ensure the domain key exists, falling back to HR if needed
        if source_key not in QUESTION_BANK:
             source_key = 'HR'
             
        q_list = QUESTION_BANK.get(source_key, QUESTION_BANK['HR'])
            
        # Use (q_count) and modulus to rotate through the list safely
        q_index = st.session_state.question_count % len(q_list)
        question = q_list[q_index]
            
        # Switch to resume-based next
        st.session_state.next_question_type = 'resume'
            
    else: # 'resume' flow
        # Generate a question based on extracted keywords (Skills or Projects)
        
        keywords = st.session_state.keywords # Contains {"skills": [...], "projects": [...]}
        q_count = st.session_state.question_count
        
        if q_count % 2 == 0 and keywords['projects']:
            # Project-based question (uses rotation on projects)
            project_index = (q_count // 2) % len(keywords['projects'])
            project_name = keywords['projects'][project_index]
            question = f"In your resume, you mention working on **{project_name}**. Could you describe the biggest challenge you faced during its development and how you solved it?"
        
        elif keywords['skills']:
            # Skill-based question (uses rotation on skills)
            skill_index = (q_count // 2) % len(keywords['skills'])
            skill = keywords['skills'][skill_index]
            question = f"I see you listed **{skill}** as a key skill. Can you elaborate on your experience with it, perhaps by walking me through a time you applied it effectively?"
        
        else:
            # Fallback if no keywords were found/extracted
            question = "That concludes our discussion on your projects. Let's return to some general behavioral questions."
            
        # Switch to hr/domain-based next
        st.session_state.next_question_type = 'hr/domain'

    # 2. Update session state (This part remains the same)
    st.session_state.chat_history.append({"role": "interviewer", "content": question})
    st.session_state.question_count += 1
    st.session_state.interview_log += f"\n--- Q{st.session_state.question_count} ({current_flow_type.upper()}): {question}\n"
    st.toast(f"Question {st.session_state.question_count} asked! Type: {current_flow_type.upper()}")
        # except Exception as e:
        #     # Catch the specific 'client has been closed' error here.
        #     # If the error is persistent, the chat object might be corrupted.
        #     st.error(f"Error generating question: {e}. Attempting to restart chat session (if possible).")
        #     # If it fails here, the user likely needs to restart the interview from the setup stage.
        #     # You might choose to set st.session_state.stage = 'setup' here for safety.
def handle_answer_submission(answer):
    """Processes the user's answer and logs it."""
    if not answer.strip():
        st.error("Please provide an answer before clicking next.")
        return

    # 1. Log the answer
    st.session_state.chat_history.append({"role": "student", "content": answer})
    st.session_state.interview_log += f"A{st.session_state.question_count}: {answer}\n"
    st.session_state.last_response_text = answer # Keep the text for the next re-run if needed
    
    # 2. Clear the answer input for the next question (handled by form clear_on_submit)
    
    # 3. This function does NOT call get_next_question() directly;
    # it lets the Streamlit rerun logic handle the 30-second timer/next button click.

# --- 2.5. SPEECH-TO-TEXT FUNCTION ---
import speech_recognition as sr

def record_and_transcribe():
    """Listens to the microphone and transcribes the speech to text."""
    r = sr.Recognizer()
    
    # # Use the default microphone
    # with sr.Microphone() as source:
    #     st.info("👂 System is actively listening... Please start speaking now.")
    #     r.adjust_for_ambient_noise(source, duration=0.5) # Adjust for noise
        
    #     try:
    #         # Listen for up to 30 seconds
    #         audio = r.listen(source, timeout=30, phrase_time_limit=30)
    #     except sr.WaitTimeoutError:
    #         st.warning("⚠️ Microphone timed out. No speech detected.")
    #         return "[No verbal response detected]"
    # Use the default microphone
    with sr.Microphone() as source:
        # Note: Added print for debugging in terminal
        print("Microphone active. Listening for 30 seconds...")
        st.info("👂 System is actively listening... Please start speaking now.")
        r.adjust_for_ambient_noise(source, duration=0.5) 
        
        try:
            audio = r.listen(source, timeout=30, phrase_time_limit=30)
        except sr.WaitTimeoutError:
            st.warning("⚠️ Microphone timed out. No speech detected.")
            return "[No verbal response detected]"

    st.info("🧠 Transcribing your answer...")
    
    try:
        # Use Google's Web Speech API for transcription (Requires internet)
        text = r.recognize_google(audio)
        return text
    
    except sr.UnknownValueError:
        st.error("❌ Google Speech Recognition could not understand audio.")
        return "[Audio not understood]"
    except sr.RequestError as e:
        st.error(f"❌ Could not request results from Google Speech Recognition service; {e}")
        return "[API Request Failed]"
    


def interview_session():
    """Main interview display and interaction loop, using side-by-side columns."""
    st.header(f"🎙️ Interview Session: {st.session_state.interview_type}")
    st.caption(f"Domain: {st.session_state.domain or 'N/A'} | Candidate: **{st.session_state.name}** | Q Type: **{st.session_state.next_question_type.upper()}**")
    
    # --- THIS IS THE SINGLE CHANGE: Combining A/V and Response into one row ---
    col_av_feed, col_response_controls = st.columns([1, 1]) 
    
    # --- LEFT COLUMN: LIVE A/V FEED AND STOP BUTTON (from your old col_video/col_stop) ---
    with col_av_feed:
        st.subheader("Live A/V Feed (Mandatory Recording)")
        
        # Initialize or reuse the WebRTC context (Assuming necessary imports are present)
        webrtc_ctx = st.session_state.get('webrtc_ctx')
        
        try:
             # This is the streamlined way to use the WebRTC component
             webrtc_ctx = webrtc_streamer(
                key="interview_stream",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                media_stream_constraints={"video": True, "audio": True},
            )
             st.session_state.webrtc_ctx = webrtc_ctx
        except NameError:
             # This should only happen if imports are missing
             st.error("WebRTC component error. Ensure all dependencies are installed.")
        
        if webrtc_ctx and not webrtc_ctx.state.playing:
            st.warning("Click 'Start' above to enable your camera and microphone.")

        # Stop Interview Button placed below the camera feed
        # st.markdown("---")
        # if st.button("🛑 Stop Interview and Get Feedback", type="primary", use_container_width=True):
        #     st.session_state.stage = 'feedback'
        #     if webrtc_ctx:
        #          webrtc_ctx.state.playing = False 
        #     st.rerun()
        # Stop Interview Button placed below the camera feed
        st.markdown("---")
        if st.button("🛑 Stop Interview and Get Feedback", type="primary", use_container_width=True):
            # 1. Update the stage immediately
            st.session_state.stage = 'feedback'
            
            # 2. DO NOT MANUALLY SET webrtc_ctx.state.playing = False
            #    The stream will be terminated naturally when Streamlit reruns
            #    and the component is no longer drawn (because stage != 'interview').
            
            # 3. Force the page transition
            st.rerun()

    # --- RIGHT COLUMN: YOUR RESPONSE CONTROLS (Your old 'Single-Click Interaction' section) ---
    with col_response_controls:
        st.subheader("Your Response (Speak Now)")

        # Initialize transcription storage in session state
        if 'current_transcription' not in st.session_state:
            st.session_state.current_transcription = ""

        # Use a form to capture the transcription/text and submission
        with st.form("stt_submission_form", clear_on_submit=False):
            
            # 1. The Record Button
            record_button = st.form_submit_button("🎙️ Record Answer", type="secondary")
            
            # 2. Display the Transcribed Text (The user can edit this after recording)
            st.session_state.current_transcription = st.text_area(
                "Transcribed Text (Edit if needed, or click 'Record Answer' to speak again):",
                value=st.session_state.current_transcription,
                height=150,
                key='answer_text_area' # Use a key for reliable state tracking
            )
            
            # 3. Submission Button
            submit_button = st.form_submit_button("✅ Submit Answer & Next Question", type="primary")

            
            # VVVV EXECUTION LOGIC INSIDE THE FORM CONTEXT VVVV

            # A. Logic after clicking the RECORD button
            if record_button:
                transcribed_text = record_and_transcribe()
                st.session_state.current_transcription = transcribed_text
                st.rerun()

            # B. Logic after clicking the SUBMIT button
            if submit_button:
                answer = st.session_state.current_transcription

                if not answer or answer.strip() in ["[No verbal response detected]", "[Audio not understood]", "[API Request Failed]", ""]:
                    st.error("Please provide a valid spoken or typed answer to proceed.")
                else:
                    # Removed st.write("Processing your answer...") for cleaner UI
                    handle_answer_submission(answer)
                    
                    st.session_state.current_transcription = ""
                    get_next_question()
                    st.rerun()
                    
    st.markdown("---") # Separator after the controls
    
    # --- Chat Display Area (Below the Controls) ---
    chat_container = st.container(height=450, border=True)

    with chat_container:
        # Initial greeting and first question logic
        if st.session_state.question_count == 0:
            st.session_state.chat_history.append({"role": "interviewer", "content": f"Hello {st.session_state.name}, welcome. Please ensure your camera and microphone are on. We will begin the interview now."})
            st.chat_message("assistant").write(st.session_state.chat_history[0]['content'])
            get_next_question() # Get the very first question
            st.rerun() # Re-run to display the question
            
        # Display the chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            
            if role == "interviewer":
                q_num = st.session_state.chat_history.index(message) // 2 + 1 
                st.chat_message("assistant").markdown(f"**Q{q_num}:** {content}")
            elif role == "student":
                st.chat_message("user").write(content)

# --- 2.6. KEYWORD EXTRACTION FUNCTION new ---

def extract_resume_keywords(resume_text):
    """Uses Gemini to extract key technical skills and project names from the resume."""
    prompt = f"""
    Analyze the following resume and extract the TOP 5 most relevant technical skills (e.g., Python, AWS, React) and the name of the TOP 2 projects/experiences.
    Return the result as a simple JSON object: {{"skills": ["skill1", "skill2"], "projects": ["project1", "project2"]}}
    
    RESUME TEXT:
    {resume_text}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "skills": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                        "projects": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING)),
                    }
                )
            )
        )
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Error extracting keywords from resume: {e}")
        return {"skills": ["Python", "SQL"], "projects": ["Portfolio Project", "Internship"]} # Fallback data
# --- 4.3. FEEDBACK STAGE ---

def feedback_session():
    """Analyzes the full interview log and displays a detailed report."""
    st.header("✨ Interview Feedback & Analysis")
    
    if st.session_state.interview_log.strip() == "":
        st.warning("No questions were asked. Please complete at least one round of Q&A.")
        if st.button("Go back to Setup"):
            st.session_state.stage = 'setup'
            # Reset only the interview-specific state, not history
            st.session_state.question_count = 0
            st.session_state.interview_log = ""
            st.session_state.gemini_chat = None
            st.rerun()
        return
        
    st.markdown("Click the button below to generate your comprehensive feedback report.")
    
    # Button to trigger analysis
    if st.button("📊 Analyze Feedback", type="primary"):
        # Full Prompt for the Final Report
        feedback_prompt = f"""
        Analyze the full interview transcript provided below. Critically evaluate the user's responses based on the simulated video/audio factors (Pitch, Tone, Confidence, Body Language, Fluency, etc.) derived from the text provided, as if the text was a live transcript.

        Your analysis must strictly follow the required JSON schema.

        FULL INTERVIEW TRANSCRIPT:
        {st.session_state.interview_log}

        REMINDER: STRICTLY generate ONLY the JSON object.
        """

        # Call Gemini for analysis
        with st.spinner("🧠 AI is analyzing your secure recording and performance..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash", # Use Pro model for better reasoning and JSON structure adherence
                    contents=feedback_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=FEEDBACK_SCHEMA
                    )
                )
                # Parse the JSON response
                feedback_data = json.loads(response.text)
                st.session_state.feedback_data = feedback_data # Store for display
                
                # Save to Database
                db_session = SessionLocal()
                new_session = InterviewSession(
                    name=st.session_state.name,
                    interview_type=st.session_state.interview_type,
                    domain=st.session_state.domain,
                    score=feedback_data.get('performance_score', 0),
                    feedback_summary=feedback_data.get('summary', 'Analysis complete.'),
                    full_feedback=response.text # Save the raw JSON for full record
                )
                db_session.add(new_session)
                db_session.commit()
                db_session.close()

            except Exception as e:
                st.error(f"Error during feedback analysis (Gemini API or JSON parsing): {e}")
                st.session_state.feedback_data = None
                return
    
    # --- Display the Feedback Report (using the parsed JSON data) ---
    if 'feedback_data' in st.session_state and st.session_state.feedback_data is not None:
        feedback_data = st.session_state.feedback_data

        # 1. Scorecard and Summary
        score = feedback_data.get('performance_score', 0)
        stars = "⭐" * feedback_data.get('star_rating', 0)
        
        st.markdown(f"""
        ## Performance Score: **<span style='font-size: 36px; color:#007BFF;'>{score}/100</span>**
        **Star Rating:** {stars}
        > <p style="font-style: italic; font-size: 18px; color: #666666;">"{feedback_data.get('summary')}"</p>
        """, unsafe_allow_html=True)
        
        st.markdown("---")

        # 2. Detailed Breakdown (Strengths & Improvements)
        col_str, col_imp = st.columns(2)
        with col_str:
            st.subheader("👍 Strengths")
            st.success("\n".join(f"* {s}" for s in feedback_data.get('strengths', ['N/A'])))
        
        with col_imp:
            st.subheader("👎 Areas of Improvement")
            st.warning("\n".join(f"* {a}" for a in feedback_data.get('areas_of_improvement', ['N/A'])))

        st.markdown("---")

        # 3. Tips and Technical Recommendations
        col_comm, col_tech = st.columns(2)
        with col_comm:
            st.subheader("🗣️ Confidence & Communication Tips")
            st.info("\n".join(f"* {t}" for t in feedback_data.get('confidence_communication_tips', ['N/A'])))

        with col_tech:
            st.subheader("💻 Technical Recommendations")
            if feedback_data.get('technical_recommendations'):
                st.info("\n".join(f"* {r}" for r in feedback_data.get('technical_recommendations', ['N/A'])))
            else:
                st.markdown("*(Not applicable or no specific technical gaps found)*")

        st.markdown("---")

        # 4. Numeric Breakdown (Visual)
        st.subheader("📊 Numeric Breakdown (Out of 10)")
        breakdown = feedback_data.get('numeric_breakdown', {})
        
        st.progress(breakdown.get('content_correctness', 0) / 10, text="Content & Correctness")
        st.progress(breakdown.get('language_fluency', 0) / 10, text="Language & Fluency")
        st.progress(breakdown.get('confidence_tone', 0) / 10, text="Confidence & Tone")
        st.progress(breakdown.get('body_language', 0) / 10, text="Body Language (Simulated)")
        st.progress(breakdown.get('structure_conciseness', 0) / 10, text="Structure & Conciseness")


        st.markdown("---")

        # 5. Improvement Path
        st.subheader("🚀 Improvement Action Plan (Step-by-Step Guidance)")
        action_plan = feedback_data.get('action_plan', {})
        
        col_30, col_60, col_90 = st.columns(3)
        col_30.metric("30 Days Goal", action_plan.get('30_days', 'N/A'))
        col_60.metric("60 Days Goal", action_plan.get('60_days', 'N/A'))
        col_90.metric("90 Days Goal", action_plan.get('90_days', 'N/A'))

        st.markdown("---")
        
        # New Interview Button (resets only the stage, keeps history)
        if st.button("Start New Interview Session", use_container_width=True):
            # Reset everything for a new session except user info
            st.session_state.stage = 'setup'
            st.session_state.chat_history = []
            st.session_state.gemini_chat = None
            st.session_state.question_count = 0
            st.session_state.interview_log = ""
            if 'feedback_data' in st.session_state:
                del st.session_state['feedback_data']
            st.rerun()

# --- 4.4. NAVIGATION (SIDEBAR) ---

def show_history():
    """Displays a list of all past interview sessions from the database."""
    st.sidebar.subheader("Past Interview History")
    db_session = SessionLocal()
    sessions = db_session.query(InterviewSession).order_by(InterviewSession.date.desc()).all()
    db_session.close()

    if sessions:
        for s in sessions:
            with st.sidebar.expander(f"**{s.date.strftime('%Y-%m-%d')}** - {s.score}/100"):
                st.write(f"**Name:** {s.name}")
                st.write(f"**Type:** {s.interview_type} ({s.domain or 'N/A'})")
                st.write(f"**Summary:** {s.feedback_summary}")
    else:
        st.sidebar.info("No past sessions found. Start an interview to see history!")

# --- 4.5. MAIN APP EXECUTION ---

def main():
    """The main function to run the Streamlit app."""
    # Apply custom styles first
    set_custom_styles() 
    
    st.sidebar.title("AI Interview Simulator")
    show_history()

    if st.session_state.stage == 'setup':
        setup_form()
    elif st.session_state.stage == 'interview':
        interview_session()
    elif st.session_state.stage == 'feedback':
        feedback_session()

if __name__ == '__main__':
    main()