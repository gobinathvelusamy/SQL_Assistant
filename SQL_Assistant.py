import os
import time

import pandas as pd

from app_secrets import OPENAI_API_KEY
import streamlit as st
#from code_editor import code_editor
from utils.setup import setup_session_state
from utils.func_sql import prompt_sql, execute_sf_query, prompt_ques, exec_code, generate_plotly_code, add_training
from langchain import OpenAI


###Outline of page
st.sidebar.image(
    "https://www.tcs.com/content/dam/global-tcs/en/images/home/dark-theme.svg",
    use_column_width=True)
# st.sidebar.title("Output Settings")
# st.sidebar.checkbox("Show Question", value=True, key="show_question")
# st.sidebar.checkbox("Show Table", value=True, key="show_table")
# st.sidebar.checkbox("Show Plotly Code", value=True, key="show_plotly_code")
# st.sidebar.checkbox("Show Chart", value=True, key="show_chart")
# st.sidebar.checkbox("Show Follow-up Questions", value=True, key="show_followup")
st.sidebar.button("Rerun", on_click=setup_session_state, use_container_width=True)

st.title("Personalized SQL assistant")
st.write("Ask your questions, and we will query it!")
#st.sidebar.write(st.session_state)


# setup env variable
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = OpenAI(temperature=0)


def set_question(question):
    st.session_state["my_question"] = question


st.session_state["run_id"] = 1
text = st.empty()
assistant_message_suggested = st.chat_message(
    "assistant", avatar="logo.jpg"
)

if assistant_message_suggested.button("Click to show suggested questions"):
    st.session_state["my_question"] = None
    suggested_questions = prompt_ques(st.session_state.get("my_question"), llm)
    suggested_questions = list(suggested_questions)
    questions_ = ''.join(suggested_questions)
    individual_questions_ = questions_.split('\n')
    for i, question in enumerate(individual_questions_):
        time.sleep(0.05)
        key_iterate = "ques" + str(i)
        button = st.button(
            question,
            key=key_iterate,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    key_for_ques = "key_new_q" + str(st.session_state.get("run_id"))
    my_question = st.chat_input(
        "Ask me a question about your data"
        # key= key_for_ques
    )

if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = prompt_sql(my_question, llm)

    if sql:
        if st.session_state.get("show_sql", True):
            assistant_message_sql = st.chat_message(
                "assistant", avatar="logo.jpg"
            )
            assistant_message_sql.code(sql, language="explanation", line_numbers=True)

        # user_message_sql_check = st.chat_message("user")
        # user_message_sql_check.write(f"Are you happy with the generated SQL code?")
        # key_sql = "key_sql" + str(st.session_state.get("run_id"))
        # with user_message_sql_check:
        #     happy_sql = st.radio(
        #         "Please choose:",
        #         options=["", "yes", "no"],
        #         key=key_sql,
        #         index=0,
        #     )
        #
        # if happy_sql == "no":
        #     st.warning(
        #         "Please fix the generated SQL code. Once you're done hit Ctrl + Enter to submit"
        #     )
        #     sql_response = code_editor(sql, lang="explanation")
        #     fixed_sql_query = sql_response["text"]
        #
        #     if fixed_sql_query != "":
        #         df = execute_sf_query(fixed_sql_query)
        #     else:
        #         df = None
        # elif happy_sql == "yes":
        #     df = execute_sf_query(sql)
        # else:
        #     df = None


        df= execute_sf_query(sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar="logo.jpg",
                )

                if len(df) > 10:
                    assistant_message_table.text("First 10 rows of data")
                    assistant_message_table.dataframe(df.head(10))
                else:
                    assistant_message_table.dataframe(df)

                # setup_session_state()
                # st.session_state["my_question"] = None

            code = generate_plotly_code(my_question, sql, st.session_state.get("df"), llm)
            #print(code)
            if st.session_state.get("show_plotly_code", True):
                assistant_message_plotly_code = st.chat_message(
                    "assistant",
                    avatar="logo.jpg",
                )
                assistant_message_plotly_code.code(
                    code, language="python", line_numbers=True
                )
            #
            # user_message_plotly_check = st.chat_message("user")
            # user_message_plotly_check.write(
            #     f"Are you happy with the generated Plotly code?"
            # )
            #
            #
            # def unhappy_plotly():
            #     st.warning(
            #         "Please fix the generated Python code. Once you're done hit Ctrl + Enter to submit"
            #     )
            #     python_code_response = code_editor(code, lang="python")
            #     st.session_state["code"] = python_code_response["text"]
            #
            #
            # def happy_plotly():
            st.session_state["code"] = code
            #
            #
            # with user_message_plotly_check:
            #     plotly_yes = st.button("Yes", key="plot_yes", on_click=happy_plotly)
            #     plotly_no = st.button("No", key="plot_no", on_click=unhappy_plotly)
            #
            # st.session_state["code"] = code
            #
            if st.session_state.get("code") is not None and st.session_state.get("code") != "":
                assistant_message_chart = st.chat_message(
                    "assistant",
                    avatar="logo.jpg",
                )
                exec_code(code, st.session_state.get("df"))
            #
            #     add_train = st.button("Add to training data")
            #     if add_train:
            #         add_training(my_question=my_question, sql=sql, code=code)

            # user_message_rerun = st.chat_message("user")
            # user_message_rerun.write(f"Do you want to ask another question?")
            #
            #
            # def no_rerun():
            #     setup_session_state()
            #     st.write("Thank you!")


            def rerun():
                if st.session_state.get("show_followup", True):
                    assistant_message_followup = st.chat_message(
                        "assistant",
                        avatar="logo.jpg",
                    )
                    followup_questions = prompt_ques(st.session_state.get("my_question"), llm)
                    followup_questions = list(followup_questions)
                    questions = ''.join(followup_questions)
                    individual_questions = questions.split('\n')

                    setup_session_state()
                    if len(followup_questions) > 0:
                        assistant_message_followup.text(
                            "Here are some possible follow-up questions"
                        )
                    i = 0
                    for question in individual_questions:
                        time.sleep(0.05)
                        i += 1
                        key_iterate_2 = "follow_q" + str(i)
                        button_1 = st.button(
                            question,
                            key=key_iterate_2,
                            on_click=set_question,
                            args=(question,)
                        )
                        # assistant_message_followup.write(question)
                else:
                    setup_session_state()

            rerun()
            #
            #
            # with user_message_rerun:
            #     rerun_yes = st.button("Yes", key="yes_rerun", on_click=rerun)
            #     rerun_no = st.button("No", key="no_rerun", on_click=no_rerun)


    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar="logo.jpg"
        )
        assistant_message_error.error("I wasn't able to generate SQL for that question")