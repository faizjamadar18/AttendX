import streamlit as st 
from src.ui.base_layout import style_base_layout,style_background_dashboard
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
import numpy as np
from PIL import Image
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embeddings
from src.database.db import get_all_students, create_student, get_student_attendence, get_student_subjects, unenroll_student_to_subject
from src.components.dialog_enroll_subject import enroll_subject_dialog
from src.components.subject_card import subject_card
import time

def student_dashboard():
    student_data = st.session_state.student_data 

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f""" Welcome {student_data['name']}""", text_alignment='right')
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace", width='stretch'):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()


    st.divider()

    col1, col2 = st.columns(2)
    with col1: 
        st.header("Your Subjects")
    with col2: 
        if st.button("Enroll in subject", width='stretch', type='primary'):
            enroll_subject_dialog()

   

    student_id = student_data['student_id']
    with st.spinner("Loading your subjects..."):
        subjects = get_student_subjects(student_id)
        attendence_logs = get_student_attendence(student_id)

        stats_maps = {}
        for log in attendence_logs: 
            sub_id = log["subject_id"]

            if sub_id not in stats_maps:
                stats_maps[sub_id] = {"total" : 0, "attended" : 0}
            
            stats_maps[sub_id]["total"] += 1 

            if log.get('is_present'):
                stats_maps[sub_id]["attended"] += 1

        for i, sub in enumerate(subjects): 
            sub_node = sub["subjects"]
            sub_id = sub_node['subject_id']

            stats = stats_maps.get(sub_id, {"total" : 0, "attended" : 0})  # if not get then total=0 and attended=0

            def unenroll_button():
                if st.button("Unenroll from tihs course", type='tertiary', width='stretch', icon=':material/delete_forever:'):
                    unenroll_student_to_subject(student_id, sub_id)
                    st.toast(f'Unenrolled from {sub_node['name']} successfully!')
                    st.rerun()

            cols = st.columns(2)    
            with cols[i % 2]:
                subject_card(
                    name = sub_node['name'],
                    code =sub_node['subject_code'],
                    section = sub_node['section'],
                    stats = [
                        ('📅', 'Total', stats['total']),
                        ('✅', 'Attended', stats['attended']),
                    ],
                    footer_callback=unenroll_button
                )

    footer_dashboard()

def student_screen():
    style_background_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return 

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace", width='stretch'):
            st.session_state.login_type = None
            st.rerun()

    st.divider()
    st.header("Login using FaceId", text_alignment='center')

    show_registration = False

    photo = st.camera_input("Position our face in center")
    if photo:
        img = np.array(Image.open(photo))

        with st.spinner("AI is Scanning..."):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("Face not found!")
            elif num_faces > 1:
                st.warning("Multiple faces found")
            else:
                if detected:
                    # detected = {"S101": True}
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()

                    student = next((s for s in all_students if s['student_id'] == student_id), None)
                    # (s           for s in all_students   if s['student_id'] == student_id)
                    #  ↑ output        ↑ loop variable         ↑ condition
                    # next() gives the first matching result If nothing found → returns None (instead of error)

                    if student:
                        st.session_state.is_logged_in = True 
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else :
                    st.info("Face not recognized! You might be a new Student")
                    show_registration = True 

    if show_registration : 
        with st.container(border=True):
            st.header("Register new Profile")
            new_name = st.text_input("Enter Your name", placeholder="E.g Akash Kumar")

            st.subheader('Optional : Voice Enrollement')
            st.info("Enroll Yourself for voice only attendence")

            audio_data = None 
            try:
                audio_data = st.audio_input('Record a short Phase like I am present, My name is Akash.')
            except Exception:
                st.error("Audio data Failed")

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile...'):
                        img = np.array(Image.open(photo))
                        embeddings = get_face_embeddings(img)
                        if embeddings:
                            face_emb = embeddings[0].tolist()
                            voice_emb = None 
                            if audio_data:
                                voice_emb = get_voice_embeddings(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data :
                                train_classifier()
                                st.session_state.is_logged_in = True 
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0] 
                                st.toast(f"Profile Created Hii {new_name}")
                                time.sleep(1)
                                st.rerun()

                        else:
                            st.error('Couldnt able to capture your facial features for registeration ')

                else:
                    st.warning("Please enter your name!")



            
        

    footer_dashboard()

