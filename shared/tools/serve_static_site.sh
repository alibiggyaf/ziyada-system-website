#!/usr/bin/env bash
set -euo pipefail

# Usage: serve_static_site.sh <site_dir> [port] [host]
SITE_DIR="${1:-}"
PORT="${2:-8099}"
HOST="${3:-127.0.0.1}"

if [[ -z "$SITE_DIR" ]]; then
  echo "Usage: $(basename "$0") <site_dir> [port] [host]"
  exit 1
fi

if [[ "$SITE_DIR" == "/absolute/path/to/site" ]]; then
  echo "Error: replace /absolute/path/to/site with your real folder path"
  echo "Example: $(basename "$0") \"projects/ziyada-system/.tmp/zip_check_695d3ef_v2\" 8099 127.0.0.1"
  exit 1
fi

if [[ ! -d "$SITE_DIR" ]]; then
  echo "Error: directory not found: $SITE_DIR"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required to serve static files"
  exit 1
fi

KEY=$(printf "%s:%s:%s" "$SITE_DIR" "$PORT" "$HOST" | shasum -a 256 | awk '{print $1}')
PID_FILE="/tmp/static_site_${KEY}.pid"
LOG_FILE="/tmp/static_site_${KEY}.log"

is_pid_listening() {
  local pid="$1"
  if [[ -z "$pid" ]]; then
    return 1
  fi

  if ! kill -0 "$pid" >/dev/null 2>&1; then
    return 1
  fi

  lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | awk 'NR>1 {print $2}' | grep -qx "$pid"
}

if [[ -f "$PID_FILE" ]]; then
  existing_pid=$(cat "$PID_FILE" 2>/dev/null || true)
  if is_pid_listening "$existing_pid"; then
    echo "Server already running"
    echo "PID: $existing_pid"
    echo "Root: $SITE_DIR"
    echo "URL: http://$HOST:$PORT/"
    if [[ -f "$SITE_DIR/index.html" ]]; then
      echo "Home: http://$HOST:$PORT/index.html"
    fi
    if [[ -f "$SITE_DIR/ar.html" ]]; then
      echo "Arabic: http://$HOST:$PORT/ar.html"
    fi
    exit 0
  fi
fi

if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Error: port $PORT is already in use by another process"
  echo "Try another port, e.g.: $(basename "$0") \"$SITE_DIR\" 8100 $HOST"
  exit 1
fi

(
  cd "$SITE_DIR"
  nohup python3 -m http.server "$PORT" --bind "$HOST" >"$LOG_FILE" 2>&1 &
  echo $! >"$PID_FILE"
)

new_pid=$(cat "$PID_FILE")

# Health-check the server for up to 5 seconds.
for _ in {1..10}; do
  if python3 - "$PORT" "$HOST" <<'PY' >/dev/null 2>&1
import sys
from urllib.request import urlopen
port = sys.argv[1]
host = sys.argv[2]
urlopen(f"http://{host}:{port}/", timeout=1)
PY
  then
    echo "Server started"
    echo "PID: $new_pid"
    echo "Root: $SITE_DIR"
    echo "URL: http://$HOST:$PORT/"
    if [[ -f "$SITE_DIR/index.html" ]]; then
      echo "Home: http://$HOST:$PORT/index.html"
    fi
    if [[ -f "$SITE_DIR/ar.html" ]]; then
      echo "Arabic: http://$HOST:$PORT/ar.html"
    fi
    echo "Log: $LOG_FILE"
    exit 0
  fi
  sleep 0.5
done

echo "Error: server failed to become healthy on port $PORT"
echo "Check log: $LOG_FILE"
exit 1
