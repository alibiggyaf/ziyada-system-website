#!/usr/bin/env bash
set -euo pipefail

# Usage: stop_static_site.sh <site_dir> [port] [host]
SITE_DIR="${1:-}"
PORT="${2:-8099}"
HOST="${3:-127.0.0.1}"

if [[ -z "$SITE_DIR" ]]; then
  echo "Usage: $(basename "$0") <site_dir> [port] [host]"
  exit 1
fi

KEY=$(printf "%s:%s:%s" "$SITE_DIR" "$PORT" "$HOST" | shasum -a 256 | awk '{print $1}')
PID_FILE="/tmp/static_site_${KEY}.pid"

cleanup_pidfile() {
  python3 - "$PID_FILE" <<'PY'
import os, sys
path = sys.argv[1]
try:
    os.remove(path)
except FileNotFoundError:
    pass
PY
}

if [[ ! -f "$PID_FILE" ]]; then
  echo "No managed server found for $SITE_DIR on $HOST:$PORT"
  exit 0
fi

pid=$(cat "$PID_FILE" 2>/dev/null || true)
if [[ -z "$pid" ]]; then
  cleanup_pidfile
  echo "No valid PID found; cleaned stale PID file"
  exit 0
fi

if kill -0 "$pid" >/dev/null 2>&1; then
  kill "$pid" >/dev/null 2>&1 || true
  sleep 0.5
  if kill -0 "$pid" >/dev/null 2>&1; then
    kill -9 "$pid" >/dev/null 2>&1 || true
  fi
  echo "Stopped server PID $pid on $HOST:$PORT"
else
  echo "Process $pid not running; cleaned stale PID file"
fi

cleanup_pidfile
