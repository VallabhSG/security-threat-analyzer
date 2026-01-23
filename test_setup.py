# test_setup.py
print("Python works")

try:
    from langchain_ollama import OllamaLLM
    print("LangChain Ollama works")
except:
    print("LangChain Ollama FAILED")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
    print("Embeddings work")
except:
    print("Embeddings FAILED")

try:
    from langchain_community.vectorstores import FAISS
    print("Vector DB works")
except:
    print("Vector DB FAILED")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("Text splitter works")
except:
    print("Text splitter FAILED")

print("\nAll setup complete!")
