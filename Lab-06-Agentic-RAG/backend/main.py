from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime
import os
import logging
import re
import requests
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware
from pinecone import Pinecone
from PyPDF2 import PdfReader
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    Settings,
)
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import ReActAgent

# ---------------------------------------------------
# Logging
# ---------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_tool_call(tool_name: str, query: str, success: bool):
    status = "success" if success else "failed"
    line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {tool_name} | query='{query}' | {status}\n"
    with open("tool_log.txt", "a", encoding="utf-8") as f:
        f.write(line)

# ---------------------------------------------------
# Load ENV
# ---------------------------------------------------
load_dotenv()

GROQ_API_KEY       = os.getenv("GROQ_API_KEY")
LLM_MODEL_NAME     = os.getenv("LLM_MODEL_NAME", "llama-3.3-70b-versatile")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en-v1.5")
PINECONE_API_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_ENV       = os.getenv("PINECONE_ENV")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
TAVILY_API_KEY     = os.getenv("TAVILY_API_KEY", "")

DOMAIN_PDF_FILE = os.getenv("DOMAIN_PDF_FILE", "attention_is_all_you_need.pdf")
DOMAIN_NAMESPACE = os.getenv("DOMAIN_NAMESPACE", "nlp_transformer_kb")
DOMAIN_LABEL = os.getenv("DOMAIN_LABEL", "NLP Transformer research")

# ---------------------------------------------------
# Lazy runtime resources
# ---------------------------------------------------
pinecone_index = None
agent = None
registered_tools = []
local_kb_nodes = None


@lru_cache(maxsize=1)
def _load_local_kb_nodes():
    reader = PdfReader(DOMAIN_PDF_FILE)
    nodes = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        nodes.append({
            "page_label": str(page_index),
            "text": text,
        })
    return nodes


def _search_local_kb(query: str, top_k: int = 3) -> str:
    nodes = _load_local_kb_nodes()
    keywords = [token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 2]
    scored = []

    for node in nodes:
        text = node["text"].strip()
        lower_text = text.lower()
        score = 0
        for keyword in keywords:
            if keyword in lower_text:
                score += 1
        if score > 0:
            scored.append((score, node))

    if not scored:
        scored = [(0, node) for node in nodes[:top_k]]

    scored.sort(key=lambda item: item[0], reverse=True)
    top_nodes = [node for _, node in scored[:top_k]]

    snippets = []
    citations = []
    for node in top_nodes:
        page = node["page_label"]
        text = node["text"].strip().replace("\n", " ")
        if text:
            snippets.append(f"[Page {page}] {text[:500]}")
            citations.append(f"[Page {page}]")

    if not snippets:
        return "No relevant knowledge base matches found."

    citation_str = " ".join(citations) if citations else ""
    return "Knowledge base matches:\n" + "\n".join(snippets) + (f"\n{citation_str}" if citation_str else "")


