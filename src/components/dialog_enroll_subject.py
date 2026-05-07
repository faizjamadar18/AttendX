import streamlit as st 
from src.database.db import create_subject
from src.database.config import supabase
from src.database.db import enroll_student_to_subject
import time

# Flow :
# 1> input(subject code from user) 
# 2> finding subject_id using above subject code from subjects table 
# 3> check whether the login user have already enrolled in the subject or not 
# 4> if not then enroll him/her 

@st.dialog("Enroll in Subject")
def enroll_subject_dialog():
    st.write('Enter the subject code provided by your teacher to enroll')
    join_code = st.text_input("Subject Code", placeholder='Eg. CS101')

    if st.button("Enroll now", type='primary', width='stretch'):
        if join_code:
            res = supabase.table("subjects").select("subject_id", "name", "subject_code").eq("subject_code", join_code).execute()
            if res.data:
                subject = res.data[0]
                subject_id = subject["subject_id"]
                student_id = st.session_state.student_data['student_id']

                check = supabase.table("subject_students").select("*").eq("subject_id", subject_id).eq("student_id", student_id).execute()
                if check.data: 
                    st.warning('You are already enrolled in this program')
                else:
                    enroll_student_to_subject(student_id, subject_id)
                    st.success("Successfully Enrolled")
                    time.sleep(1)
                    st.rerun()
        else:
            st.warning('Please enter a subject code')
