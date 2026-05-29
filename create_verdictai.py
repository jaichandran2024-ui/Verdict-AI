import os
import zipfile
from pathlib import Path

PROJECT_NAME = "verdictai"

files = {

# ── Root config ──────────────────────────────────────────────────────────────

".gitignore": """\
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/
.eggs/
*.egg
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
coverage.xml

# Node / Next.js
node_modules/
.next/
out/
.npm
*.tsbuildinfo
next-env.d.ts

# Env
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Docker
*.log

# ChromaDB
chroma_db/
""",

"LICENSE": """\
MIT License

Copyright (c) 2025 Jaichandra N

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",

"README.md": """\
# VerdictAI ⚖️

An AI-powered courtroom simulation platform featuring multi-agent legal debate, RAG-based evidence retrieval, and real-time verdict generation.

## Features

- 🤖 **Multi-Agent System** — Judge, Prosecutor, Defense Lawyer, and Witness agents
- 📄 **Evidence Upload** — PDF and DOCX parsing with semantic indexing
- 🔍 **RAG Pipeline** — ChromaDB vector store with semantic search
- ⚡ **Streaming Verdicts** — Real-time AI-powered verdict generation
- 🔐 **Authentication** — JWT-based auth with protected routes
- 📊 **Admin Dashboard** — Case analytics and user management
- 🌙 **Dark Mode** — Full dark/light theme support

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Shadcn UI |
| Backend | FastAPI, LangChain, Gemini API |
| Vector DB | ChromaDB |
| Auth | JWT (python-jose) |
| File Parsing | PyMuPDF, python-docx |

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- Gemini API Key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example .env   # fill in your keys
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
cp ../.env.example .env.local  # fill in NEXT_PUBLIC_API_URL
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

See `.env.example` for all required variables.

## Docker

```bash
docker-compose up --build
```

## Running Tests

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm test
```

## Project Structure

```
verdictai/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── agents/   # LangChain agent definitions
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Config, security, logging
│   │   ├── db/       # ChromaDB client
│   │   ├── models/   # Pydantic schemas
│   │   └── services/ # Business logic
│   └── tests/
├── frontend/         # Next.js application
│   ├── app/          # App Router pages
│   ├── components/   # UI components
│   ├── lib/          # API client, utils
│   └── types/
└── docker-compose.yml
```

## License

MIT © Jaichandra N
""",

".env.example": """\
# Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# JWT
SECRET_KEY=your_super_secret_jwt_key_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
""",

"docker-compose.yml": """\
version: "3.9"

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: verdictai_backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
      - CHROMA_PERSIST_DIR=/app/chroma_db
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
    volumes:
      - chroma_data:/app/chroma_db
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: verdictai_frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  chroma_data:
""",

# ── GitHub Actions ────────────────────────────────────────────────────────────

".github/workflows/ci.yml": """\
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: pip
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio httpx
      - name: Run backend tests
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          SECRET_KEY: test_secret_key
          ALGORITHM: HS256
          ACCESS_TOKEN_EXPIRE_MINUTES: 60
          CHROMA_PERSIST_DIR: /tmp/chroma_test
        run: pytest tests/ -v

  frontend-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: npm
          cache-dependency-path: frontend/package-lock.json
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --passWithNoTests

  docker-build:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker images
        run: docker-compose build
""",

".github/workflows/deploy.yml": """\
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
          RENDER_SERVICE_ID: ${{ secrets.RENDER_BACKEND_SERVICE_ID }}
        run: |
          curl -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \\
            -H "Authorization: Bearer ${RENDER_API_KEY}" \\
            -H "Content-Type: application/json"

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - name: Deploy to Vercel
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
        run: |
          npm i -g vercel
          cd frontend
          vercel --prod --token=$VERCEL_TOKEN
""",

# ── Backend ───────────────────────────────────────────────────────────────────

"backend/Dockerfile": """\
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/uploads /app/chroma_db

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",

"backend/requirements.txt": """\
fastapi==0.111.0
uvicorn[standard]==0.30.1
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.7.1
pydantic-settings==2.3.1
langchain==0.2.5
langchain-google-genai==1.0.6
langchain-chroma==0.1.1
chromadb==0.5.3
google-generativeai==0.7.2
PyMuPDF==1.24.5
python-docx==1.1.2
aiofiles==23.2.1
httpx==0.27.0
pytest==8.2.2
pytest-asyncio==0.23.7
""",

"backend/app/__init__.py": "",

"backend/app/main.py": """\
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import auth, cases, agents, evidence, admin, analytics
from app.db.chroma import get_chroma_client

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting VerdictAI backend...")
    client = get_chroma_client()
    client.heartbeat()
    logger.info("ChromaDB connected.")
    yield
    logger.info("Shutting down VerdictAI backend.")


app = FastAPI(
    title="VerdictAI API",
    description="Multi-agent AI courtroom simulation platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "VerdictAI API"}
""",

"backend/app/core/__init__.py": "",

"backend/app/core/config.py": """\
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
""",

"backend/app/core/logging.py": """\
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Quiet noisy libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
""",

"backend/app/core/security.py": """\
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store (replace with a real DB in production)
_users: dict[str, dict] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def get_user(email: str) -> Optional[dict]:
    return _users.get(email)


def create_user(email: str, password: str, name: str, role: str = "user") -> dict:
    user = {
        "email": email,
        "name": name,
        "hashed_password": hash_password(password),
        "role": role,
    }
    _users[email] = user
    return {k: v for k, v in user.items() if k != "hashed_password"}


def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return {k: v for k, v in user.items() if k != "hashed_password"}


def list_users() -> list[dict]:
    return [{k: v for k, v in u.items() if k != "hashed_password"} for u in _users.values()]
""",

"backend/app/core/deps.py": """\
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_token

bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    return current_user
""",

"backend/app/db/__init__.py": "",

"backend/app/db/chroma.py": """\
import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_or_create_collection(name: str) -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
""",

"backend/app/models/__init__.py": "",

"backend/app/models/schemas.py": """\
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class CaseCreate(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=10)
    charges: List[str]


class CaseResponse(BaseModel):
    id: str
    title: str
    description: str
    charges: List[str]
    status: str
    created_by: str
    created_at: str


class AgentRole(str, Enum):
    judge = "judge"
    prosecutor = "prosecutor"
    defense = "defense"
    witness = "witness"


class DebateRequest(BaseModel):
    case_id: str
    message: str
    role: AgentRole
    history: List[dict] = []


class VerdictRequest(BaseModel):
    case_id: str
    debate_history: List[dict]


class EvidenceIngestRequest(BaseModel):
    case_id: str


class SearchRequest(BaseModel):
    case_id: str
    query: str
    top_k: int = 5
""",

"backend/app/services/__init__.py": "",

"backend/app/services/case_store.py": """\
\"\"\"In-memory case store (swap for PostgreSQL in production).\"\"\"
import uuid
from datetime import datetime, timezone
from typing import Optional

_cases: dict[str, dict] = {}


def create_case(title: str, description: str, charges: list[str], created_by: str) -> dict:
    case_id = str(uuid.uuid4())
    case = {
        "id": case_id,
        "title": title,
        "description": description,
        "charges": charges,
        "status": "open",
        "created_by": created_by,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": None,
    }
    _cases[case_id] = case
    return case


def get_case(case_id: str) -> Optional[dict]:
    return _cases.get(case_id)


def list_cases(user_email: Optional[str] = None) -> list[dict]:
    if user_email:
        return [c for c in _cases.values() if c["created_by"] == user_email]
    return list(_cases.values())


def update_verdict(case_id: str, verdict: str) -> Optional[dict]:
    case = _cases.get(case_id)
    if case:
        case["verdict"] = verdict
        case["status"] = "closed"
    return case


def get_stats() -> dict:
    total = len(_cases)
    closed = sum(1 for c in _cases.values() if c["status"] == "closed")
    return {"total_cases": total, "closed_cases": closed, "open_cases": total - closed}
""",

"backend/app/services/file_parser.py": """\
\"\"\"Parse PDF and DOCX files into plain text.\"\"\"
import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document

logger = logging.getLogger(__name__)


def parse_pdf(data: bytes) -> str:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
        texts = [page.get_text() for page in doc]
        doc.close()
        return "\\n".join(texts).strip()
    except Exception as exc:
        logger.error("PDF parse failed: %s", exc)
        raise ValueError(f"Could not parse PDF: {exc}") from exc


def parse_docx(data: bytes) -> str:
    try:
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\\n".join(paragraphs).strip()
    except Exception as exc:
        logger.error("DOCX parse failed: %s", exc)
        raise ValueError(f"Could not parse DOCX: {exc}") from exc


def parse_file(filename: str, data: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return parse_pdf(data)
    if suffix in (".docx", ".doc"):
        return parse_docx(data)
    raise ValueError(f"Unsupported file type: {suffix}")
""",

"backend/app/services/rag.py": """\
\"\"\"RAG pipeline: embed evidence chunks into ChromaDB.\"\"\"
import logging
import uuid
from typing import List

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.core.config import settings
from app.db.chroma import get_or_create_collection

logger = logging.getLogger(__name__)

_embeddings: GoogleGenerativeAIEmbeddings | None = None


def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.GEMINI_API_KEY,
        )
    return _embeddings


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap
    return chunks


def ingest_evidence(case_id: str, filename: str, text: str) -> int:
    \"\"\"Chunk text and upsert into ChromaDB collection for the case.\"\"\"
    collection = get_or_create_collection(f"case_{case_id}")
    embedder = _get_embeddings()
    chunks = _chunk_text(text)
    if not chunks:
        return 0

    ids = [str(uuid.uuid4()) for _ in chunks]
    embeddings = embedder.embed_documents(chunks)
    metadatas = [{"filename": filename, "chunk": i} for i in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    logger.info("Ingested %d chunks for case %s from %s", len(chunks), case_id, filename)
    return len(chunks)


def semantic_search(case_id: str, query: str, top_k: int = 5) -> List[dict]:
    \"\"\"Return top_k relevant evidence chunks for query.\"\"\"
    collection = get_or_create_collection(f"case_{case_id}")
    embedder = _get_embeddings()
    query_embedding = embedder.embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count() or 1),
        include=["documents", "metadatas", "distances"],
    )
    output = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        output.append({"text": doc, "metadata": meta, "score": 1 - dist})
    return output
""",

"backend/app/agents/__init__.py": "",

"backend/app/agents/prompts.py": """\
JUDGE_SYSTEM = \"\"\"You are an impartial Judge in a courtroom simulation.
Your role is to:
- Maintain order and ensure fair proceedings
- Rule on the admissibility of evidence
- Ask clarifying questions to both sides
- Ensure legal procedures are followed
- Deliver a final verdict based on presented evidence and arguments

Base your rulings on the evidence provided. Be authoritative, fair, and concise.
When delivering a verdict, structure it as:
VERDICT: [GUILTY/NOT GUILTY]
REASONING: [detailed legal reasoning]
SENTENCE: [if applicable]\"\"\"

PROSECUTOR_SYSTEM = \"\"\"You are an aggressive but ethical Prosecutor.
Your role is to:
- Present the strongest possible case against the defendant
- Cross-examine witnesses effectively
- Highlight inconsistencies in the defense's arguments
- Present evidence in the most damning light
- Argue for conviction based on facts

Be persuasive, logical, and relentless. Use the evidence provided to build a compelling case.\"\"\"

DEFENSE_SYSTEM = \"\"\"You are a skilled Defense Lawyer committed to your client's innocence.
Your role is to:
- Challenge the prosecution's evidence and witnesses
- Present alternative interpretations of events
- Highlight reasonable doubt
- Protect your client's constitutional rights
- Argue for acquittal or reduced charges

Be creative, thorough, and empathetic. Always find angles that benefit your client.\"\"\"

WITNESS_SYSTEM = \"\"\"You are a Witness in the courtroom.
Your role is to:
- Answer questions truthfully based on what you observed
- Stay consistent with your testimony
- Respond only to what you were directly asked
- Show appropriate emotion and uncertainty where relevant
- Not speculate beyond your direct knowledge

Be realistic, specific, and credible.\"\"\"


def build_agent_prompt(role: str, case_context: str, evidence_context: str) -> str:
    base = {
        "judge": JUDGE_SYSTEM,
        "prosecutor": PROSECUTOR_SYSTEM,
        "defense": DEFENSE_SYSTEM,
        "witness": WITNESS_SYSTEM,
    }[role]

    return f\"\"\"{base}

CASE CONTEXT:
{case_context}

RELEVANT EVIDENCE:
{evidence_context}

Respond in character. Be concise and legally precise.\"\"\".strip()
""",

"backend/app/agents/agent.py": """\
\"\"\"LangChain-powered agent execution with Gemini.\"\"\"
import logging
from typing import AsyncIterator, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings
from app.agents.prompts import build_agent_prompt
from app.services.rag import semantic_search
from app.services.case_store import get_case

logger = logging.getLogger(__name__)


def _build_llm(streaming: bool = False) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        streaming=streaming,
    )


def _history_to_messages(history: List[dict]) -> List:
    mapping = []
    for msg in history:
        if msg["role"] == "user":
            mapping.append(HumanMessage(content=msg["content"]))
        else:
            mapping.append(AIMessage(content=msg["content"]))
    return mapping


async def run_agent(
    case_id: str,
    role: str,
    user_message: str,
    history: List[dict],
) -> str:
    case = get_case(case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found")

    evidence_chunks = semantic_search(case_id, user_message, top_k=5)
    evidence_context = "\\n\\n".join(c["text"] for c in evidence_chunks) or "No evidence uploaded yet."

    case_context = (
        f"Title: {case['title']}\\n"
        f"Charges: {', '.join(case['charges'])}\\n"
        f"Description: {case['description']}"
    )

    system_prompt = build_agent_prompt(role, case_context, evidence_context)
    llm = _build_llm(streaming=False)

    messages = [SystemMessage(content=system_prompt)]
    messages.extend(_history_to_messages(history))
    messages.append(HumanMessage(content=user_message))

    response = await llm.ainvoke(messages)
    return response.content


async def stream_verdict(case_id: str, debate_history: List[dict]) -> AsyncIterator[str]:
    \"\"\"Stream a final verdict from the judge agent.\"\"\"
    case = get_case(case_id)
    if not case:
        raise ValueError(f"Case {case_id} not found")

    evidence_chunks = semantic_search(case_id, "final verdict summary evidence", top_k=10)
    evidence_context = "\\n\\n".join(c["text"] for c in evidence_chunks) or "No evidence."

    case_context = (
        f"Title: {case['title']}\\n"
        f"Charges: {', '.join(case['charges'])}\\n"
        f"Description: {case['description']}"
    )

    from app.agents.prompts import build_agent_prompt
    system_prompt = build_agent_prompt("judge", case_context, evidence_context)

    debate_summary = "\\n".join(
        f"[{m['role'].upper()}]: {m['content']}" for m in debate_history
    )
    final_message = (
        f"The debate has concluded. Here is the full debate transcript:\\n\\n{debate_summary}\\n\\n"
        "Please deliver your final VERDICT now."
    )

    llm = _build_llm(streaming=True)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=final_message)]

    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content
""",

"backend/app/api/__init__.py": "",

"backend/app/api/routes/__init__.py": "",

"backend/app/api/routes/auth.py": """\
import logging
from fastapi import APIRouter, HTTPException, status, Depends

from app.models.schemas import UserRegister, UserLogin, TokenResponse
from app.core.security import create_user, authenticate_user, create_access_token, get_user
from app.core.deps import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister):
    if get_user(body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = create_user(body.email, body.password, body.name)
    token = create_access_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    logger.info("New user registered: %s", body.email)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    user = authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user["email"], "role": user["role"], "name": user["name"]})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
""",

"backend/app/api/routes/cases.py": """\
import logging
from fastapi import APIRouter, HTTPException, Depends

from app.models.schemas import CaseCreate, CaseResponse
from app.core.deps import get_current_user
from app.services.case_store import create_case, get_case, list_cases

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CaseResponse, status_code=201)
async def create_new_case(body: CaseCreate, current_user: dict = Depends(get_current_user)):
    case = create_case(body.title, body.description, body.charges, current_user["sub"])
    logger.info("Case created: %s by %s", case["id"], current_user["sub"])
    return case


@router.get("/", response_model=list[CaseResponse])
async def get_my_cases(current_user: dict = Depends(get_current_user)):
    role = current_user.get("role")
    email = current_user["sub"]
    if role == "admin":
        return list_cases()
    return list_cases(user_email=email)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case_detail(case_id: str, current_user: dict = Depends(get_current_user)):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
""",

"backend/app/api/routes/evidence.py": """\
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends

from app.core.deps import get_current_user
from app.services.file_parser import parse_file
from app.services.rag import ingest_evidence, semantic_search
from app.models.schemas import SearchRequest
from app.services.case_store import get_case

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload")
async def upload_evidence(
    case_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10 MB)")

    try:
        text = parse_file(file.filename, data)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    chunks = ingest_evidence(case_id, file.filename, text)
    return {"filename": file.filename, "chunks_ingested": chunks, "case_id": case_id}


@router.post("/search")
async def search_evidence(body: SearchRequest, current_user: dict = Depends(get_current_user)):
    results = semantic_search(body.case_id, body.query, top_k=body.top_k)
    return {"results": results, "query": body.query}
""",

"backend/app/api/routes/agents.py": """\
import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.core.deps import get_current_user
from app.models.schemas import DebateRequest, VerdictRequest
from app.agents.agent import run_agent, stream_verdict
from app.services.case_store import get_case, update_verdict

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/debate")
async def debate(body: DebateRequest, current_user: dict = Depends(get_current_user)):
    case = get_case(body.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    try:
        reply = await run_agent(body.case_id, body.role.value, body.message, body.history)
    except Exception as exc:
        logger.error("Agent error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    return {"role": body.role.value, "content": reply}


@router.post("/verdict/stream")
async def verdict_stream(body: VerdictRequest, current_user: dict = Depends(get_current_user)):
    case = get_case(body.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    full_verdict = []

    async def generator():
        async for token in stream_verdict(body.case_id, body.debate_history):
            full_verdict.append(token)
            yield token
        # Persist final verdict
        update_verdict(body.case_id, "".join(full_verdict))

    return StreamingResponse(generator(), media_type="text/plain")
""",

"backend/app/api/routes/admin.py": """\
from fastapi import APIRouter, Depends
from app.core.deps import require_admin
from app.core.security import list_users
from app.services.case_store import list_cases, get_stats

router = APIRouter()


@router.get("/users")
async def get_all_users(admin: dict = Depends(require_admin)):
    return list_users()


@router.get("/cases")
async def get_all_cases(admin: dict = Depends(require_admin)):
    return list_cases()


@router.get("/stats")
async def get_stats_admin(admin: dict = Depends(require_admin)):
    stats = get_stats()
    stats["total_users"] = len(list_users())
    return stats
""",

"backend/app/api/routes/analytics.py": """\
from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.services.case_store import list_cases, get_stats

router = APIRouter()


@router.get("/overview")
async def analytics_overview(current_user: dict = Depends(get_current_user)):
    stats = get_stats()
    my_cases = list_cases(user_email=current_user["sub"])
    stats["my_cases"] = len(my_cases)
    stats["my_closed"] = sum(1 for c in my_cases if c["status"] == "closed")
    return stats
""",

"backend/tests/__init__.py": "",

"backend/tests/test_auth.py": """\
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_register_and_login():
    payload = {"email": "test@verdictai.io", "password": "Password123", "name": "Test User"}
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert "access_token" in data

    r2 = client.post("/api/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_me_requires_auth():
    r = client.get("/api/auth/me")
    assert r.status_code == 403


def test_me_with_token():
    payload = {"email": "me@verdictai.io", "password": "Password123", "name": "Me User"}
    r = client.post("/api/auth/register", json=payload)
    token = r.json()["access_token"]
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["sub"] == payload["email"]
""",

"backend/tests/test_cases.py": """\
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _get_token(email="case_user@verdictai.io"):
    client.post("/api/auth/register", json={"email": email, "password": "Password123", "name": "Case User"})
    r = client.post("/api/auth/login", json={"email": email, "password": "Password123"})
    return r.json()["access_token"]


def test_create_and_list_case():
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"title": "State vs Smith", "description": "Defendant accused of fraud.", "charges": ["fraud"]}
    r = client.post("/api/cases/", json=payload, headers=headers)
    assert r.status_code == 201
    case_id = r.json()["id"]

    r2 = client.get("/api/cases/", headers=headers)
    assert r2.status_code == 200
    assert any(c["id"] == case_id for c in r2.json())
""",

# ── Frontend ──────────────────────────────────────────────────────────────────

"frontend/Dockerfile": """\
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
""",

"frontend/package.json": """\
{
  "name": "verdictai-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "jest"
  },
  "dependencies": {
    "next": "15.0.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "typescript": "^5.4.5",
    "@types/node": "^20.12.12",
    "@types/react": "^18.3.1",
    "@types/react-dom": "^18.3.0",
    "tailwindcss": "^3.4.3",
    "postcss": "^8.4.38",
    "autoprefixer": "^10.4.19",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "lucide-react": "^0.383.0",
    "tailwind-merge": "^2.3.0",
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "axios": "^1.7.2"
  },
  "devDependencies": {
    "eslint": "^8.57.0",
    "eslint-config-next": "15.0.0",
    "@testing-library/react": "^15.0.7",
    "@testing-library/jest-dom": "^6.4.5",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0"
  }
}
""",

"frontend/tsconfig.json": """\
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
""",

"frontend/tailwind.config.ts": """\
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [],
};
export default config;
""",

"frontend/postcss.config.js": """\
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
""",

"frontend/next.config.ts": """\
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },
};

export default nextConfig;
""",

"frontend/app/globals.css": """\
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 224 71.4% 4.1%;
    --card: 0 0% 100%;
    --card-foreground: 224 71.4% 4.1%;
    --primary: 262.1 83.3% 57.8%;
    --primary-foreground: 210 20% 98%;
    --secondary: 220 14.3% 95.9%;
    --secondary-foreground: 220.9 39.3% 11%;
    --muted: 220 14.3% 95.9%;
    --muted-foreground: 220 8.9% 46.1%;
    --accent: 220 14.3% 95.9%;
    --accent-foreground: 220.9 39.3% 11%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 20% 98%;
    --border: 220 13% 91%;
    --input: 220 13% 91%;
    --ring: 262.1 83.3% 57.8%;
    --radius: 0.5rem;
  }
  .dark {
    --background: 224 71.4% 4.1%;
    --foreground: 210 20% 98%;
    --card: 224 71.4% 4.1%;
    --card-foreground: 210 20% 98%;
    --primary: 263.4 70% 50.4%;
    --primary-foreground: 210 20% 98%;
    --secondary: 215 27.9% 16.9%;
    --secondary-foreground: 210 20% 98%;
    --muted: 215 27.9% 16.9%;
    --muted-foreground: 217.9 10.6% 64.9%;
    --accent: 215 27.9% 16.9%;
    --accent-foreground: 210 20% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 20% 98%;
    --border: 215 27.9% 16.9%;
    --input: 215 27.9% 16.9%;
    --ring: 263.4 70% 50.4%;
  }
}

@layer base {
  * { @apply border-border; }
  body { @apply bg-background text-foreground; }
}
""",

"frontend/app/layout.tsx": """\
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import { Toaster } from "@/components/ui/toaster";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VerdictAI – AI Courtroom Simulator",
  description: "Multi-agent AI courtroom simulation platform with real-time verdict generation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
""",

"frontend/app/page.tsx": """\
import Link from "next/link";
import { Scale, Shield, Gavel, Users } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background to-secondary flex flex-col items-center justify-center px-4">
      <div className="max-w-4xl w-full text-center space-y-8">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Scale className="w-12 h-12 text-primary" />
          <h1 className="text-5xl font-bold tracking-tight">VerdictAI</h1>
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Experience AI-powered courtroom simulations with multi-agent debate, RAG-based evidence
          retrieval, and real-time verdict generation.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-10">
          {[
            { icon: Gavel, title: "Judge Agent", desc: "Impartial AI judge delivering fair rulings" },
            { icon: Shield, title: "Defense Lawyer", desc: "AI defense counsel fighting for acquittal" },
            { icon: Users, title: "Prosecutor", desc: "Relentless AI prosecutor building the case" },
            { icon: Scale, title: "Witness Agent", desc: "Realistic AI witnesses providing testimony" },
          ].map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-card border rounded-xl p-6 text-left hover:shadow-lg transition-shadow">
              <Icon className="w-8 h-8 text-primary mb-3" />
              <h3 className="font-semibold text-lg">{title}</h3>
              <p className="text-muted-foreground text-sm mt-1">{desc}</p>
            </div>
          ))}
        </div>

        <div className="flex gap-4 justify-center mt-8">
          <Link
            href="/auth/register"
            className="bg-primary text-primary-foreground px-8 py-3 rounded-lg font-semibold hover:opacity-90 transition-opacity"
          >
            Get Started
          </Link>
          <Link
            href="/auth/login"
            className="border border-border px-8 py-3 rounded-lg font-semibold hover:bg-accent transition-colors"
          >
            Sign In
          </Link>
        </div>
      </div>
    </main>
  );
}
""",

"frontend/app/auth/login/page.tsx": """\
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Scale } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.post("/api/auth/login", form);
      login(data.access_token, data.user);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Scale className="w-10 h-10 text-primary mx-auto mb-2" />
          <h1 className="text-3xl font-bold">Welcome back</h1>
          <p className="text-muted-foreground mt-1">Sign in to VerdictAI</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-card border rounded-xl p-8 space-y-4">
          {error && <p className="text-destructive text-sm bg-destructive/10 p-3 rounded">{error}</p>}
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-primary-foreground py-2 rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition"
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
          <p className="text-center text-sm text-muted-foreground">
            No account?{" "}
            <Link href="/auth/register" className="text-primary hover:underline">Register</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
""",

"frontend/app/auth/register/page.tsx": """\
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Scale } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.post("/api/auth/register", form);
      login(data.access_token, data.user);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Scale className="w-10 h-10 text-primary mx-auto mb-2" />
          <h1 className="text-3xl font-bold">Create account</h1>
          <p className="text-muted-foreground mt-1">Join VerdictAI</p>
        </div>
        <form onSubmit={handleSubmit} className="bg-card border rounded-xl p-8 space-y-4">
          {error && <p className="text-destructive text-sm bg-destructive/10 p-3 rounded">{error}</p>}
          <div>
            <label className="block text-sm font-medium mb-1">Full Name</label>
            <input
              type="text"
              required
              minLength={2}
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary text-primary-foreground py-2 rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-primary hover:underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
""",

"frontend/app/dashboard/page.tsx": """\
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Scale, Plus, Gavel, LogOut, BarChart2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

interface Case {
  id: string;
  title: string;
  description: string;
  charges: string[];
  status: string;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const { token, user, logout } = useAuth();
  const [cases, setCases] = useState<Case[]>([]);
  const [stats, setStats] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    Promise.all([
      api.get("/api/cases/", token),
      api.get("/api/analytics/overview", token),
    ]).then(([casesData, statsData]) => {
      setCases(casesData);
      setStats(statsData);
    }).finally(() => setLoading(false));
  }, [token, router]);

  if (loading) return <div className="min-h-screen flex items-center justify-center"><p>Loading...</p></div>;

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Scale className="w-6 h-6 text-primary" />
          <span className="font-bold text-lg">VerdictAI</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            {user?.name}
          </span>
          <button onClick={() => { logout(); router.push("/"); }} className="text-muted-foreground hover:text-foreground">
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold">My Cases</h1>
          <Link href="/dashboard/cases/new"
            className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90">
            <Plus className="w-4 h-4" /> New Case
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Total Cases", value: stats.my_cases ?? 0, icon: Gavel },
            { label: "Closed Cases", value: stats.my_closed ?? 0, icon: BarChart2 },
            { label: "Open Cases", value: (stats.my_cases ?? 0) - (stats.my_closed ?? 0), icon: Scale },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="bg-card border rounded-xl p-5 flex items-center gap-4">
              <Icon className="w-8 h-8 text-primary" />
              <div>
                <p className="text-2xl font-bold">{value}</p>
                <p className="text-muted-foreground text-sm">{label}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {cases.length === 0 && (
            <p className="text-muted-foreground col-span-3 text-center py-12">
              No cases yet. Create your first case to get started.
            </p>
          )}
          {cases.map(c => (
            <Link key={c.id} href={`/dashboard/cases/${c.id}`}
              className="bg-card border rounded-xl p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{c.title}</h3>
                <span className={`text-xs px-2 py-1 rounded-full ${c.status === "closed" ? "bg-green-500/20 text-green-400" : "bg-yellow-500/20 text-yellow-400"}`}>
                  {c.status}
                </span>
              </div>
              <p className="text-sm text-muted-foreground line-clamp-2">{c.description}</p>
              <div className="mt-3 flex flex-wrap gap-1">
                {c.charges.map(ch => (
                  <span key={ch} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                    {ch}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
""",

"frontend/app/dashboard/cases/new/page.tsx": """\
"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Scale, Plus, X } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function NewCasePage() {
  const router = useRouter();
  const { token } = useAuth();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [charges, setCharges] = useState<string[]>([""]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const filteredCharges = charges.filter(c => c.trim());
    if (!filteredCharges.length) { setError("Add at least one charge"); return; }
    setLoading(true);
    try {
      const data = await api.post("/api/cases/", { title, description, charges: filteredCharges }, token!);
      router.push(`/dashboard/cases/${data.id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create case");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card px-6 py-4 flex items-center gap-3">
        <Scale className="w-6 h-6 text-primary" />
        <span className="font-bold text-lg">VerdictAI</span>
        <span className="text-muted-foreground">/</span>
        <span className="text-muted-foreground">New Case</span>
      </nav>
      <div className="max-w-2xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Create New Case</h1>
        <form onSubmit={handleSubmit} className="bg-card border rounded-xl p-8 space-y-5">
          {error && <p className="text-destructive text-sm bg-destructive/10 p-3 rounded">{error}</p>}
          <div>
            <label className="block text-sm font-medium mb-1">Case Title</label>
            <input required value={title} onChange={e => setTitle(e.target.value)}
              placeholder="State vs. John Doe"
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Case Description</label>
            <textarea required rows={4} value={description} onChange={e => setDescription(e.target.value)}
              placeholder="Describe the case, events, and context..."
              className="w-full border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary resize-none" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Charges</label>
            {charges.map((c, i) => (
              <div key={i} className="flex gap-2 mb-2">
                <input value={c} onChange={e => { const n = [...charges]; n[i] = e.target.value; setCharges(n); }}
                  placeholder="e.g. Grand Theft Auto"
                  className="flex-1 border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary" />
                {charges.length > 1 && (
                  <button type="button" onClick={() => setCharges(charges.filter((_, j) => j !== i))}
                    className="text-destructive hover:opacity-70"><X className="w-5 h-5" /></button>
                )}
              </div>
            ))}
            <button type="button" onClick={() => setCharges([...charges, ""])}
              className="flex items-center gap-1 text-sm text-primary hover:underline mt-1">
              <Plus className="w-4 h-4" /> Add Charge
            </button>
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-primary text-primary-foreground py-2 rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 transition">
            {loading ? "Creating..." : "Create Case"}
          </button>
        </form>
      </div>
    </div>
  );
}
""",

"frontend/app/dashboard/cases/[id]/page.tsx": """\
"use client";
import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Scale, Upload, Gavel, Shield, Users, FileText, Send, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Role = "judge" | "prosecutor" | "defense" | "witness";

