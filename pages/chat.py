import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image

def run_code(container):
    output = st.session_state.agent.run_code()
    
    with container:
        if isinstance(output, str): 
            st.markdown(output)
        elif output == None:
            image = Image.open('data/plot.png')
            st.image(image)

if 'agent' not in st.session_state:
    st.error("No agent found. Please upload a file on the main page first.")
    st.stop()

st.title("Chat and Edit")

st.session_state['executed'] = False

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = st.session_state.agent.chat(prompt)
        st.markdown(response)

    container = st.container(border=True)
    st.button(label="Execute", on_click=run_code, args=(container, ))
    
    st.session_state.messages.append({"role": "assistant", "content": response})