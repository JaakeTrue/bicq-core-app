import os
import json
import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- Constants ---
DIAGNOSTIC_FILES = {
    "Grade 1": "grade1_diagnostic.json",
    "Grade 2": "grade2_diagnostic.json",
    "Grade 3": "grade3_diagnostic.json",
    "Grade 4": "grade4_diagnostic.json",
    "Grade 5": "grade5_diagnostic.json",
    "Grade 6": "grade6_diagnostic.json",
    "Grade 7": "grade7_diagnostic.json",
    "Grade 8": "grade8_diagnostic.json",
    "GED": "ged_diagnostic.json"
}
DIAGNOSTIC_PATH = "diagnostics"
STUDENT_LIST = ["Select Student", "Izzy", "Jayden", "Maria", "Jake", "Masaki"]

# --- Utility Functions ---
def initialize_session_state():
    if "pq_scores" not in st.session_state:
        st.session_state.pq_scores = {
            "Participation": 5, 
            "Effort": 5, 
            "Mindset": 5, 
            "Growth": 5, 
            "Focus": 5
        }
    if "diagnostic_data" not in st.session_state:
        st.session_state.diagnostic_data = {
            "questions": [],
            "index": 0,
            "answers": [],
            "reinforcement_mode": False,
            "reinforcement_questions": [],
            "reinforcement_index": 0,
            "reinforcement_results": defaultdict(list),
            "secret_gift_given": False,
            "mastered_topics": set(),
            "weak_areas": []
        }

def draw_radar(trait_scores, label="Today"):
    traits = list(trait_scores.keys())
    values = list(trait_scores.values()) + [trait_scores[traits[0]]]
    angles = np.linspace(0, 2 * np.pi, len(traits), endpoint=False).tolist() + [0]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=label)
    ax.fill(angles, values, alpha=0.25)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(traits)
    ax.legend(loc='upper right')
    st.pyplot(fig)

def draw_spiral_placeholder():
    t = np.linspace(0, 6 * np.pi, 100)
    r = 0.5 * t
    x = r * np.cos(t)
    y = r * np.sin(t)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Spiral Growth Placeholder")
    st.pyplot(fig)

def load_diagnostic_questions(grade):
    filename = DIAGNOSTIC_FILES[grade]
    filepath = os.path.join(DIAGNOSTIC_PATH, filename)
    
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            st.warning(f"{filename} not found. Using sample questions.")
            return [{
                "subject": "Math",
                "topic": "Sample",
                "difficulty": "Easy",
                "question": "What is 2 + 2?",
                "answer": "4"
            }]
    except Exception as e:
        st.error(f"Error loading questions: {str(e)}")
        return []

# --- UI Setup ---
st.set_page_config(page_title="Game Changer Diagnostic", layout="wide")
st.title("🧠 Game Changer Diagnostic System")

# --- Sidebar - Student Selection ---
with st.sidebar:
    st.header("👤 Student Login")
    selected_student = st.selectbox("Choose a student:", STUDENT_LIST)
    student_grade = st.selectbox("Grade:", list(DIAGNOSTIC_FILES.keys()))
    login_date = datetime.today().strftime("%Y-%m-%d")
    st.write(f"📅 Session: {login_date}")

# Initialize session state
initialize_session_state()

# --- Main App Flow ---
if selected_student == "Select Student":
    st.info("👈 Please select a student from the sidebar to begin")
