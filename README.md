# SnowComment

## Create the Application
```sql
CREATE DATABASE SNOWCOMMENT;

CREATE OR REPLACE GIT REPOSITORY SNOWCOMMENT.PUBLIC.snowcomment
  API_INTEGRATION = git_api_integration
  ORIGIN = 'https://github.com/michaelgorkow/SnowComment.git';

CREATE OR REPLACE STREAMLIT SNOWCOMMENT.PUBLIC.SnowCommentGIT2
ROOT_LOCATION = '@SNOWCOMMENT.PUBLIC.SnowComment/branches/main'
MAIN_FILE = '/app.py'
QUERY_WAREHOUSE = COMPUTE_WH;
```