from flask import Flask, render_template, request, render_template_string,redirect
import random
import joblib
import numpy as np
import re
from scipy.sparse import hstack
import threading
import subprocess
import requests
import time
import sys
import webbrowser

app = Flask(__name__)

# ----------------------------
# Previous code: interest_domain_courses
# ----------------------------
interest_domain_courses = {
    "Data Science": [
        "IBM Data Science Professional Certificate (Coursera)",
        "Kaggle Micro-Courses",
        "DataCamp Data Science Track",
        "freeCodeCamp Data Science Full Course (YouTube)"
    ],
    "Machine Learning": [
        "Andrew Ng Machine Learning (Coursera)",
        "Hands-On ML with Scikit-Learn and TensorFlow",
        "fast.ai Practical Deep Learning Course",
        "freeCodeCamp Machine Learning Full Course (YouTube)"
    ],
    "Artificial Intelligence": [
        "AI For Everyone (Coursera)",
        "Elements of AI",
        "Artificial Intelligence Nanodegree (Udacity)",
        "Simplilearn AI Full Course (YouTube)"
    ],
    "Web Development": [
        "freeCodeCamp Full Stack Developer",
        "The Odin Project",
        "CS50's Web Programming (Harvard)",
        "freeCodeCamp Web Development Full Course (YouTube)"
    ],
    "Mobile Application Development": [
        "Android Developer Certification (Google)",
        "iOS Development with Swift (Udemy)",
        "Build Android Apps with Kotlin (Coursera)",
        "freeCodeCamp Mobile App Development (YouTube)"
    ],
    "Cloud Computing": [
        "AWS Certified Solutions Architect",
        "Azure Fundamentals (Microsoft Learn)",
        "Google Cloud Fundamentals (Coursera)",
        "freeCodeCamp Cloud Computing Full Course (YouTube)"
    ],
    "Cyber Security": [
        "Certified Ethical Hacker (CEH)",
        "Introduction to Cyber Security (Coursera)",
        "Cybersecurity Specialization (University of Maryland)",
        "NetworkChuck (YouTube)"
    ],
    "Internet of Things (IoT)": [
        "IoT Specialization (Coursera)",
        "IoT for Beginners (Microsoft Learn)",
        "Introduction to IoT (edX)",
        "freeCodeCamp IoT Full Course (YouTube)"
    ],
    "Robotics": [
        "Modern Robotics (Coursera)",
        "Robotics Specialization (University of Pennsylvania)",
        "Robotics: AI Techniques (edX)",
        "Robot Tutorials (YouTube)"
    ],
    "Blockchain Technology": [
        "Blockchain Basics (Coursera)",
        "Blockchain Specialization (University at Buffalo)",
        "Ethereum and Solidity (Udemy)",
        "Dapp University (YouTube)"
    ],
    "Software Testing": [
        "ISTQB Foundation Level",
        "Selenium WebDriver with Java (Udemy)",
        "Automated Software Testing (Coursera)",
        "Software Testing Tutorials (YouTube)"
    ],
    "DevOps": [
        "Docker & Kubernetes (Udemy)",
        "DevOps Foundations (LinkedIn Learning)",
        "Continuous Delivery & DevOps (Coursera)",
        "TechWorld with Nana (YouTube)"
    ],
    "Networking": [
        "Cisco CCNA Certification",
        "Networking Fundamentals (Udemy)",
        "Computer Networking (Stanford Online)",
        "NetworkChuck (YouTube)"
    ],
    "Database Management": [
        "SQL for Data Science (Coursera)",
        "Database Management Essentials (edX)",
        "MySQL Bootcamp (Udemy)",
        "freeCodeCamp SQL Full Course (YouTube)"
    ],
    "UI/UX Design": [
        "Google UX Design Professional Certificate",
        "Interaction Design Foundation Courses",
        "UI/UX Design Essentials (Udemy)",
        "The Futur (YouTube)"
    ],
    "Digital Marketing": [
        "Digital Marketing Specialization (Coursera)",
        "Google Digital Marketing Courses",
        "HubSpot Academy Marketing Courses",
        "Simplilearn Digital Marketing (YouTube)"
    ],
    "Embedded Systems": [
        "Embedded Systems - Shape the World (Coursera)",
        "Microcontroller Projects (Udemy)",
        "Embedded Systems Programming (edX)",
        "Embedded Systems Tutorials (YouTube)"
    ],
    "Computer Vision": [
        "Deep Learning for Computer Vision (Coursera)",
        "Computer Vision with Python (Udemy)",
        "OpenCV Tutorials (PyImageSearch)",
        "freeCodeCamp Computer Vision Full Course (YouTube)"
    ],
    "Natural Language Processing (NLP)": [
        "Natural Language Processing Specialization (Coursera)",
        "NLP with Python (Udemy)",
        "Hugging Face Transformers Course",
        "freeCodeCamp NLP Full Course (YouTube)"
    ],
    "Game Development": [
        "Unity Learn",
        "Unreal Engine Online Learning",
        "Game Development with Python (Udemy)",
        "Brackeys (YouTube)"
    ],
    "Big Data Analytics": [
        "Big Data Specialization (Coursera)",
        "Hadoop and Spark (Udemy)",
        "Big Data Fundamentals (edX)",
        "freeCodeCamp Big Data Full Course (YouTube)"
    ],
    "Business Intelligence": [
        "Power BI Certification (Microsoft Learn)",
        "Tableau Training (Udemy)",
        "Business Intelligence Concepts (Coursera)",
        "Power BI Full Course (YouTube)"
    ],
    "Augmented Reality (AR) / Virtual Reality (VR)": [
        "Unity AR/VR Development (Udemy)",
        "AR/VR Specialization (Coursera)",
        "XR Development (edX)",
        "VR Dev Tutorials (YouTube)"
    ],
    "Automation": [
        "RPA Developer Foundation (UiPath Academy)",
        "Automation with Python (Udemy)",
        "Test Automation Specialization (Coursera)",
        "Automation Anywhere Tutorials (YouTube)"
    ],
    "Hardware Design": [
        "Digital Electronics Courses (NPTEL)",
        "VLSI Design (Coursera)",
        "FPGA Design (Udemy)",
        "Hardware Design Tutorials (YouTube)"
    ],
    "Electronics Design": [
        "Analog & Digital Electronics (Coursera)",
        "Electronics Foundations (Udemy)",
        "Circuit Design (edX)",
        "All About Circuits (YouTube)"
    ],
    "Software Development": [
        "CS50 Introduction to Computer Science (Harvard)",
        "Complete Python Bootcamp (Udemy)",
        "Full Stack Software Development (Coursera)",
        "freeCodeCamp Full Software Development Course (YouTube)"
    ],
    "Information Technology (IT) Support": [
        "Google IT Support Professional Certificate (Coursera)",
        "IT Fundamentals (Udemy)",
        "CompTIA A+ Certification",
        "Google IT Support (YouTube)"
    ],
    "Project Management": [
        "PMP Certification Training (PMI)",
        "Agile Project Management (Coursera)",
        "Project Management Principles (Udemy)",
        "Project Management Simplified (YouTube)"
    ],
    "Data Engineering": [
        "Data Engineering on Google Cloud (Coursera)",
        "ETL and Data Pipelines (Udemy)",
        "Big Data & Data Engineering Specialization (edX)",
        "Data Engineering Tutorials (YouTube)"
    ]
}

