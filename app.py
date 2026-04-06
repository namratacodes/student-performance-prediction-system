import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from recommendation import recommend
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
import io

# Load model
model = pickle.load(open("model.pkl", "rb"))

# Page Config
st.set_page_config(page_title="Student Performance Predictor", layout="wide")

# Sidebar Theme
theme = st.sidebar.selectbox("Select Theme", ["Light", "Dark"])

# Theme CSS
if theme == "Dark":
    st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: white;
        }

        label, div, p, h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <style>
        .stApp {
            background-color: white;
            color: black;
        }

        label, div, p, h1, h2, h3, h4, h5, h6 {
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Title
st.title("🎓 AI Student Performance Prediction Dashboard")

# Sidebar Student Profile
st.sidebar.header("Student Profile")

name = st.sidebar.text_input("Student Name")
roll = st.sidebar.text_input("Roll Number")
department = st.sidebar.text_input("Department")

# Dynamic card colors
card_bg = "#f0f2f6" if theme == "Light" else "#1e1e1e"
text_color = "black" if theme == "Light" else "white"

# Student Card
st.markdown(f"""
<div style="padding:15px;border-radius:10px;background-color:{card_bg};color:{text_color};">
<h3>Student Profile Card</h3>
<p><b>Name:</b> {name}</p>
<p><b>Roll No:</b> {roll}</p>
<p><b>Department:</b> {department}</p>
</div>
""", unsafe_allow_html=True)

# Input Section
st.header("Enter Academic Details")

col1, col2 = st.columns(2)

with col1:
    attendance = st.number_input("Attendance (%)", 0, 100)
    study_hours = st.number_input("Study Hours per Day", 0, 12)
    previous_marks = st.number_input("Previous Marks", 0, 100)
    assignments = st.number_input("Assignments Completed", 0, 10)

with col2:
    test_score = st.number_input("Internal Test Score", 0, 100)
    internet_usage = st.number_input("Internet Usage (hours/day)", 0, 12)
    sleep_hours = st.number_input("Sleep Hours", 0, 12)
    extracurricular = st.number_input("Extracurricular Participation", 0, 10)

# Predict Button
if st.button("Predict Performance"):

    data = np.array([[attendance, study_hours, previous_marks,
                      assignments, test_score, internet_usage,
                      sleep_hours, extracurricular]])

    prediction = model.predict(data)
    confidence = np.max(model.predict_proba(data)) * 100

    st.success(f"Prediction: {prediction[0]}")
    st.info(f"Prediction Confidence: {confidence:.2f}%")

    # Recommendations
    st.subheader("Recommendations")
    tips = recommend(attendance, study_hours, test_score)

    if tips:
        for tip in tips:
            st.warning(tip)
    else:
        st.success("Excellent academic performance")

    # Performance Chart
    st.subheader("Performance Trend")

    values = [attendance, study_hours*10, previous_marks, test_score]
    labels = ["Attendance", "Study Score", "Previous Marks", "Test Score"]

    fig, ax = plt.subplots()
    ax.plot(labels, values, marker='o')
    st.pyplot(fig)

    # Save graph to memory
    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    # Recommendation text
    recommendation_text = ", ".join(tips) if tips else "Excellent academic performance"

    # Create PDF in memory
    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)

    elements = []

    # Table data
    data_table = [
        ["Field", "Value"],
        ["Student Name", name],
        ["Roll Number", roll],
        ["Department", department],
        ["Attendance", attendance],
        ["Study Hours", study_hours],
        ["Previous Marks", previous_marks],
        ["Assignments", assignments],
        ["Test Score", test_score],
        ["Internet Usage", internet_usage],
        ["Sleep Hours", sleep_hours],
        ["Extracurricular", extracurricular],
        ["Prediction", prediction[0]],
        ["Confidence", f"{confidence:.2f}%"],
        ["Recommendations", recommendation_text]
    ]

    table = Table(data_table)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("GRID", (0,0), (-1,-1), 1, colors.black)
    ]))

    elements.append(table)

    # Graph image
    img = Image(img_buffer, width=400, height=250)
    elements.append(img)

    # Build PDF
    doc.build(elements)

    pdf_buffer.seek(0)

    # Download PDF
    st.download_button(
        label="Download PDF Report",
        data=pdf_buffer,
        file_name="student_report.pdf",
        mime="application/pdf"
    )