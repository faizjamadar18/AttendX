import streamlit as st 
from PIL import Image

@st.dialog("Capture or Upload Photo")
def add_photo_dialog():

    st.write("Add classrooms photos to scan for attendence")

    if "photo_tab" not in st.session_state: 
        st.session_state.photo_tab = "camera"
    
    tab1, tab2 = st.columns(2)

    with tab1: 
        type_camera = "primary" if st.session_state.photo_tab == "camera" else "tertiary"
        if st.button("Camera", type=type_camera, width='stretch'):
            st.session_state.photo_tab = "camera"

    with tab2: 
        type_upload = "primary" if st.session_state.photo_tab == "upload" else "tertiary"
        if st.button("Upload", type=type_upload, width='stretch'):
            st.session_state.photo_tab = "upload"

    if st.session_state.photo_tab == "camera": 
        cam_photo = st.camera_input("Take Snapshot", key="camera_dialog")
        if cam_photo: 
            st.session_state.attendence_images.append(Image.open(cam_photo))
            st.toast("Photo Captured")
            st.rerun()

    if st.session_state.photo_tab == "upload": 
        uploaded_files = st.file_uploader("choose image files", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
        if uploaded_files: 
            for file in uploaded_files:
                st.session_state.attendence_images.append(Image.open(file))
            st.toast("Photos Uploaded Successfully")
            st.rerun()

    st.divider()
    if st.button('Done', type="primary", width="stretch"): 
        st.rerun()

    


    