# ----------------------------
# Previous code: skills_to_courses mapping
# ----------------------------
skills_to_courses = {
    'communication': ['Public Speaking', 'Soft Skills Training'],
    'cgpa': ['Time Management', 'Study Strategies'],
    'projects_done': ['Build more projects', 'Participate in hackathons'],
    "Python": ["Coursera: Python for Everybody", "Udemy Python Bootcamp", "freeCodeCamp Python Course (YouTube)"],
    "Java": ["Java Programming Masterclass (Udemy)", "Coursera Java Specialization", "Programming with Mosh (YouTube)"],
    "C++": ["C++ For C Programmers (Coursera)", "Learn C++ (Udemy)", "The Cherno (YouTube)"],
    "SQL": ["SQL for Data Science (Coursera)", "The Complete SQL Bootcamp (Udemy)", "freeCodeCamp SQL Course (YouTube)"],
    "JavaScript": ["JavaScript Basics (freeCodeCamp)", "The Complete JavaScript Course (Udemy)", "Programming with Mosh (YouTube)"],
    "React": ["React - The Complete Guide (Udemy)", "React Official Docs", "freeCodeCamp React Course (YouTube)"],
    "Angular": ["Angular - The Complete Guide (Udemy)", "Angular Official Tutorial", "Codevolution Angular Tutorials (YouTube)"],
    "Node.js": ["Node.js Developer Course (Udemy)", "The Complete Node.js Course (Coursera)", "freeCodeCamp Node.js Course (YouTube)"],
    "Machine Learning": ["Andrew Ng ML Course (Coursera)", "Hands-On ML with Scikit-Learn and TensorFlow", "freeCodeCamp Machine Learning Course (YouTube)"],
    "Data Analysis": ["Data Analysis with Python (Coursera)", "Pandas for Data Analysis (Udemy)", "freeCodeCamp Data Analysis Course (YouTube)"],
    "Deep Learning": ["Deep Learning Specialization (Coursera)", "Deep Learning with Python (Udemy)", "freeCodeCamp Deep Learning Course (YouTube)"],
    "Communication": ["Effective Communication Skills (Coursera)", "Toastmasters", "Simple Programmer (YouTube)"],
    "Networking": ["Cisco CCNA Certification", "Networking Fundamentals (Udemy)", "NetworkChuck (YouTube)"],
    "Docker": ["Docker Mastery (Udemy)", "Docker for Beginners (YouTube)", "TechWorld with Nana (YouTube)"],
    "Kubernetes": ["Kubernetes for Beginners (Udemy)", "Kubernetes Official Docs", "TechWorld with Nana (YouTube)"],
    "Cloud Computing": ["AWS Certified Solutions Architect", "Azure Fundamentals (Microsoft Learn)", "freeCodeCamp Cloud Computing (YouTube)"],
    "HTML": ["HTML Full Course (freeCodeCamp)", "HTML & CSS Crash Course (Udemy)", "freeCodeCamp HTML (YouTube)"],
    "CSS": ["CSS Full Course (freeCodeCamp)", "CSS Flexbox & Grid (Udemy)", "freeCodeCamp CSS (YouTube)"],
    "Flask": ["Flask Mega-Tutorial (Miguel Grinberg)", "Python Flask Course (Udemy)", "freeCodeCamp Flask (YouTube)"],
    "Django": ["Django for Beginners (Udemy)", "Django Official Tutorial", "freeCodeCamp Django (YouTube)"],
    "TensorFlow": ["TensorFlow in Practice (Coursera)", "Deep Learning with TensorFlow (Udemy)", "freeCodeCamp TensorFlow (YouTube)"],
    "PyTorch": ["Deep Learning with PyTorch (Udemy)", "PyTorch Official Tutorials", "freeCodeCamp PyTorch (YouTube)"],
    "Big Data": ["Big Data Specialization (Coursera)", "Hadoop and Spark (Udemy)", "freeCodeCamp Big Data (YouTube)"],
    "DevOps": ["DevOps Foundations (LinkedIn Learning)", "Docker & Kubernetes (Udemy)", "TechWorld with Nana (YouTube)"],
    "Blockchain": ["Blockchain Basics (Coursera)", "Ethereum and Solidity (Udemy)", "Dapp University (YouTube)"],
    "Cyber Security": ["Certified Ethical Hacker (CEH)", "Introduction to Cyber Security (Coursera)", "NetworkChuck (YouTube)"],
    "UI/UX Design": ["Google UX Design Certificate", "Interaction Design Foundation Courses", "The Futur (YouTube)"],
    "Project Management": ["PMP Certification Training (PMI)", "Agile Project Management (Coursera)", "Project Management Simplified (YouTube)"],
    "Android Development": ["Android Developer Certification (Google)", "Android App Development with Kotlin (Udemy)", "Coding in Flow (YouTube)"],
    "iOS Development": ["iOS Development with Swift (Udemy)", "Stanford iOS Development Course (YouTube)", "CodeWithChris (YouTube)"]
}

