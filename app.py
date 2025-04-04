import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

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
    st.subheader("Spiral Growth Tracker (RMQ-based)")
    if len(rmq_list) < 2:
        st.info("Not enough entries to draw a spiral yet.")
        return

    theta = np.linspace(0, 2 * np.pi * len(rmq_list), len(rmq_list))
    a = 1  # base radius
    b = 0.2  # growth scaling factor

    rmq_scaled = np.array(rmq_list)
    r = a + b * rmq_scaled

    x = r * np.cos(theta)
    y = r * np.sin(theta)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(x, y, linewidth=2)
    ax.set_title("Pursuit Growth Spiral", fontsize=14)
    ax.axis("off")
    st.pyplot(fig)

# ---------- Main Dashboard ----------
def dashboard():
    st.title("BICQ-PT Dashboard")

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

    if st.button("Save Entry"):
        new_row = {"Student": student, "Date": date, "PQ": pq_score}
        new_row.update(traits)

        if os.path.exists("data.csv"):
            df = pd.read_csv("data.csv")
            prev_entry = df[df["Student"] == student].sort_values("Date")
            if not prev_entry.empty:
                last_score = prev_entry.iloc[-1]["PQ"]
                delta = pq_score - last_score

                if delta >= 2:
                    st.success("🎉 Congrats! Your PQ score improved by 2+!")
                    st.info("Teacher alert: Student PQ increased significantly.")
                elif delta <= -2:
                    st.warning("⚠️ PQ score dropped by 2+. Keep going — growth isn't always linear.")
                    st.info("Teacher alert: Check in with this student for encouragement.")

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])

        df.to_csv("data.csv", index=False)
        st.success("Entry saved!")

    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        student_data = df[df["Student"] == student]

        if not student_data.empty:
            st.subheader("Radar Chart (PQ Traits)")
            latest = student_data.iloc[-1]
            categories = list(traits.keys())
            values = [latest[cat] for cat in categories] + [latest[categories[0]]]
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]

            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            ax.fill(angles, values, alpha=0.25)
            ax.plot(angles, values, linewidth=2)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_yticklabels([])
            ax.set_title(f"{student}'s PQ Profile", size=13)
            st.pyplot(fig)

            # Spiral
            rmq_list = student_data["PQ"].tolist()
            draw_spiral(rmq_list)

            # Download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download My Data (CSV)", csv, "bicq_data.csv", "text/csv")

            # Encouragement
            st.subheader("💬 Encouragement")
            st.markdown("Your effort defines your success — not comparison.")
            st.markdown("Growth is a journey, not a race.")
            st.markdown("Every small effort today builds a stronger tomorrow.")
            st.markdown("The best version of you is ahead — keep going!")

# ---------- Run App ----------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    dashboard()
else:
    login()