import streamlit as st 
from src.database.db import create_subject

@st.dialog("Enter Subject Details")
def create_subject_dialog(teacher_id):
    subject_code = st.text_input("Enter Subject Code", placeholder='CS101')
    subject_name = st.text_input("Enter Subject Name", placeholder='Introduction to Computer Science')
    subject_section = st.text_input("Enter Subject Section", placeholder='A')


    if st.button("Create Subject Now", type='primary', width='stretch'):
        if subject_code and subject_name and subject_section:
            try:
                create_subject(subject_code, subject_name, subject_section, teacher_id)
                st.toast("Subject Created Successfully!")
                st.rerun()
            except Exception as e :
                st.error(f"Error: {str(e)}")
        else :
            st.warning("Please fill all the fields")