# Import python packages
import streamlit as st
from snowflake.core import Root
from snowcomment.create_session import create_snowpark_session

st.set_page_config(layout="wide")
st.title("SnowComment")

# Get the current credentials
session = create_snowpark_session(1)
root = Root(session)

if st.button("Generate Comments for Tables and Columns"):
    st.switch_page("pages/comment_generator.py")