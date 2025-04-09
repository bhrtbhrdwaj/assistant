from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver

import sqlite3
# In memory if we supply :memory: then it creates an inmemory database
#conn = sqlite3.connect(":memory:", check_same_thread = False)


db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)


load_dotenv()

memory = SqliteSaver(conn)

def multiply(a: int, b: int) -> int:
    """Multiply two numbers together"""
    print("multiply params: " + a + "---" + b)
    return a * b
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    print("add params: " + a + "---" + b)
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract second number from first number"""
    print("subtract params: " + a + "---" + b)
    return a - b

def square(x: int) -> int:
    """Square a number"""
    return x * x


tools = [multiply, add, subtract, square]

class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

def chatbot_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(ChatState)

builder.add_node("assistant", chatbot_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")


assistant_v = builder.compile(checkpointer=memory)
