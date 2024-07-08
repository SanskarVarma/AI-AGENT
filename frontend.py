import streamlit as st
import requests

st.title("MongoDB Query Agent")

user_query = st.text_input("Enter your query:")
if st.button("Submit"):
    try:
        response = requests.post('http://127.0.0.1:5000/query', json={'query': user_query})
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)
        result = response.json()
        st.write(result)
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    except ValueError:
        st.error("Failed to decode JSON response from the server.")
