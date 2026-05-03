# Generative AI Applications in Software Engineering — Lab Portfolio

**Student:** M Ehtisham Amjad (231996)  
**Program:** BSSE-VI-B  
**Instructor:** Dr. Humaira Waqas  
**Institution:** Air University, Department of Creative Technologies — FCAI  
**Period:** Spring 2026

## 📚 Overview

This repository contains a complete progression through 6 advanced labs in Generative AI, covering:

- **Lab 01:** n8n Workflow Automation (Webhooks, Scheduling, File I/O)
- **Lab 02:** Google Sheets & LLM Integration (Groq, Quality Gates)
- **Lab 03:** Webhook-Based APIs with Validation & Duplicate Detection
- **Lab 04:** RAG Fundamentals (Keyword-Based Retrieval, Knowledge Base)
- **Lab 05:** Hybrid RAG (Vector + Keyword Search, Healthcare Domain)
- **Lab 06:** Agentic RAG (Multi-Tool Systems, FastAPI, Pinecone)

## 🚀 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Workflow Automation** | n8n | Event-driven and scheduled workflows |
| **LLM Integration** | Groq (llama3-8b) | Fast inference, cost-effective |
| **Vector Database** | Pinecone | Semantic search, embeddings |
| **Embeddings** | BAAI/bge-small-en-v1.5, Ollama | Text vectorization |
| **Backend Framework** | FastAPI | Agentic API endpoints |
| **Cloud Services** | Google Sheets, Google Drive, Tavily | External integrations |

## 📋 Lab Summary

### Lab 01: n8n Automation Fundamentals
- ✅ Webhook-based mini API (HTTP 200/400 responses)
- ✅ Scheduled office-hours logger (Mon–Fri 09:00)
- ✅ Input validation with IF nodes
- ✅ File operations and timestamp logging

### Lab 02: Google Sheets & LLM
- ✅ Google Sheets trigger + AI post generation
- ✅ Quality gate (word count ≥80, ≥1 hashtag)
- ✅ Rejection logging to separate sheet
- ✅ Groq LLM integration (switched from Gemini due to quota)

### Lab 03: API Development & Validation
- ✅ Webhook-based student Q&A submission API
- ✅ Input validation (name format, question length ≥10 chars)
- ✅ Duplicate detection logic
- ✅ Auto-generated submission IDs and timestamps
- ✅ Complete API documentation

### Lab 04: RAG Foundations
- ✅ Keyword-based retrieval with relevance scoring
- ✅ Multi-topic knowledge base (20+ entries)
- ✅ Three-way status classification (success, low_confidence, no_context)
- ✅ Audit logging to Google Sheets
- ✅ Financial domain knowledge base (fraud, credit scoring, AML)

### Lab 05: Hybrid RAG Pipeline
- ✅ Dynamic similarity threshold (minScore parameter)
- ✅ Parallel keyword + vector retrieval
- ✅ Result deduplication and tagging
- ✅ Healthcare AI domain expansion (6 new KB entries)
- ✅ Comprehensive retrieval comparison tests

### Lab 06: Agentic AI System
- ✅ FastAPI backend with 4 tools (KB search, web search, calculator, Wikipedia)
- ✅ Tool call logging with timestamps
- ✅ Domain-specific PDF ingestion (Transformer paper)
- ✅ HTML widget for interactive chatbot
- ✅ Agent tool trace and citation rendering
- ✅ Production deployment strategies

## 📊 Marks Distribution

| Lab | Task | Marks | Status |
|-----|------|-------|--------|
| 01 | Task 1: Webhook Validation | 5 | ✅ |
| 01 | Task 2: Office-Hours Filter | 7 | ✅ |
| 01 | Task 3: Export & Documentation | 8 | ✅ |
| 02 | Activity 1: Post Generator | — | ✅ |
| 02 | Activity 2: Quality Gate | — | ✅ |
| 03 | Task 1: Input Validation | 5 | ✅ |
| 03 | Task 2: Duplicate Detection | 7 | ✅ |
| 03 | Task 3: API Documentation | 8 | ✅ |
| 04 | Task 1: Relevance Threshold | 5 | ✅ |
| 04 | Task 2: KB Expansion | 10 | ✅ |
| 04 | Task 3: Audit Logging | 10 | ✅ |
| 05 | Task 1: Dynamic Threshold | 5 | ✅ |
| 05 | Task 2: Domain KB Expansion | 10 | ✅ |
| 05 | Task 3: Hybrid RAG | 10 | ✅ |
| 06 | Task 1: Wikipedia Tool | 5 | ✅ |
| 06 | Task 2: Tool Logging | 5 | ✅ |
| 06 | Task 3: Domain KB & Reflection | 10 | ✅ |

