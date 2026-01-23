from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain



print("Step 1: Loading vector database from REAL logs...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
vectorstore = FAISS.load_local(
    "faiss_index_real",
    embeddings,
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

print("✓ Vector database from REAL logs loaded!")

print("\nStep 2: Setting up LLM...")
llm = OllamaLLM(model="gemma3:1b", temperature=0)

print("✓ LLM ready!")

print("\nStep 3: Creating security-focused prompt...")
prompt_template = """You are a security analyst copilot. Analyze the provided REAL security logs and answer the user's question.

REAL Network Log Data (from Kaggle dataset):
{context}

Question: {input}

Instructions:
- Answer based ONLY on the provided REAL logs
- If you find malicious activity, describe it clearly
- Suggest security actions if threats are detected
- Be concise and factual
- If information is not in the logs, say "Not found in the provided logs"

Answer:"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "input"]
)

print("✓ Prompt template created!")

print("\nStep 4: Creating RAG chain with REAL data...")
document_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, document_chain)

print("✓ RAG chain ready with REAL data!")

print("\n" + "="*60)
print("TESTING RAG CHAIN ON REAL DATA")
print("="*60)

# Test queries relevant to real security logs
test_queries = [
    "What malicious network traffic patterns appear in the logs?",
    "Which source IPs have the most suspicious activity?",
    "List all TCP connections with malicious traffic",
    "What are the common threat patterns in this dataset?",
    "Show me normal vs malicious traffic distribution"
]

for i, query in enumerate(test_queries, 1):
    print(f"\n[Test {i}] Query: {query}")
    print("-" * 60)
    
    result = rag_chain.invoke({"input": query})
    answer = result['answer']
    
    print(f"Answer: {answer[:200]}...")
    print()

print("="*60)
print("✓ RAG chain working with REAL Kaggle data!")
print("="*60)
