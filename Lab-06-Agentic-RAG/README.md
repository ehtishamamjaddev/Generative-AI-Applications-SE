# Lab 06: Agentic RAG System

## 🎯 Objective
Build a production-grade Agentic AI application using FastAPI, capable of multi-step reasoning, dynamic tool selection, and transparent execution traces.

## 🛠️ Implementation Details
- **FastAPI Backend:** Created asynchronous REST endpoints hosting the ReAct agent logic.
- **Multi-Tool Reasoning:** Provided the LLM with 4 specific tools:
  - `search_knowledge_base` (Pinecone)
  - `search_web` (Tavily API)
  - `calculate` (Mathematical evaluation)
  - `get_wikipedia_summary` (REST API integration)
- **Tool Tracing:** Implemented comprehensive logging to track which tools the LLM decides to call, when, and with what parameters.
- **Widget Frontend:** Developed an HTML/JS frontend to provide an interactive chatbot UI displaying both answers and tool citations.

## 🧪 Test Results
- ✅ The agent successfully routes math queries to the calculator and factual queries to Wikipedia/KB.
- ✅ Multi-turn conversations track context.
- ✅ Tool execution logs confirm the agentic reasoning process.
