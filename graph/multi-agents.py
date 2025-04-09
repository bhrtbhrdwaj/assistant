from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

memory = MemorySaver()

def multiply(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtract second number from first number"""
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


assistant = builder.compile(checkpointer=memory)