**Total: 120 marks**

## 🔑 Key Learning Outcomes

### Workflow Automation
- Event-driven and time-based trigger patterns
- API integration without coding (n8n visual workflows)
- File operations and data transformation

### LLM Integration
- Prompt engineering and quality gates
- Multiple provider switching (Gemini → Groq)
- Rate limiting and error handling

### Retrieval-Augmented Generation
- Keyword-based vs. vector-based retrieval trade-offs
- Knowledge base chunking and embedding strategies
- Relevance scoring and confidence thresholds

### Agentic Systems
- Tool selection and routing based on docstrings
- Multi-step reasoning with tool traces
- Production considerations (auth, monitoring, rate limiting)

## 🏗️ Technical Architecture

### Lab 04-05: RAG Pipeline
User Query
↓
Query Embedding (BAAI/bge-small-en-v1.5)
↓
Pinecone Vector Search
↓
Relevance Filtering (threshold ≥0.60)
↓
Context Block Assembly
↓
Groq LLM (llama3-8b8192)
↓
Audit Logging
↓
JSON Response (answer + sources + scores)

### Lab 06: Agentic System
User Question
↓
ReActAgent (Claude-based reasoning)
↓
Tool Selection & Routing
├→ search_knowledge_base (Pinecone)
├→ search_web (Tavily API)
├→ calculate (expressions)
└→ get_wikipedia_summary (REST API)
↓
Tool Execution & Logging
↓
Response Generation
↓
Citations & Tool Trace

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Docker (for n8n labs)
- API keys: Groq, Pinecone, Tavily, Google Cloud
- n8n instance (local or cloud)

### Installation

```bash
# Clone repository
git clone https://github.com/ehtishamamjaddev/Generative-AI-Applications-SE.git
cd Generative-AI-Applications-SE

# Lab 06 Backend Setup
cd Lab-06-Agentic-RAG/backend
cp .env.example .env
# Fill in API keys in .env
pip install -r requirements.txt
python main.py
```

## 📖 Lab-Specific Documentation

Each lab folder contains:
- **README.md** — Objective, implementation details, test results
- **REFLECTION.md** — Key learnings, challenges, production considerations
- **Screenshots/** — Visual evidence of working implementations
- **Code/Workflows/** — Exported JSON, Python scripts, API docs

## 🔐 Research Domain

**Primary Focus:** Financial AI & Automated Compliance Systems

The knowledge bases and test cases emphasize:
- Regulatory compliance (Basel III, FATF AML, PCI DSS)
- Financial fraud detection
- Credit risk assessment
- Transaction monitoring

This domain knowledge is evident in:
- Lab 04 KB entries (fraud detection, credit scoring)
- Lab 05 KB expansion planning (regulatory, AML)
- Lab 06 production reflection (compliance, auditability)

## ⚙️ Production Deployment Considerations

From Lab 06 reflection:
- **Authentication:** OAuth2 / API key validation with RBAC
- **Vector Database:** Production Pinecone index with replication
- **Rate Limiting:** Control Groq/Tavily API costs
- **Monitoring:** Tool call logs, retrieval quality metrics (NDCG/MRR)
- **Chunking:** Overlapping windows (512 tokens, 50-token overlap)
- **Compliance:** Audit trails, model versioning, human-in-the-loop

## 📚 Resources & References

### Key Papers & Documentation
- Transformer Architecture (Vaswani et al., 2017) — Lab 06 knowledge base
- BAAI Embeddings (Xiao et al., 2023)
- n8n Workflow Documentation
- FastAPI Framework
- Pinecone Vector Database Docs
- Groq Cloud Console

### External APIs
- [Groq Console](https://console.groq.com)
- [Pinecone](https://www.pinecone.io)
- [Tavily Search API](https://tavily.com)
- [Google Cloud APIs](https://cloud.google.com)

## 📝 License

This project is licensed under the MIT License — see LICENSE file for details.

## 👤 Author

**M Ehtisham Amjad**
- Student ID: 231996
- Program: BSSE-VI-B
- Air University, Islamabad, Pakistan

## 📧 Contact

For questions or collaboration, reach out through GitHub Issues.

---

**Last Updated:** May 2026  
**Course Completion Status:** ✅ All 6 Labs Complete
