#!/bin/sh
# Bridge first (it owns the socket the bot connects to), then the bot in the
# foreground so the container's lifetime is the bot's lifetime.
set -e
mkdir -p "$RUN_DIR/pending" "$STANDARDS_RAW" "$STANDARDS_ROOT/index" "$STANDARDS_ROOT/state"

: "${BRIDGE_SOCKET:=$RUN_DIR/bridge.sock}"
export BRIDGE_SOCKET
export BRIDGE_NAME="${BRIDGE_NAME:-chapter-and-verse}"
export BRIDGE_STATE="$RUN_DIR/bridge-state.json"
export BRIDGE_PENDING_DIR="$RUN_DIR/pending"
export BRIDGE_WORKDIR=/app/engine
export BRIDGE_OUTPUT=plain
export BRIDGE_SPAWN='["python3","/app/engine/ask.py","-p","{message}"]'
export BRIDGE_ENGINE_STATE="$STANDARDS_ROOT/state/history.json"
export SOCKET_PATH="$BRIDGE_SOCKET"

rm -f "$BRIDGE_SOCKET"
node /app/gateway/bridge-server.js &
BRIDGE_PID=$!

# Wait for the socket rather than sleeping a guessed number of seconds.
i=0
while [ ! -S "$BRIDGE_SOCKET" ] && [ $i -lt 50 ]; do i=$((i+1)); sleep 0.1; done
[ -S "$BRIDGE_SOCKET" ] || { echo "bridge did not create $BRIDGE_SOCKET"; exit 1; }

trap 'kill $BRIDGE_PID 2>/dev/null' TERM INT
exec node /app/gateway/bot.js
