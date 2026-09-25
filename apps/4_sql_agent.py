from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

db = SQLDatabase.from_uri("sqlite:///todo.db")

db.run("""
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT CHECK (status IN ('pending', 'in_progress', 'completed')) NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

print("DB Table created successfully!")

llm = ChatGroq(model="openai/gpt-oss-120b")
toolkit = SQLDatabaseToolkit(db=db, llm = llm)
tools = toolkit.get_tools()
memory = InMemorySaver()

system_prompt = """
You are a task managment assistant that inetracts with a SQL database containing a 'todo'
TASK RULES:
1. Limit SELECT queries to 10 result max with   ORDER BY created_at DESC
2. After CREATE/UPDATE/DELETE, confirm with SELECT query.
3. If the user requests a list of tasks, present the output in a standard table format to ensure clean and organised display in the browser.

CRUD OPERATIONS:
 CREATE: INSERT INTO todos(title, description, status)
 READ: SELECT * FROM todos WHERE ... LIMIT 10
 UPDATE: UPDATE todos SET status =? WHERE id = ? OR title = ?
 DELETE: DELETE FROM todos WHERE id = ? or title = ?

Table schema: id, title, description, status(pending/progress/completed), created_at
"""
@st.cache_resource
def get_agent():
    agent = create_agent(
        model = llm,
        tools = tools,
        checkpointer = memory,
        system_prompt = system_prompt,
    )
    return agent

st.subheader("My Task Management Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = message ["role"]
    content = message ["content"]
    st.chat_message["role"].markdown(message["content"])                     

prompt = st.chat_input("Ask me anything about your tasks...")
if prompt:
    agent = get_agent()
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role" : "user", "content" : prompt })
    with st.chat_message("Ai") :
        with st.spinner("Thinking..."):

            response = agent.invoke(
                {"messages" : [{"role": "user", "content": prompt}]},
                {"configurable" : {"thread_id": "1"}} 
            )
            result = response["messages"][-1].content
            st.markdown(result)
    print("AI: ", result)
