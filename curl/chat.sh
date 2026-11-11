#!/bin/sh
set -eu
: "${REDROUTER_API_KEY:?Set REDROUTER_API_KEY first}"

curl --fail-with-body --silent --show-error --max-time 120 \
  https://redrouter.org/v1/chat/completions \
  -H "Authorization: Bearer $REDROUTER_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"glm-5.3-flash-red","max_tokens":256,"messages":[{"role":"user","content":"Give three checks for reviewing access control in my own API."}]}'
