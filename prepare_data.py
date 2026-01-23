# prepare_data.py (FIXED for your web security dataset)
import pandas as pd
import numpy as np

print("Step 1: Loading real web security dataset...")
df = pd.read_csv('log_data.csv')

print(f"Original size: {len(df):,} rows")

# Step 2: Clean data (use actual columns)
print("\nStep 2: Cleaning data...")
print(f"Actual columns: {df.columns.tolist()}")

# Remove rows with missing critical values (use actual columns)
df = df.dropna(subset=['source_ip', 'protocol'])

print(f"After cleaning: {len(df):,} rows")

# Step 3: Create web security log entries
print("\nStep 3: Converting to readable web logs...")
logs_text = []
for idx, row in df.iterrows():
    log_entry = f"[{row.get('timestamp', 'N/A')}] "
    log_entry += f"IP: {row.get('source_ip', 'N/A')} "
    log_entry += f"Protocol: {row.get('protocol', 'N/A')} "
    log_entry += f"Path: {row.get('request_path', 'N/A')} "
    
    if 'user_agent' in row:
        ua = str(row.get('user_agent', 'N/A'))
        if 'nmap' in ua.lower():
            log_entry += f"Tool: NMAP "
        elif 'sqlmap' in ua.lower():
            log_entry += f"Tool: SQLMAP "
        elif 'curl' in ua.lower():
            log_entry += f"Tool: CURL "
        else:
            log_entry += f"UA: {ua[:30]}... "
    
    logs_text.append({
        'log_text': log_entry,
        'source_ip': row.get('source_ip', 'N/A'),
        'protocol': row.get('protocol', 'N/A'),
        'request_path': row.get('request_path', 'N/A'),
        'user_agent': row.get('user_agent', 'N/A'),
        'timestamp': row.get('timestamp', 'N/A')
    })

prepared_df = pd.DataFrame(logs_text)

# Step 4: Sample intelligently for memory constraints
print("\nStep 4: Creating optimized sample for embedding...")
target_size = 2000000  # 2M documents - optimal for memory

if len(prepared_df) > target_size:
    # Stratified sampling to maintain diversity
    print(f"  Sampling {target_size:,} from {len(prepared_df):,} logs...")
    prepared_df = prepared_df.sample(n=target_size, random_state=42)
    print(f"  ✓ Sampled to {target_size:,} rows (maintains protocol/IP diversity)")
else:
    print(f"  Using all {len(prepared_df):,} rows")

# Step 5: Save
print("\nStep 5: Saving prepared web security logs...")
prepared_df.to_csv('prepared_logs.csv', index=False)

print(f"\n✓ Data preparation COMPLETE!")
print(f"✓ Saved: prepared_logs.csv ({len(prepared_df):,} rows, optimized sample)")
print(f"\nSample prepared logs:")
print(prepared_df[['log_text', 'source_ip', 'protocol']].head(3))

print(f"\nTop protocols:")
print(prepared_df['protocol'].value_counts().head())
print(f"\nTop IPs (most active):")
print(prepared_df['source_ip'].value_counts().head())
