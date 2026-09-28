# 🌊 MARINE-SHIELD
### AI-Powered Marine Pollution Detection, Assessment & Grounded Response System

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B.svg)](https://streamlit.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-MobileNetV3-EE4C2C.svg)](https://pytorch.org)
[![RAG](https://img.shields.io/badge/RAG-FAISS%20%2B%20SentenceTransformers-7928CA.svg)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 1. Project Overview

**MARINE-SHIELD** is an enterprise-ready, AI-driven marine and coastal environmental protection platform. It provides end-to-end intelligence for coastal observers, environmental responders, research scientists, and municipal agencies:

1. **Computer Vision Classification:** Detects visible coastal and marine debris across 6 standard classes (*Plastic Waste, Fishing Net, Glass, Metal, Organic Waste, Other Waste*) using transfer learning with MobileNetV3.
2. **Explainable Severity Assessment:** Multi-factor triage scoring (`LOW`, `MEDIUM`, `HIGH`) combining category ecological threat with visual density, edge clutter, and confidence weighting.
3. **RAG Environmental Intelligence:** Automatic semantic retrieval of marine conservation and cleanup guidance from a persistent FAISS vector store.
4. **Grounded AI Recommendations:** Factually constrained recommendations formatted into 5 standardized sections (*Detection Explanation, Environmental Significance, Recommended Response, Monitoring Considerations, Limitations*).
5. **Interactive Q&A:** Semantic search and grounding for environmental inquiries and coastal incident triage.
6. **PDF Assessment Reports:** Publication-grade incident reports formatted according to international coastal survey standards with embedded visual evidence and metadata.

---

## 2. System Architecture

```
                                     USER / OBSERVER
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     ▼                                             ▼
          Streamlit Frontend (Port 8501)                Mobile / Drone Camera
                     │                                             │
                     └──────────────────────┬──────────────────────┘
                                            │ HTTP / Multipart Upload
                                            ▼
                               FastAPI Backend (Port 8000)
                                            │
                     ┌──────────────────────┼──────────────────────┐
                     ▼                      ▼                      ▼
           [Image Preprocessing]    [SQLite Database]      [PDF Generator]
            - Integrity check        - Analyses table       - ReportLab engine
            - Resize & Normalize     - Sources table        - Publication spec
            - Feature extraction     - Reports table        - Auto-numbering
                     │
                     ▼
           [Computer Vision Model]
            - MobileNetV3-Small
            - Softmax probabilities
            - Low-confidence filter
                     │
                     ▼
           [Prototype Severity Module]
            - Hazard weight matrix
            - Visual clutter score
            - Rule-based rationale
                     │
                     ▼
           [RAG Semantic Retrieval]
            - Sentence Transformers (all-MiniLM-L6-v2)
            - Persistent FAISS IndexFlatIP (Cosine)
            - 6 Specialized Environmental Manuals
                     │
                     ▼
           [Grounded AI Synthesizer]
            - Google Gemini / OpenAI / Offline Grounded Synthesizer
            - Strict anti-hallucination system prompt
            - 5-part structured environmental guidance
```

---

## 3. Technology Stack

- **Frontend:** Streamlit 1.38+ with custom ocean-themed CSS and interactive cards
- **Backend:** FastAPI, Uvicorn, Pydantic v2
- **Computer Vision:** PyTorch, torchvision, MobileNetV3, PIL (Pillow)
- **RAG & Vector Search:** Sentence Transformers (`all-MiniLM-L6-v2`), FAISS-CPU
- **Generative AI:** Google Gemini (`google-genai`), OpenAI, or deterministic offline grounded synthesizer
- **Database:** SQLite with SQLAlchemy ORM
- **Reports:** ReportLab Platypus PDF generator
- **Testing:** Pytest (24 automated tests across all pipelines)
- **Containerization:** Docker, Docker Compose

---

## 4. Marine Pollution Classes

Configurable in `ml/config.py`:
1. **Plastic Waste:** Polyethylene bottles, packaging film, microplastic precursors.
2. **Fishing Net:** Abandoned, lost, or discarded fishing gear (ALDFG) causing acute ghost-fishing mortality.
3. **Glass:** Discarded glass beverage containers, broken shards posing physical laceration hazards.
4. **Metal:** Corroded aluminum, steel food tins, oxidized marine debris.
5. **Organic Waste:** Pelagic sargassum inundations, decomposing macroalgae, wrack-line detritus.
6. **Other Waste:** Industrial rubber, tires, composite debris requiring manual triage.

---

## 5. Local Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.14
- Git

### Step 1: Clone Repository & Create Environment
```bash
git clone https://github.com/your-org/marine-shield.git
cd marine-shield

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables
```bash
cp .env.example .env
```
Edit `.env` to set your desired options:
```env
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
BACKEND_URL=http://localhost:8000

DATABASE_URL=sqlite:///./marine_shield.db
VECTOR_DB_PATH=./vectorstore
MODEL_PATH=./models/marine_shield_model.pth
LOW_CONFIDENCE_THRESHOLD=0.60

# LLM Provider Options: offline | gemini | openai
LLM_PROVIDER=offline
LLM_MODEL=gemini-2.5-flash
LLM_API_KEY=
```

---

## 6. Model Training & Evaluation

### Step 1: Prepare or Generate Dataset
The project includes an automatic starter coastal dataset generator in `data/create_samples.py`:
```bash
python -m data.create_samples
```

### Step 2: Train MobileNetV3 Classifier
```bash
python -m ml.train --epochs 5 --batch-size 8 --lr 0.0003
```
Output:
- Checkpoint: `models/marine_shield_model.pth`
- Empirical Metrics: `models/evaluation_metrics.json`
- Generates accuracy, precision, recall, F1-score, and confusion matrix.

### Step 3: Evaluate Model
```bash
python -c "from ml.evaluate import load_evaluation_metrics; print(load_evaluation_metrics())"
```

---

## 7. RAG Knowledge Base Ingestion

Ingest environmental markdown manuals into the persistent FAISS vector index:
```bash
python -m rag.ingest
```
Documents indexed from `data/knowledge_base/`:
- `marine_plastic_pollution.md` (KB-DOC-001)
- `ghost_fishing_nets_impact.md` (KB-DOC-002)
- `marine_glass_metal_debris.md` (KB-DOC-003)
- `organic_coastal_waste.md` (KB-DOC-004)
- `coastal_cleanup_guidelines.md` (KB-DOC-005)
- `environmental_monitoring_protocols.md` (KB-DOC-006)

---

## 8. Running the Application

### Option A: Run Backend & Frontend Separately

**Terminal 1 (Backend API):**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Health: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

**Terminal 2 (Frontend Dashboard):**
```bash
python -m streamlit run frontend/app.py --server.port 8501
```
- Web Application: [http://localhost:8501](http://localhost:8501)

---

## 9. Docker Deployment

### Run with Docker Compose
```bash
# Build and run containers
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Access Services
- **Streamlit Web Application:** [http://localhost:8501](http://localhost:8501)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

## 10. Automated Testing

Run the comprehensive pytest suite:
```bash
python -m pytest -v
```
All 24 test cases verify:
- Image validation, format checks, and corruption detection
- MobileNetV3 inference and top-k class probabilities
- Explainable severity scoring and low-confidence dampening
- SentenceTransformers embedding generation and FAISS retrieval
- Grounded AI response generation across all 5 sections
- ReportLab PDF generation and file integrity
- SQLite database transactions and relationship cascading
- FastAPI API endpoints (`/health`, `/analyze`, `/ask`, `/reports`, `/analyses`, `/evaluation`, `/knowledge`)

---

## 11. REST API Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status and root links |
| `GET` | `/api/health` | Component operational health status |
| `POST` | `/api/analyze` | Upload and analyze marine photo |
| `POST` | `/api/ask` | Ask grounded environmental questions |
| `POST` | `/api/reports` | Generate structured PDF incident report |
| `GET` | `/api/reports` | List all archived reports |
| `GET` | `/api/reports/{id}/download` | Download PDF assessment report |
| `GET` | `/api/analysis/{id}` | Retrieve specific analysis by ID |
| `GET` | `/api/analyses` | List recent analyses for dashboard |
| `GET` | `/api/evaluation` | Verified test metrics and confusion matrix |
| `GET` | `/api/knowledge` | Knowledge base status and chunk stats |
| `POST` | `/api/knowledge/reindex` | Trigger persistent vectorstore reindexing |

---

## 12. Important Safety & Prototype Disclaimers

1. **Not Official Regulatory Certification:** MARINE-SHIELD is an AI decision-support tool. Predictions, severity scores, and recommendations do not constitute official environmental regulatory citations or legal liability assessments.
2. **Human-in-the-Loop Required:** Any prediction marked with low confidence (< 0.60) or high severity must be confirmed on-site by certified coastal management personnel before dispatching hazmat or specialized recovery equipment.
3. **No Hallucinated Data:** The RAG generator strictly grounds recommendations on indexed scientific documents. If an answer cannot be grounded, the system explicitly reports insufficient knowledge base information.

---

## 13. License
MIT License. Developed for ocean conservation and coastal environmental protection.