interface Message { role: Role | "user" | "verdict"; content: string; }

const ROLE_CONFIG: Record<Role, { label: string; icon: React.ElementType; color: string }> = {
  judge: { label: "Judge", icon: Gavel, color: "text-yellow-400" },
  prosecutor: { label: "Prosecutor", icon: Users, color: "text-red-400" },
  defense: { label: "Defense", icon: Shield, color: "text-blue-400" },
  witness: { label: "Witness", icon: FileText, color: "text-green-400" },
};

export default function CasePage() {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const router = useRouter();

  const [caseData, setCaseData] = useState<Record<string, unknown> | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [activeRole, setActiveRole] = useState<Role>("prosecutor");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [verdictLoading, setVerdictLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    api.get(`/api/cases/${id}`, token).then(setCaseData);
  }, [id, token, router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const data = await api.post("/api/agents/debate", {
        case_id: id, message: input, role: activeRole, history,
      }, token!);
      setMessages(prev => [...prev, { role: data.role, content: data.content }]);
    } finally {
      setLoading(false);
    }
  }

  async function generateVerdict() {
    setVerdictLoading(true);
    const history = messages.map(m => ({ role: m.role, content: m.content }));
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/agents/verdict/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ case_id: id, debate_history: history }),
    });
    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let verdict = "";
    setMessages(prev => [...prev, { role: "verdict", content: "" }]);
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      verdict += decoder.decode(value, { stream: true });
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "verdict", content: verdict };
        return updated;
      });
    }
    setVerdictLoading(false);
  }

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("case_id", id as string);
    try {
      await api.upload("/api/evidence/upload", formData, token!);
      setMessages(prev => [...prev, {
        role: "judge",
        content: `Evidence uploaded: "${file.name}" has been indexed and is now available for the court.`,
      }]);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <nav className="border-b bg-card px-6 py-4 flex items-center gap-3 shrink-0">
        <Scale className="w-6 h-6 text-primary" />
        <span className="font-bold text-lg">VerdictAI</span>
        <span className="text-muted-foreground">/</span>
        <span className="text-muted-foreground truncate max-w-xs">{(caseData?.title as string) ?? "Loading..."}</span>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div className="w-64 border-r bg-card p-4 flex flex-col gap-4 shrink-0">
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-2 uppercase tracking-wide">Agents</h3>
            {(Object.keys(ROLE_CONFIG) as Role[]).map(role => {
              const { label, icon: Icon, color } = ROLE_CONFIG[role];
              return (
                <button key={role} onClick={() => setActiveRole(role)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition mb-1 ${activeRole === role ? "bg-primary/20 text-primary" : "hover:bg-accent"}`}>
                  <Icon className={`w-4 h-4 ${color}`} />
                  {label}
                </button>
              );
            })}
          </div>

          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-2 uppercase tracking-wide">Evidence</h3>
            <input ref={fileRef} type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" />
            <button onClick={() => fileRef.current?.click()} disabled={uploading}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm border hover:bg-accent disabled:opacity-50">
              <Upload className="w-4 h-4" />
              {uploading ? "Uploading..." : "Upload Evidence"}
            </button>
          </div>

          <div className="mt-auto">
            <button onClick={generateVerdict} disabled={verdictLoading || messages.length < 2}
              className="w-full flex items-center gap-2 bg-primary text-primary-foreground px-3 py-2 rounded-lg text-sm font-semibold hover:opacity-90 disabled:opacity-50">
              <Zap className="w-4 h-4" />
              {verdictLoading ? "Generating..." : "Get Verdict"}
            </button>
          </div>
        </div>

        {/* Courtroom */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.length === 0 && (
              <div className="text-center text-muted-foreground mt-20">
                <Gavel className="w-12 h-12 mx-auto mb-3 opacity-30" />
                <p>Select an agent and begin the proceedings.</p>
              </div>
            )}
            {messages.map((m, i) => {
              const isUser = m.role === "user";
              const isVerdict = m.role === "verdict";
              const cfg = !isUser && !isVerdict ? ROLE_CONFIG[m.role as Role] : null;
              return (
                <div key={i} className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-2xl rounded-xl px-4 py-3 text-sm whitespace-pre-wrap ${
                    isUser ? "bg-primary text-primary-foreground" :
                    isVerdict ? "bg-yellow-500/10 border border-yellow-500/30 text-foreground w-full" :
                    "bg-card border text-foreground"
                  }`}>
                    {!isUser && cfg && (
                      <p className={`text-xs font-semibold mb-1 ${cfg.color}`}>{cfg.label}</p>
                    )}
                    {isVerdict && <p className="text-xs font-semibold mb-1 text-yellow-400">⚖️ VERDICT</p>}
                    {m.content}
                  </div>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>

          <div className="border-t bg-card px-4 py-3 flex gap-3 items-center shrink-0">
            <span className="text-xs text-muted-foreground">
              Speaking as <span className="text-primary font-medium">{ROLE_CONFIG[activeRole].label}</span>
            </span>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage()}
              placeholder={`${ROLE_CONFIG[activeRole].label} speaks...`}
              className="flex-1 border rounded-lg px-3 py-2 bg-background focus:outline-none focus:ring-2 focus:ring-primary text-sm"
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}
              className="bg-primary text-primary-foreground p-2 rounded-lg hover:opacity-90 disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
""",

"frontend/app/admin/page.tsx": """\
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Scale, Users, Gavel, BarChart2 } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AdminPage() {
  const router = useRouter();
  const { token, user } = useAuth();
  const [stats, setStats] = useState<Record<string, number>>({});
  const [users, setUsers] = useState<Record<string, string>[]>([]);
  const [cases, setCases] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    if (user?.role !== "admin") { router.push("/dashboard"); return; }
    Promise.all([
      api.get("/api/admin/stats", token),
      api.get("/api/admin/users", token),
      api.get("/api/admin/cases", token),
    ]).then(([s, u, c]) => { setStats(s); setUsers(u); setCases(c); });
  }, [token, user, router]);

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card px-6 py-4 flex items-center gap-3">
        <Scale className="w-6 h-6 text-primary" />
        <span className="font-bold text-lg">VerdictAI Admin</span>
      </nav>
      <div className="max-w-6xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: "Total Users", value: stats.total_users ?? 0, icon: Users },
            { label: "Total Cases", value: stats.total_cases ?? 0, icon: Gavel },
            { label: "Open Cases", value: stats.open_cases ?? 0, icon: BarChart2 },
            { label: "Closed Cases", value: stats.closed_cases ?? 0, icon: Scale },
          ].map(({ label, value, icon: Icon }) => (
            <div key={label} className="bg-card border rounded-xl p-4 flex items-center gap-3">
              <Icon className="w-6 h-6 text-primary" />
              <div>
                <p className="text-xl font-bold">{value}</p>
                <p className="text-muted-foreground text-xs">{label}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-card border rounded-xl p-5">
            <h2 className="font-semibold mb-4">Users ({users.length})</h2>
            <div className="space-y-2">
              {users.map(u => (
                <div key={u.email} className="flex justify-between text-sm py-2 border-b last:border-0">
                  <span>{u.name}</span>
                  <span className="text-muted-foreground">{u.email}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-card border rounded-xl p-5">
            <h2 className="font-semibold mb-4">Recent Cases ({cases.length})</h2>
            <div className="space-y-2">
              {cases.slice(0, 10).map((c) => (
                <div key={c.id as string} className="flex justify-between text-sm py-2 border-b last:border-0">
                  <span className="truncate max-w-xs">{c.title as string}</span>
                  <span className={`text-xs ${c.status === "closed" ? "text-green-400" : "text-yellow-400"}`}>
                    {c.status as string}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
""",

"frontend/lib/api.ts": """\
const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request(method: string, path: string, body?: unknown, token?: string): Promise<unknown> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

async function upload(path: string, formData: FormData, token: string): Promise<unknown> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export const api = {
  get: (path: string, token?: string) => request("GET", path, undefined, token),
  post: (path: string, body: unknown, token?: string) => request("POST", path, body, token),
  upload,
};
""",

"frontend/lib/auth.ts": """\
"use client";
import { useState, useCallback } from "react";

interface User { email: string; name: string; role: string; }

let _token: string | null = null;
let _user: User | null = null;

if (typeof window !== "undefined") {
  _token = localStorage.getItem("verdictai_token");
  const u = localStorage.getItem("verdictai_user");
  if (u) _user = JSON.parse(u);
}

export function useAuth() {
  const [token, setToken] = useState<string | null>(_token);
  const [user, setUser] = useState<User | null>(_user);

  const login = useCallback((newToken: string, newUser: User) => {
    _token = newToken;
    _user = newUser;
    if (typeof window !== "undefined") {
      localStorage.setItem("verdictai_token", newToken);
      localStorage.setItem("verdictai_user", JSON.stringify(newUser));
    }
    setToken(newToken);
    setUser(newUser);
  }, []);

  const logout = useCallback(() => {
    _token = null;
    _user = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("verdictai_token");
      localStorage.removeItem("verdictai_user");
    }
    setToken(null);
    setUser(null);
  }, []);

  return { token, user, login, logout };
}
""",

"frontend/components/theme-provider.tsx": """\
"use client";
import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ThemeProviderProps } from "next-themes/dist/types";

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>;
}
""",

"frontend/components/ui/toaster.tsx": """\
"use client";
import { useToast } from "@/components/ui/use-toast";
import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from "@/components/ui/toast";

export function Toaster() {
  const { toasts } = useToast();
  return (
    <ToastProvider>
      {toasts.map(({ id, title, description, action, ...props }) => (
        <Toast key={id} {...props}>
          <div className="grid gap-1">
            {title && <ToastTitle>{title}</ToastTitle>}
            {description && <ToastDescription>{description}</ToastDescription>}
          </div>
          {action}
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  );
}
""",

"frontend/components/ui/toast.tsx": """\
"use client";
import * as React from "react";
import * as ToastPrimitives from "@radix-ui/react-toast";
import { X } from "lucide-react";

const ToastProvider = ToastPrimitives.Provider;
const ToastViewport = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Viewport>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Viewport>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Viewport
    ref={ref}
    className={"fixed top-0 z-[100] flex max-h-screen w-full flex-col-reverse p-4 sm:bottom-0 sm:right-0 sm:top-auto sm:flex-col md:max-w-[420px] " + (className || "")}
    {...props}
  />
));
ToastViewport.displayName = ToastPrimitives.Viewport.displayName;

const Toast = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Root>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Root
    ref={ref}
    className={"group pointer-events-auto relative flex w-full items-center justify-between space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all bg-background text-foreground " + (className || "")}
    {...props}
  />
));
Toast.displayName = ToastPrimitives.Root.displayName;

const ToastClose = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Close>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Close>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Close
    ref={ref}
    className={"absolute right-2 top-2 rounded-md p-1 opacity-0 transition-opacity group-hover:opacity-100 " + (className || "")}
    {...props}
  >
    <X className="h-4 w-4" />
  </ToastPrimitives.Close>
));
ToastClose.displayName = ToastPrimitives.Close.displayName;

const ToastTitle = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Title>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Title>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Title ref={ref} className={"text-sm font-semibold " + (className || "")} {...props} />
));
ToastTitle.displayName = ToastPrimitives.Title.displayName;

