import streamlit as st
from snowflake.cortex import Complete
import json 

# Function to call an LLM with formatted prompt to generate a table comment
def generate_table_description(table_name, df):
    sample_data = df.limit(3).to_pandas().to_markdown()
    prompt = st.session_state['table_prompt'].format(table_name=table_name, sample_data=sample_data)
    st.session_state['llm_history'].append({'role':'prompt', 'content':prompt})
    result = Complete(st.session_state['llm'], prompt, options={'max_tokens':st.session_state['max_tokens'], 'temperature':st.session_state['temperature'], 'top_p':st.session_state['top_p']})
    result = json.loads(result)['choices'][0]['messages']
    st.session_state['llm_history'].append({'role':'response', 'content':result})
    return result

# Function to call an LLM with formatted prompt to generate comments for columns.
def generate_column_descriptions(table_name, df, columns):
    sample_data = df.select(columns).limit(3).to_pandas().to_markdown()
    prompt = st.session_state['column_prompt'].format(table_name=table_name, sample_data=sample_data)
    st.session_state['llm_history'].append({'role':'prompt', 'content':prompt})
    result = Complete(st.session_state['llm'], prompt, options={'max_tokens':st.session_state['max_tokens'], 'temperature':st.session_state['temperature'], 'top_p':st.session_state['top_p']})
    result = json.loads(result)['choices'][0]['messages']
    st.session_state['llm_history'].append({'role':'response', 'content':result})
    return result