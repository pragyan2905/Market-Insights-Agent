# Optylize Insight Generation Agent

Optylize Insight Generation Agent is a multi-agent, Web-RAG (Retrieval-Augmented Generation) platform engineered to synthesize quantitative and qualitative market intelligence from live web data. The architecture utilizes asynchronous agent orchestration, dynamic vector indexing, and strict schema guardrails to produce deterministic, low-latency market research reports.

## Architecture and Core Components

The backend is built on FastAPI and LangChain, integrating Qdrant for ephemeral vector storage and Google Gemini for embedding and text generation. The system operates via a three-tier agentic pipeline:

1. **Supervisor Agent (`agents/supervisor.py`)**
   - **Role:** Workflow orchestration and query decomposition.
   - **Mechanism:** Ingests the primary user query and utilizes an LLM to generate targeted, natural-language search vectors to maximize search engine yield while bypassing boolean constraints.

2. **Researcher Agent (`agents/researcher.py`)**
   - **Role:** Web crawling, document processing, and RAG retrieval.
   - **Mechanism:** Executes DuckDuckGo API searches based on the decomposed queries. Fetches and parses raw HTML using `trafilatura`. Text is chunked via `RecursiveCharacterTextSplitter` and embedded using `models/gemini-embedding-001`. Data is temporarily indexed in a session-specific Qdrant local vector database where a semantic similarity search retrieves the top-K relevant contexts. Chunk limitations are enforced to respect API rate limits.

3. **Analyst Agent (`agents/analyst.py`)**
   - **Role:** Data extraction and JSON structuring.
   - **Mechanism:** Synthesizes the raw RAG context against the original query using strict prompting and Pydantic-defined schemas (`guardrails/output_parser.py`). It enforces deterministic output structures for quantitative metrics, qualitative trends, and strategic recommendations, returning a validated JSON object to the frontend.

## System Requirements

- Python 3.10+
- A valid Google Gemini API Key with access to `gemini-3.0-pro` and `models/gemini-embedding-001`

## Local Development Setup

1. **Clone the repository and initialize the virtual environment:**
   ```bash
   git clone https://github.com/optylize/InsightGenerationAgent.git
   cd InsightGenerationAgent
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   LOG_LEVEL=INFO
   ```

## Execution

The system requires both the FastAPI backend and the Streamlit frontend to be running simultaneously.

1. **Start the API Backend:**
   Run the following command from the root directory to initialize the Uvicorn server on port 8000:
   ```bash
   python -m uvicorn api.main:app --reload
   ```
   *The Swagger UI documentation for the API can be accessed at `http://localhost:8000/docs`.*

2. **Start the Streamlit Frontend:**
   Open a new terminal session, activate the virtual environment, and run:
   ```bash
   streamlit run ui/app.py
   ```
   *The UI will launch on port 8501 by default.*
