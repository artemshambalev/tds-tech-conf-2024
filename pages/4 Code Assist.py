# region imports
import os

import streamlit as st
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_ollama import ChatOllama

from agent_tools.react_agent import prompt as react_agent
from utils import load_codebase_to_vectorstore, prompts_with_examples

# endregion

# region UI
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
UNITY_PROJECT_PATH = os.environ.get("UNITY_PROJECT_PATH", "../unity/FlappyBirdClone")


st.set_page_config(
    page_title="Code Assist",
    page_icon="🧊",
    layout="centered",
    initial_sidebar_state="collapsed",
)
st.write("<style>.stAppHeader { zoom:0.2 !important; } </style>", unsafe_allow_html=True)
st.title("Code Assist")

with st.spinner("Loading codebase..."):
    vectorstore, client = load_codebase_to_vectorstore(f"{UNITY_PROJECT_PATH}/Assets/Scripts/")
    st.session_state.vectorstore = vectorstore
    st.session_state.client = client
# endregion


@tool
def codebase_qa(question: str):
    """Ask a question about the codebase. The answer will be based on the codebase. Always include the source file path in the answer."""
    docs = st.session_state.vectorstore.similarity_search(question)
    content = [f"File `{x.metadata['source']}`:\n{x.page_content}\n" for x in docs]
    prompt_template = PromptTemplate.from_template(
        """\
    Given context about the subject, answer the question based on the context provided to the best of your ability.
    Always include the source file path in the answer.
    Context: {context}
    Question:
    {question}
    Answer:
    """
    )
    prompt = prompt_template.format(context=content, question=question)
    answer = st.session_state.llm.invoke(prompt)
    return answer


@tool
def codebase_read(keyword: str):
    """Return the content of the files that contain certain keyword (classname, method etc.)."""
    global vectorstore
    docs = vectorstore.similarity_search(keyword, k=2)
    content = [f"File `{x.metadata['source']}`:\n{x.page_content}\n" for x in docs]
    return "\n".join(content)


tools = [codebase_qa, codebase_read]
llm = ChatOllama(model=OLLAMA_MODEL)
st.session_state.llm = llm
memory = ConversationBufferMemory()
agent = create_react_agent(llm, tools, prompt=react_agent)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, handle_parsing_errors=True)

# region UI
if prompt := prompts_with_examples(
    [
        "Why is the camera is moving so slow? What can I do to make it faster?",
        """I have an error after bird die:
NullReferenceException: Object reference not set to an instance of an object
DeadCanvas_Manager.SetScoreValues (System.Int32 currentSc, System.Int32 bestSc) (at Assets/Scripts/DeadCanvas_Manager.cs:13)
Game_Manager.Die () (at Assets/Scripts/Game_Manager.cs:98)
FlappyBirdController.Die () (at Assets/Scripts/FlappyBirdController.cs:100)
FlappyBirdController.OnCollisionEnter2D (UnityEngine.Collision2D collider) (at Assets/Scripts/FlappyBirdController.cs:87)
        """,
    ]
):
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        st_callback = StreamlitCallbackHandler(st.container(), collapse_completed_thoughts=False)
        response = agent_executor.invoke({"input": prompt}, {"callbacks": [st_callback]})
        st.success(response["output"], icon=":material/smart_toy:")
# endregion
