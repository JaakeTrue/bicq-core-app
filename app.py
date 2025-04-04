import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

# --- Secure Login ---
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "jake" and password == "Tes":
            st.session_state["logged_in"] = True
        else:
            st.error("Invalid credentials")

# --- Main Dashboard ---
def dashboard():
    st.title("BICQ-PT Growth Dashboard")

    student = st.text_input("Student Name/ID")
    date = st.date_input("Date", datetime.date.today())

    traits = {
        "Class Participation": st.slider("Class Participation", 1, 10),
        "Test Preparation": st.slider("Test Preparation", 1, 10),
        "Learning Organization": st.slider("Learning Organization", 1, 10),
        "Homework/Assignments": st.slider("Homework/Assignments", 1, 10),
        "Grade Improvement": st.slider("Grade Improvement", 1, 10),
    }

    if st.button("Save Entry"):
        row = {"Student": student, "Date": date}
        row.update(traits)
        df = pd.DataFrame([row])
        if os.path.exists("data.csv"):
            df_existing = pd.read_csv("data.csv")
            df = pd.concat([df_existing, df], ignore_index=True)
        df.to_csv("data.csv", index=False)
        st.success("Entry saved!")

    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        student_data = df[df["Student"] == student]
        
        if not student_data.empty:
            st.subheader("Radar Chart: Growth Over Time")
            fig, ax = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
            categories = list(traits.keys())
            N = len(categories)

            for _, row in student_data.iterrows():
                values = [row[cat] for cat in categories]
                values += values[:1]
                angles = [n / float(N) * 2 * np.pi for n in range(N)]
                angles += angles[:1]
                ax.plot(angles, values, linewidth=1, linestyle='solid', label=row["Date"])

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            st.pyplot(fig)

            latest = student_data.iloc[-1]
            if latest["Grade Improvement"] > 7:
                st.success("You’ve made strong progress! Keep it up!")
            else:
                st.info("Your awareness is growing — keep showing up and growing!")

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download My Data (CSV)", csv, "bicq_data.csv", "text/csv")

# --- Main Logic ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state["logged_in"]:
    dashboard()
else:
    login()
