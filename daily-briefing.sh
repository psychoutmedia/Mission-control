#!/bin/bash

# Daily Briefing Script for Clawdbot
# Run at 9am daily via: crontab -e
# Add line: 0 9 * * * /Users/marksstephenson/clawd/daily-briefing.sh

curl -s -X POST http://localhost:18789/api/agent/message \
  -H "Authorization: Bearer aee79b4648f3f3660daaa00b746e624d8ffc1ffc03afc39e" \
  -H "Content-Type: application/json" \
  -d '{"sessionKey":"agent:main:main","message":"Morning briefing please - weather, AI news, overnight work review, backlog status, and learning plan ideas."}'
