# 🔒 Security Threat Analyzer Copilot

An AI-powered security log analysis chatbot that uses **RAG (Retrieval-Augmented Generation)** to analyze 2 million+ network security logs and identify threats, malicious IPs, and attack patterns.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.39-red)
![LangChain](https://img.shields.io/badge/LangChain-1.2-green)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple)

## 🎯 Features

- **2M+ Security Logs** - Trained on real Kaggle cybersecurity threat detection dataset
- **Natural Language Queries** - Ask questions in plain English about security threats
- **Fast Retrieval** - FAISS vector database with sub-second search across millions of documents
- **Local LLM** - Runs entirely on your machine using Ollama (no API keys needed)
- **Low Memory Mode** - Optimized for systems with limited VRAM (4GB+)

## 📊 Dataset

The system is trained on the [Kaggle Cybersecurity Threat Detection Logs](https://www.kaggle.com/) dataset containing:

| Metric | Value |
|--------|-------|
| Total Logs | 2,000,000 |
| Protocols | TCP, HTTP, HTTPS, UDP, ICMP, FTP, SSH |
| Unique Source IPs | 354 |
| Time Range | Jan 2024 - Dec 2024 |

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

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- [Ollama](https://ollama.ai/) installed and running
- 8GB+ RAM recommended
- 4GB+ disk space for vector database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/security-threat-analyzer.git
   cd security-threat-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv rag_env
   
   # Windows
   .\rag_env\Scripts\Activate.ps1
   
   # Linux/Mac
   source rag_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the LLM model**
   ```bash
   ollama pull gemma3:1b
   ```

5. **Start Ollama**
   ```bash
   ollama serve
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

7. **Open in browser**
   ```
   http://localhost:8501
   ```

## 💬 Example Queries

| Query | Description |
|-------|-------------|
| "What malicious IPs exist in the logs?" | Lists dangerous source IPs |
| "Show me SQL injection attacks" | Finds injection attempt patterns |
| "Which IPs are doing brute force attacks?" | Identifies login attack sources |
| "What attack tools were detected?" | Lists tools like NMAP, CURL |
| "What protocols are used in malicious traffic?" | Protocol-based threat analysis |
| "Show threat statistics" | Overall threat summary |

## 📁 Project Structure

```
security_copilot/
├── app.py                    # Streamlit web application
├── evaluate_system.py        # System evaluation & testing
├── quick_test.py             # Quick validation script
├── test_setup.py             # Dependency verification
├── rag_chain_real.py         # RAG chain implementation
├── build_vectordb_real.py    # Vector database builder
├── create_embeddings_real.py # Embedding generator
├── prepare_data.py           # Data preparation script
├── requirements.txt          # Python dependencies
├── prepared_logs.csv         # Processed log dataset (368 MB)
├── faiss_index_real/         # FAISS vector index (3.3 GB)
│   └── index.faiss
└── rag_env/                  # Virtual environment
```

## ⚙️ Configuration

### Model Selection

The default model is `gemma3:1b` (815 MB) optimized for low VRAM. For better responses with more VRAM:

```python
# In app.py, change:
llm = OllamaLLM(model="gemma3:1b", ...)

# To:
llm = OllamaLLM(model="llama3.1", ...)  # Requires 8GB+ VRAM
```

### Available Models

| Model | Size | VRAM Required | Quality |
|-------|------|---------------|---------|
| gemma3:1b | 815 MB | 4GB | Good |
| llama3.1 | 4.9 GB | 8GB+ | Better |
| llama3.1:70b | 40 GB | 48GB+ | Best |

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Basic setup test
python test_setup.py

# Quick system check
python quick_test.py

# Full evaluation (requires Ollama running)
python evaluate_system.py
```

### Expected Output

```
======================================================================
SECURITY THREAT ANALYZER - SYSTEM EVALUATION
======================================================================
✓ Components loaded in 19.13s
✓ Vector database contains 2,000,000 documents
✓ Avg retrieval time: 0.28s
✓ Avg response time: 2.86s
======================================================================
✅ EVALUATION COMPLETE - System ready for deployment
======================================================================
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM Framework**: LangChain 1.2
- **Vector Database**: FAISS
- **Embeddings**: HuggingFace sentence-transformers
- **Local LLM**: Ollama with Gemma/Llama models
- **Data Processing**: Pandas, NumPy

## 📈 Performance

| Metric | Value |
|--------|-------|
| Vector retrieval | ~0.28s |
| LLM response time | 1-8s |
| Documents indexed | 2,000,000 |
| Index size | 3.3 GB |

## 🔧 Troubleshooting

### Ollama Connection Error
```bash
# Make sure Ollama is running
ollama serve
```

### CUDA Out of Memory
```bash
# Use CPU mode or smaller model
# The app automatically uses gemma3:1b for low VRAM
```

### Slow Loading
The first load takes ~60s to load embeddings. Subsequent queries are fast due to Streamlit caching.

## 📄 License

MIT License - feel free to use and modify for your projects.

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, open an issue on GitHub.

---

**Built with ❤️ using LangChain, Ollama, and Streamlit**
