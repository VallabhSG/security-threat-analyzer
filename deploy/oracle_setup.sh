#!/bin/bash
# Oracle Cloud VM Setup Script for Security Threat Analyzer
# Run this after SSH into your VM: ssh ubuntu@<your-vm-ip>

set -e
echo "=========================================="
echo "Security Threat Analyzer - Oracle Cloud Setup"
echo "=========================================="

# Update system
echo "[1/8] Updating system..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "[2/8] Installing dependencies..."
sudo apt install -y python3.12 python3.12-venv python3-pip git curl

# Install Ollama
echo "[3/8] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
echo "[4/8] Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama
sleep 5

# Pull the model
echo "[5/8] Downloading Gemma 3 1B model..."
ollama pull gemma3:1b

# Clone your repository
echo "[6/8] Cloning repository..."
cd ~
git clone https://github.com/VallabhSG/security-threat-analyzer.git
cd security-threat-analyzer

# Create virtual environment
echo "[7/8] Setting up Python environment..."
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Health check
echo "[8/8] Running health check..."
python -m security_analyzer check-health || true

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "⚠️  IMPORTANT: Upload your data files:"
echo "    scp prepared_logs.csv ubuntu@<VM-IP>:~/security-threat-analyzer/"
echo "    scp -r faiss_index_real ubuntu@<VM-IP>:~/security-threat-analyzer/"
echo ""
echo "Then run the app:"
echo "    cd ~/security-threat-analyzer"
echo "    source .venv/bin/activate"
echo "    streamlit run app.py --server.port=8501 --server.address=0.0.0.0"
echo ""
echo "Open firewall port 8501 in Oracle Cloud Console:"
echo "    Networking → Virtual Cloud Networks → Security Lists → Add Ingress Rule"
echo "    Source CIDR: 0.0.0.0/0, Port: 8501"
echo ""
