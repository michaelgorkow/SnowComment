# Import python packages
import streamlit as st
import pandas as pd
from snowflake.core import Root
from src.get_session import create_snowpark_session
from src.DEFAULTS import llms, default_table_prompt, default_column_prompt
from src.generation import generate_table_description, generate_column_descriptions

st.set_page_config(layout="wide")
st.title("SnowComment")

# Get the current credentials
session = create_snowpark_session(1)
root = Root(session)

# Setup history for LLM prompts and results
if 'llm_history' not in st.session_state:
    st.session_state['llm_history'] = []

# Default prompt to generate table comments
if 'table_prompt' not in st.session_state:
    st.session_state['table_prompt'] = default_table_prompt

# Default prompt to generate column prompts
if 'column_prompt' not in st.session_state:
    st.session_state['column_prompt'] = default_column_prompt

# Default LLM
if 'llm' not in st.session_state:
    st.session_state['llm'] = 'llama3.1-8b'

# Default LLM
if 'max_tokens' not in st.session_state:
    st.session_state['max_tokens'] = 4096

# Default LLM temperature
if 'temperature' not in st.session_state:
    st.session_state['temperature'] = 0.2

# Default LLM top_p
if 'top_p' not in st.session_state:
    st.session_state['top_p'] = 0.0

# Reset saved table description
def reset_table_description():
    # Remove 'table_description' from session state if it exists
    if 'table_description' in st.session_state:
        del st.session_state['table_description']

# Reset saved column description
def reset_column_description():
    # Remove 'table_description' from session state if it exists
    if 'new_column_descriptions' in st.session_state:
        del st.session_state['new_column_descriptions']

# Reset LLM history
def reset_llm_history():
    # Remove 'table_description' from session state if it exists
    if 'llm_history' in st.session_state:
        del st.session_state['llm_history']

# Reset LLM history
def reset_prompts():
    st.session_state['table_prompt'] = default_table_prompt
    st.session_state['column_prompt'] = default_column_prompt

# Reset LLM settings
def reset_llm():
    st.session_state['llm'] = 'llama3.1-8b'
    st.session_state['max_tokens'] = 4096
    st.session_state['temperature'] = 0.2
    st.session_state['top_p'] = 0.0
    

# Reset comments
def reset_descriptions():
    reset_table_description()
    reset_column_description()

# Reset everything
def reset():
    reset_descriptions()
    reset_llm_history()
    reset_prompts()
    reset_llm()
    st.rerun()

# Retrieve columns without comments
@st.cache_data(ttl=3600)
def get_comment_counts(tables):
    comment_counts = []
    for table in tables:
        t = root.databases[f'"{selected_db}"'].schemas[f'"{selected_schema}"'].tables[f'"{table}"'].fetch()
        comment_counts.append(round(len([val.comment for val in t.columns if val.comment is not None])/len(t.columns)*100,2))
    return comment_counts

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

# Get all available databases
databases = [val.name for val in root.databases.iter()]

# Sidebar Menu
with st.sidebar:
    st.subheader("Select Table or View:")
    selected_db = st.selectbox('Database:', databases, on_change=reset_descriptions)
    schemas = [val.name for val in root.databases[f'"{selected_db}"'].schemas.iter()]
    schemas.remove('INFORMATION_SCHEMA')
    selected_schema = st.selectbox('Schema:', schemas, on_change=reset_descriptions)
    tables = [val.name for val in root.databases[f'"{selected_db}"'].schemas[f'"{selected_schema}"'].tables.iter()]
    #views = [val.name for val in root.databases[selected_db].schemas[selected_schema].views.iter()] # views are part of snowflake.core 0.13.0 which does not work in SiS
    comment_counts = get_comment_counts(tables)
    merged_list = [f"{name} ({percentage}%)" for name, percentage in zip(tables, comment_counts)]
    selected_table = st.selectbox('Table:', merged_list, on_change=reset_descriptions, help='Percentage shows how many columns have comments.')
    selected_table = selected_table.split('(')[0][:-1]
    st.subheader("Configuration & Help:")
    #selected_llm = st.selectbox('LLM:', llms)
    if st.button('Configure Generation', use_container_width=True):
        setup_prompts()
    if st.button('LLM History', use_container_width=True):
        llm_history()
    if st.button('Reset', use_container_width=True):
        reset()
        st.rerun()
    if st.button('Help', use_container_width=True):
        help()
    