else:
    # --- Student Dashboard Header ---
    st.header(f"Student Dashboard: {selected_student}")
    st.subheader(f"📊 {student_grade} Performance Metrics")

    # --- PQ Trait Assessment ---
    st.subheader("🔧 PQ Trait Self-Check")
    for trait in st.session_state.pq_scores:
        st.session_state.pq_scores[trait] = st.slider(
            trait, 1, 10, st.session_state.pq_scores[trait]
        )

    # --- Visualization Section ---
    col1, col2 = st.columns(2)
    with col1:
        with st.expander("📊 PQ Trait Radar Chart"):
            draw_radar(st.session_state.pq_scores)
    with col2:
        with st.expander("🌀 Spiral Growth View"):
            draw_spiral_placeholder()

    # --- Diagnostic Test Flow ---
    data = st.session_state.diagnostic_data
    
    if not data["questions"] and not data["reinforcement_mode"]:
        if st.button("Start Diagnostic Test"):
            data["questions"] = load_diagnostic_questions(student_grade)
            data["index"] = 0
            data["answers"] = []

    if data["questions"] and not data["reinforcement_mode"]:
        if data["index"] < len(data["questions"]):
            q = data["questions"][data["index"]]
            st.subheader(f"Question {data['index'] + 1} of {len(data['questions'])}")
            st.write(f"**Subject:** {q['subject']}")
            st.write(f"**Topic:** {q['topic']} ({q['difficulty']})")
            st.write(q['question'])
            answer = st.text_input("Your Answer:", key=f"answer_{data['index']}")

            if st.button("Next Question"):
                data["answers"].append({
                    "question": q['question'],
                    "answer": answer,
                    "subject": q['subject'],
                    "topic": q['topic'],
                    "correct": None
                })
                data["index"] += 1
        else:
            st.success("🎉 Diagnostic complete!")
            df = pd.DataFrame(data["answers"])
            st.dataframe(df)

            data["weak_areas"] = df["topic"].value_counts().tail(5).index.tolist()
            st.subheader("🧩 Recommended Reinforcement Topics")
            for topic in data["weak_areas"]:
                st.write(f"- {topic}")

            if st.button("Start Reinforcement Phase"):
                pool = [q for q in data["questions"] if q['topic'] in data["weak_areas"]]
                data["reinforcement_questions"] = random.sample(pool, min(15, len(pool)))
                data["reinforcement_mode"] = True
                data["reinforcement_index"] = 0
                data["reinforcement_results"] = defaultdict(list)
                data["mastered_topics"] = set()

    # --- Reinforcement Phase ---
    if data["reinforcement_mode"]:
        if data["reinforcement_index"] < len(data["reinforcement_questions"]):
            rq = data["reinforcement_questions"][data["reinforcement_index"]]
            st.subheader(f"🔁 Reinforcement Question {data['reinforcement_index'] + 1} of {len(data['reinforcement_questions'])}")
            st.write(f"**Subject:** {rq['subject']}")
            st.write(f"**Topic:** {rq['topic']} ({rq['difficulty']})")
            st.write(rq['question'])
            r_answer = st.text_input("Your Answer:", key=f"reinforce_{data['reinforcement_index']}")

            if st.button("Next Reinforcement"):
                topic = rq['topic']
                correct = random.choice([True, False])
                data["reinforcement_results"][topic].append(correct)

                if data["reinforcement_results"][topic].count(True) == 4 and not data["secret_gift_given"]:
                    data["secret_gift_given"] = True
                    st.session_state.pq_scores["Growth"] += 0.5

                total = len(data["reinforcement_results"][topic])
                corrects = data["reinforcement_results"][topic].count(True)
                if total >= 10 and corrects / total >= 0.8:
                    data["mastered_topics"].add(topic)

                data["reinforcement_index"] += 1
        else:
            st.balloons()
            st.success("🌟 Reinforcement Complete!")
            
            if data["mastered_topics"]:
                st.subheader("✅ Topics Mastered:")
                for t in data["mastered_topics"]:
                    st.write(f"- {t}")

            if data["secret_gift_given"]:
                st.markdown("## 🎁 Secret Gift Unlocked!")
                st.image("https://cdn-icons-png.flaticon.com/512/471/471664.png", width=150)
                st.success("You've shown significant improvement!")
                st.info("📬 Teacher Notification:")
                st.write(f"Student {selected_student} has made excellent progress.")
                st.write("Spiral score shifted +5% upward in 'Growth'.")
            else:
                st.info("Keep going! You're building confidence and power through effort ✨")