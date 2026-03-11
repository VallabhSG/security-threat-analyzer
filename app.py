"""Streamlit UI for the Security Threat Analyzer.

This is a thin presentation layer — all business logic lives in the
``security_analyzer`` package.
"""

import sys
import time
from pathlib import Path

import streamlit as st

# Ensure the src directory is importable when running with `streamlit run`
_SRC_DIR = str(Path(__file__).resolve().parent / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from security_analyzer.config import settings
from security_analyzer.llm import get_llm
from security_analyzer.rag import create_rag_chain
from security_analyzer.vectorstore import get_retriever
from security_analyzer.agent import create_pandas_agent, get_router_chain
from langchain_ollama import ChatOllama
from security_analyzer.data import load_prepared_data

# ── Page config ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Security Threat Analyzer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    "<style>.main { padding: 2rem; }</style>",
    unsafe_allow_html=True,
)

st.title("🔒 Security Threat Analyzer Copilot")
st.markdown(
    "Analyze REAL Kaggle security logs using AI. "
    "Ask questions about network threats and get instant insights."
)

# ── Sidebar ──────────────────────────────────────────────────────────

st.sidebar.markdown("### 📊 About This Project")
st.sidebar.info(
    f"**Dataset:** Kaggle Cybersecurity Threat Detection Logs\n"
    f"- 2M+ real network traffic entries\n"
    f"- Ground truth labels (Normal vs Malicious)\n"
    f"- Real-world threat patterns\n\n"
    f"**Model:** {settings.ollama_model} with RAG\n"
    f"- Searches real logs for relevant entries\n"
    f"- Analyzes threat patterns\n"
    f"- Provides security insights"
)

st.sidebar.markdown("### 💡 Example Questions")
EXAMPLE_QUESTIONS = [
    "What malicious traffic patterns exist?",
    "List the most dangerous source IPs",
    "What protocols are used in threats?",
    "Show me TCP vs UDP traffic",
    "Identify common attack patterns",
]
for example in EXAMPLE_QUESTIONS:
    st.sidebar.caption(f"→ {example}")

# ── Load models (cached) ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def _load_models():
    """Load and validate the retriever and LLM, then build the RAG chain & agents."""
    retriever = get_retriever()
    llm = get_llm(validate=True)
    chain = create_rag_chain(retriever, llm)
    
    # Setup Pandas Agent & Router
    chat_llm = ChatOllama(model=settings.ollama_model)
    df = load_prepared_data()
    pandas_agent = create_pandas_agent(chat_llm, df)
    router_chain = get_router_chain(chat_llm)
    
    return chain, pandas_agent, router_chain


with st.spinner("⏳ Loading AI models…"):
    try:
        rag_chain, pandas_agent, router_chain = _load_models()
    except Exception as exc:
        st.error(f"❌ **Error Loading Models**: {exc}")
        st.info(
            "**Solution:**\n"
            f"1. Start Ollama: `ollama serve`\n"
            f"2. Pull the model: `ollama pull {settings.ollama_model}`\n"
            "3. Refresh this page"
        )
        st.stop()

# ── Chat history ─────────────────────────────────────────────────────

st.markdown("### 💬 Analysis History")
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
else:
    st.info("Ask a question about the security logs to get started!")

# ── User input ───────────────────────────────────────────────────────

st.markdown("### 🔍 Ask About the Logs")

col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input(
        "Enter your security question:",
        placeholder="e.g., What malicious IPs are in the data?",
    )
with col2:
    search_button = st.button("🔎 Analyze", use_container_width=True)

if search_button and user_query:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    # 2. Show assistant message with streaming
    with st.chat_message("assistant"):
        try:
            start_time = time.time()
            
            with st.spinner("🔄 Classifying query…"):
                route = router_chain.invoke({"question": user_query})
            
            if route.strip() == "ANALYZE":
                used_agent = "Data Analyst Agent"
                with st.spinner("📊 Analyzing entire dataset and calculating…"):
                    result = pandas_agent.invoke({"input": user_query})
                    answer = result.get("output", str(result))
                    st.write(answer)
            else:
                used_agent = "RAG Search Agent"
                def stream_answer():
                    for chunk in rag_chain.stream({"input": user_query}):
                        if "answer" in chunk:
                            yield chunk["answer"]
                
                with st.spinner("🔄 Searching REAL logs and analyzing…"):
                    answer = st.write_stream(stream_answer)
                
            elapsed = time.time() - start_time
            st.session_state.messages.append({"role": "assistant", "content": answer})

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Response Time", f"{elapsed:.2f}s")
            m2.metric("Agent Used", used_agent)
            m3.metric("Data Source", "Kaggle (2M logs)")
            m4.metric("Model", settings.ollama_model)

        except Exception as exc:
            st.error(f"Error processing query: {exc}")
            st.info(f"Make sure Ollama is running: `ollama serve`")

# ── Footer ───────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "**Built with:** LangChain · Ollama · Streamlit · FAISS  \n"
    "**Dataset:** Kaggle Cybersecurity Threat Detection Logs"
)
