import streamlit as st
from agent import PandasAgent
from utils import upload_file
from dotenv import load_dotenv
import os

st.title('AI-Data Tool')
st.divider()

load_dotenv()

df = upload_file()

if df is not None:
    if 'agent' not in st.session_state:
        st.session_state['agent'] = PandasAgent(
            api_key=os.environ['API-KEY'], # It's better to use st.secrets for API keys
            model="gpt-oss:20b",
            df=st.session_state['df']
        )
    st.dataframe(st.session_state['df'])
if st.button(label="Chat now"):
    st.switch_page("pages/chat.py")

with st.sidebar:
    with open('data/data.csv') as f:
        content = f.read()
    st.download_button(label="Download Preprocessed Data", data=content, file_name="data.csv")