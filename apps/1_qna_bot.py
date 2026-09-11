
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
import streamlit as st
llm = ChatGroq(model="openai/gpt-oss-120b")

st.title("My First QnA Bot")
st.markdown("My QnA bot with Langchain and Groq!!!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message ["role"]
    content = message ["content"]
    st.chat_message(role).markdown(content)

query = st.chat_input("Ask me anything <3...")
if query:
    st.session_state.messages.append({"role" : "user", "content" : query })
    st.chat_message("user").markdown(query)
    res = llm.invoke(query)
    st.chat_message("ai").markdown(res.content)
    st.session_state.messages.append({"role" : "ai", "content" : res.content })