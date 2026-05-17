import streamlit as st
from files import logic

with st.container(border=True):
    col1, col2 = st.columns(2)

    with col1:
        st.title("ceKelas.1")
        st.badge("Kredensial Juri, username: dwi ; Password: 12345")
        #login logic
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            if logic.login(username, password):
                st.switch_page("pages/app.py")  
            else:
                st.error("Username atau password salah!")

        # #register logic masih tahap pengembangan
        # usernameReg = st.text_input("Username", key="userReg")
        # passwordReg = st.text_input("Password", key=userPassReg)

        # if st.button("Register", use_container_width=True):
        #     logic.init_db()
        #     logic.register(usernameReg, passwordReg)

    with col2:
        st.image("images/ruriSinaga.jpeg")