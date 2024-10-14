# Import python packages
import streamlit as st
import pandas as pd
from snowflake.core import Root
from snowcomment.create_session import create_snowpark_session
from snowcomment.DEFAULTS import default_table_prompt, default_column_prompt
from snowcomment.generation import generate_table_description, generate_column_descriptions
from snowcomment.dialogs import help, success, llm_history, setup_prompts

st.set_page_config(layout="wide")
st.title("SnowComment")

# Get the current credentials
session = create_snowpark_session(1)
root = Root(session)

if st.button("Generate Comments for Tables and Columns"):
    st.switch_page("comment_generator.py")