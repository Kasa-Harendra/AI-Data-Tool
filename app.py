import streamlit as st
from agent import PandasAgent
from utils import upload_file
from dotenv import load_dotenv
import os
from uuid import uuid1
import weakref

def cleanup(session_id):
    print(f"Cleaning up files for session: {session_id}")
    csv_path = os.path.join('data', f'{session_id}.csv')
    png_path = os.path.join('data', f'{session_id}.png')
    if os.path.exists(csv_path):
        os.remove(csv_path)
    if os.path.exists(png_path):
        os.remove(png_path)

st.set_page_config('AI Data Tool', page_icon="📊")

st.title('AI-Data Tool')
st.divider()

load_dotenv()

df = upload_file()

if df is not None:
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = str(uuid1())
        # Create a dummy object and register a finalizer for cleanup
        # This will be called when the session ends and the object is garbage collected.
        dummy_obj = object()
        weakref.finalize(dummy_obj, cleanup, st.session_state['session_id'])

    if 'agent' not in st.session_state:
        st.session_state['agent'] = PandasAgent(
            api_key=st.secrets['API-KEY'], # It's better to use st.secrets for API keys
            model="gpt-oss:20b",
            df=st.session_state['df']
        )
    st.dataframe(st.session_state['df'])
if st.button(label="Chat now"):
    st.switch_page("pages/chat.py")

with st.sidebar:
    # with open('data/data.csv') as f:
    #     content = f.read()
    st.session_state['content'] = ''
    st.download_button(label="Download Preprocessed Data", data=st.session_state['content'], file_name="data.csv")