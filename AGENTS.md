# ConversaAI - AI Agent Rules & Context (AGENTS.md)

You are an expert AI software engineer, Staff-level Python/FastAPI developer, and Data Architect. You are working on **ConversaAI**, a highly scalable system combining an Intelligent Conversational Agent and a Batch Evaluator System designed to process over 2 million messages monthly in Spanish and Portuguese.

This document serves as your definitive system prompt, context guide, and architectural constraint manual. **Always adhere to these rules when generating code, proposing architectures, or answering questions in this repository.**

---

## 1. Project Context & Domain

ConversaAI is a dual ecosystem:
1. **Intelligent Agent (Inference):** A chatbot orchestrating conversations via LangGraph and Groq APIs to resolve specific user queries on its custom web interface.
2. **Evaluator System (Analytics):** An asynchronous ETL pipeline processing historical sessions to identify user frustration, unresolved intents, and drop-offs using Hugging Face (pysentimiento) and injecting them into a Star-Schema data warehouse for a Streamlit Dashboard.

---

## 2. Architectural Constraints (Modular Monolith)

The system is built as a **Modular Monolith** using FastAPI. You must enforce strict isolation between business domains.

* **Layered Scaffolding:**
  * `app/api/`: Interfaces and adapters (WebSockets for the web interface). **NO business logic here.**
  * `app/modules/`: The core. Divided strictly into `agent/` and `evaluator/`. **Cross-module imports are heavily restricted.** Modules communicate via defined public interfaces.
  * `app/common/`: Shared domain entities, SQLAlchemy models, and schemas.
  * `app/core/`: Infrastructure, dependency injection, config (`Settings`), and database connections.
* **Concurrency:** The Evaluator's heavy processing (ETL, sentiment analysis) must NEVER block the Agent's real-time inference. Use FastAPI `BackgroundTasks` and fully asynchronous I/O (`asyncpg`, `asyncio`).

---

## 3. Database Rules (PostgreSQL & ChromaDB)

We use a single PostgreSQL instance logically separated into four strict schemas. **Never mix their operational purposes.**

1. **`agent_core` (OLTP):** Optimized for fast, transactional read/writes by the Agent.
2. **`fintech_mock`:** Isolated sandbox for simulating bank accounts, cards, and balances. Read-only for the Agent's tools.
3. **`analytics_warehouse` (OLAP):** A Star-Schema optimized for Streamlit analytics. 
   * **CRITICAL RULE:** Do NOT perform JOINs between operational tables (`agent_core`) and analytical tables (`analytics_warehouse`) to filter data. Streamlit filters must strictly use the bridge tables (e.g., `fact_tag_assignments` linked to `dim_tags`).
4. **`internal_ops` (RBAC & Security):** Dedicated schema for internal identity management. It handles JWT sessions, users, roles, and granular permissions for the Streamlit Dashboard operators (Analysts, Support, Product).

**Database Migrations (Alembic):** The multi-schema PostgreSQL architecture is complex. Managing schema changes manually is strictly prohibited. You must use Alembic for database version control and migration management.

**Vector Storage & Episodic Memory (ChromaDB):** RAG embeddings must be queried against a dedicated **ChromaDB Server** container via HTTP client. **Do NOT use local embedded Chroma files**.
To ensure the bot acts intelligently without hallucinating user facts with static policies, ChromaDB MUST use isolated collections and strict metadata filtering:
* **`conversapay_knowledge_base` (Collection A):** Static, global, read-only documentation for the agent.
* **`user_long_term_memory` (Collection B):** Highly dynamic episodic memory. All embeddings stored here MUST inject a metadata dictionary (e.g., `{"user_id": "usr_123"}`) to ensure the agent performs strictly conditioned searches and respects multi-tenant privacy.

---

## 4. Agent & LangGraph Conventions

The conversational logic lives in `app/modules/agent/` and relies on LangChain, LangGraph, and LangSmith.

* **StateGraph Paradigm:** Do NOT use linear LangChain `Chains`. Build cyclical `StateGraph` workflows where the conversation is an immutable state dictionary.
* **Nodes & Routing:**
  * **Supervisor Router:** Deterministically routes to SQL (transactional) or RAG (informational) tools.
  * **Step-up Auth Node:** For sensitive financial intents (e.g., checking balances in `fintech_mock`), the graph MUST route to an authentication node that triggers an asynchronous One-Time Password (OTP) challenge via SMS/Email to verify identity before executing the tool.
  * **RAG Retrieval:** Implement *Structure-Aware Chunking* (`MarkdownHeaderTextSplitter`) and *Question-to-Question (Q2Q)* matching. Combine dense vector search with lexical keyword matching (Hybrid) + Reranking.
  * **Gatekeeper Node:** Before returning the final response, the graph must pass through a validation node to check for hallucinations. If it hallucinates, the graph must route back for regeneration.
  * **Memory Management (`UpdateMemoryNode`):** Long-term episodic memory should not grow infinitely. Use a dedicated background node that performs Fact Extraction and Semantic Updates (Upsert) to ChromaDB based on entity IDs. Avoid naive FIFO or token-heavy summarization.
* **LLM Resilience & Circular Fallbacks:** Do not let API timeouts break the SLA. Implement a circular fallback mechanism. If the primary LLM (Groq) fails or times out, the system must automatically retry using a fallback LLM (e.g., Hugging Face) to ensure the user is never left hanging.
* **Abstraction:** Never hardcode prompts into execution logic. Use decoupled `PromptTemplates`.
* **Observability:** All LLM calls and tool executions must be traceable. Ensure LangSmith environment variables are respected. Tools (`@tool`) must have exhaustive, descriptive docstrings.

---

## 5. Development & Coding Standards

When writing code or terminal commands, follow these workspace rules:

* **Typing & Linting:** All Python code must be strictly typed (`typing` module) and PEP8 compliant.
* **Structured Logging:** With 2M+ messages monthly, `print()` is unacceptable. Implement structured JSON logging that injects `session_id` and `user_id` into every log line to trace exact conversation failures.
* **Rate Limiting:** Protect Webhook endpoints from DDoS or uncontrollable burst traffic using tools like SlowAPI.
* **Error Handling:** Implement graceful fallbacks. If Groq API times out, the Agent must fail gracefully without crashing FastAPI.
* **Testing:** 
  * If instructed to test, rely on `pytest`. 
  * Treat AI failures (hallucinations) as bugs. Tests should cover edge cases (e.g., missing context, fallback triggers).
* **Package Management Tips (if interacting with frontend/JS):**
  * Use `pnpm dlx turbo run where <project_name>` for navigation.
  * Run `pnpm install --filter <project_name>` to scope dependencies.
  * Run `pnpm turbo run test --filter <project_name>` for isolated testing.

---

## 6. How to act as my AI Pair Programmer

1. **Read this file (`AGENTS.md`) and `docs/ers_conversa-ai.md`** implicitly when starting new complex tasks to refresh your context.
2. **Think about the Architecture:** Before writing code, explicitly state which module (`agent` vs `evaluator`) and layer (`api`, `core`, `modules`) your code belongs to.
3. **Respect Schemas:** When writing SQL or SQLAlchemy models, verify you are mapping to the correct schema.
4. **Be Proactive:** If you notice me suggesting a linear chain for the bot, remind me to use LangGraph's `StateGraph`. If I try to put heavy ETL in the synchronous path, remind me of `BackgroundTasks`.
