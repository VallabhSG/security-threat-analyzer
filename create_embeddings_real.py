# create_embeddings_real.py
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

# Step 1: Load prepared real logs
print("Step 1: Loading prepared real logs...")
df = pd.read_csv('prepared_logs.csv')

print(f"✓ Loaded {len(df):,} real log entries")

# Step 2: Extract log text
print("\nStep 2: Extracting log text...")
logs_text = df['log_text'].tolist()
full_text = "\n".join(logs_text)

print(f"✓ Total text size: {len(full_text):,} characters")

# Step 3: Split into chunks
print("\nStep 3: Splitting real logs into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Each chunk is ~500 characters
    chunk_overlap=50,    # Overlap to preserve context
    separators=["\n", " "]
)
chunks = splitter.split_text(full_text)

print(f"✓ Created {len(chunks):,} chunks from real data")
print(f"\nExample chunk from real data:")
print(chunks)
print("\n---\n")

# Step 4: Generate embeddings
print("Step 4: Generating embeddings from real logs...")
print("(This may take a minute or two...)")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Create embeddings for first few chunks
sample_embeddings = embeddings.embed_documents(chunks[:5])

print(f"✓ Embedding size: {len(sample_embeddings)} dimensions")
print(f"✓ First embedding (first 10 values): {sample_embeddings[:10]}")

print(f"\n✓ Embeddings generation complete!")
print(f"Ready to build vector database with {len(chunks):,} chunks")
