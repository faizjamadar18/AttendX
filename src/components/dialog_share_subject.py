import streamlit as st 
import segno
import io


@st.dialog("Scan class link")
def share_subject_dialog(subject_name, subject_code):
    
    # Generating QR code
    app_domain = "attendx.streamlit.app"
    join_url = f"{app_domain}/?join-code={subject_code}"
    qr = segno.make(join_url)
    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)


    st.header("Scan to Join")
    col1, col2 = st.columns(2)

    with col1: 
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info("Copy this link to share on Whatsapp or Email")    

    with col2:
        st.markdown('### Scan to Join')
        st.image(out.getvalue(), caption="QRCode for class joining")    