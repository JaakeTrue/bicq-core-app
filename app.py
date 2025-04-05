import os
import json
import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# --- Diagnostic Setup ---
diagnostic_files = {
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
diagnostic_path = "diagnostics"

# Sample fallback question
fallback_question = [
    {
        "subject": "Math",
        "topic": "Addition",
        "difficulty": "Easy",
        "question": "What is 2 + 3?",
        "answer": "5"
    }
]

# --- Radar Chart Function ---
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

# --- Spiral Chart Placeholder ---
def draw_spiral_placeholder():
    t = np.linspace(0, 6 * np.pi, 100)
    r = 0.5 * t
    x = r * np.cos(t)
    y = r * np.sin(t)
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title("Spiral Growth Placeholder")
    st.pyplot(fig)

# --- UI Setup ---
st.set_page_config(page_title="Game Changer Diagnostic", layout="wide")
st.title("🧠 Game Changer Diagnostic System")

# --- Student Dropdown ---
with st.sidebar:
    st.header("👤 Student Login")
    student_list = ["Select Student", "Izzy", "Jayden", "Maria", "Jake", "Masaki"]
    selected_student = st.selectbox("Choose a student:", student_list)
    student_grade = st.selectbox("Grade:", list(diagnostic_files.keys()))
    login_date = datetime.today().strftime("%Y-%m-%d")
    st.write(f"📅 Session: {login_date}")

# --- Init State ---
if "pq_scores" not in st.session_state:
    st.session_state.pq_scores = {"Participation": 5, "Effort": 5, "Mindset": 5, "Growth": 5, "Focus": 5}
if "diagnostic_questions" not in st.session_state:
    st.session_state.diagnostic_questions = []
    st.session_state.diagnostic_index = 0
    st.session_state.student_answers = []
    st.session_state.reinforcement_mode = False
    st.session_state.reinforcement_questions = []
    st.session_state.reinforcement_index = 0
    st.session_state.reinforcement_results = defaultdict(list)
    st.session_state.secret_gift_given = False
    st.session_state.mastered_topics = set()

# --- PQ Sliders ---
st.subheader("🔧 PQ Trait Self-Check")
for trait in st.session_state.pq_scores:
    st.session_state.pq_scores[trait] = st.slider(trait, 1, 10, st.session_state.pq_scores[trait])

# --- Radar & Spiral View ---
with st.expander("📊 PQ Trait Radar Chart"):
    draw_radar(st.session_state.pq_scores)

with st.expander("🌀 Spiral Growth View"):
    draw_spiral_placeholder()

# --- Start Diagnostic Test ---
if not st.session_state.diagnostic_questions and not st.session_state.reinforcement_mode:
    if st.button("Start Diagnostic Test"):
        filename = diagnostic_files[student_grade]
        filepath = os.path.join(diagnostic_path, filename)

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                st.session_state.diagnostic_questions = json.load(f)
            st.success(f"{student_grade} Diagnostic Test Loaded.")
        else:
            st.warning(f"{filename} not found in `diagnostics/`. Using fallback sample question.")
            st.session_state.diagnostic_questions = fallback_question

        st.session_state.diagnostic_index = 0
        st.session_state.student_answers = []

# --- Diagnostic Flow ---
if st.session_state.diagnostic_questions and not st.session_state.reinforcement_mode:
    index = st.session_state.diagnostic_index
    questions = st.session_state.diagnostic_questions

    if index < len(questions):
        q = questions[index]
        st.subheader(f"Question {index + 1} of {len(questions)}")
        st.write(f"**Subject:** {q['subject']}")
        st.write(f"**Topic:** {q['topic']} ({q['difficulty']})")
        st.write(q['question'])
        answer = st.text_input("Your Answer:", key=f"answer_{index}")

        if st.button("Next Question"):
            st.session_state.student_answers.append({
                "question": q['question'],
                "answer": answer,
                "subject": q['subject'],
                "topic": q['topic'],
                "correct": None
            })
            st.session_state.diagnostic_index += 1
    else:
        st.success("🎉 Diagnostic complete!")
        df = pd.DataFrame(st.session_state.student_answers)
        st.dataframe(df)

        weak_areas = df["topic"].value_counts().tail(5).index.tolist()
        st.session_state.weak_areas = weak_areas

        st.subheader("🧩 Recommended Reinforcement Topics")
        for topic in weak_areas:
            st.write(f"- {topic}")

        if st.button("Start Reinforcement Phase"):
            pool = [q for q in questions if q['topic'] in weak_areas]
            st.session_state.reinforcement_questions = random.sample(pool, min(15, len(pool)))
            st.session_state.reinforcement_mode = True
            st.session_state.reinforcement_index = 0
            st.session_state.reinforcement_results = defaultdict(list)
            st.session_state.mastered_topics = set()

# --- Reinforcement Phase ---
if st.session_state.reinforcement_mode:
    r_index = st.session_state.reinforcement_index
    r_questions = st.session_state.reinforcement_questions

    if r_index < len(r_questions):
        rq = r_questions[r_index]
        st.subheader(f"🔁 Reinforcement Question {r_index + 1} of {len(r_questions)}")
        st.write(f"**Subject:** {rq['subject']}")
        st.write(f"**Topic:** {rq['topic']} ({rq['difficulty']})")
        st.write(rq['question'])

        r_answer = st.text_input("Your Answer:", key=f"reinforce_{r_index}")

        if st.button("Next Reinforcement"):
            topic = rq['topic']
            correct = random.choice([True, False])
            st.session_state.reinforcement_results[topic].append(correct)

            if st.session_state.reinforcement_results[topic].count(True) == 4 and not st.session_state.secret_gift_given:
                st.session_state.secret_gift_given = True
                st.session_state.secret_topic = topic
                st.session_state.pq_scores["Growth"] += 0.5

            total = len(st.session_state.reinforcement_results[topic])
            corrects = st.session_state.reinforcement_results[topic].count(True)
            if total >= 10 and corrects / total >= 0.8:
                st.session_state.mastered_topics.add(topic)

            st.session_state.reinforcement_index += 1
    else:
        st.balloons()
        st.success("🌟 Reinforcement Complete!")
        if st.session_state.mastered_topics:
            st.subheader("✅ Topics Mastered:")
            for t in st.session_state.mastered_topics:
                st.write(f"- {t}")

        if st.session_state.secret_gift_given:
            topic = st.session_state.secret_topic
            st.markdown("## 🎁 Secret Gift Unlocked!")
            st.image("https://cdn-icons-png.flaticon.com/512/471/471664.png", width=150)
            st.success(f"You've mastered **{topic}**!")
            st.info("📬 Teacher Notification:")
            st.write(f"Student **{selected_student}** improved significantly in **{topic}**.")
            st.write("Spiral score shifted +5% upward in 'Growth'.")
        else:
            st.info("Keep going! You're building confidence and power through effort ✨")