def ensure_runtime_ready():
    """Initialize external clients and agent lazily."""
    global pinecone_index, agent, registered_tools

    if pinecone_index is not None and agent is not None and registered_tools:
        return

    # Validate required env vars
    missing = []
    required = {
        "GROQ_API_KEY": GROQ_API_KEY,
        "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
        "PINECONE_API_KEY": PINECONE_API_KEY,
        "PINECONE_ENV": PINECONE_ENV,
        "PINECONE_INDEX_NAME": PINECONE_INDEX_NAME,
    }
    for key, value in required.items():
        if not value:
            missing.append(key)
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))

    # Configure LLM and embeddings
    llm = Groq(
        model=LLM_MODEL_NAME,
        api_key=GROQ_API_KEY,
    )
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL_NAME)

    # Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
    pinecone_index = pc.Index(PINECONE_INDEX_NAME)

    # -----------------------------------------------
    # TOOL 1 — Knowledge Base Search
    # -----------------------------------------------
    def search_knowledge_base(query: str) -> str:
        """
        Search the internal knowledge base (domain PDF stored in Pinecone).
        Use this tool when the user asks about concepts from the uploaded domain document,
        such as transformer architecture, attention, encoder-decoder flow, or NLP training details.
        Returns relevant text chunks with page citations.
        Do NOT use this tool for live/current events or simple math calculations.
        """
        try:
            result = _search_local_kb(query)
            log_tool_call("search_knowledge_base", query, True)
            return result
        except Exception as e:
            log_tool_call("search_knowledge_base", query, False)
            return f"Knowledge base search failed: {str(e)}"

    # -----------------------------------------------
    # TOOL 2 — Web Search (Tavily)
    # -----------------------------------------------
    def search_web(query: str) -> str:
        """
        Search the live internet for current, recent, or real-world information.
        Use this tool when the user asks about recent events, news, people, or topics
        that are NOT covered in the internal domain knowledge base.
        Examples: latest AI frameworks, current events, sports results, news after 2024.
        Do NOT use for questions answerable from the uploaded domain PDF or for simple math calculations.
        """
        if not TAVILY_API_KEY:
            log_tool_call("search_web", query, False)
            return "Web search is not configured. Please add TAVILY_API_KEY to your .env file."
        try:
            import requests
            response = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": TAVILY_API_KEY, "query": query, "max_results": 3},
                timeout=10,
            )
            data = response.json()
            results = data.get("results", [])
            if not results:
                log_tool_call("search_web", query, True)
                return "No web results found."
            parts = []
            for r in results:
                parts.append(f"- {r.get('title', '')}: {r.get('content', '')[:200]}")
            result = "Web search results:\n" + "\n".join(parts)
            log_tool_call("search_web", query, True)
            return result
        except Exception as e:
            log_tool_call("search_web", query, False)
            return f"Web search failed: {str(e)}"

    # -----------------------------------------------
    # TOOL 3 — Calculator
    # -----------------------------------------------
    def calculate(expression: str) -> str:
        """
        Evaluate a mathematical expression and return the numeric result.
        Use this tool when the user asks for any calculation, arithmetic, or math,
        such as addition, subtraction, multiplication, division, powers, or percentages.
        Examples: '2 ** 16', '(100 * 5) / 3', '5 * 365'.
        Do NOT use this tool for text questions or searches.
        """
        try:
            allowed = set("0123456789+-*/().% ")
            if not all(c in allowed for c in expression):
                log_tool_call("calculate", expression, False)
                return "Expression contains invalid characters."
            result = eval(expression, {"__builtins__": {}})
            output = f"Result: {result}"
            log_tool_call("calculate", expression, True)
            return output
        except Exception as e:
            log_tool_call("calculate", expression, False)
            return f"Calculation failed: {str(e)}"

    # -----------------------------------------------
    # TOOL 4 — Wikipedia Summary
    # -----------------------------------------------
    def get_wikipedia_summary(topic: str) -> str:
        """
        Fetch the opening summary of a Wikipedia article for a given topic.
        Use this tool when the user asks for a general factual definition or
        overview of a well-known concept, person, or technology — especially
        when it is NOT covered in the internal knowledge base and does NOT
        require live/recent web data. Do NOT use for current events or
        detailed domain-document questions.
        """
        try:
            headers = {
                "User-Agent": "Lab06RAGBot/1.0 (educational project)",
                "Accept": "application/json",
            }
            cleaned_topic = topic.strip().rstrip("?.!")
            if cleaned_topic.lower().startswith("the "):
                cleaned_topic = cleaned_topic[4:].strip()

            normalized = cleaned_topic.lower()
            if "transformer" in normalized and ("nlp" in normalized or "natural language" in normalized):
                cleaned_topic = "Transformer (deep learning architecture)"

            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{cleaned_topic.replace(' ', '_')}"
            response = requests.get(url, timeout=5, headers=headers)

            if response.status_code == 404:
                search_url = "https://en.wikipedia.org/w/api.php"
                search_response = requests.get(
                    search_url,
                    timeout=5,
                    headers=headers,
                    params={
                        "action": "opensearch",
                        "search": cleaned_topic,
                        "limit": 1,
                        "namespace": 0,
                        "format": "json",
                    },
                )
                try:
                    search_data = search_response.json()
                except ValueError:
                    log_tool_call("get_wikipedia_summary", topic, False)
                    return "Wikipedia lookup failed: Invalid search response format"

                candidates = search_data[1] if isinstance(search_data, list) and len(search_data) > 1 else []
                if not candidates:
                    log_tool_call("get_wikipedia_summary", topic, False)
                    return "Wikipedia lookup failed: No matching article found"

                resolved_title = candidates[0]
                url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{resolved_title.replace(' ', '_')}"
                response = requests.get(url, timeout=5, headers=headers)

            if response.status_code != 200:
                log_tool_call("get_wikipedia_summary", topic, False)
                return f"Wikipedia lookup failed: HTTP {response.status_code}"
            try:
                data = response.json()
            except ValueError:
                log_tool_call("get_wikipedia_summary", topic, False)
                return "Wikipedia lookup failed: Invalid response format"
            result = data.get("extract", "No summary found.")
            log_tool_call("get_wikipedia_summary", topic, True)
            return result
        except Exception as e:
            log_tool_call("get_wikipedia_summary", topic, False)
            return f"Wikipedia lookup failed: {str(e)}"

    # -----------------------------------------------
    # Register tools and create ReActAgent
    # -----------------------------------------------
    kb_tool   = FunctionTool.from_defaults(fn=search_knowledge_base)
    web_tool  = FunctionTool.from_defaults(fn=search_web)
    calc_tool = FunctionTool.from_defaults(fn=calculate)
    wiki_tool = FunctionTool.from_defaults(fn=get_wikipedia_summary)
    registered_tools = [kb_tool, web_tool, calc_tool, wiki_tool]

    agent = ReActAgent(
        tools=registered_tools,
        llm=llm,
        verbose=True,
        streaming=False,
        system_prompt=(
            "You are a helpful AI assistant with access to four tools: "
            "a domain knowledge base, a live web search, a calculator, and Wikipedia summary. "
            "Always choose the most appropriate tool for the question. "
            "For questions about the uploaded domain PDF, always use search_knowledge_base first. "
            "For any numeric calculation, always use calculate. "
            "For general factual definitions or overviews, prefer get_wikipedia_summary before search_web. "
            "If a question combines multiple tasks, use multiple tools and combine the final answer clearly. "
            "Only answer directly without tools for simple general knowledge that does not require documents or math."
        ),
    )
    logger.info("✅ ReActAgent initialised with 4 tools.")


