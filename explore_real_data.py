# explore_real_data.py
import pandas as pd

# Load the real CSV data
df = pd.read_csv('log_data.csv')

print("="*60)
print("📊 REAL DATASET OVERVIEW")
print("="*60)

print(f"\nTotal log entries: {len(df):,}")
print(f"Date range: {df['timestamp'].min() if 'timestamp' in df else 'N/A'} to {df['timestamp'].max() if 'timestamp' in df else 'N/A'}")

if 'source_ip' in df.columns:
    print(f"Unique source IPs: {df['source_ip'].nunique():,}")
if 'destination_ip' in df.columns:
    print(f"Unique destination IPs: {df['destination_ip'].nunique():,}")
if 'protocol' in df.columns:
    print(f"\nProtocols used:")
    print(df['protocol'].value_counts())

if 'label' in df.columns:
    print(f"\nThreat Distribution:")
    print(df['label'].value_counts())
    print(f"\nMalicious events: {(df['label'] == 'Malicious').sum():,}")
    print(f"Normal events: {(df['label'] == 'Normal').sum():,}")

print(f"\nSample logs:")
print(df.head(10))

print(f"\n✓ Real data is ready!")
