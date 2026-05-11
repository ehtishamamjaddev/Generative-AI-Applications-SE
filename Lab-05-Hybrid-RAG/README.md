# Lab 05: Hybrid RAG Pipeline

## 🎯 Objective
Enhance retrieval accuracy by combining semantic vector search with exact keyword matching, and expand the knowledge domain.

## 🛠️ Implementation Details
- **Vector Search:** Transitioned to semantic embeddings (BAAI/bge-small-en-v1.5) stored in a Pinecone vector database.
- **Hybrid Approach:** Ran parallel keyword and vector retrievals, deduplicating and tagging results to maximize context quality.
- **Dynamic Thresholds:** Implemented a `minScore` parameter allowing the system to adjust strictness dynamically.
- **KB Expansion:** Added a Healthcare AI domain (6 new KB entries) assessing clinical context capabilities.

## 🧪 Test Results
- ✅ Vector search successfully caught synonymous queries that keyword search missed.
- ✅ System deduplicated instances where both keyword and vector search fetched the same KB entry.
- ✅ Healthcare domain correctly retrieved HIPAA and patient data guidelines.