const ToastDescription = React.forwardRef<
  React.ElementRef<typeof ToastPrimitives.Description>,
  React.ComponentPropsWithoutRef<typeof ToastPrimitives.Description>
>(({ className, ...props }, ref) => (
  <ToastPrimitives.Description ref={ref} className={"text-sm opacity-90 " + (className || "")} {...props} />
));
ToastDescription.displayName = ToastPrimitives.Description.displayName;

export { ToastProvider, ToastViewport, Toast, ToastClose, ToastTitle, ToastDescription };
export type ToastProps = React.ComponentPropsWithoutRef<typeof Toast>;
""",

"frontend/components/ui/use-toast.ts": """\
import { useState, useCallback } from "react";

type Toast = { id: string; title?: string; description?: string; variant?: "default" | "destructive" };

let _toasts: Toast[] = [];
let _listeners: Array<(toasts: Toast[]) => void> = [];

function notify() { _listeners.forEach(l => l([..._toasts])); }

export function toast(t: Omit<Toast, "id">) {
  const id = Math.random().toString(36).slice(2);
  _toasts = [..._toasts, { ...t, id }];
  notify();
  setTimeout(() => {
    _toasts = _toasts.filter(x => x.id !== id);
    notify();
  }, 5000);
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>(_toasts);
  const subscribe = useCallback((fn: (t: Toast[]) => void) => {
    _listeners.push(fn);
    return () => { _listeners = _listeners.filter(l => l !== fn); };
  }, []);
  useState(() => { const unsub = subscribe(setToasts); return unsub; });
  return { toasts, toast };
}
""",

"frontend/types/index.ts": """\
export interface Case {
  id: string;
  title: string;
  description: string;
  charges: string[];
  status: "open" | "closed";
  created_by: string;
  created_at: string;
  verdict?: string;
}