# ----------------------------
# Previous code: domain_required_skills
# ----------------------------
domain_required_skills = {
    "Data Science": ["Python", "SQL", "Data Analysis", "Machine Learning"],
    "Machine Learning": ["Python", "Machine Learning", "Deep Learning", "Data Analysis"],
    "Artificial Intelligence": ["Python", "Machine Learning", "Deep Learning", "Computer Vision"],
    "Web Development": ["HTML", "CSS", "JavaScript", "React"],
    "Mobile Application Development": ["Java", "Kotlin", "Swift", "Android Development"],
    "Cloud Computing": ["Cloud Computing", "Docker", "Kubernetes", "Linux"],
    "Cyber Security": ["Cyber Security", "Networking", "Linux"],
    "Internet of Things (IoT)": ["Embedded Systems", "C/C++", "Python"],
    "Robotics": ["Embedded Systems", "Control Systems", "Python"],
    "Blockchain Technology": ["Blockchain", "Solidity", "Cryptography"],
    "Software Testing": ["Software Testing", "Selenium", "Automation"],
    "DevOps": ["Docker", "Kubernetes", "CI/CD"],
    "Networking": ["Networking", "Cisco", "Network Security"],
    "Database Management": ["SQL", "Database Design"],
    "UI/UX Design": ["UI/UX Design", "Figma"],
    "Digital Marketing": ["Digital Marketing", "SEO"],
    "Embedded Systems": ["Embedded Systems", "C/C++"],
    "Computer Vision": ["Computer Vision", "Deep Learning", "OpenCV"],
    "Natural Language Processing (NLP)": ["NLP", "Python", "Transformers"],
    "Big Data Analytics": ["Big Data", "Spark", "Hadoop"],
    "Software Development": ["Python", "Java", "C++", "Data Structures"],
    "Information Technology (IT) Support": ["IT Support", "Hardware", "Networking"],
    "Project Management": ["Project Management", "Agile"],
    "Data Engineering": ["SQL", "ETL", "Big Data"]
}

