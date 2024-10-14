import streamlit as st
import os
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
import snowflake.connector

# Function to create a Snowpark session
@st.cache_resource
def create_snowpark_session(cache_id):
    # Check if running in SPCS (Snowflake Python Connector Services)
    if os.path.isfile("/snowflake/session/token"):
        creds = {
            'host': os.getenv('SNOWFLAKE_HOST'),
            'protocol': "https",
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'authenticator': "oauth",
            'token': open('/snowflake/session/token', 'r').read(),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA'),
            'client_session_keep_alive': True
        }
    # Check if running Streamlit externally and use environment variables from .env file
    elif os.path.isfile(".env"):
        from dotenv import load_dotenv
        load_dotenv()
        creds = {
            'account': os.getenv('SNOWFLAKE_ACCOUNT'),
            'user': os.getenv('SNOWFLAKE_USER'),
            'password': os.getenv('SNOWFLAKE_PASSWORD'),
            'role': os.getenv('SNOWFLAKE_ROLE'),
            'warehouse': os.getenv('SNOWFLAKE_WAREHOUSE'),
            'database': os.getenv('SNOWFLAKE_DATABASE'),
            'schema': os.getenv('SNOWFLAKE_SCHEMA'),
            'client_session_keep_alive': True
        }
    else:
        session = get_active_session()
        return session
    
    connection = snowflake.connector.connect(**creds)
    session = Session.builder.configs({"connection": connection}).create()
    return session