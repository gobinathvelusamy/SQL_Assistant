import streamlit as st


def setup_session_state():
    num = st.session_state.get("run_id")
    num += 1
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.clear()
    st.cache_data.clear()
    st.session_state["run_id"] = num