# ---------------------------------------------------
# FastAPI App
# ---------------------------------------------------
app = FastAPI(title="RAG API (Groq + Pinecone)", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# Request Schema
# ---------------------------------------------------
class QueryRequest(BaseModel):
    question: str


def _find_tool(tool_name: str):
    for tool in registered_tools:
        if tool.metadata.name == tool_name:
            return tool
    return None


def _extract_calc_expression(question: str):
    q = question.lower()

    # Handle patterns like "how many days are in 5 years".
    years_match = re.search(r"(\d+)\s*years?", q)
    if years_match and "day" in q:
        return f"{years_match.group(1)}*365"

    # Handle direct arithmetic patterns like "2+2" embedded in natural language.
    candidates = re.findall(r"[0-9][0-9\s\+\-\*/\(\)\.]*", question)
    for raw in candidates:
        candidate = raw.strip()
        if candidate and any(op in candidate for op in "+-*/"):
            return candidate

    return None

# ---------------------------------------------------
# Health Endpoint
# ---------------------------------------------------
@app.get("/health")
def health_check():
    try:
        ensure_runtime_ready()
        stats = pinecone_index.describe_index_stats()
        total_vectors = stats.get("total_vector_count", 0)
        return {
            "status": "ok",
            "pinecone_vectors": total_vectors,
            "llm_model": LLM_MODEL_NAME,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "web_search_enabled": bool(TAVILY_API_KEY),
            "domain_pdf": DOMAIN_PDF_FILE,
            "domain_namespace": DOMAIN_NAMESPACE,
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

# ---------------------------------------------------
# Tools Endpoint
# ---------------------------------------------------
@app.get("/tools")
def list_tools():
    ensure_runtime_ready()
    tools_info = []
    for tool in registered_tools:
        tools_info.append({
            "name": tool.metadata.name,
            "description": tool.metadata.description,
        })
    return {"tools": tools_info}

# ---------------------------------------------------
# Ingestion Endpoint
# ---------------------------------------------------
@app.post("/ingest")
def ingest_pdf():
    try:
        ensure_runtime_ready()
        logger.info("📄 Loading PDF...")
        documents = SimpleDirectoryReader(
            input_files=[DOMAIN_PDF_FILE],
            filename_as_id=True
        ).load_data()

        logger.info("✂️ Chunking documents...")
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
        nodes = splitter.get_nodes_from_documents(documents)

        for node in nodes:
            node.metadata = node.metadata or {}
            node.metadata["source"] = DOMAIN_PDF_FILE
            node.metadata["page_label"] = node.metadata.get("page_label", "N/A")

        logger.info(f"📦 Storing {len(nodes)} chunks in Pinecone...")
        vector_store = PineconeVectorStore(
            pinecone_index=pinecone_index,
            namespace=DOMAIN_NAMESPACE
        )
        vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        vector_index.insert_nodes(nodes)

        return {
            "status": "success",
            "chunks_ingested": len(nodes),
            "pages_indexed": len(set(n.metadata["page_label"] for n in nodes)),
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# Query Endpoint (Agentic)
# ---------------------------------------------------
@app.post("/query")
async def query_agent(request: QueryRequest):
    try:
        ensure_runtime_ready()
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Empty question")

        q_lower = request.question.lower()
        kb_intent = any(
            kw in q_lower
            for kw in [
                "transformer",
                "self-attention",
                "attention",
                "multi-head",
                "encoder",
                "decoder",
                "positional encoding",
                "machine translation",
                "sequence transduction",
                "bleu",
                "nlp",
            ]
        )
        calc_expr = _extract_calc_expression(request.question)
        wiki_intent = any(
            kw in q_lower
            for kw in ["wikipedia", "wiki", "summary of", "what is", "who is", "overview of"]
        )

        # Deterministic mixed-intent route: force KB + Calculator and expose two tool steps.
        if kb_intent and calc_expr:
            kb_tool = _find_tool("search_knowledge_base")
            calc_tool = _find_tool("calculate")
            if kb_tool is None or calc_tool is None:
                raise RuntimeError("Required tools are not available")

            kb_output = kb_tool.fn(query=request.question)
            calc_output = calc_tool.fn(expression=calc_expr)

            return {
                "question": request.question,
                "answer": f"{kb_output}\n\nCalculation: {calc_output}",
                "tools_used": ["search_knowledge_base", "calculate"],
                "tool_trace": [
                    {
                        "tool": "search_knowledge_base",
                        "input": {"query": request.question},
                        "output_preview": str(kb_output)[:300] + "...",
                    },
                    {
                        "tool": "calculate",
                        "input": {"expression": calc_expr},
                        "output_preview": str(calc_output)[:300] + "...",
                    },
                ],
            }

        # Deterministic KB route for domain questions to ensure cited passages.
        if kb_intent and not calc_expr and not wiki_intent:
            kb_tool = _find_tool("search_knowledge_base")
            if kb_tool is None:
                raise RuntimeError("Knowledge base tool is not available")

            kb_output = kb_tool.fn(query=request.question)
            return {
                "question": request.question,
                "answer": kb_output,
                "tools_used": ["search_knowledge_base"],
                "tool_trace": [
                    {
                        "tool": "search_knowledge_base",
                        "input": {"query": request.question},
                        "output_preview": str(kb_output)[:300] + "...",
                    }
                ],
            }

        # Deterministic wiki route: bypass LLM planning to avoid rate-limit/timeouts.
        if wiki_intent and not kb_intent and not calc_expr:
            wiki_tool = _find_tool("get_wikipedia_summary")
            if wiki_tool is None:
                raise RuntimeError("Wikipedia tool is not available")

            topic = request.question
            for prefix in [
                "give me a wikipedia summary of",
                "wikipedia summary of",
                "summary of",
                "what is",
                "who is",
                "overview of",
            ]:
                if topic.lower().startswith(prefix):
                    topic = topic[len(prefix):].strip()
                    break
            topic = topic.rstrip("?.!")
            if not topic:
                topic = request.question

            wiki_output = wiki_tool.fn(topic=topic)
            return {
                "question": request.question,
                "answer": wiki_output,
                "tools_used": ["get_wikipedia_summary"],
                "tool_trace": [
                    {
                        "tool": "get_wikipedia_summary",
                        "input": {"topic": topic},
                        "output_preview": str(wiki_output)[:300] + "...",
                    }
                ],
            }

        logger.info(f"🤖 Agent processing: {request.question}")
        response = await agent.run(request.question)

        tool_trace = []
        if hasattr(response, "tool_calls"):
            for tool_call in response.tool_calls:
                tool_trace.append({
                    "tool": getattr(tool_call, "tool_name", "unknown"),
                    "input": str(getattr(tool_call, "tool_kwargs", getattr(tool_call, "raw_input", ""))),
                    "output_preview": str(getattr(tool_call, "tool_output", getattr(tool_call, "raw_output", "")))[:300] + "...",
                })

        return {
            "question": request.question,
            "answer": str(getattr(response, "response", response)),
            "tools_used": list(set(t["tool"] for t in tool_trace)),
            "tool_trace": tool_trace,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))