if selected_table is not None:
    # Visualize first 5 rows of data
    st.subheader('Data:')
    df = session.table(f'"{selected_db}"."{selected_schema}"."{selected_table}"').limit(3)
    st.dataframe(df)
    st.subheader('Comments:')
    my_table = root.databases[f'"{selected_db}"'].schemas[f'"{selected_schema}"'].tables[f'"{selected_table}"'].fetch()
    tab1, tab2 = st.tabs(["Table/View", "Columns"])
    with tab1:
        # Initialize session state for the text area if not already set
        if 'table_description' not in st.session_state:
            st.session_state['table_description'] = my_table.comment
        table_description = st.text_area('Table Comment:', st.session_state['table_description'], height=200)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('🪄 Generate Table Comment', use_container_width=True):
                new_table_desc = generate_table_description(selected_table, df)
                # code to update the text_area table_description with my_new_table_desc
                st.session_state['table_description'] = new_table_desc
                st.rerun()
        with col2:
            if st.button('💾 Update Table Comment', use_container_width=True):
                my_table.comment = table_description
                my_table_res = root.databases[f'"{selected_db}"'].schemas[f'"{selected_schema}"'].tables[f'"{selected_table}"']
                my_table_res.create_or_alter(my_table)
                success('save_table_desc')

    with tab2:
        if 'new_column_descriptions' in st.session_state:
            column_descriptions = st.session_state['new_column_descriptions']
        if 'new_column_descriptions' not in st.session_state:
            column_descriptions = pd.DataFrame([[val.name, val.comment, False] for val in my_table.columns], columns=['COLUMN','COMMENT','SELECT'])
        row_order = column_descriptions['COLUMN'].tolist()
        column_selection_df = st.data_editor(
            column_descriptions, 
            height=375,
            #height=len(column_descriptions)*35,
            use_container_width=True,
            hide_index=True,
            column_config={
                "COLUMN": st.column_config.TextColumn(
                    "COLUMN",
                    help="Column Name in Table",
                    width='small'
                ),
                "COMMENT": st.column_config.TextColumn(
                    "COMMENT",
                    help="Comment for Column.",
                    width='large'
                ),
                "SELECT": st.column_config.CheckboxColumn(
                    "SELECT",
                    help="Select this column for comment generation.",
                    width='small'
                ),
            }
        )
        column_selection = [f'"{val}"' for val in column_selection_df.loc[column_selection_df["SELECT"] == True]['COLUMN'].tolist()]
            
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button('☑️ Select All columns', use_container_width=True):
                column_descriptions['SELECT'] = True
                st.session_state['new_column_descriptions'] = column_descriptions
                st.rerun()
        with col2:
            if st.button('🪄 Generate Column Comments', use_container_width=True, disabled=len(column_selection) == 0):
                new_col_desc = generate_column_descriptions(selected_table, df, column_selection)
                new_col_desc = pd.DataFrame([[val.split(':')[0].strip(),val.split(':')[1].strip(), True] for val in new_col_desc.split('<Columns>')[1].split('</Columns>')[0].split('\n')[1:-1]], columns=['COLUMN','COMMENT','SELECT'])
                new_df = column_descriptions[~column_descriptions['COLUMN'].isin(new_col_desc['COLUMN'])]
                combined_df = pd.concat([new_df, new_col_desc], ignore_index=True)
                combined_df = combined_df.set_index('COLUMN').loc[row_order].reset_index()
                st.session_state['new_column_descriptions'] = combined_df
                st.rerun()
        with col3:
            if st.button('💾 Update Column Comments', use_container_width=True):
                try:
                    for ix, row in column_selection_df.iterrows():
                        for col_ in my_table.columns:
                            if col_.name == row['COLUMN']:
                                if row['COMMENT'].upper() == 'UNKNOWN':
                                    col_.comment = ""
                                else:
                                    col_.comment = row['COMMENT']
                                continue
                    my_table_res = root.databases[f'"{selected_db}"'].schemas[f'"{selected_schema}"'].tables[f'"{selected_table}"']
                    my_table_res.create_or_alter(my_table)
                    success('save_col_desc')
                except Exception as e:
                    st.error(f'There was an error when generating the column comments. The full error:\n {e}')

if selected_table is None:
    st.info('Please select a table or view first.')