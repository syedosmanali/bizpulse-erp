#!/bin/bash

echo ""
echo "========================================"
echo "   BizPulse ERP - Live Demo Server"
echo "========================================"
echo ""

# Start the Flask app in background
echo "Starting BizPulse ERP server..."
python app.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 5

# Start ngrok tunnel
echo ""
echo "Creating secure tunnel with ngrok..."
echo ""
echo "========================================"
echo "   SHARE THIS LINK WITH YOUR CLIENT:"
echo "========================================"
echo ""

ngrok http 5000

# Cleanup when ngrok stops
echo ""
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null
echo "Server stopped."