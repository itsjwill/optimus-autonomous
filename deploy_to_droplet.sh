#!/bin/bash
# Deploy Optimus Trading Brain to DigitalOcean Droplet
# Run this from local machine: ./deploy_to_droplet.sh

set -e

DROPLET="botsniper"
REMOTE_DIR="/root/optimus-brain"

echo "=========================================="
echo "Deploying Optimus Trading Brain"
echo "=========================================="

# 1. Create remote directory
echo "[1/6] Creating remote directory..."
ssh $DROPLET "mkdir -p $REMOTE_DIR"

# 2. Copy Optimus files
echo "[2/6] Copying Optimus files..."
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    ./ $DROPLET:$REMOTE_DIR/

# 3. Install dependencies
echo "[3/6] Installing dependencies..."
ssh $DROPLET "cd $REMOTE_DIR && /root/venv/bin/pip install anthropic aiohttp requests -q"

# 4. Create systemd service
echo "[4/6] Creating systemd service..."
ssh $DROPLET "cat > /etc/systemd/system/optimus-brain.service << 'EOF'
[Unit]
Description=Optimus Trading Brain - AI-Powered Autonomous Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/optimus-brain
ExecStart=/root/venv/bin/python3 run_trading_brain.py --daemon --interval 3600
EnvironmentFile=/root/.env
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF"

# 5. Reload and start service
echo "[5/6] Starting Optimus Brain service..."
ssh $DROPLET "systemctl daemon-reload && systemctl enable optimus-brain && systemctl restart optimus-brain"

# 6. Verify
echo "[6/6] Verifying deployment..."
ssh $DROPLET "sleep 3 && systemctl status optimus-brain | head -15"

echo ""
echo "=========================================="
echo "Optimus Trading Brain Deployed!"
echo "=========================================="
echo ""
echo "Commands:"
echo "  ssh botsniper 'journalctl -u optimus-brain -f'     # View logs"
echo "  ssh botsniper 'systemctl status optimus-brain'     # Check status"
echo "  ssh botsniper 'systemctl restart optimus-brain'    # Restart"
echo ""
echo "The brain runs every hour with 4 AI agents:"
echo "  - TradeAnalyst: Analyzes patterns in trade data"
echo "  - Optimizer: Recommends parameter changes"
echo "  - RiskGuard: Assesses risk of changes"
echo "  - Executor: Makes final APPLY/DEFER/REJECT decisions"
echo ""
