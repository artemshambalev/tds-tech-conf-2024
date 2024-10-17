import os
import streamlit as st
from langchain.agents import AgentExecutor
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_core.vectorstores import VectorStore
import chromadb


def load_codebase_to_vectorstore(path: str) -> tuple[VectorStore, chromadb.ClientAPI]:
    UNITY_PROJECT_PATH = os.environ.get("UNITY_PROJECT_PATH", "../unity/FlappyBirdClone")
    client = chromadb.Client()
    loader = DirectoryLoader(f"{UNITY_PROJECT_PATH}/Assets/Scripts/", glob="**/*.cs")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    all_splits = text_splitter.split_documents(data)

    local_embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vectorstore = Chroma.from_documents(
        collection_name="codebase",
        documents=all_splits,
        embedding=local_embeddings,
        client=client,
    )
    return vectorstore, client


def prompts_with_examples(examples: list[str]):
    prompt = st.chat_input()
    if os.environ.get("DEMO", False):
        return prompt
    with st.popover("Sample inputs"):
        for example in examples:
            if st.button(example):
                prompt = example
    return prompt


def streamlit_chat(title: str, agent_executor: AgentExecutor):
    st.title(title)

    with st.popover("Open popover"):
        st.code("You're in a project folder. What it is about?")
    if prompt := st.chat_input():
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            response = agent_executor.invoke(
                {"input": prompt}, {"callbacks": [st_callback]}
            )
            st.write(response["output"])

