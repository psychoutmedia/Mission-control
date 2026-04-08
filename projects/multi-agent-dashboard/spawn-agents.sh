#!/bin/bash
# Spawn multiple OpenClaw agents for testing the dashboard
# Each agent runs in embedded mode with a unique session-id

AGENTS=(
  "Claude-1"
  "Claude-2"
  "Codex-1"
  "Codex-2"
)

echo "🚀 Spawning ${#AGENTS[@]} embedded OpenClaw agents..."
echo ""

for NAME in "${AGENTS[@]}"; do
  echo "Starting $NAME..."
  
  # Run agent in background with unique session-id
  clawdbot agent \
    --agent=openclaw \
    --session-id="$NAME" \
    --local \
    --message="You are $NAME. Your job is to respond to chat messages from other agents. Keep responses brief." \
    > /tmp/openclaw-$NAME.log 2>&1 &
  
  PID=$!
  echo "  ✓ $NAME started (PID: $PID)"
  sleep 0.5
done

echo ""
echo "✅ All agents started!"
echo ""
echo "Agent logs:"
for NAME in "${AGENTS[@]}"; do
  echo "  tail -f /tmp/openclaw-$NAME.log"
done
echo ""
echo "To stop all agents:"
echo "  pkill -f 'clawdbot agent.*session-id='"
