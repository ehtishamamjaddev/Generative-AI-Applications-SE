# Lab 04: RAG Fundamentals

## 🎯 Objective
Understand and implement the foundations of Retrieval-Augmented Generation (RAG) using keyword-based retrieval and a structured knowledge base.

## 🛠️ Implementation Details
- **Knowledge Base Creation:** Developed a multi-topic KB containing 20+ entries focused on the financial domain (fraud, credit scoring, AML).
- **Keyword Retrieval:** Implemented relevance scoring based on keyword overlap between user queries and KB entries.
- **Status Classification:** Classified retrieval results into `success`, `low_confidence`, or `no_context` based on score thresholds.
- **Audit Logging:** Built a mechanism to log queries, retrieved contexts, and generation outputs for compliance tracking.

## 🧪 Test Results
- ✅ Financial queries successfully pull relevant KB blocks.
- ✅ Unrelated queries trigger `no_context` fallbacks, preventing hallucinations.
- ✅ Audit logging accurately captures generation traces.
