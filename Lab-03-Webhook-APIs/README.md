# Lab 03: Webhook-Based APIs

## 🎯 Objective
Build a robust, production-like API using webhooks that includes rigorous input validation, duplicate detection, and structured documentation.

## 🛠️ Implementation Details
- **Student Q&A API:** A POST endpoint accepting student questions.
- **Input Validation:** Requires proper name formatting and question length (≥ 10 characters). Returns HTTP 400 for invalid data.
- **Duplicate Detection:** Checks previous submissions (e.g., against a Google Sheet backend) and rejects exact matches with an HTTP 409 Conflict.
- **Data Enrichment:** Auto-generates submission IDs and timestamps for valid queries before storage.

## 🧪 Test Results
- ✅ Edge cases (short questions, missing names) return clear error structures.
- ✅ Resubmitting the same question triggers the duplicate detection branch.
- ✅ Valid entries are stored correctly with IDs.
