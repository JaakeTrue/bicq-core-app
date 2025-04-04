import streamlit as st
import random

# ---------- Game Changer Phase 1 & 2 ----------
def game_changer_v2():
    st.header("🎮 Game Changer+ — Diagnostic Phase")

    # Phase 1: Grade Selection
    levels = ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", 
              "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", 
              "Grade 11", "Grade 12", "GED"]
    selected_level = st.selectbox("Select Your Grade or Program:", levels)

    # Phase 2: Diagnostic Test 1 - Sample Questions (Math only for now)
    st.subheader("📘 Diagnostic Test 1: Math")

    test_questions = [
        {
            "question": "You have 3/4 of a pizza and eat 1/2 of it. How much pizza is left?",
            "type": "word",
            "input": st.text_input("Q1: Fraction Word Problem")
        },
        {
            "question": "Solve for x: 3x + 5 = 20",
            "type": "algebra",
            "input": st.text_input("Q2: Solve Algebra")
        },
        {
            "question": "Below is a paragraph about a data table. Read it and answer: 

'The class collected data on rainfall each day. On Monday it rained 10 mm, Tuesday 0 mm, Wednesday 5 mm...'

What was the average rainfall?",
            "type": "paragraph",
            "input": st.text_input("Q3: Paragraph Style Question")
        }
    ]

    if st.button("✅ Submit Diagnostic Test 1"):
        st.success("Your answers have been submitted! Two more tests will follow. Stay ready!")

# Call it as a placeholder
game_changer_v2()