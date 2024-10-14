import streamlit as st
from snowcomment.DEFAULTS import llms

# Dialog to confirm succesful saving of comments
@st.experimental_dialog("Success!")
def success(task):
    if task == 'save_table_desc':
        st.write("Saved Table Description.")
        if st.button('Close ❌', key='close_success_1'):
            st.rerun()
    if task == 'save_col_desc':
        st.write("Saved Column Descriptions.")
        if st.button('Close ❌', key='close_success_2'):
            st.rerun()

# Dialog to show the LLM history
@st.experimental_dialog("LLM History", width='large')
def llm_history():
    if len(st.session_state['llm_history']) == 0:
        st.info('Nothing here yet. :(')
    else:
        for ix, output in enumerate(st.session_state['llm_history']):
            if output['role'] == 'response':
                st.info(output['content'], icon='🤖')
            if output['role'] == 'prompt':
                st.info(output['content'], icon='🤓')
    if st.button('Close ❌', key='close_llm_history'):
        st.rerun()

# Dialog to allow user to setup prompts
@st.experimental_dialog("Setup Prompts", width='large')
def setup_prompts():
    tab1, tab2, tab3 = st.tabs(["LLM","Table Prompt", "Column Prompt"])
    with tab1:
        llms.remove(st.session_state['llm'])
        llms.insert(0,st.session_state['llm'])
        selected_llm = st.selectbox('LLM:', llms)
        max_tokens = st.number_input("Max Tokens:", min_value=10, max_value=10000, value=st.session_state['max_tokens'])
        st.write("Sets the maximum number of output tokens in the response. Small values can result in truncated responses.")
        temperature = st.number_input("Temperature:", min_value=0.0, max_value=1.0, value=st.session_state['temperature'])
        st.write("A value from 0 to 1 (inclusive) that controls the randomness of the output of the language model. A higher temperature (for example, 0.7) results in more diverse and random output, while a lower temperature (such as 0.2) makes the output more deterministic and focused.")
        top_p = st.number_input("Top p:", min_value=0.0, max_value=1.0, value=st.session_state['top_p'])
        st.write("A value from 0 to 1 (inclusive) that controls the randomness and diversity of the language model, generally used as an alternative to temperature. The difference is that top_p restricts the set of possible tokens that the model outputs, while temperature influences which tokens are chosen at each step.")
        if st.button('💾 Update LLM Configuration'):
            st.session_state['llm'] = selected_llm
            st.session_state['max_tokens'] = max_tokens
            st.session_state['temperature'] = temperature
            st.session_state['top_p'] = top_p
            st.success('LLM configuration saved.')
    with tab2:
        table_prompt = st.text_area('Prompt used to generate Table Descriptions:',value=st.session_state['table_prompt'], height=500)
        if st.button('💾 Update Table Prompt'):
            st.session_state['table_prompt'] = table_prompt
            st.success('Prompt saved.')
    with tab3:
        column_prompt = st.text_area('Prompt used to generate Column Descriptions:',value=st.session_state['column_prompt'], height=500)
        if st.button('💾 Update Column Prompt'):
            st.session_state['column_prompt'] = column_prompt
            st.success('Prompt saved.')
    if st.button('Close ❌', key='close_prompt_setup'):
        st.rerun()

# Help Dialog
@st.experimental_dialog("Help for SnowComment", width='large')
def help():
    st.write("""SnowComment helps you in generating comments for tables, views and columns in your Snowflake Account.'
    To generate comments, SnowComment uses LLMs and the following contextual information:""")
    st.write("""
    - Table Name
    - Column Names
    - First few rows of the data as sample
    """)
    st.subheader('How to Generate Table Comments:')
    st.write("""
    1. Select your Table or View in the side menu.
    2. Switch to the 'Table/View' Tab.
    3. Click 'Generate Table Comment'.""")
    st.subheader('How to Generate Column Comments:')
    st.write("""
    1. Select your Table or View in the side menu.
    2. Switch to the 'Columns' Tab.
    3. Select the columns for which you want to generate a comment or click on 'Select All Columns'.
    4. Click 'Generate Column Comments'.""")
    st.subheader('Configuration:')
    st.write("""
    You can customize the comment generation by clicking on "Configure Generation".
    The configuration allows you to choose different LLMs from Cortex, as well as setting parameteres like max_tokens, temperature and top_p.
    You can also define your own prompts for table and column comment generation.
    """)
    st.subheader('Error when generating comments for columns:')
    st.write("""This happens sometimes, when the LLM output does not follow the requested format of column_name: comment.
    Try using a larger LLM like mistral-large2.""")
    if st.button('Close ❌', key='close_help'):
        st.rerun()