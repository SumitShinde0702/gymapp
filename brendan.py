import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import io

# Define pages for exercises
pages = ["Legs", "Chest", "Back", "Core & Abs", "Data Overview"]

# Sidebar page selector
page = st.sidebar.selectbox("Select Exercise Category", pages)

# Initialize session state for logs, start date, and stopwatch
if "logs" not in st.session_state:
    st.session_state["logs"] = {}
for category in pages[:-1]:  # Exclude Data Overview
    if category not in st.session_state["logs"]:
        st.session_state["logs"][category] = {}

if "start_date" not in st.session_state:
    st.session_state["start_date"] = datetime.now().date()
if "stopwatch" not in st.session_state:
    st.session_state["stopwatch"] = {"start_time": None, "elapsed_time": timedelta(0)}
if "current_day" not in st.session_state:
    st.session_state["current_day"] = {"week": 1, "day": 1, "date": datetime.now().date()}

# Function to get the current week number and day count based on the start date
def get_week_and_day():
    today = datetime.now().date()
    start_date = st.session_state["start_date"]

    # Calculate the week number (1-indexed)
    week_number = st.session_state["current_day"]["week"]

    # Check if it's a new day
    if today != st.session_state["current_day"]["date"]:
        # Check if day has reached 7; if so, start a new week
        if st.session_state["current_day"]["day"] == 7:
            st.session_state["current_day"]["week"] += 1
            st.session_state["current_day"]["day"] = 1
        else:
            st.session_state["current_day"]["day"] += 1
        # Update the date to today's date
        st.session_state["current_day"]["date"] = today

    # Ensure the current week's logs exist in the selected category
    if week_number not in st.session_state.logs[page]:
        st.session_state.logs[page][week_number] = {}

    return st.session_state["current_day"]["week"], st.session_state["current_day"]["day"]

# Stopwatch functions
def start_stopwatch():
    if st.session_state.stopwatch["start_time"] is None:
        st.session_state.stopwatch["start_time"] = datetime.now()

def stop_stopwatch():
    if st.session_state.stopwatch["start_time"]:
        st.session_state.stopwatch["elapsed_time"] += datetime.now() - st.session_state.stopwatch["start_time"]
        st.session_state.stopwatch["start_time"] = None

def reset_stopwatch():
    st.session_state.stopwatch["start_time"] = None
    st.session_state.stopwatch["elapsed_time"] = timedelta(0)

def display_stopwatch():
    elapsed = st.session_state.stopwatch["elapsed_time"]
    if st.session_state.stopwatch["start_time"]:
        elapsed += datetime.now() - st.session_state.stopwatch["start_time"]
    # Display the timer with a larger font
    st.markdown(f"<h1 style='text-align: center; font-size: 48px;'>{str(elapsed).split('.')[0]}</h1>", unsafe_allow_html=True)

# Exercise logging function
def log_exercise():
    week_number, day_number = get_week_and_day()

    # Log the exercise details
    exercise = st.text_input("Exercise Name")
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.5)
    sets = st.number_input("Sets", min_value=1, step=1)
    reps = st.number_input("Reps per Set", min_value=1, step=1)
    exercise_type = st.text_input("Type (e.g., cable, plate)")

    if st.button("Add Exercise"):
        if exercise:
            if day_number not in st.session_state.logs[page][week_number]:
                st.session_state.logs[page][week_number][day_number] = []

            # Log the exercise under the specific week and day
            st.session_state.logs[page][week_number][day_number].append({
                "Exercise": exercise,
                "Weight (kg)": weight,
                "Sets": sets,
                "Reps": reps,
                "Type": exercise_type,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"Exercise logged successfully for Week {week_number} - Day {day_number}")
        else:
            st.error("Please enter an exercise name.")

# Button to manually start a new day
if st.button("Start a New Day"):
    if st.session_state["current_day"]["day"] == 7:
        st.session_state["current_day"]["week"] += 1
        st.session_state["current_day"]["day"] = 1
    else:
        st.session_state["current_day"]["day"] += 1
    st.session_state["current_day"]["date"] = datetime.now().date()
    st.success(f"Started a new day for {page} in Week {st.session_state['current_day']['week']} - Day {st.session_state['current_day']['day']}")

# Display exercise logs
def display_logs():
    st.write("### Exercise Log")
    week_logs = st.session_state.logs.get(page, {})
    
    if week_logs:
        for week, days in sorted(week_logs.items()):
            st.write(f"## Week {week}")
            for day, exercises in sorted(days.items()):
                st.write(f"### Day {day}")
                st.table(exercises)
    else:
        st.write("No logs yet.")

# Page content for Exercise Logging
if page != "Data Overview":
    st.title(f"{page} Workout")

    # Stopwatch controls
    st.write("### Stopwatch")
    if st.button("Start Stopwatch"):
        start_stopwatch()
    if st.button("Stop Stopwatch"):
        stop_stopwatch()
    if st.button("Reset Stopwatch"):
        reset_stopwatch()
    display_stopwatch()

    # Exercise logging
    st.write("### Log Exercise")
    log_exercise()

    # Display logs
    display_logs()

# Data Overview Page
if page == "Data Overview":
    st.title("Data Overview")

    # Display overall data logs
    all_logs = st.session_state.logs
    all_data = []

    for category, weeks in all_logs.items():
        for week, days in weeks.items():
            for day, exercises in days.items():
                for exercise in exercises:
                    all_data.append(exercise)

    df_logs = pd.DataFrame(all_data)

    # Show a preview of the data
    st.write("### Exercise Data Overview")
    st.dataframe(df_logs)

    def download_excel(df):
        # Create an in-memory buffer to write the Excel file to
        output = io.BytesIO()

        # Use pandas to write to the in-memory buffer
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        
        # Seek to the beginning of the buffer so it can be read
        output.seek(0)
        
        return output

    # Download button
    st.download_button(
        label="Download Exercise Logs as Excel",
        data=download_excel(df_logs),
        file_name="exercise_logs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
