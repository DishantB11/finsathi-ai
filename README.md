# FinSathi AI – Project README

## Overview
FinSathi AI is an AI-powered Digital Financial Literacy assistant for Indian users.
Built with IBM Granite (via watsonx.ai) and RAG (Retrieval-Augmented Generation).

## Tech Stack
- **AI Model**: IBM Granite (ibm/granite-13b-chat-v2) via watsonx.ai
- **RAG**: LangChain + ChromaDB + Sentence Transformers
- **Backend**: FastAPI (Python)
- **Frontend**: React.js
- **Deployment**: IBM Cloud Code Engine / Cloud Foundry

## Features
- UPI & Digital Payments explanation
- Personal Budgeting guidance
- Loan & EMI calculator knowledge
- Government schemes (Jan Dhan, Mudra, APY, PMSBY)
- Online fraud awareness & prevention
- Bilingual support (English + Hindi)
- RAG with trusted financial knowledge base

## Project Structure
```
FinSathi-AI/
├── backend/
│   ├── main.py            # FastAPI app + IBM Granite integration
│   ├── rag_pipeline.py    # ChromaDB vector store + retrieval
│   ├── knowledge_base.py  # Financial knowledge documents
│   ├── config.py          # IBM credentials configuration
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React chat component
│   │   ├── index.js       # React entry point
│   │   └── index.css      # Global styles
│   └── package.json       # Node dependencies
└── README.md
```

## Running Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/` | API info |
| GET  | `/health` | Health check |
| POST | `/chat` | Send question, get AI answer |
| POST | `/rebuild-knowledge-base` | Rebuild vector store |

## IBM Services Used
- watsonx.ai (IBM Granite model)
- IBM Cloud Object Storage (document storage)
- IBM Code Engine (deployment)
