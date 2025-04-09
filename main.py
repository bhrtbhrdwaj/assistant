from graph.assistant import assistant
from graph.assistant_v import assistant_v

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from langserve import add_routes

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langgraph.graph import StateGraph
import asyncio
import json
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

"""  # Initialize FastAPI app
app = FastAPI()

# Add routes to serve the LangGraph workflow
add_routes(app, assistant, path="/chat")

# Run the app using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 """

#------------------------------------------------------------
class QueryRequest(BaseModel):
    message: str
    thread_id: int


app_fastapi = FastAPI()

# cors
app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app_fastapi.get("/chats")
async def chat_endpoint(thread_id: int, message: str):
    config = {"configurable": {"thread_id": thread_id}}
    state = {"messages": [HumanMessage(content=message)]}
    try:
        async def message_stream():
            for chunks in assistant.stream(state, config, stream_mode="updates"):
                content = chunks['assistant']["messages"][-1].content
                for act in content.split():
                    yield f"data: {act}\n\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error " + e)
    
    return StreamingResponse(message_stream(), media_type="text/event-stream")

@app_fastapi.post("/chat-v2")
async def chat_endpointa(request: QueryRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    state = {"messages": [HumanMessage(content=request.message)]}
    result = assistant_v.invoke(state, config)
    return {"response": result["messages"][-1].content}


@app_fastapi.post("/chat")
async def chat_endpoints(request: QueryRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    state = {"messages": [HumanMessage(content=request.message)]}
    try:
        async def message_stream():
            for chunks in assistant.stream(state, config, stream_mode="updates"):
                content = chunks['assistant']["messages"][-1].content
                for act in content.split():
                    yield f"data: {act}\n\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error " + e)
    
    return StreamingResponse(message_stream(), media_type="text/event-stream")

    """ try:
        async def message_stream():
            async for event in assistant.astream_events(state, config,version="v2"):
                print(f"Node: {event['metadata'].get('langgraph_node','')}. Type: {event['event']}. Name: {event['name']}")
                # Get chat model tokens from a particular node 
                if event['event'] == "on_chain_start" and event['metadata'].get('langgraph_node','') == 'assistant':
                    print("debug 2---------------")
                    print(f"Node: {event['metadata'].get('langgraph_node','')}. Type: {event['event']}. Name: {event['name']}")
                    data = event["data"]
                    print(data)
                    act = data["chunk"].content
                    print(act)
                    yield f"{act}\n\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error " + e)
    
    return StreamingResponse(message_stream(), media_type="text/event-stream") """