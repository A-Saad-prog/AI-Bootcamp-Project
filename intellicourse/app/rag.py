from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
from app.config import settings

class CourseRetriever:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX)
        self.embedder = SentenceTransformer(settings.EMBED_MODEL)

    def query(self, user_query: str, top_k: int = 5):
        qvec = self.embedder.encode(user_query).tolist()
        res = self.index.query(vector=qvec, top_k=top_k, include_metadata=True)
        # return texts plus basic source info
        contexts = []
        for m in res["matches"]:
            meta = m["metadata"]
            contexts.append({"text": meta["text"], "source": meta.get("source", ""), "score": m["score"]})
        return contexts
