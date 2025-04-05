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
WORKSHEET_FOLDER = "3rd_English_Worksheets"
STUDENT_LIST = ["Select Student", "Izzy", "Jayden", "Maria", "Jake", "Masaki"]

# --- Worksheet Structure ---
WORKSHEET_CATEGORIES = {
    "Grammar": {
        "Pronouns": ["Subject Pronouns", "Pronoun Replacement"],
        "Verbs": ["Present Tense", "Present Progressive", "Do/Does/Did"],
        "Nouns": ["Common/Proper Nouns", "There is/There are"],
        "Prepositions": ["Preposition Practice"]
    },
    "Reading": {
        "Grasshopper Story": ["Reading Passage", "Comprehension Questions", "Cloze Activity"],
        "Three Rs Story": ["Reading Passage", "Vocabulary Exercise", "True/False Questions"]
    },
    "Writing": {
        "Capitalization": ["Sentence Correction", "Paragraph Correction"],
        "Alphabetical Order": ["ABC Practice"]
    },
    "Vocabulary": {
        "General": ["Number Words Matching"]
    }
}

# Sample questions database
SAMPLE_QUESTIONS = {
    "Subject Pronouns": [
        {
            "question": "_____ am a student. (I/She/They)",
            "answer": "I",
            "difficulty": "Easy"
        },
        {
            "question": "_____ are family. (Mark and Daniel)",
            "answer": "They",
            "difficulty": "Medium"
        }
    ],
    "Pronoun Replacement": [
        {
            "question": "Charles puts the books on the table. → _____ puts the books on the table.",
            "options": ["It", "Me", "Us", "He"],
            "answer": "He",
            "difficulty": "Easy"
        }
    ]
}

# --- Utility Functions ---
def load_worksheet(category, subcategory, worksheet):
    """Load worksheet questions from JSON files"""
    filepath = os.path.join(WORKSHEET_FOLDER, category, subcategory, f"{worksheet.replace(' ', '_')}.json")
    
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            st.warning(f"Worksheet not found: {worksheet}")
            return SAMPLE_QUESTIONS.get(worksheet, [])
    except Exception as e:
        st.error(f"Error loading worksheet: {str(e)}")
        return []

def display_question(question, index, total):
    """Render question with appropriate input type"""
    st.subheader(f"Question {index + 1} of {total}")
    
    if 'options' in question:
        answer = st.radio(question["question"], 
                         question["options"],
                         key=f"q_{index}")
    else:
        st.write(question["question"])
        answer = st.text_input("Your answer:", key=f"q_{index}")
    
    return answer

# --- UI Setup ---
st.set_page_config(page_title="3rd Grade English Learning System", layout="wide")
st.title("📚 3rd Grade English Learning System")

# --- Sidebar - Student Selection ---
with st.sidebar:
    st.header("👤 Student Profile")
    selected_student = st.selectbox("Select Student:", STUDENT_LIST)
    
    if selected_student != "Select Student":
        st.subheader("📝 Worksheet Categories")
        selected_category = st.selectbox("Category:", list(WORKSHEET_CATEGORIES.keys()))
        
        if selected_category:
            selected_subcategory = st.selectbox("Subcategory:", 
                                              list(WORKSHEET_CATEGORIES[selected_category].keys()))
            
            if selected_subcategory:
                selected_worksheet = st.selectbox("Worksheet:", 
                                                 WORKSHEET_CATEGORIES[selected_category][selected_subcategory])

# --- Main Content ---
if selected_student == "Select Student":
    st.info("👈 Please select a student to begin")
else:
    st.header(f"{selected_student}'s English Practice")
    
    # Initialize session state
    if "worksheet_data" not in st.session_state:
        st.session_state.worksheet_data = {
            "questions": [],
            "current_index": 0,
            "answers": [],
            "score": 0
        }
    
    # Load selected worksheet
    if st.button("📂 Load Worksheet"):
        st.session_state.worksheet_data["questions"] = load_worksheet(
            selected_category, 
            selected_subcategory, 
            selected_worksheet
        )
        st.session_state.worksheet_data["current_index"] = 0
        st.session_state.worksheet_data["answers"] = []
        st.session_state.worksheet_data["score"] = 0
        st.success(f"Loaded {selected_worksheet} worksheet!")
    
    # Display current question
    data = st.session_state.worksheet_data
    if data["questions"]:
        if data["current_index"] < len(data["questions"]):
            q = data["questions"][data["current_index"]]
            user_answer = display_question(q, data["current_index"], len(data["questions"]))
            
            if st.button("✅ Submit Answer"):
                is_correct = False
                if 'options' in q:
                    is_correct = user_answer == q["answer"]
                else:
                    # Simple text answer checking (could be enhanced)
                    is_correct = user_answer.lower().strip() == q["answer"].lower().strip()
                
                data["answers"].append({
                    "question": q["question"],
                    "user_answer": user_answer,
                    "correct_answer": q["answer"],
                    "is_correct": is_correct
                })
                
                if is_correct:
                    data["score"] += 1
                    st.success("Correct! 🎉")
                else:
                    st.error(f"Oops! The correct answer is: {q['answer']}")
                
                if 'explanation' in q:
                    st.info(f"Explanation: {q['explanation']}")
                
                data["current_index"] += 1
                st.experimental_rerun()
        else:
            # Show results
            st.balloons()
            st.success(f"Worksheet complete! Score: {data['score']}/{len(data['questions'])}")
            
            # Display all questions and answers
            st.subheader("📝 Your Answers")
            for i, answer in enumerate(data["answers"]):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"Q{i+1}: {answer['question']}")
                    st.write(f"Your answer: {answer['user_answer']}")
                    st.write(f"Correct answer: {answer['correct_answer']}")
                with col2:
                    st.write("✅ Correct" if answer["is_correct"] else "❌ Incorrect")
            
            # Progress visualization
            st.subheader("📊 Performance")
            fig, ax = plt.subplots()
            ax.bar(["Correct", "Incorrect"], 
                  [data["score"], len(data["questions"]) - data["score"]],
                  color=["green", "red"])
            st.pyplot(fig)
            
            if st.button("🔄 Start New Worksheet"):
                st.session_state.worksheet_data = {
                    "questions": [],
                    "current_index": 0,
                    "answers": [],
                    "score": 0
                }
                st.experimental_rerun()
    else:
        st.info("👉 Select a worksheet category and click 'Load Worksheet' to begin")

# --- Instructions for Teachers ---
with st.expander("ℹ️ Teacher Instructions"):
    st.write("""
    **How to use this system:**
    1. Select a student from the sidebar
    2. Choose a worksheet category and specific worksheet
    3. Click 'Load Worksheet'
    4. Students answer questions one by one
    5. View results and explanations after completion
    
    **Adding New Worksheets:**
    - Create JSON files in the `3rd_English_Worksheets` folder
    - Follow the same structure as the sample questions
    - Organize by category/subcategory
    """)