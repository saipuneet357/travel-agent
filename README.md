# Awara Chat

An AI-powered travel assistant chatbot with semantic caching, user authentication, and LLM integration.

## Tech Stack

### Frontend
- **Streamlit** - Web application framework for Python
- **Auth0** - Authentication and authorization platform

### Backend Services
- **Ollama** - Local LLM inference server (running models like `granite3.2:2b`, `awara`)
- **FastAPI** - API framework (optional, available for future extensions)

### Data Layer
- **PostgreSQL** - User data and relational storage
- **Redis** (with Redis Stack) - Semantic caching of LLM responses using vector search

### Infrastructure
- **Docker Compose** - Container orchestration for PostgreSQL and Redis

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Layer                               │
│                    (Browser / Streamlit UI)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit Application                        │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐   │
│  │   home.py    │      │  pages/app.py│      │   Auth0      │   │
│  │  (Login)     │──────▶│ (Chat UI)   │◀────▶│ (Auth)       │   │
│  └──────────────┘      └──────────────┘      └──────────────┘   │
│         │                       │                              │
│         └───────────────────────┘                              │
│                    │                                           │
│              db.py (User data)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Redis Cache                          │    │
│  │  (Semantic similarity search for cached responses)     │    │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐        │    │
│  │  │Embeddings│    │  Vector  │    │  Cache   │        │    │
│  │  │ Generation│───▶│  Search  │───▶│ Storage  │        │    │
│  │  └──────────┘    └──────────┘    └──────────┘        │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
│              Cache Miss      │      Cache Hit                   │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Ollama LLM                           │    │
│  │               (Local LLM Inference)                     │    │
│  │              http://localhost:11434                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage                                 │
│                                                                 │
│  ┌──────────────┐              ┌──────────────┐                │
│  │  PostgreSQL  │              │    Redis     │                │
│  │  Users Table │              │    Cache     │                │
│  │  (lara DB)   │              │  (Vectors)   │                │
│  └──────────────┘              └──────────────┘                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **User Authentication**: User logs in via Auth0 (Google OAuth) → User record created/retrieved in PostgreSQL
2. **Chat Query**: User sends message
   - Check Redis cache using semantic similarity (384-dim embeddings)
   - If cache hit: Return cached response
   - If cache miss: Query Ollama LLM → Store response in Redis → Return response

## Key Modules

| File | Purpose | Status |
|------|---------|--------|
| `home.py` | Auth0 login/logout handler | **Used** |
| `pages/app.py` | Main chat interface with streaming | **Used** |
| `db.py` | PostgreSQL connection & user management | **Used** |
| `redis_db.py` | Semantic caching with Redis vector search | **Used** |
| `ml_api.py` | Ollama API client for embeddings & chat | **Used** |
| `model_test.py` | Standalone test for Ollama API | *Unused* |
| `test.py` | Generator function experiments | *Unused* |
| `langchain_test.py` | LangChain SQL experiments | *Unused* |
| `langchain_ollama_connector.py` | LangChain connector utilities | *Unused* |
| `features/service_features.py` | Feature store utilities | *Unused* |
| `features/feature_view.py` | Empty feature view file | *Unused* |
| `online_store/` | Feast feature store examples | *Unused* |

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.10+
- Ollama running locally

### Environment Setup

1. Copy environment templates:
```bash
cp .env.example .env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. Fill in your actual values in `.env` and `.streamlit/secrets.toml`

3. Start infrastructure services:
```bash
docker-compose up -d
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Streamlit app:
```bash
streamlit run home.py
```

### Redis Vector Index Setup

Create the RediSearch index for semantic caching:
```bash
redis-cli FT.CREATE idx:prompts_vss ON JSON PREFIX 1 prompts: SCHEMA $.prompt TEXT $.response TEXT $.prompt_embedding AS vector VECTOR FLAT 6 TYPE FLOAT32 DIM 384 DISTANCE_METRIC COSINE
```

## Configuration

### Auth0 Setup
1. Create an Auth0 application
2. Configure OAuth2 credentials
3. Add to `.streamlit/secrets.toml`:
```toml
[auth.auth0]
domain = "your-domain.auth0.com"
client_id = "YOUR_CLIENT_ID"
client_secret = "YOUR_CLIENT_SECRET"
```

### Ollama Models
Required models:
- `all-minilm` - For embeddings (384-dim)
- `granite3.2:2b` or `awara` - For chat completion

```bash
ollama pull all-minilm
ollama pull granite3.2:2b
```

## Security Considerations

- All secrets stored in environment variables / secrets.toml (gitignored)
- Database credentials use environment variables with defaults for local dev
- Auth0 handles authentication securely via OAuth2

## License

MIT
