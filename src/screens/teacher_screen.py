import streamlit as st 
from src.ui.base_layout import style_base_layout,style_background_dashboard
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.database.db import check_unique_username, create_teacher, login_teacher, get_teacher_subjects, get_attendence_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.subject_card import subject_card
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photo_dialog
from src.pipelines.face_pipeline import predict_attendance
from src.database.config import supabase
from src.components.dialog_attendence_record import attendence_result_dialog
from src.components.dialog_voice_attendence import voice_attendence_dialog
import numpy as np
from datetime import datetime
import pandas as pd 

def teacher_screen():
    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data 

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f""" Welcome {teacher_data['name']}""", text_alignment='right')
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace", width='stretch'):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()
    st.space()

    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendence'

    tab1, tab2, tab3 = st.columns(3) 
    with tab1 : 
        type1 = 'primary' if st.session_state.current_teacher_tab == 'take_attendence' else 'tertiary' 
        if st.button("Take Attendence", type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendence'
            st.rerun()

    with tab2 :
        type2 = 'primary' if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary'
        if st.button("Manage Subject", type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3 :
        type3 = 'primary' if st.session_state.current_teacher_tab == 'attendence_records' else 'tertiary'
        if st.button("Attendence Records", type=type3, width='stretch', icon=':material/cards_stack:'): 
            st.session_state.current_teacher_tab = 'attendence_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == 'take_attendence':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'attendence_records':
        teacher_tab_attendence_record()

    footer_dashboard()



def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header("Subjects : ")
    with col2:
        if st.button("Create New Subject", width='stretch'):
            create_subject_dialog(teacher_id)
     
    #  List All teachers subjects:
    subjects = get_teacher_subjects(teacher_id)
    if subjects: 
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes'])
            ]

            def share_btn():
                if st.button(f"Share Code: {sub["name"]}", key=f"share_{sub["subject_code"]}", icon=":material/share:"):
                    share_subject_dialog(sub["name"], sub["subject_code"])
                st.space()

            subject_card(
                name = sub["name"],
                code = sub["subject_code"],
                section = sub["section"],
                stats = stats,
                footer_callback = share_btn
            )
    else: 
        st.info("No Subject Found, Create one above")


def teacher_tab_take_attendance():
    
    st.header("Take AI Attendence")

    if 'attendence_images' not in st.session_state:
        st.session_state.attendence_images = []
        
    teacher_id = st.session_state.teacher_data["teacher_id"]
    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}" : s['subject_id'] for s in subjects}
    # subject_options = {
    #     "Maths - M101": 1,
    #     "Physics - P102": 2,
    #     "Chemistry - C103": 3
    # }

    col1, col2 = st.columns([3,1], vertical_alignment='bottom')

    with col1: 
        selected_subject_label = st.selectbox("Select Subject", options=list(subject_options.keys()))

    with col2:
        if st.button("Add photos", type="primary", width='stretch', icon=":material/photo_prints:"):
            add_photo_dialog()

    selected_subject_id = subject_options[selected_subject_label]
    st.divider()

    if st.session_state.attendence_images: 
        st.header("Add Photos")
        gallary_cols = st.columns(4)

        for i,img in enumerate(st.session_state.attendence_images): 
            with gallary_cols[i % 4]:
                st.image(img, width='stretch', caption=f'Photo {i+1}') 


    has_photos = bool(st.session_state.attendence_images) # for disabling buttons
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("Clear All Photos", type='tertiary',width='stretch', icon=":material/delete:", disabled=not has_photos):
            st.session_state.attendence_images = []
            st.rerun()
    with c2: 
        if st.button("Run Face Analytics", type='secondary',width='stretch', icon=":material/analytics:", disabled=not has_photos):
            all_detected_ids = {}
            for i, img in enumerate(st.session_state.attendence_images):
                img_np = np.array(img.convert("RGB"))
                detected_student_id, _, _  = predict_attendance(img_np)

                if detected_student_id: 
                    for st_id in detected_student_id.keys(): 
                        student_id = int(st_id)
                        
                        if student_id not in all_detected_ids:
                            all_detected_ids[student_id] = []

                        all_detected_ids[student_id].append(f"Photo {i+1}")

            # all_detected_ids = {
            #     101: ["Photo 1", "Photo 2"],
            #     102: ["Photo 1"]
            # }
                
            enrolled_res = supabase.table("subject_students").select("*, students(*)").eq("subject_id", selected_subject_id).execute()
            # enrolled_res = [
            #     {
            #         "id": 1,
            #         "student_id": 101,
            #         "subject_id": 10,

            #         "students": {
            #             "student_id": 101,
            #             "name": "Faiz",
            #             "roll_no": "A1"
            #         }
            #     },
            #}
            
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No Student Enrolled in these subject")
            else: 
                results, attendence_to_log = [], []

                current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S") 
                # "2026-05-04T18:45:30" Why "T" is used? This is ISO 8601 format

                for node in enrolled_students:
                    student = node["students"]
                    photo_sources = all_detected_ids.get(int(student["student_id"]),[])
                    is_present = len(photo_sources) > 0

                    results.append({
                        "Name" : student["name"],
                        "ID" : student["student_id"],
                        "Source" : ", ".join(photo_sources) if is_present else "-",
                        "Status": "✅ Present" if is_present else "❌ Absent"
                    }) 

                    attendence_to_log.append({
                        "student_id" : student["student_id"],
                        "subject_id" : selected_subject_id,
                        "timestamp" : current_timestamp,
                        "is_present" : bool(is_present)
                    })

            
            attendence_result_dialog(pd.DataFrame(results), attendence_to_log)

    with c3: 
        if st.button("Voice attendence", type='primary', width='stretch', icon=":material/mic:"):
            voice_attendence_dialog(selected_subject_id)


