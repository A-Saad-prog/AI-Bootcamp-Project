from pathlib import Path
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec

from app.config import settings

RAW_DIR = Path("data/raw")

def load_documents():
    docs = []
    for p in RAW_DIR.glob("*"):
        if p.suffix.lower() in {".txt", ".md"}:
            docs.append((p.name, p.read_text(encoding="utf-8")))
        elif p.suffix.lower() == ".pdf":
            from langchain_community.document_loaders import PyPDFLoader
            pages = PyPDFLoader(str(p)).load()
            joined = "\n".join([pg.page_content for pg in pages])
            docs.append((p.name, joined))
    return docs

def chunk_documents(docs, chunk_size=800, chunk_overlap=120):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = []
    for fname, text in docs:
        for i, chunk in enumerate(splitter.split_text(text)):
            chunks.append({"id": f"{fname}-{i}", "source": fname, "text": chunk})
    return chunks

def ensure_pinecone_index(pc: Pinecone, name: str, dimension: int):
    if name not in [idx["name"] for idx in pc.list_indexes()]:
        pc.create_index(
            name=name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENV)
        )

def upsert_to_pinecone(chunks, model_name):
    embedder = SentenceTransformer(model_name)
    vectors = []
    for ch in chunks:
        vec = embedder.encode(ch["text"]).tolist()
        vectors.append({
            "id": ch["id"],
            "values": vec,
            "metadata": {"source": ch["source"], "text": ch["text"]}
        })

    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    ensure_pinecone_index(pc, settings.PINECONE_INDEX, dimension=len(vectors[0]["values"]))
    index = pc.Index(settings.PINECONE_INDEX)
    # upsert in batches
    B = 100
    for i in range(0, len(vectors), B):
        index.upsert(vectors=vectors[i:i+B])

if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    upsert_to_pinecone(chunks, settings.EMBED_MODEL)
    print(f"Ingested {len(chunks)} chunks into Pinecone '{settings.PINECONE_INDEX}'.")
