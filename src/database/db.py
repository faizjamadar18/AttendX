from src.database.config import supabase
import bcrypt

def hash_pass(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_pass(password, hased_password):
    return bcrypt.checkpw(password.encode(), hased_password.encode())

def check_unique_username(username):
    response = supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0

def create_teacher(usename, password, name):
    data = {
        "username" : usename,
        "password" : hash_pass(password),
        "name" : name
    }  
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def login_teacher(username, password):
    response = supabase.table("teachers").select("*").eq("username", username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password ,teacher['password']):
            return teacher
    else:
        return None
    
def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

def create_student(new_name, face_embedding=None, voice_embedding=None):
    data = {'name': new_name, 'face_embedding':face_embedding, "voice_embedding": voice_embedding}
    response = supabase.table('students').insert(data).execute()
    return response.data

def create_subject(subject_code, subject_name, subject_section, teacher_id):
    data = {"subject_code" : subject_code, "name" : subject_name, "section" : subject_section, "teacher_id" : teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data 

def get_teacher_subjects(teacher_id):
    response =  supabase.table("subjects").select("*, subject_students(count), attendence_log(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data
    
    # get() is a dictionary method 
    # dictionary.get(key, default_value)
    # key → what you want to find 
    # default_value → what to return if key is NOT present to prevent further error
    for sub in subjects:
        sub["total_students"] = sub.get("subject_students", [{}])[0].get("count",0) if sub.get("subject_students") else 0

        attendence = sub.get("attendence_log", [])
        unique_sessions = len(set(log['timestamp'] for log in attendence))
        sub["total_classes"] = unique_sessions

def get_teacher_subjects(teacher_id):
    # Fetch subjects for given teacher_id
    # Also fetch:
    # - number of students in each subject (subject_students)
    # - attendance timestamps (attendence_logs)
    response = supabase.table('subjects') \
        .select("*, subject_students(count), attendence_logs(timestamp)") \
        .eq("teacher_id", teacher_id) \
        .execute()

    # Extract actual data from response
    subjects = response.data

    # Loop through each subject
    for sub in subjects:

        # Get total number of students safely
        # - subject_students returns a list like [{"count": X}]
        # - if missing → return 0 (safe handling)
        sub['total_students'] = (
            sub.get("subject_students", [{}])[0].get('count', 0)
            if sub.get('subject_students') else 0
        )

        # Get attendance logs (list of timestamps)
        # if missing → empty list
        attendance = sub.get('attendence_logs', [])

        # Count unique class sessions
        # - extract timestamps
        # - convert to set (removes duplicates)
        # - count unique valuesv 
        unique_sessions = len(set(log['timestamp'] for log in attendance))

        # Store total number of classes conducted
        sub['total_classes'] = unique_sessions

        # Remove unnecessary raw data to clean final output
        sub.pop('subject_students', None)   # safe remove (no error if key missing)
        sub.pop('attendence_logs', None)
        # sub = {
        # "id": 1,
        # "subject_name": "Math",
        # "teacher_id": 101,
        # "total_students": 3,
        # "total_classes": 2
        # }
    # Return cleaned and processed data
    return subjects

def enroll_student_to_subject(student_id, subject_id):
    data = {"student_id": student_id, "subject_id" : subject_id}
    res = supabase.table("subject_students").insert(data).execute()
    return res.data

def unenroll_student_to_subject(student_id, subject_id):
    res = supabase.table("subject_students").delete().eq("student_id", student_id).eq("subject_id", subject_id).execute()
    return res.data

def get_student_subjects(student_id):
    res = supabase.table('subject_students').select("*, subjects(*)").eq("student_id", student_id).execute()
    return res.data

def get_student_attendence(student_id):
    res = supabase.table('attendence_logs').select("*, subjects(*)").eq("student_id", student_id).execute()
    return res.data

def create_attendence(logs):
    response = supabase.table("attendence_logs").insert(logs).execute()
    return response.data

def get_attendence_for_teacher(teacher_id):
    response = supabase.table("attendence_logs").select("*, subjects!inner(*)").eq("subjects.teacher_id", teacher_id).execute()
    return response.data

