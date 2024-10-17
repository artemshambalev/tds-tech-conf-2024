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
    """List the contents of a specified dir, relative to the current directory.
    `dir` must by always provided as quoted string. Use '.' to get current project's files."""
    try:
        dir = dir.strip("'" + '"').replace("*", "")
        contents = os.listdir(dir)
        return f"Contents of {dir}:\n{[c for c in contents if not c.startswith('.') and not c.startswith('__p')]}"
    except Exception as e:
        return f"Listing Directory Failed due to: {e}"


@tool
def read_file(file: str):
    """Read the contents of a file. Use on files that was previously listed."""
    file = file.strip("'" + '"')
    try:
        with open(file, "r") as f:
            contents = f.read()
        return f"Contents of {file}:\n{contents}"
    except Exception as e:
        return f"Reading File Failed due to: {e}"


tools = [read_file, list_files]
llm = ChatOllama(model=OLLAMA_MODEL)
memory = ConversationBufferMemory()
agent = create_react_agent(llm, tools, prompt=react_agent)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, handle_parsing_errors=True)

# region UI
st.set_page_config(
    page_title="Extra Tool",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.title("Extra Tool")
if prompt := prompts_with_examples(
    [
        "There is a Python project in '.'. Can you find out what does it do?",
        "Can you check on what system this code is running by analyzing folder structure in '/' (root)?",
    ]
):
    st.chat_message("user").write(prompt)
    with st.chat_message("ai"):
        st_callback = StreamlitCallbackHandler(st.container(), collapse_completed_thoughts=False)
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})
        st.success(response["output"], icon=":material/smart_toy:")
        if "tds" in response["output"].lower() or "techconf" in response["output"].lower():
            st.balloons()
# endregion
