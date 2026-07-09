<div align="center">
  <h1>Market Insight Agent</h1>
  <p><strong>A high-performance, multi-agent Web-RAG platform for autonomous market intelligence generation.</strong></p>
  <a href="https://client-4hd3.onrender.com"><strong>Live Demo (Client Interface)</strong></a>
</div>

---

## Overview

Market Insight Agent is a deterministic, low-latency market research platform. By orchestrating multiple specialized AI agents, the system autonomously synthesizes live web data into highly structured, schema-validated quantitative and qualitative market intelligence. 

It leverages an asynchronous **Web-Retrieval-Augmented Generation (Web-RAG)** architecture to bypass the hallucination issues common in standard LLMs when dealing with real-time financial or market data.

## Core Architecture

The system operates via a decoupled client-server architecture:
- **Frontend:** A high-performance React client (Vite) implementing a premium, glassmorphic UI.
- **Backend:** A FastAPI and LangChain-driven microservice utilizing Google Gemini models.

### Multi-Agent Pipeline

The generation of intelligence is orchestrated via a three-tier agentic pipeline:

1. **Supervisor Agent (`agents/supervisor.py`)**
   - **Role:** Workflow orchestration and query decomposition.
   - **Mechanism:** Ingests the primary user query and utilizes an LLM to generate targeted, natural-language search vectors to maximize search engine yield while bypassing strict boolean constraints.

2. **Researcher Agent (`agents/researcher.py`)**
   - **Role:** Asynchronous web crawling, document chunking, and semantic RAG retrieval.
   - **Mechanism:** Executes DuckDuckGo API searches based on the decomposed query vectors. It fetches and parses raw HTML using `trafilatura`. Text is chunked via `RecursiveCharacterTextSplitter` and embedded using `models/gemini-embedding-001`. Data is temporarily indexed in a session-specific **Qdrant** local vector database. An ephemeral semantic similarity search retrieves the top-K relevant contexts, enforcing strict chunk limitations to respect API rate limits.

3. **Analyst Agent (`agents/analyst.py`)**
   - **Role:** Data extraction, synthesis, and JSON strict structuring.
   - **Mechanism:** Synthesizes the raw RAG context against the original query using strict prompt engineering and Pydantic-defined schemas (`guardrails/output_parser.py`). It enforces deterministic JSON output structures for quantitative metrics, qualitative trends, and strategic recommendations, returning a validated payload back to the React UI.

## Technology Stack

- **Large Language Model:** Google Gemini (`gemini-2.5-pro`)
- **Backend Framework:** FastAPI, Uvicorn, Python 3.10+
- **Agent Orchestration:** LangChain, LangChain Google GenAI
- **Vector Database:** Qdrant (Local ephemeral storage)
- **Frontend:** React, TypeScript, Vite, Vanilla CSS
- **Data Validation:** Pydantic

## Local Development Setup

### 1. Repository Initialization
Clone the repository and initialize your virtual environment:
```bash
git clone https://github.com/pragyan2905/Market-Insights-Agent.git
cd Market-Insights-Agent
python -m venv venv
source venv/bin/activate
```

### 2. Backend Environment Configuration
Install backend dependencies and configure your environment:
```bash
pip install -r requirements.txt
```
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
LOG_LEVEL=INFO
```

### 3. Frontend Environment Configuration
Install frontend dependencies:
```bash
cd frontend
npm install
```
*(Optional)* Create a `.env` file in the `frontend/` directory to point to your local or remote backend:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Execution
The system requires both the FastAPI backend and the React frontend to run simultaneously.

**Start the API Backend (Root Directory):**
```bash
python -m uvicorn api.main:app --reload
```
*API Docs available at `http://localhost:8000/docs`*

**Start the React Client (`frontend/` Directory):**
```bash
npm run dev
```
*Client available at `http://localhost:5173`*

## Deployment

This project is built for zero-downtime, serverless/PaaS deployments.

- **Backend (Render):** A `render.yaml` blueprint is provided in the root directory. You can automatically deploy the FastAPI service by connecting the repository to Render as a Blueprint. It binds to `$PORT` automatically.
- **Frontend (Vercel / Render Static):** The `frontend/` directory can be deployed as a standard Static Site. Ensure the `VITE_API_URL` environment variable is injected during the build step (`npm run build`) to properly route traffic to the backend API.
