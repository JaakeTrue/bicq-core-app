import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# --- Constants ---
WORKSHEET_FOLDER = "3rd_Grade_Materials"
STUDENT_LIST = ["Select Student", "Izzy", "Jayden", "Maria", "Jake", "Masaki"]
NSM_INTERVALS = [3, 7, 21]  # Days between spiral PQs
GAME_XP = {"Easy": 10, "Medium": 20, "Hard": 30}

# --- Initialize Session State ---
if "student_data" not in st.session_state:
    st.session_state.student_data = {
        "current_worksheet": None,
        "current_question": 0,
        "answers": [],
        "total_xp": 0,
        "game_unlocked": False
    }

# --- Game Changer Mini-Game ---
def launch_minigame(question):
    """Simplified HTML5 drag-and-drop game"""
    html_code = f"""
    <div style="font-family:Arial; text-align:center; padding:20px; border:2px solid #4CAF50; border-radius:10px;">
        <h4>{question['question']}</h4>
        <div style="display:flex; gap:10px; justify-content:center; margin:20px 0;">
            <div id="drag1" draggable="true" style="padding:8px 15px; background:#4CAF50; color:white; border-radius:5px; cursor:grab;">
                {question['answer']}
            </div>
            <div id="drag2" draggable="true" style="padding:8px 15px; background:#f44336; color:white; border-radius:5px; cursor:grab;">
                {random.choice(['X','Y','Z'])}
            </div>
        </div>
        <div id="dropzone" style="width:100%; height:50px; background:#f0f0f0; display:flex; align-items:center; justify-content:center; margin:10px 0;">
            Drop answer here
        </div>
        <p id="feedback" style="font-weight:bold;"></p>
    </div>

    <script>
        function allowDrop(e) {{
            e.preventDefault();
        }}

        function drag(e) {{
            e.dataTransfer.setData("text", e.target.textContent);
        }}

        function drop(e) {{
            e.preventDefault();
            const answer = e.dataTransfer.getData("text");
            const correct = "{question['answer']}";
            
            if (answer === correct) {{
                document.getElementById("feedback").innerHTML = "✅ Correct! +{GAME_XP[question['difficulty']]} XP";
                document.getElementById("feedback").style.color = "#4CAF50";
                window.parent.postMessage({{"type": "game_won", "xp": {GAME_XP[question['difficulty']]}}}, "*");
            }} else {{
                document.getElementById("feedback").innerHTML = "❌ Try again!";
                document.getElementById("feedback").style.color = "#f44336";
            }}
        }}

        document.getElementById("dropzone").addEventListener("dragover", allowDrop);
        document.getElementById("dropzone").addEventListener("drop", drop);
        document.getElementById("drag1").addEventListener("dragstart", drag);
        document.getElementById("drag2").addEventListener("dragstart", drag);
    </script>
    """
    st.components.v1.html(html_code, height=250)

# --- Load Worksheets ---
def load_worksheet(category, subcategory, worksheet):
    """Load questions from JSON files"""
    try:
        filepath = os.path.join(
            WORKSHEET_FOLDER,
            category,
            subcategory,
            f"{worksheet.replace(' ', '_')}.json"
        )
        
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                questions = json.load(f)
                # Initialize NSM tracking
                for q in questions:
                    if "nsm_attempts" not in q:
                        q.update({
                            "nsm_attempts": 0,
                            "last_attempt": None,
                            "next_review": None
                        })
                return questions
        return []
    except Exception as e:
        st.error(f"Error loading worksheet: {str(e)}")
        return []

# --- Main App ---
st.set_page_config(page_title="NSM Learning", layout="wide")
st.title("🧠 Neuro-Spaced Mastery Learning")

# --- Sidebar ---
with st.sidebar:
    st.header("👤 Student Profile")
    student = st.selectbox("Select Student:", STUDENT_LIST)
    
    if student != "Select Student":
        st.subheader("📚 Subjects")
        category = st.selectbox("Category:", ["Mathematics", "English"])
        
        if category:
            subcategories = {
                "Mathematics": ["Arithmetic", "Geometry"],
                "English": ["Grammar", "Reading"]
            }
            subcategory = st.selectbox("Subcategory:", subcategories[category])
            
            if subcategory:
                worksheets = {
                    "Arithmetic": ["Addition", "Subtraction"],
                    "Grammar": ["Pronouns", "Verbs"]
                }.get(subcategory, [])
                worksheet = st.selectbox("Worksheet:", worksheets)
                
                if st.button("📂 Load Worksheet"):
                    questions = load_worksheet(category, subcategory, worksheet)
                    if questions:
                        st.session_state.student_data.update({
                            "current_worksheet": questions,
                            "current_question": 0,
                            "answers": [],
                            "game_unlocked": False
                        })
                        st.success(f"Loaded {worksheet}!")
                    else:
                        st.warning("Worksheet not found")

