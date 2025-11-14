import subprocess
import sys

def check_everything() -> None:
    req_version = (3, 11)
    curr_version = (sys.version_info.major, sys.version_info.minor)
    if curr_version < req_version or curr_version > req_version:
        print("Please change Python verson to Python 3.11")

    try:
        import PyQt6
    except ModuleNotFoundError:
        try:
            subprocess.run('pip install pyqt6 --no-cache-dir', shell=True)
        except ImportError:
            print("Please install PyQt6")

    try:
        from typing import List
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document, load_index_from_storage, \
            Response
        from llama_index.core.schema import NodeWithScore
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        from qdrant_client import QdrantClient
        from qdrant_client.models import Distance
        from typing import List, Optional, Literal, Callable, Any
        from langchain_core.tools import StructuredTool
        from langchain.tools import tool
        import sqlite3
        from langgraph.graph import StateGraph, START, END
        import os
        from dotenv import load_dotenv
        from langchain_ollama import OllamaLLM
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
        from typing import List
        from pydantic import BaseModel
    except ModuleNotFoundError:
        try:
            subprocess.run('python.exe -m pip install --upgrade pip', shell=True)
            subprocess.run('pip install -r requirements.txt --no-cache-dir', shell=True)
        except ImportError:
            print('Please install requirements.txt')

if __name__ == '__main__':
    check_everything()