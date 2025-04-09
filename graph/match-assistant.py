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

class MatchSummary(BaseModel):
    summary: str
    match: str
    man_of_the_match: str

match_tool_instructions = """ 
    You are required to summarize a match based on user request and you have to uses {content} as your sources.
    the output should be well formatted Match field should be the title of the match.
"""
match_tool_response = """
    Match: {match}
    Summary: {summary}
    Man of the Match: {man_of_the_match}    
"""
def match_summary(query: str) -> str:
      """Creates match summary"""
      loader_multiple_pages = WebBaseLoader(["https://www.cricbuzz.com/"])
      docs = loader_multiple_pages.load()
      content = docs[0].page_content
      tool_prompt = match_tool_instructions.format(content = content)
      match_summary = llm2.with_structured_output(MatchSummary).invoke([SystemMessage(content=tool_prompt)] + [HumanMessage(content=query)]) 
      return match_tool_response.format(match=match_summary.match, summary=match_summary.summary, 
                                                                        man_of_the_match=match_summary.man_of_the_match)

tools = [match_summary]
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

state = assistant.invoke({"messages": [HumanMessage(content="Upcomming IPL match")]}, {"configurable": {"thread_id": 1}})
for message in state["messages"]:
     message.pretty_print()
