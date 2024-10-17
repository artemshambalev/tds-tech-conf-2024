# region Imports
import os

import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

from agent_tools.react_agent import prompt as react_agent
from utils import prompts_with_examples

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
# endregion


@tool
def list_files(dir: str):
    """List the contents of a specified director, relative to the current directory.
    `dir` must by always provided as quoted string."""
    try:
        dir = dir.strip("'" + '"').replace("*", "")
        files = os.listdir(dir)
        return f"Contents of {dir}:\n{[c for c in files if not c.startswith('.') and not c.startswith('__p')]}"
    except Exception as e:
        return f"Listing Directory Failed due to: {e}"


tools = [list_files]
llm = ChatOllama(model=OLLAMA_MODEL)
memory = ConversationBufferMemory()
agent = create_react_agent(llm, tools, prompt=react_agent)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, handle_parsing_errors=True)

# region UI
st.set_page_config(
    page_title="Simple Tool",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.write("<style>.stAppHeader { zoom:0.2 !important; } </style>", unsafe_allow_html=True)
st.title("Simple Tool")
if prompt := prompts_with_examples(
    [
        "What does the project in `.` do?",
        'Can you check on what system this code is running by analyzing folder structure in "/" (root)?',
    ]
):
    st.chat_message("user").write(prompt)
    with st.chat_message("ai"):
        st_callback = StreamlitCallbackHandler(st.container(), collapse_completed_thoughts=False)
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})
        st.success(response["output"], icon=":material/smart_toy:")
# endregion
