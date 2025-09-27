from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import QueryRequest, QueryResponse
from app.agent_graph import app_graph

app = FastAPI(title="IntelliCourse API", version="1.0")

# If you'll call from a browser file
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

@app.post("/chat", response_model=QueryResponse)
def chat(req: QueryRequest):
    state = {"query": req.query, "route": "unknown", "context": [], "answer": "", "source_tool": "none"}
    final = app_graph.invoke(state)
    return QueryResponse(
        answer=final["answer"],
        source_tool=final["source_tool"],
        retrieved_context=final["context"][:3]  # trim response size
    )