# ----------------------------
# Load trained ML model and preprocessor
# ----------------------------
MODEL_PATH = "placement_model_calibrated.pkl"
PREPROC_PATH = "preprocessor.pkl"

try:
    model = joblib.load(MODEL_PATH)
    preproc = joblib.load(PREPROC_PATH)
    vectorizer = preproc.get("vectorizer")
    scaler = preproc.get("scaler")
    le_intern = preproc.get("le_intern")
    le_backlogs = preproc.get("le_backlogs")
    le_domain = preproc.get("le_domain")
    numeric_cols = preproc.get("numeric_cols", [
        'project_count','communication','cgpa','marks_10','marks_12','cert_count',
        'skills_count','domain_skill_match_ratio','internship_enc','backlogs_enc','interest_domain_enc'
    ])
    domain_required_skills = preproc.get("domain_required_skills", domain_required_skills)
    skills_to_courses = preproc.get("skills_to_courses", skills_to_courses)
    interest_domain_courses = preproc.get("interest_domain_courses", interest_domain_courses)
except Exception as e:
    print("Error loading ML model or preprocessor:", e)
    model = None
    preproc = None
    vectorizer = None
    scaler = None
    le_intern = None
    le_backlogs = None
    le_domain = None

# ----------------------------
# Helper functions
# ----------------------------
def normalize_skill(s):
    return s.strip().lower()

