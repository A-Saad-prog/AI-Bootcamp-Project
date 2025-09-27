Project Setup and Usage Instructions

Open a terminal and navigate to the project folder located at:
C:\Users\Hp\Desktop\intellicourse

Create and activate a virtual environment.
PowerShell command to create the environment:
python -m venv .venv

PowerShell command to activate it:
.venv\Scripts\Activate.ps1

If using Command Prompt instead of PowerShell, activate with:
.venv\Scripts\activate.bat

After activation, the terminal should show (.venv) at the beginning of the line.

Install the required Python packages using the terminal while the virtual environment is active. The packages to install are:
fastapi
uvicorn
sentence-transformers
pinecone
python-dotenv
requests
langchain-google-genai
langgraph

In the root folder of the project (C:\Users\Hp\Desktop\intellicourse), create a file named .env if it does not already exist.

Inside the .env file, add the following lines. Replace the placeholder text with your actual API keys.
GOOGLE_API_KEY=your_google_key
PINECONE_API_KEY=your_pinecone_key
TAVILY_API_KEY=your_tavily_key
PINECONE_ENV=us-east-1
PINECONE_INDEX=bootcamp-final
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
APP_ENV=development

Place any PDF or text files you want to use for course retrieval inside the folder:
intellicourse/data/raw

If you want to upload your documents to Pinecone, run the ingest script using:
python -m app.ingest
This step reads the files from data/raw, embeds them, and uploads the vectors to the Pinecone index.

Start the FastAPI server using:
uvicorn app.api:app --reload
When the server is running, it will show a local URL such as:
http://127.0.0.1:8000

To access the automatically generated API documentation, open this address in a web browser:
http://127.0.0.1:8000/docs

Each time you return to the project in the future, repeat the following steps:
a. Open a terminal and navigate to C:\Users\Hp\Desktop\intellicourse
b. Activate the virtual environment again using either:
.venv\Scripts\Activate.ps1 (PowerShell)
or
.venv\Scripts\activate.bat (Command Prompt)
c. Start the server again with:
uvicorn app.api:app --reload
