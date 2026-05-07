import streamlit as st 
import base64

def get_base64(img_path):
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return data

img = get_base64("src/assets/logo2.png")

def header_home():
    
    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:30px;margin-top:-30px;">
            <img src='data:image/png;base64,{img}'  style="height:180px">
            <h1 style='text-align:center; color:#FFFFFF ; margin-top:-25px; margin-right:-15px'>AttendX</h1>
        </div>   
                
                """, unsafe_allow_html=True)
    
def header_dashboard():

    
    st.markdown(f"""
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            <img src='data:image/png;base64,{img}'  style="height:120px">
            <h2 style='display:flex; justify-content:center; color:#FFFFFF'>AttendX
        </div>   
                
                """, unsafe_allow_html=True)