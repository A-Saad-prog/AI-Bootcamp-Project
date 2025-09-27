from typing import Literal, TypedDict, List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from app.rag import CourseRetriever
from app.config import settings
import os

# Simple Tavily wrapper
class TavilySearch:
    def __init__(self, api_key: str):
        self.api_key = api_key
    def search(self, query: str) -> List[Dict]:
        import requests
        r = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": self.api_key, "query": query, "max_results": 5}
        )
        r.raise_for_status()
        data = r.json()
        # normalize
        return [{"title": it.get("title"), "url": it.get("url"), "content": it.get("content")} for it in data.get("results", [])]

class AgentState(TypedDict):
    query: str
    route: Literal["course", "web", "unknown"]
    context: List[Dict]  # retrieved chunks or web results
    answer: str
    source_tool: Literal["course_retriever", "web_search", "none"]

# Nodes
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=settings.GOOGLE_API_KEY)
retriever = CourseRetriever()
tavily = TavilySearch(api_key=settings.TAVILY_API_KEY)

def router_node(state: AgentState) -> AgentState:
    prompt = (
        "Classify the user query as 'course' if it asks about courses, prerequisites, course topics, "
        "departments, catalogs, scheduling, degree requirements at the university; "
        "otherwise 'web' for general knowledge. Respond with only 'course' or 'web'.\n"
        f"Query: {state['query']}"
    )
    out = llm.invoke(prompt).content.strip().lower()
    route = "course" if "course" in out else "web"
    state["route"] = route
    return state

def course_node(state: AgentState) -> AgentState:
    ctx = retriever.query(state["query"], top_k=5)
    state["context"] = ctx
    state["source_tool"] = "course_retriever"
    return state

def web_node(state: AgentState) -> AgentState:
    results = tavily.search(state["query"])
    state["context"] = results
    state["source_tool"] = "web_search"
    return state

def generation_node(state: AgentState) -> AgentState:
    # Build a compact context string
    if state["source_tool"] == "course_retriever":
        ctx_text = "\n\n".join([c["text"] for c in state["context"]])
    else:
        ctx_text = "\n\n".join([f"{c.get('title','')}\n{c.get('content','')}" for c in state["context"]])

    sys = (
        "You are IntelliCourse, an AI course advisor. "
        "Use the provided context to answer accurately and concisely. "
        "If the answer is not in context, say what you can and note limitations."
    )
    user = f"Question: {state['query']}\n\nContext:\n{ctx_text}"
    completion = llm.invoke([("system", sys), ("user", user)])
    state["answer"] = completion.content
    return state

# Graph wiring
graph = StateGraph(AgentState)
graph.add_node("router", router_node)
graph.add_node("course", course_node)
graph.add_node("web", web_node)
graph.add_node("generate", generation_node)

graph.add_edge(START, "router")
graph.add_conditional_edges("router", lambda s: s["route"], {"course": "course", "web": "web"})
graph.add_edge("course", "generate")
graph.add_edge("web", "generate")
graph.add_edge("generate", END)

app_graph = graph.compile()
