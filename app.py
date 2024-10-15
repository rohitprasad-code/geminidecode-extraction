import os
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Function to get the response from Gemini API
def get_gemini_response(input_data):
    url = "https://gemini-pro-api.com/endpoint"
    headers = {"Authorization": f"Bearer {GOOGLE_API_KEY}"}
    data = {"input": input_data}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Streamlit UI
st.title("Gemini Multilanguage Document Extraction")
user_input = st.text_area("Enter the document text or upload a file")

if st.button("Extract Data"):
    result = get_gemini_response(user_input)
    st.write(result)
