#!/bin/bash
cd "$(dirname "$0")"

echo "🎯 Starting Mission Control Server..."
echo ""
echo "Server will run at: http://localhost:8888"
echo "Press Ctrl+C to stop"
echo ""

node mission-control-server.js
