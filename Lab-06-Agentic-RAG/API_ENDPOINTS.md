# API Endpoints: Agentic RAG Backend

## Base URL
`http://localhost:8000/api/v1`

---

## 1. Chat Endpoint
**POST** `/chat`

Main endpoint for interacting with the agentic system.

### Request Body
```json
{
  "message": "What is the Transformer architecture and calculate 25 * 4?",
  "session_id": "session_12345"
}
```

### Response
```json
{
  "response": "The Transformer architecture is a neural network design introduced in 'Attention Is All You Need'..., and by the way, 25 * 4 is 100.",
  "tools_used": [
    {
      "tool_name": "search_knowledge_base",
      "action": "Queried Pinecone for 'Transformer architecture'"
    },
    {
      "tool_name": "calculate",
      "action": "Evaluated expression '25 * 4'"
    }
  ],
  "citations": ["Attention Is All You Need (Vaswani et al., 2017)"]
}
```

---

## 2. Health Check
**GET** `/health`

Used for monitoring backend status.

### Response
```json
{
  "status": "online",
  "vector_db": "connected",
  "llm_api": "ok"
}
```