# --- Main Content ---
if student == "Select Student":
    st.info("👈 Select a student to begin")
else:
    data = st.session_state.student_data
    
    if data["current_worksheet"] and len(data["current_worksheet"]) > 0:
        q_idx = data["current_question"]
        questions = data["current_worksheet"]
        
        if q_idx < len(questions):
            q = questions[q_idx]
            
            # Check if question is due for review
            review_due = (not q["next_review"] or 
                         datetime.now() >= datetime.strptime(q["next_review"], "%Y-%m-%d"))
            
            if review_due:
                st.subheader(f"Question {q_idx + 1} of {len(questions)}")
                st.write(f"**{q['question']}**")
                
                # Answer input
                if "options" in q:
                    user_answer = st.radio("Options:", q["options"], key=f"opt_{q_idx}")
                else:
                    user_answer = st.text_input("Your answer:", key=f"txt_{q_idx}")
                
                # Game Changer Button
                if st.button("🎮 Play Mini-Game", key=f"game_{q_idx}"):
                    data["game_unlocked"] = True
                
                if data["game_unlocked"]:
                    launch_minigame(q)
                
                # Submit logic
                if st.button("✅ Submit Answer"):
                    is_correct = str(user_answer).strip().lower() == str(q["answer"]).lower()
                    
                    # Update NSM tracking
                    q["nsm_attempts"] += 1
                    q["last_attempt"] = datetime.now().strftime("%Y-%m-%d")
                    
                    if q["nsm_attempts"] < len(NSM_INTERVALS):
                        next_review = datetime.now() + timedelta(days=NSM_INTERVALS[q["nsm_attempts"]])
                        q["next_review"] = next_review.strftime("%Y-%m-%d")
                    
                    # Store results
                    data["answers"].append({
                        "question": q["question"],
                        "user_answer": user_answer,
                        "correct_answer": q["answer"],
                        "is_correct": is_correct,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    
                    if is_correct:
                        st.success("Correct! 🎉")
                        data["total_xp"] += GAME_XP.get(q["difficulty"], 10)
                    else:
                        st.error(f"Oops! Correct answer: {q['answer']}")
                    
                    if "explanation" in q:
                        st.info(f"💡 Explanation: {q['explanation']}")
                    
                    data["current_question"] += 1
                    data["game_unlocked"] = False
                    st.experimental_rerun()
            else:
                st.info(f"🔁 This question will unlock on {q['next_review']}")
                data["current_question"] += 1
                st.experimental_rerun()
        else:
            # Show results
            st.balloons()
            st.success(f"Worksheet complete! Total XP: {data['total_xp']}")
            
            # Display performance
            st.subheader("📊 Your Performance")
            if data["answers"]:
                df = pd.DataFrame(data["answers"])
                st.dataframe(df)
                
                # Calculate accuracy
                accuracy = sum(df["is_correct"]) / len(df)
                st.metric("Accuracy", f"{accuracy:.0%}")
            
            # Reset for new worksheet
            if st.button("🔄 Start New Worksheet"):
                data.update({
                    "current_question": 0,
                    "answers": [],
                    "game_unlocked": False
                })
                st.experimental_rerun()
    else:
        st.info("👉 Load a worksheet from the sidebar")

# --- Teacher Tools ---
with st.expander("🧑‍🏫 Teacher Dashboard"):
    st.subheader("Class Analytics")
    
    if student != "Select Student" and "answers" in data and len(data["answers"]) > 0:
        # Problem areas
        incorrect = [ans for ans in data["answers"] if not ans["is_correct"]]
        if incorrect:
            st.write("**🚩 Common Struggle Questions:**")
            for item in incorrect[:3]:  # Show top 3
                st.write(f"- {item['question']} (Missed by {student})")
        
        # Export data
        st.download_button(
            label="📥 Export Student Data",
            data=pd.DataFrame(data["answers"]).to_csv(index=False),
            file_name=f"nsm_progress_{student}.csv"
        )
    else:
        st.info("No student data available yet")

# --- Footer ---
st.markdown("---")
st.caption("🚀 Powered by Neuro-Spaced Mastery Learning v1.0")