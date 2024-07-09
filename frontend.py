import streamlit as st
import requests

st.title("AI-based Analytics")

user_query = st.text_input("Enter your query:")

if st.button("Submit"):
    try:
        response = requests.post("http://127.0.0.1:5000/query", json={"query": user_query})
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            st.error(result["error"])
        else:
            st.json(result)
    except Exception as e:
        st.error(f"Error in fetching data: {str(e)}")