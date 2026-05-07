import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st 
from src.database.db import get_all_students

@st.cache_resource # This function is expensive to run, so we cache its result and reuse it instead of running it again
def load_dlib_models():
    # for detecting all the Faces from the group image 
    detetctor = dlib.get_frontal_face_detector()


    # Take a face → return 68 landmark points
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()  # Path of the trained model from face_recognition_models
    )

    # Convert a face → into a 128-dimensional vector (embedding)
    face_recog = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detetctor, sp, face_recog

def get_face_embeddings(group_img_np):
    detector, sp, face_recog = load_dlib_models()

    faces = detector(group_img_np, 1) #1 = image upscaling for better face detection,
    # faces = [face1, face2]

    embeddings = []

    for face in faces:
        landmarks  = sp(group_img_np, face)  # 68 landmarks 

        face_descriptor  = face_recog.compute_face_descriptor(group_img_np, landmarks, 1)  # 1 = number of times the face is reprocessed for more accurate embedding.

        embeddings.append(np.array(face_descriptor))
    
    return embeddings

st.cache_resource
def get_trained_model():

    X = []   # student embedding 
    y = []   # student Corresponding IDs

    students = get_all_students()

    if not students : 
        return None 
    
    for student in students:
        embedding = student.get('face_embedding')
        if embedding :
            X.append(np.array(embedding))
            y.append(student.get('student_id'))

    if len(X) == 0:
        return 0
        
    clf = SVC(
        kernel='linear',        # Use a linear decision boundary (best for face embeddings which are already well-separated)
        probability=True,       # Enable probability estimates (allows use of predict_proba for confidence scores)
        class_weight='balanced' # Automatically adjust weights to handle class imbalance (fewer samples get higher importance)
    )

    try:
        clf.fit(X,y)
    except ValueError:
        pass

    return {'clf':clf, 'X':X , 'y':y}

def train_classifier():
    st.cache_resource.clear()
    model = get_trained_model()
    return bool(model)  # If we get the model it will return true else it will return false

def predict_attendance(class_image_np):
    embeddings = get_face_embeddings(class_image_np)

    detected_student = {}

    model = get_trained_model()
    if not model:
        return detected_student, [], len(embeddings)
    

    clf = model['clf']
    X_train = model['X']
    y_train = model['y']

    all_students = sorted(list(set(y_train)))
    # remove the all duplicated faces 

    for embedding in embeddings:
        if(len(all_students) >= 2):
            predicted_id = int(clf.predict([embedding])[0])
        else :
            predicted_id = int(all_students[0])

        predicted_student_embeddings = X_train[y_train.index(predicted_id)]

        thresold = 0.6 
        best_match_score = np.linalg.norm(predicted_student_embeddings - embedding)
        

        if best_match_score <= thresold:
            detected_student[predicted_id] = True

    return detected_student, all_students, len(embeddings)
    # (
    #   {101: True, 102: True},   # detected students
    #   [101, 102, 103, 104],     # all students
    #   5                         # total faces detected
    # )

    