def tokenize_skills_text(text):
    if not isinstance(text, str) or text.strip() == "":
        return []
    parts = re.split(r'[,\;/\|]+', text)
    return [p.strip() for p in parts if p.strip()]

def compute_domain_match(skills_tokens, domain):
    req = domain_required_skills.get(domain, [])
    if not req:
        return 0.0
    matched = sum(1 for r in req if r.strip().lower() in [s.lower() for s in skills_tokens])
    return matched / len(req)

# ----------------------------
# Streamlit integration
# ----------------------------
STREAMLIT_PORT = 8501
STREAMLIT_URL = f"http://localhost:{STREAMLIT_PORT}"
STREAMLIT_SCRIPT = "interview_simulator.py"

def is_streamlit_running(timeout=1.0):
    try:
        resp = requests.get(STREAMLIT_URL, timeout=timeout)
        return resp.status_code == 200 or resp.status_code == 302
    except Exception:
        return False

def start_streamlit():
    if is_streamlit_running():
        return
    cmd = [sys.executable, "-m", "streamlit", "run", STREAMLIT_SCRIPT,
           "--server.port", str(STREAMLIT_PORT), "--server.headless", "true"]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)


# ----------------------------
# Routes
# ----------------------------



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/predict_result', methods=['POST'])
def predict_result():
    # ------------------
    # Read form fields
    # ------------------
    name = request.form.get('name', 'Student')
    raw_skills = request.form.get('skills', '')
    skills_tokens = tokenize_skills_text(raw_skills)
    skills_joined = " ".join(skills_tokens)
    skills_count = len(skills_tokens)

    project_count = int(request.form.get('project_count', 0))
    internship = request.form.get('internship', 'No')
    communication = int(request.form.get('communication', 3))
    cgpa = float(request.form.get('cgpa', 0.0))
    certificates = request.form.get('certificates', '')
    cert_count = len([c for c in certificates.split(',') if c.strip() != ""])
    backlogs = request.form.get('backlogs', 'No')
    marks_10 = float(request.form.get('marks_10', 0.0))
    marks_12 = float(request.form.get('marks_12', 0.0))
    interest_domain = request.form.get('interest_domain', 'Other')

    domain_skill_match_ratio = compute_domain_match(skills_tokens, interest_domain)

    # ------------------
    # Build ML features
    # ------------------
    X_skills = vectorizer.transform([skills_joined])
    numeric_vals = []
    for col in numeric_cols:
        if col == 'cgpa':
            numeric_vals.append(cgpa)
        elif col == 'project_count':
            numeric_vals.append(project_count)
        elif col == 'communication':
            numeric_vals.append(communication)
        elif col == 'marks_10':
            numeric_vals.append(marks_10)
        elif col == 'marks_12':
            numeric_vals.append(marks_12)
        elif col == 'cert_count':
            numeric_vals.append(cert_count)
        elif col == 'skills_count':
            numeric_vals.append(skills_count)
        elif col == 'domain_skill_match_ratio':
            numeric_vals.append(domain_skill_match_ratio)
        elif col == 'internship_enc':
            try:
                numeric_vals.append(le_intern.transform([internship])[0])
            except:
                numeric_vals.append(0)
        elif col == 'backlogs_enc':
            try:
                numeric_vals.append(le_backlogs.transform([backlogs])[0])
            except:
                numeric_vals.append(0)
        elif col == 'interest_domain_enc':
            try:
                if interest_domain in list(le_domain.classes_):
                    numeric_vals.append(le_domain.transform([interest_domain])[0])
                else:
                    numeric_vals.append(0)
            except:
                numeric_vals.append(0)
        else:
            numeric_vals.append(0)

    X_num_scaled = scaler.transform(np.array(numeric_vals).reshape(1, -1))
    X_all = hstack([X_skills, X_num_scaled])

    # ------------------
    # Predict ML probability
    # ------------------
    prob = model.predict_proba(X_all)[:, 1][0]

    # ------------------
    # RULES-BASED BOOST (Option 3)
    # ------------------
    # Boost based on skills
    if skills_count >= 3 and domain_skill_match_ratio >= 0.7:
        prob += 0.15  # +15% boost for good skills
    # Boost if at least 1 project
    if project_count >= 1:
        prob += 0.10
    # Boost if CGPA >= 7.5
    if cgpa >= 7.5:
        prob += 0.05
    # Reduce slightly if no internship
    if internship.lower() == "no":
        prob -= 0.05
    # Cap probability between 0 and 0.99
    prob = min(max(prob, 0), 0.99)

    prediction_percent = round(prob * 100, 2)

    # ------------------
    # Generate suggestions
    # ------------------
    message = (f"Congratulations {name}! Your predicted placement chance is {prediction_percent}%."
               if prediction_percent >= 70 else
               f"Don't worry {name}, your predicted placement chance is {prediction_percent}%. Focus on improving your skills.")

    weak_areas = []
    course_suggestions = []
    missing_skills = []

    if communication < 3:
        weak_areas.append("Communication")
        if "Communication" in skills_to_courses:
            course_suggestions.extend(skills_to_courses["Communication"])

    if internship.lower() == "no":
        weak_areas.append("Internship Experience")
        course_suggestions.append("Work on mini-projects or apply on Internshala/LinkedIn.")

    if project_count == 0:
        weak_areas.append("Project Experience")
        course_suggestions.append(f"Start a project related to {interest_domain}.")

    if cgpa < 7:
        weak_areas.append("CGPA / Academic Performance")
        course_suggestions.append("Focus on fundamentals and subject-specific revision.")

    if backlogs.lower() == "yes":
        weak_areas.append("Backlogs")
        course_suggestions.append("Clear backlogs with guided study.")

    # Domain-based suggestions
    domain_courses = interest_domain_courses.get(interest_domain, [])
    course_suggestions.extend(domain_courses)

    required_skills = domain_required_skills.get(interest_domain, [])
    for req in required_skills:
        if req.lower() not in [s.lower() for s in skills_tokens]:
            missing_skills.append(req)
            weak_areas.append(f"Missing: {req}")
            if req in skills_to_courses:
                course_suggestions.extend(skills_to_courses[req])
            else:
                course_suggestions.append(f"Find beginner course for {req} online.")

    # Deduplicate suggestions
    seen = set()
    deduped_suggestions = []
    for item in course_suggestions:
        if item not in seen:
            deduped_suggestions.append(item)
            seen.add(item)

    return render_template('predict_result.html',
                           name=name,
                           prediction_percent=prediction_percent,
                           message=message,
                           interest_domain=interest_domain,
                           weak_areas=weak_areas,
                           missing_skills=missing_skills,
                           course_suggestions=deduped_suggestions)


# ----------------------------
# Other navbar pages
# ----------------------------
@app.route('/resume')
def resume():
    try:
        return render_template('resume.html')
    except:
        return render_template_string("<h2>Resume Section Placeholder</h2>")

@app.route('/courses')
def courses():
    try:
        return render_template('courses.html')
    except:
        return render_template_string("<h2>Courses Section Placeholder</h2>")

@app.route('/interview')
def interview():
    # This is the crucial route: It renders the template that holds the iframe.
    # return render_template('interview.html', current_page='interview')
      # Launch Streamlit in background if not already running
    if not is_streamlit_running():
        threading.Thread(target=start_streamlit, daemon=True).start()
        # Wait for Streamlit to start
        for i in range(20):
            if is_streamlit_running(timeout=0.5):
                break
            time.sleep(0.5)
    # Redirect user to Streamlit UI
    return redirect(STREAMLIT_URL)

# ----------------------------
# Run app
# ----------------------------
if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")  # automatically open browser
    app.run(debug=True, port=5000)
   
    
