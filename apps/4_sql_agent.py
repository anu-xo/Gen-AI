from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_commuinity.agent_toolkits import SQLDatabaseToolkit

db = SQLDatabase.from_uri("sqlite:///todo.db")