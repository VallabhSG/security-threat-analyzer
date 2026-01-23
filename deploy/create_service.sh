#!/bin/bash
# Create systemd service to run app on boot

sudo tee /etc/systemd/system/security-analyzer.service > /dev/null <<EOF
[Unit]
Description=Security Threat Analyzer
After=network.target ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/security-threat-analyzer
Environment="PATH=/home/ubuntu/security-threat-analyzer/venv/bin"
ExecStart=/home/ubuntu/security-threat-analyzer/venv/bin/streamlit run app.py --server.port=8501 --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable security-analyzer
sudo systemctl start security-analyzer

echo "✅ Service created! App will auto-start on boot."
echo "   Check status: sudo systemctl status security-analyzer"
echo "   View logs: sudo journalctl -u security-analyzer -f"
