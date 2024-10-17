# region Imports
import os

import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_ollama import ChatOllama

from agent_tools.jira import jira_issues
from agent_tools.react_agent import prompt as react_agent
from utils import prompts_with_examples

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
# endregion


tools = [jira_issues]
llm = ChatOllama(model=OLLAMA_MODEL)
memory = ConversationBufferMemory()
agent = create_react_agent(llm, tools, prompt=react_agent)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, handle_parsing_errors=True)


# region UI
st.set_page_config(
    page_title="Returning from vacation 🏖️",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.write("<style>.stAppHeader { zoom:0.2 !important; } </style>", unsafe_allow_html=True)
st.title("Returning from vacation 🏖️")
if prompt := prompts_with_examples(
    [
        "Hey! I was on a vacation for two weeks. Can you tell me what my team has been up to?",
    ]
):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container(), collapse_completed_thoughts=False)
        response = agent_executor.invoke(
            {"input": prompt + "\n Final answer must be in short 4 line poem."},
            {"callbacks": [st_callback]},
        )
        st.success(response["output"].replace("\n", "\n\n"), icon=":material/smart_toy:")
# endregion
