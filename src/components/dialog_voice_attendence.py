import streamlit as st 
from PIL import Image
from src.database.config import supabase
from datetime import datetime
from src.pipelines.voice_pipeline import process_bulk_audio
import pandas as pd 
from src.components.dialog_attendence_record import show_attendence_result

@st.dialog("Voice Attendance")
def voice_attendence_dialog(selected_subject_id):
    st.write('Record audio of students saying I am present. Then AI will recognize the students')

    audio_data = None 
    audio_data = st.audio_input("Record classroom audio")

    if st.button("Analyze Audio", width='stretch',type='primary'):
        if not audio_data:
            st.warning("Please record audio first")
            return
        
        with st.spinner("Processing audio data"):
            enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No student enrolled in this subject")
                return 
            
            candidates_dict = {}
            
            for s in enrolled_students:
                student = s['students']
                
                if student.get('voice_embedding'):
                    student_id = student['student_id']
                    voice_embedding = student['voice_embedding']
                    
                    candidates_dict[student_id] = voice_embedding

            if not candidates_dict:
                st.error('No enrolled students have voice profiles registerd')
                return
            
            audio_byte = audio_data.read()
            detected_scores = process_bulk_audio(audio_byte, candidates_dict)


            # same code as that of the photo wala 
            results, attendence_to_log = [], []

            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") 
            # "2026-05-04T18:45:30" Why "T" is used? This is ISO 8601 format

            for node in enrolled_students:
                student = node["students"]
                voice_score = detected_scores.get(student["student_id"], 0.0)
                is_present = bool(voice_score > 0)

                results.append({
                    "Name" : student["name"],
                    "ID" : student["student_id"],
                    "Score": f"{voice_score:.2f}" if is_present else "-",
                    "Status": "✅ Present" if is_present else "❌ Absent"
                }) 

                attendence_to_log.append({
                    "student_id" : student["student_id"],
                    "subject_id" : selected_subject_id,
                    "timestamp" : current_timestamp,
                    "is_present" : bool(is_present)
                })
            
            st.session_state.voice_attendance_result = (pd.DataFrame(results), attendence_to_log)


    if st.session_state.get("voice_attendance_result"):
        st.divider()
        df, logs = st.session_state.voice_attendance_result
        show_attendence_result(df, logs) 

