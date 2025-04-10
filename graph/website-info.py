from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

load_dotenv()
from langchain_community.document_loaders import WebBaseLoader

memory = MemorySaver()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm2 = ChatOpenAI(model="gpt-4o", temperature=0) 

class WebsiteInfo(BaseModel):
    company_name: str = "Not found"
    about: str = "Not available"
    domain: str = "Unknown"
    partners: list[str] = []
    competitors: list[str] = []

website_info_tool_instructions = """ 
    You are required to extract a breif about company from given {content} in below format. Include to 10 competitors.

    Please return the result in **valid JSON** format matching this schema:

```json
{{
  "company_name": "string",
  "about": "string",
  "category": "string",
  "competitors": ["string", ...]
}}

"""

web_info_response = """

"""

def web_site_info(website: str) -> str:
      """Extract info from web site"""
      loader_multiple_pages = WebBaseLoader([website])
      docs = loader_multiple_pages.load()
      content = docs[0].page_content
      tool_prompt = website_info_tool_instructions.format(content = content)
      web_site_info = llm2.invoke([SystemMessage(content=tool_prompt)]) 
      return web_site_info.content

tools = [web_site_info]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

def chatbot_node(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


builder = StateGraph(MessagesState)

builder.add_node("assistant", chatbot_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")


assistant = builder.compile(checkpointer=memory)

state = assistant.invoke({"messages": [HumanMessage(content="Get info from https://www.raydiant.com/")]}, {"configurable": {"thread_id": 1}})
for message in state["messages"]:
     message.pretty_print()
