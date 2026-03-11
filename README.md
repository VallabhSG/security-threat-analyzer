# 🔒 Security Threat Analyzer Copilot

An AI-powered security log analysis chatbot that uses **RAG (Retrieval-Augmented Generation)** to analyze 2 million+ network security logs and identify threats, malicious IPs, and attack patterns.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)
![LangChain](https://img.shields.io/badge/LangChain-1.2-green)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)

## 🎯 Features

- **2M+ Security Logs** — Trained on real Kaggle cybersecurity threat detection dataset
- **Natural Language Queries** — Ask questions in plain English about security threats
- **Fast Retrieval** — FAISS vector database with sub-second search across millions of documents
- **Local LLM** — Runs entirely on your machine using Ollama (no API keys needed)
- **Low Memory Mode** — Optimized for systems with limited VRAM (4GB+)

## 📊 Dataset

| Metric | Value |
|--------|-------|
| Total Logs | 2,000,000 |
| Protocols | TCP, HTTP, HTTPS, UDP, ICMP, FTP, SSH |
| Unique Source IPs | 354 |
| Time Range | Jan 2024 – Dec 2024 |

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User Query    │────▶│  FAISS Vector DB │────▶│  Relevant Logs  │
└─────────────────┘     │   (2M documents) │     └────────┬────────┘
                        └──────────────────┘              │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│    Response     │◀────│   Ollama LLM     │◀────│  RAG Context    │
│                 │     │   (gemma3:1b)    │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 📁 Project Structure

```
security-threat-analyzer/
├── src/
│   └── security_analyzer/        # Core Python package
│       ├── __init__.py            # Package init + version
│       ├── __main__.py            # python -m entry point
│       ├── config.py              # Centralized settings (.env support)
│       ├── embeddings.py          # Embedding model factory
│       ├── vectorstore.py         # FAISS load / build / save
│       ├── llm.py                 # Ollama LLM + health checks
│       ├── rag.py                 # RAG chain + prompt templates
│       ├── data.py                # Data prep + validation
│       ├── evaluate.py            # Evaluation suite
│       └── cli.py                 # CLI subcommands
├── app.py                         # Streamlit UI (thin layer)
├── deploy/
│   ├── create_service.sh          # systemd service setup
│   └── oracle_setup.sh            # Oracle Cloud VM setup
├── pyproject.toml                 # Project metadata + deps
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Configuration template
├── .gitignore
├── start_ollama_cpu.bat           # Windows CPU-mode launcher
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed
- 8GB+ RAM recommended
- 4GB+ disk space for vector database

### Installation

```bash
# Clone
git clone https://github.com/VallabhSG/security-threat-analyzer.git
cd security-threat-analyzer

# Virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows
# source .venv/bin/activate          # Linux/Mac

# Install
pip install -r requirements.txt
pip install -e .                     # editable install of the package

# Configuration (optional — defaults work out of the box)
cp .env.example .env                 # edit values as needed
```

### Set Up Ollama

```bash
ollama serve                         # start the server
ollama pull gemma3:1b                # download the model (~815 MB)
```

### Run the App

```bash
streamlit run app.py
# Open http://localhost:8501
```

## 🛠️ CLI Reference

All pipeline operations are available via a unified CLI:

```bash
# Check Ollama connectivity
python -m security_analyzer check-health

# Prepare raw CSV → embedding-ready logs
python -m security_analyzer prepare-data -i log_data.csv

# Build FAISS vector index from prepared data
python -m security_analyzer build-index

# Run full evaluation suite
python -m security_analyzer evaluate

# See all options
python -m security_analyzer --help
```

## ⚙️ Configuration

All settings are configurable via environment variables or a `.env` file.
See [`.env.example`](.env.example) for the full list. Key options:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `gemma3:1b` | Ollama model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
| `RETRIEVER_K` | `5` | Number of docs to retrieve per query |
| `FAISS_INDEX_PATH` | `faiss_index_real` | Path to FAISS index directory |

### Model Options

| Model | Size | VRAM Required | Quality |
|-------|------|---------------|---------|
| gemma3:1b | 815 MB | 4GB | Good |
| llama3.1 | 4.9 GB | 8GB+ | Better |
| llama3.1:70b | 40 GB | 48GB+ | Best |

To switch models, set `OLLAMA_MODEL=llama3.1` in your `.env` file.

## 💬 Example Queries

| Query | Description |
|-------|-------------|
| "What malicious IPs exist in the logs?" | Lists dangerous source IPs |
| "Show me SQL injection attacks" | Finds injection attempt patterns |
| "Which IPs are doing brute force attacks?" | Identifies login attack sources |
| "What attack tools were detected?" | Lists tools like NMAP, CURL |
| "What protocols are used in malicious traffic?" | Protocol-based threat analysis |

## 📈 Performance

| Metric | Value |
|--------|-------|
| Vector retrieval | ~0.28s |
| LLM response time | 1-8s |
| Documents indexed | 2,000,000 |
| Index size | 3.3 GB |

## 🔧 Troubleshooting

**Ollama won't connect** — Make sure it's running: `ollama serve`

**CUDA out of memory** — Use CPU mode: `start_ollama_cpu.bat` (Windows) or `OLLAMA_NUM_GPU=0 ollama serve`

**Slow first load** — The initial load takes ~60s for embeddings. Subsequent queries are cached by Streamlit.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| LLM Framework | LangChain |
| Vector Database | FAISS |
| Embeddings | HuggingFace sentence-transformers |
| Local LLM | Ollama (Gemma / Llama) |
| Data | Pandas, NumPy |

## 📄 License

MIT License — feel free to use and modify for your projects.

---

**Built with ❤️ using LangChain, Ollama, and Streamlit**