def teacher_tab_attendence_record():
    st.header("Attendance Record")

    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendence_for_teacher(teacher_id)

    if not records: 
        return 
    
    data = []
    for r in records: 
        timestamp = r.get("timestamp")
        data.append({
            "timestamp_grp" : timestamp.split(".")[0] if timestamp else None, 
            "Time" : datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %I:%M %p") if timestamp else "N/A",
            "Subject" : r["subjects"]["name"],
            "Subject Code" : r["subjects"]["subject_code"],
            "is_present" :bool(r.get("is_present", False))
        })
    # data = [
    #     {
    #         "timestamp_grp": "2026-05-06T10:30:25",
    #         "Time": "2026-05-06 10:30 AM",
    #         "Subject": "DBMS",
    #         "Subject code": "CS301",
    #         "is_present": True
    #     },
    # ]

    df = pd.DataFrame(data)


    # Before groupby():
    # | timestamp_grp         | Time     | Subject | Subject Code | is_present |
    # | ---------------- | -------- | ------- | ------------ | ---------- |
    # | 2026-05-06T10:30 | 10:30 AM | DBMS    | CS301        | True       |
    # | 2026-05-06T10:30 | 10:30 AM | DBMS    | CS301        | False      |
    # | 2026-05-06T10:30 | 10:30 AM | DBMS    | CS301        | True       |
    # | 2026-05-06T12:00 | 12:00 PM | CN      | CS302        | True       |
    # | 2026-05-06T12:00 | 12:00 PM | CN      | CS302        | True       |

    summary = (
        df.groupby(["timestamp_grp", "Time", "Subject", "Subject Code"]).agg(
            Present_count = ("is_present", "sum"),
            Total_count = ("is_present", "count")
        ).reset_index()
    )

    # After groupby():
    # | ts_group         | Time     | Subject | Subject Code | Present_Count | Total_Count |
    # | ---------------- | -------- | ------- | ------------ | ------------- | ----------- |
    # | 2026-05-06T10:30 | 10:30 AM | DBMS    | CS301        | 2             | 3           |
    # | 2026-05-06T12:00 | 12:00 PM | CN      | CS302        | 2             | 2           |

    summary["Attendance Stats"] =( "✅" + summary["Present_count"].astype(str) + "/" + summary["Total_count"].astype(str) + " Students")

    display_df = (summary.sort_values(by="timestamp_grp", ascending=False)[["Time", "Subject", "Subject Code", "Attendance Stats"]])

    st.dataframe(display_df, width='stretch', hide_index=True)

def register_teacher(username, name, psw, conf_psw):
    if not username or not name or not psw : 
        return False, "All fields are required"
    if check_unique_username(username):
        return False, "username already exist"
    if psw != conf_psw : 
        return False, "Password does not match"
    
    try : 
        create_teacher(username, psw, name)
        return True, "Successfully registered !! Login Now"
    except Exception as e :
        return False, "Uexpected Error"



def teacher_login(teacher_username, teacher_pass):
    if not teacher_username or not teacher_pass:
        return False
    
    teacher = login_teacher(teacher_username, teacher_pass)
    if teacher: 
        st.session_state.teacher_data = teacher
        st.session_state.user_role = teacher
        st.session_state.is_logged_in = True 
        return True
    
    return False

def teacher_screen_login():
    style_background_dashboard()
    style_base_layout()

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace", width='stretch'):
            st.session_state["login_type"] = None
            st.rerun()
    st.space()
    st.space()

    st.markdown(
        "<h2 style='text-align: center; color: #FFFFFF;'>Login Using Password</h2>",
        unsafe_allow_html=True
    )


    teacher_username = st.text_input("Enter username", placeholder="@abhishek")
    teacher_pass = st.text_input("Enter password", placeholder="Enter password", type="password")

    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1: 
        if st.button("Login", type="secondary",icon=':material/passkey:', width="stretch"):
            if teacher_login(teacher_username, teacher_pass):
                st.toast("Welcome Back", icon="👋")
                import time 
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid Username or password")
    with btnc2: 
        if st.button("Register instead", type="primary", width="stretch", icon=':material/passkey:'):
            st.session_state.teacher_login_type = "register"
            st.rerun()


def teacher_screen_register():
    style_background_dashboard()
    style_base_layout()

    c1, c2 = st.columns(2, vertical_alignment='center', gap='large')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to home", type='secondary', key='loginbackbtn', shortcut="control+backspace", width='stretch'):
            st.session_state.login_type = None
            st.rerun()
    st.space()
    st.space()
    st.header("Register your profile", text_alignment='center')



    teacher_username = st.text_input("Enter username", placeholder="@abhishek")
    teacher_name = st.text_input("Enter name", placeholder="Abhishek Roy")
    teacher_pass = st.text_input("Enter password", placeholder="Enter password", type="password")
    teacher_pass_confirm = st.text_input("Conform password", placeholder="Confirm password", type="password")

    st.divider()

    btnc1, btnc2 = st.columns(2)
    with btnc1: 
        if st.button("Register now", type="secondary",icon=':material/passkey:', width="stretch"):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success: 
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else: 
                st.error(message)
        
    with btnc2: 
        if st.button("Login instead", type="primary", width="stretch", icon=':material/passkey:'):
            st.session_state.teacher_login_type= "login"
            st.rerun()