from pydantic import BaseModel
from typing import List, Dict, Optional

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    source_tool: str
    retrieved_context: Optional[List[Dict]] = None
