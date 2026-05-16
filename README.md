# AI PDF Chatbot (RAG Assistant) 🚀
### "Unlock your documents' potential with semantic intelligence."
**An end-to-end RAG (Retrieval-Augmented Generation) application to chat with your PDFs using Groq, Qdrant, and FastAPI.**

---

## 2. Demo Preview 📸

![Chat Assistant](docs/images/chat.png)

### 🔗 Quick Links
- **Architecture Overview:** [See Section 6](#6-system-architecture)

---

## 3. Features ✨
- **Secure Authentication:** JWT-based login and registration system.
- **Asynchronous Ingestion:** Celery-powered background processing for PDF text extraction and indexing.
- **Semantic Search:** Multi-stage retrieval using local embeddings and Qdrant Vector DB.
- **Real-time Streaming:** Smooth streaming AI responses using Server-Sent Events (SSE).
- **Rich Citations:** Automatic mapping of AI answers back to specific PDF pages and source chunks.
- **Interactive Dashboard:** Premium UI for managing documents and tracking processing status.

---

## 4. Problem Statement 🧩
Traditional PDF reading is slow and inefficient. Searching for specific information in large documents often involves manual CTRL+F and skimming hundreds of pages. 

**The Pain Points:**
- **Information Overload:** Difficult to synthesize knowledge from multiple large PDFs.
- **Context Loss:** Keyword search fails to understand the *meaning* behind a query.
- **Time Inefficiency:** Users spend 30% of their time just looking for information.

**The Solution:**
AI improves document interaction by treating your PDFs as a searchable knowledge base. It allows you to ask natural language questions and get precise, cited answers instantly.

---

## 5. Solution Overview 🛠️
Our solution implements a standard **Retrieval-Augmented Generation (RAG)** pipeline:
1. **Upload:** User uploads a PDF via the React dashboard.
2. **Extraction:** Backend uses `PyMuPDF` to extract text and metadata.
3. **Chunking:** Text is split into overlapping chunks using `RecursiveTokenChunker`.
4. **Embeddings:** Chunks are converted into 384-dimensional vectors using `all-MiniLM-L6-v2`.
5. **Storage:** Vectors are stored in **Qdrant** with mandatory `user_id` security filters.
6. **Retrieval:** On query, we fetch the most relevant chunks using cosine similarity.
7. **Generation:** The context + query are sent to **Groq (Llama 3)** to generate a final cited response.

---

## 6. System Architecture 🏗️

### 🔄 Request Flow
```mermaid
graph TD
    User((User)) -->|Query| Frontend[React / Next.js]
    Frontend -->|API Request| Backend[FastAPI]
    Backend -->|Search| Qdrant[(Qdrant Vector DB)]
    Backend -->|Context + Query| LLM[Groq - Llama 3]
    LLM -->|Stream| Backend
    Backend -->|SSE| Frontend
    Frontend -->|Render| User
```

**Workflow:**
1. **Frontend:** React + Tailwind CSS handles state and streaming UI.
2. **Backend:** FastAPI manages business logic and task orchestration.
3. **Task Queue:** Celery + Redis handles heavy lifting (extraction/indexing).
4. **Vector DB:** Qdrant stores and retrieves semantic chunks securely.

---

## 7. Tech Stack 💻

| Component | Technology |
|-----------|------------|
| **Frontend** | Next.js 15, Tailwind CSS, Lucide Icons, Axios |
| **Backend** | FastAPI, Celery, SQLAlchemy (Async), Pydantic V2 |
| **AI/ML** | Groq (Llama 3), Sentence Transformers, PyMuPDF |
| **Database** | PostgreSQL (Metadata), Qdrant (Vectors), Redis (Queue) |
| **DevOps** | Docker, Docker Compose, Windows WSL2 |

---

## 8. Folder Structure 📂
```text
pdf-chatbot/
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── api/            # API Endpoints
│   │   ├── services/       # RAG Logic (Embedding, Retrieval, Chat)
│   │   ├── worker/         # Celery Tasks
│   │   └── db/             # SQLAlchemy Models & Repos
│   └── tests/              # Pytest Suite
├── frontend/               # Next.js Application
│   ├── src/
│   │   ├── features/       # Modular features (Chat, Docs, Auth)
│   │   └── store/          # Zustand State Management
├── docs/                   # Documentation & Assets
│   └── images/             # README Screenshots
└── docker-compose.yml      # Orchestration
```

---

## 9. Installation Guide ⚙️

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/pdf-chatbot.git
cd pdf-chatbot
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Start Infrastructure (Docker)
```bash
docker-compose up -d postgres redis qdrant
```

### 5. Run Services
- **Backend:** `uvicorn app.main:app --reload`
- **Worker:** `celery -A app.worker.celery_app worker --pool=solo --loglevel=info`
- **Frontend:** `npm run dev`

---

## 10. Environment Variables 🔑
Create a `.env` file in the `backend/` directory:

| Variable | Description | Where to get? |
|----------|-------------|---------------|
| `GROQ_API_KEY` | API key for LLM | [Groq Console](https://console.groq.com/) |
| `QDRANT_URL` | Vector DB URL | `http://localhost:6333` |
| `DATABASE_URL` | Postgres URL | `postgresql+asyncpg://user:pass@localhost:5432/db` |

---

## 11. How It Works Internally 🧠
- **Text Extraction:** Uses `PyMuPDF` for high-fidelity extraction including metadata (author, title).
- **Chunking Strategy:** 700 tokens per chunk with 120 tokens overlap to ensure semantic continuity.
- **Embedding Generation:** Locally computed `all-MiniLM-L6-v2` embeddings for zero-latency indexing.
- **Similarity Search:** Cosine similarity thresholding (0.10) to ensure high-quality retrieval.
- **Prompt Construction:** Context-injection with system prompts that enforce citations: `[Page X]`.

---

## 12. API Endpoints 🛣️
- `POST /auth/register`: Create new account.
- `POST /documents/upload`: Upload and trigger ingestion.
- `GET /documents`: List user's PDFs.
- `POST /chat/stream`: SSE streaming endpoint for RAG chat.

---

## 13. Challenges Faced 🚧
- **Windows Celery Stability:** Resolved Proactor event loop issues by switching to `SelectorEventLoop` policy.
- **Vector Security:** Implemented mandatory `user_id` filtering in Qdrant to prevent data leakage between users.
- **Streaming Citations:** Designed a custom schema to yield citations at the end of an SSE stream while maintaining UI smoothness.

---

## 14. Future Improvements 🔮
- **Multi-Document Chat:** Cross-reference information between different PDFs.
- **OCR Support:** Integration with Tesseract for scanned/image-based PDFs.
- **Voice Interaction:** Using Whisper for voice-to-query functionality.
- **Advanced Reranking:** Adding a Cross-Encoder reranking step for even higher accuracy.

---

## 15. Deployment 🌐
- **Frontend:** Deployed on **Vercel** for optimal performance.
- **Backend:** Deployed on **Render** using Docker.
- **Database:** Managed **Supabase** (Postgres) and **Qdrant Cloud**.

---

## 16. Screenshots Section 🖼️

| | |
|:---:|:---:|
| ![Login](docs/images/login.png) <br> **Secure Login** | ![Dashboard](docs/images/upload.png) <br> **Document Management** |
| ![Processed](docs/images/dashboard.png) <br> **Successful Ingestion** | ![Chat](docs/images/chat.png) <br> **AI Chat with Citations** |

---

## 17. Learning Outcomes 🎓
- Mastering the **RAG Pipeline** (Extraction -> Embedding -> Search -> LLM).
- Building **Scalable Task Queues** with Celery and Redis.
- Implementing **Secure Vector Retrieval** with Qdrant.
- Handling **Real-time Streaming** in FastAPI and Next.js.

---

## 18. Credits / References 📚
- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [Groq Docs](https://console.groq.com/docs)

---
**License:** MIT License
**Author:** ZEBA NISHA