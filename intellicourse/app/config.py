from dotenv import load_dotenv
import os

load_dotenv()  # reads .env file

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    EMBED_MODEL = os.getenv("EMBED_MODEL")
    APP_ENV = os.getenv("APP_ENV")

settings = Settings()  # now you can do settings.GOOGLE_API_KEY