export interface User {
  email: string;
  name: string;
  role: "user" | "admin";
}

export interface DebateMessage {
  role: "judge" | "prosecutor" | "defense" | "witness" | "user" | "verdict";
  content: string;
}

export interface EvidenceChunk {
  text: string;
  metadata: { filename: string; chunk: number };
  score: number;
}
""",

"frontend/jest.config.js": """\
const nextJest = require("next/jest");
const createJestConfig = nextJest({ dir: "./" });
module.exports = createJestConfig({
  testEnvironment: "jest-environment-jsdom",
  setupFilesAfterFramework: ["@testing-library/jest-dom"],
});
""",

"frontend/app/dashboard/cases/[id]/loading.tsx": """\
export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-3">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-muted-foreground text-sm">Loading courtroom...</p>
      </div>
    </div>
  );
}
""",

}


def create_files():
    base = Path(PROJECT_NAME)
    for path_str, content in files.items():
        target = base / path_str
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        print(f"  Created: {target}")


def create_zip():
    zip_name = f"{PROJECT_NAME}.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(Path(PROJECT_NAME).rglob("*")):
            if path.is_file():
                zf.write(path)
                print(f"  Zipped: {path}")
    print(f"\n✅ Archive ready: {zip_name}")


if __name__ == "__main__":
    print(f"🏛️  Generating VerdictAI repository...\n")
    create_files()
    print(f"\n📦 Creating zip archive...")
    create_zip()
    print(f"\n🎉 Done! Upload '{PROJECT_NAME}.zip' to GitHub.")
    print(f"   Or cd into '{PROJECT_NAME}/' and run 'git init && git add . && git commit -m \"Initial commit\"'")
