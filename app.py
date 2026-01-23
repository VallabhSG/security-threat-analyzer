# app.py
import streamlit as st
import time
import requests
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain


# Page configuration
st.set_page_config(
    page_title="Security Threat Analyzer",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { padding: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🔒 Security Threat Analyzer Copilot")
st.markdown("Analyze REAL Kaggle security logs using AI. Ask questions about network threats and get instant insights.")

# Sidebar info
st.sidebar.markdown("### 📊 About This Project")
st.sidebar.info("""
**Dataset:** Kaggle Cybersecurity Threat Detection Logs
- 2M+ real network traffic entries (from 6M dataset)
- Ground truth labels (Normal vs Malicious)
- Real-world threat patterns

**Model:** Gemma 3 (1B) with RAG
- Searches real logs for relevant entries
- Analyzes threat patterns
- Provides security insights
""")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load models (cached for speed)
@st.cache_resource
def load_models():
    try:
        print("Loading embeddings...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        print("Loading vector database from REAL logs...")
        vectorstore = FAISS.load_local(
            "faiss_index_real",
            embeddings,
            allow_dangerous_deserialization=True
        )
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        print("Loading LLM (gemma3:1b for low memory)...")
        import requests
        
        # Check if Ollama is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code != 200:
                raise Exception("Ollama not responding")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama service not running. Start with: ollama serve")
        
        try:
            # Force CPU mode to avoid CUDA errors
            import os
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            
            llm = OllamaLLM(
                model="gemma3:1b",  # smaller model fits low VRAM/CPU
                temperature=0,
                base_url="http://localhost:11434",
                num_ctx=1536,  # keep context modest for RAM
                request_timeout=120
            )
            
            # Test the LLM
            test_result = llm.invoke("Hi")
            if test_result is None:
                raise Exception("LLM returned None on test")
            print("✓ LLM test successful")
        except Exception as e:
            print(f"LLM initialization failed: {e}")
            raise Exception(f"Failed to initialize gemma3:1b model. Try restarting Ollama with CPU mode: set OLLAMA_NUM_GPU=0 && ollama serve")
        
        return retriever, llm
    except Exception as e:
        print(f"Error loading models: {e}")
        raise

with st.spinner("⏳ Loading AI models..."):
    try:
        retriever, llm = load_models()
    except Exception as e:
        st.error(f"❌ **Error Loading Models**: {e}")
        st.info("**Solution:**\n1. Start Ollama in CPU mode: `set OLLAMA_NUM_GPU=0 && ollama serve`\n2. In another terminal, preload the small model: `ollama run gemma3:1b`\n3. Refresh this page")
        st.stop()

# Create RAG chain
prompt_template = """You are a security analyst copilot. Analyze REAL security logs and answer the user's question.

REAL Network Logs from Kaggle:
{context}

Question: {input}

Answer based ONLY on the provided logs. Suggest actions for threats."""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "input"]
)

try:
    document_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, document_chain)
except Exception as e:
    print(f"Error creating RAG chain: {e}")
    st.error(f"❌ **Error Creating RAG Chain**: {e}")
    st.stop()

# Example questions
st.sidebar.markdown("### 💡 Example Questions")
examples = [
    "What malicious traffic patterns exist?",
    "List the most dangerous source IPs",
    "What protocols are used in threats?",
    "Show me TCP vs UDP traffic",
    "Identify common attack patterns"
]

if st.sidebar.button("🎯 Show Example"):
    st.session_state.example_shown = True

for example in examples:
    st.sidebar.caption(f"→ {example}")

# Display chat history
st.markdown("### 💬 Analysis History")
if st.session_state.messages:
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message['content'])
        else:
            with st.chat_message("assistant"):
                st.write(message['content'])
else:
    st.info("Ask a question about the security logs to get started!")

# User input
st.markdown("### 🔍 Ask About the Logs")

col1, col2 = st.columns([4, 1])
with col1:
    user_query = st.text_input(
        "Enter your security question:",
        placeholder="e.g., What malicious IPs are in the data?"
    )
with col2:
    search_button = st.button("🔎 Analyze", use_container_width=True)

if search_button and user_query:
    with st.spinner("🔄 Searching REAL logs and analyzing..."):
        try:
            start_time = time.time()
            
            # Get answer from RAG
            result = rag_chain.invoke({"input": user_query})
            answer = result['answer']
            
            elapsed_time = time.time() - start_time
            
            # Store in history
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
            # Display results
            st.success("✓ Analysis complete!")
            
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                st.write(answer)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Response Time", f"{elapsed_time:.2f}s")
            with col2:
                st.metric("Data Source", "Kaggle (2M logs)")
            with col3:
                st.metric("Model", "Gemma3:1B + RAG")
        except Exception as e:
            st.error(f"Error processing query: {e}")
            st.info("Make sure Ollama is running: `ollama run llama3.1`")

# Footer
st.markdown("---")
st.markdown("""
**Built with:** LangChain + Ollama + Streamlit + FAISS
**Dataset:** Kaggle Cybersecurity Threat Detection Logs
**Purpose:** ML Internship Project
""")
