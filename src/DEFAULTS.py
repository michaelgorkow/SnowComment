# Selection of LLMs
llms = [
    "gemma-7b",
    "jamba-1.5-mini",
    "jamba-1.5-large",
    "jamba-instruct",
    "llama2-70b-chat",
    "llama3-8b",
    "llama3-70b",
    "llama3.1-8b",
    "llama3.1-70b",
    "llama3.1-405b",
    "llama3.2-1b",
    "llama3.2-3b",
    "mistral-large",
    "mistral-large2",
    "mistral-7b",
    "mixtral-8x7b",
    "reka-core",
    "reka-flash",
    "snowflake-arctic"
]

default_table_prompt = """You are asked to generate a concise business description for a table based on its name and sample data.

Table Name: {table_name}
Sample Data: 
{sample_data}
  
Provide a clear and specific business purpose for this table. 
Do not include any extra text, just the description.
"""

default_column_prompt = """You are asked to generate concise business descriptions for each column in a table.

Table Name: {table_name}
Sample Data:
{sample_data}

For each column, return a brief but clear business description that explains its purpose or usage. 
Ensure the output is formatted as follows:

<Columns>
Column1_Name: Description of the column and its business relevance.
Column2_Name: Description of the column and its business relevance.
...
</Columns>

Only return the description in the specified format, without any additional text.
"""