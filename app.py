import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import random

# ---------- Login Setup ----------
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "jake" and password == "Tes":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# ---------- Spiral Drawing ----------
def draw_spiral(rmq_list):
    theta = np.linspace(0, 2 * np.pi * len(rmq_list), len(rmq_list))
    a = 1
    b = 0.2
    rmq_scaled = np.array(rmq_list)
    r = a + b * rmq_scaled
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    colors = plt.cm.viridis(np.linspace(0, 1, len(rmq_list)))
    fig, ax = plt.subplots(figsize=(6, 6))
    for i in range(len(x)-1):
        ax.plot(x[i:i+2], y[i:i+2], color=colors[i], linewidth=3)
    ax.scatter(x[-1], y[-1], s=200, color='red', marker='*', label="Current Position")

    for i, (xi, yi, score) in enumerate(zip(x, y, rmq_list)):
        ax.text(xi + 0.3, yi + 0.3, f"{score}", fontsize=9, color="black", weight="bold")

    ax.set_title("Pursuit Growth Spiral", fontsize=14)
    ax.axis("off")
    st.pyplot(fig)

# ---------- PQ Radar Drawing ----------
def draw_radar(student_data, traits):
    if len(student_data) < 2:
        return

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    colors = plt.cm.viridis(np.linspace(0.3, 1, len(student_data)))

    angles = np.linspace(0, 2 * np.pi, len(traits), endpoint=False).tolist()
    angles += angles[:1]

    for idx, row in enumerate(student_data.itertuples()):
        values = [row._asdict()[trait] for trait in traits] + [row._asdict()[traits[0]]]
        ax.plot(angles, values, linewidth=2, label=f"{row.Date}", color=colors[idx])
        ax.fill(angles, values, alpha=0.1, color=colors[idx])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(traits)
    ax.set_yticklabels([])
    ax.set_title("PQ Growth Over Time", fontsize=14)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    st.pyplot(fig)

# ---------- Game Changer ----------
def game_changer():
    st.header("🎮 Game Changer - Daily Challenge")

    subjects = ["Math", "English", "Science"]
    question_bank = {
        "Math": ["What is 8 × 7?", "Solve: 3x + 5 = 20", "What is the square root of 64?"],
        "English": ["Define 'benevolent'", "What is a metaphor?", "Correct the sentence: 'He go to school.'"],
        "Science": ["What planet is known as the Red Planet?", "Define photosynthesis.", "What is H2O?"]
    }

    selected_subject = st.selectbox("Select Subject", subjects)
    questions = random.sample(question_bank[selected_subject], 3)

    answers = []
    for i, q in enumerate(questions):
        ans = st.text_input(f"Q{i+1}: {q}")
        answers.append(ans)

    if st.button("✅ Submit Answers"):
        st.success("Great effort! Reflect on what you got right or struggled with.")
        st.balloons()

# ---------- Dashboard Tab ----------
def dashboard():
    st.header("📊 PQ + RMQ Dashboard")

    student = st.text_input("Student Name/ID")
    date = st.date_input("Date", datetime.date.today())

    traits = {
        "Class Participation": st.slider("Class Participation", 1, 10),
        "Test Preparation": st.slider("Test Preparation", 1, 10),
        "Learning Organization": st.slider("Learning Organization", 1, 10),
        "Homework/Assignments": st.slider("Homework/Assignments", 1, 10),
        "Grade Improvement": st.slider("Grade Improvement", 1, 10),
    }

    pq_score = sum(traits.values()) / 5

    if st.button("💾 Save Entry"):
        new_row = {"Student": student, "Date": date, "PQ": pq_score}
        new_row.update(traits)
        if os.path.exists("data.csv"):
            df = pd.read_csv("data.csv")
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        df.to_csv("data.csv", index=False)
        st.success("Entry saved!")

    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        student_data = df[df["Student"] == student]
        if not student_data.empty:
            draw_radar(student_data, list(traits.keys()))
            rmq_list = student_data["PQ"].tolist()
            draw_spiral(rmq_list)

# ---------- Run App ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    tab1, tab2 = st.tabs(["📊 Dashboard", "🎮 Game Changer"])
    with tab1:
        dashboard()
    with tab2:
        game_changer()
else:
    login()