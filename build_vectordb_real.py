# build_vectordb_real.py (FIXED IMPORT)
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document  # ← FIXED IMPORT

print("Step 1: Loading prepared real logs...")
df = pd.read_csv('prepared_logs.csv')

print(f"✓ Loaded {len(df):,} real log entries")

# Step 2: Convert to LangChain documents
print("\nStep 2: Converting to LangChain documents...")
documents = []

for idx, row in df.iterrows():
    doc = Document(
        page_content=row['log_text'],
        metadata={
            'source_ip': row.get('source_ip', 'N/A'),
            'protocol': row.get('protocol', 'N/A'),
            'request_path': row.get('request_path', 'N/A'),
            'user_agent': row.get('user_agent', 'N/A'),
            'timestamp': row.get('timestamp', 'N/A'),
            'index': idx
        }
    )
    documents.append(doc)
    
    if (idx + 1) % 500 == 0:
        print(f"  Processed {idx + 1:,} documents...")

print(f"✓ Created {len(documents):,} documents from real data")

# Step 3: Split into chunks
print("\nStep 3: Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
splits = splitter.split_documents(documents)

print(f"✓ Created {len(splits):,} chunks")

# Step 4: Create embeddings
print("\nStep 4: Creating embeddings from real logs...")
print("(Processing in batches to handle large dataset...)")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 5: Build vector database incrementally
print("\nStep 5: Building FAISS vector database in batches...")
batch_size = 10000  # Smaller batches for better memory management
vectorstore = None

for i in range(0, len(splits), batch_size):
    batch = splits[i:i+batch_size]
    batch_num = i//batch_size + 1
    total_batches = (len(splits)-1)//batch_size + 1
    
    print(f"  Processing batch {batch_num}/{total_batches} ({len(batch):,} documents)...")
    
    if vectorstore is None:
        # Create initial vectorstore with first batch
        vectorstore = FAISS.from_documents(batch, embeddings)
    else:
        # Add documents incrementally (more memory efficient)
        vectorstore.add_documents(batch)
    
    print(f"  ✓ Batch {batch_num} complete (total: {min(i+batch_size, len(splits)):,} documents)")
    
    # Periodic save every 100 batches as backup
    if batch_num % 100 == 0:
        print(f"  💾 Checkpoint: Saving progress at {min(i+batch_size, len(splits)):,} documents...")
        vectorstore.save_local("faiss_index_real")

print("✓ Vector database created!")

# Step 6: Save to disk
print("\nStep 6: Saving vector database...")
vectorstore.save_local("faiss_index_real")

print("✓ Saved to faiss_index_real/")

# Step 7: Test with real data
print("\n" + "="*50)
print("TEST: Searching for web attacks")
print("="*50)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
results = retriever.invoke("SQL injection or Nmap scanning attacks")

print(f"\n✓ Found {len(results)} relevant chunks from REAL data:\n")
for i, doc in enumerate(results, 1):
    print(f"{i}. {doc.page_content[:100]}...")
    print(f"   IP: {doc.metadata.get('source_ip', 'N/A')}")
    print(f"   Protocol: {doc.metadata.get('protocol', 'N/A')}\n")

print("✓ Vector database ready for RAG!")
