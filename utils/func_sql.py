import snowflake.connector
import pandas as pd
from app_secrets import *
from langchain.prompts import load_prompt
from pathlib import Path
import streamlit as st
from langchain import OpenAI
from langchain.prompts import load_prompt

def prompt_sql(prompt,llm):
    current_dir = Path(__file__)
    root_dir = [p for p in current_dir.parents if p.parts[-1] == 'SQL_Assistant'][0]
    prompt_template_sql = load_prompt(f"{root_dir}/prompts/tpch_prompt"
                                      f".yaml")
    final_prompt_sql = prompt_template_sql.format(input=prompt)
    sql = llm(prompt=final_prompt_sql)
    return sql

def execute_sf_query(sql):
    # Snowflake connection parameters
    connection_params = {
        'user': SF_USER,
        'password': SF_PASSWORD,
        'account': SF_ACCOUNT,
        'warehouse': SF_WAREHOUSE,
        'database': SF_DATABASE,
        'schema': SF_SCHEMA,
        'role':SF_ROLE
    }
    query=sql
    try:
        # Establish a connection to Snowflake
        conn = snowflake.connector.connect(**connection_params)
        # Create a cursor object
        cur = conn.cursor()
        # Execute the query
        try:
            cur.execute(query)
        except snowflake.connector.errors.ProgrammingError as pe:
            print("Query Compilation Error:", pe)
            return("Query compilation error")
        # Fetch all results
        query_results = cur.fetchall()
        # Get column names from the cursor description
        column_names = [col[0] for col in cur.description]
        # Create a Pandas DataFrame
        data_frame = pd.DataFrame(query_results, columns=column_names)
        # Print the DataFrame
        #print(data_frame)
        return data_frame
    except snowflake.connector.errors.DatabaseError as de:
        print("Snowflake Database Error:", de)
    except Exception as e:
        print("An error occurred:", e)
    finally:
        # Close the cursor and connection
        try:
            cur.close()
        except:
            pass
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    # Snowflake query
    query = '''
            select * from tasty_bytes_sample_data.raw_pos.menu
    '''
    execute_sf_query(query)

def prompt_ques(prompt,llm):
    current_dir = Path(__file__)
    root_dir = [p for p in current_dir.parents if p.parts[-1] == 'SQL_Assistant'][0]
    prompt_template_ques = load_prompt(f"{root_dir}/prompts/generate_questions_prompt"
                                      f".yaml")
    final_prompt_ques = prompt_template_ques.format(input=prompt)
    questions = llm(prompt=final_prompt_ques)
    return questions

def exec_code(plotly_code,df):
    # Create a temporary namespace for the execution
    namespace = {'df': df}
    # Execute the provided Plotly code
    exec(plotly_code, namespace)
    # Check if 'fig' variable is present in the namespace
    if 'fig' in namespace:
        # Display the Plotly figure
        st.plotly_chart(namespace['fig'])
        st.write("Plotly code executed successfully.")
    else:
        st.write("No 'fig' variable found in the code. Unable to display the Plotly figure.")
def generate_plotly_code(prompt,sql,df,llm):
    current_dir = Path(__file__)
    root_dir = [p for p in current_dir.parents if p.parts[-1] == 'SQL_Assistant'][0]
    prompt_template_plotly = load_prompt(f"{root_dir}/prompts/plotly_code_prompt"
                                         f".yaml")
    final_prompt_plotly = prompt_template_plotly.format(prompt=prompt, df=df, sql=sql)
    plotly_code = llm(prompt=final_prompt_plotly)
    return plotly_code

def write_to_training_file(file_path, prompt, sql, code):
    try:
        with (open(file_path, 'a')) as file:
            file.write("Executed successfully: ")
            file.write("\n prompt : {}".format(prompt))
            file.write("\n explanation : {}".format(sql))
            file.write("\n code : {}".format(code))
            file.write("\n \n")
            file.close()
            return "success"
    except:
        print("problem in opening file")
        return "problem in opening file"



def add_training(my_question, sql, code):
    current_dir = Path(__file__)
    root_dir = [p for p in current_dir.parents if p.parts[-1] == 'SQL_Assistant'][0]
    file_path = f"{root_dir}/gpt_trainings.txt".format(root_dir)
    write_to_file_status = write_to_training_file(file_path=file_path, prompt=my_question, sql=sql, code=code)
    if write_to_file_status == "success":
        st.write("Scenario added to trainings file")
    else:
        st.write(write_to_file_status)

def generate_explanation(my_query, llm):
    current_dir = Path(__file__)
    root_dir = [p for p in current_dir.parents if p.parts[-1] == 'SQL_Assistant'][0]
    prompt_template_explanation = load_prompt(f"{root_dir}/prompts/sql_exaplanation_prompt"
                                         f".yaml")
    final_prompt_explanation = prompt_template_explanation.format(sql=my_query)
    explanation = llm(prompt=final_prompt_explanation)
    return explanation