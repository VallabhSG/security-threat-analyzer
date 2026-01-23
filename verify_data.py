# verify_data.py
import pandas as pd

# Load the CSV (adjust filename if needed)
df = pd.read_csv('log_data.csv')  # Change filename if different

print("✓ Dataset loaded successfully!")
print(f"\nDataset Shape: {df.shape}")
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")

print(f"\nColumn Names:")
print(df.columns.tolist())

print(f"\nFirst few rows:")
print(df.head())

print(f"\nData types:")
print(df.dtypes)

print(f"\nMissing values:")
print(df.isnull().sum())

print(f"\n✓ Data is ready for processing!")
