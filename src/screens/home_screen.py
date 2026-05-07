import streamlit as st 
from src.ui.base_layout import style_background_home, style_base_layout
from src.components.header import header_home
from src.components.footer import footer_home
import base64




def home_screen():

    style_background_home()
    header_home()
    style_base_layout()


    def get_base64(img_path):
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return data

    img1 = get_base64("src/assets/student_logo.png")
    img2 = get_base64("src/assets/teacher_logo.png")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.header("I'm Student")
        st.markdown(f"""
            <div style='text-align:center ; margin-top: -20px'>
                <img src='data:image/png;base64,{img1}' width='140'>
            </div>
        """, unsafe_allow_html=True)

        if st.button('Student Portal', type='tertiary', icon=':material/arrow_outward:', icon_position='right', width='stretch'):
            st.session_state['login_type']='student'
            st.rerun()

    with col2:
        st.header("I'm Teacher")
        # st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQiHTVbfy1g-s8lXUdZy7h9ToPpZC4DaRDp2w&s", width=145)
        st.markdown(f"""
            <div style='text-align:center; margin-top: -20px'>
                <img src='data:image/png;base64,{img2}' width='140'>
            </div>
        """, unsafe_allow_html=True)
        if st.button('Teacher Portal', type='tertiary', icon=':material/arrow_outward:', icon_position='right', width='stretch'):
            st.session_state['login_type']='teacher'
            st.rerun()

    footer_home()
