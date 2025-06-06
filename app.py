import streamlit as st
import pandas as pd
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyA-fV7I7YcLr5KiYHzK4Ug84P0eEC9m79E")
model = genai.GenerativeModel("gemini-2.0-flash")

st.title("🤖 Professor Recommender Bot")

# File handling
uploaded_file = st.file_uploader("Upload Faculty Excel File (.xlsx)", type="xlsx")
DEFAULT_PATH = "default_professors.xlsx"

try:
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Using uploaded file.")
    else:
        df = pd.read_excel(DEFAULT_PATH, engine="openpyxl")
        st.info("ℹ️ No file uploaded. Using default dataset.")
except FileNotFoundError:
    st.error(f"❌ Default file '{DEFAULT_PATH}' not found.")
    st.stop()
except ValueError as e:
    st.error(f"❌ Could not read Excel file: {e}")
    st.stop()

# Prepare professor context
prof_context = ""
for _, row in df.iterrows():
    prof_context += f"Name: {row['Name']}\nLink: {row['Profile Link']}\nResearch: {row['All Text']}\n\n"

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Display chat history
for user_q, bot_r in st.session_state.chat_history:
    st.markdown(f"**You:** {user_q}")
    st.markdown(f"**Bot:** {bot_r}")

# Chat input form
with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask a research-related question:", value="")
    submitted = st.form_submit_button("Ask")

# Handle submission
if submitted and user_input:
    st.session_state.user_input = user_input

    # Build prompt
    chat_prompt = f"""
You are an expert assistant helping students find professors based on their research interests.
You will be given a list of professors and their research areas. Recommend 4 professors whose research best matches the query.
Include profile links and 5-sentence summaries of their work. Only answer with the names of the professors, their links, and research areas.

Professor Data:
{prof_context}

Conversation so far:
"""
    for u, b in st.session_state.chat_history:
        chat_prompt += f"User: {u}\nBot: {b}\n"
    chat_prompt += f"User: {user_input}\nBot:"

    # Get Gemini response
    with st.spinner("🤖 Thinking..."):
        try:
            response = model.generate_content(chat_prompt)
            reply = response.text.strip()
        except Exception as e:
            reply = f"❌ Error: {e}"

    st.session_state.chat_history.append((user_input, reply))
    st.session_state.user_input = ""
    st.rerun()
