#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   bash shared/tools/site_shortcuts.sh start ziyada
#   bash shared/tools/site_shortcuts.sh start ali
#   bash shared/tools/site_shortcuts.sh stop ziyada
#   bash shared/tools/site_shortcuts.sh status

ACTION="${1:-status}"
TARGET="${2:-all}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SERVE_SCRIPT="$ROOT_DIR/shared/tools/serve_static_site.sh"
STOP_SCRIPT="$ROOT_DIR/shared/tools/stop_static_site.sh"
HOST="127.0.0.1"

ziyada_dir="$ROOT_DIR/projects/ziyada-system/.tmp/zip_check_695d3ef_v2"
ziyada_port="8110"

ali_dir="$ROOT_DIR/projects/ALI FALLATAH WEBSITE PORTOFOLIO/Ali website  2026/deploy-ali portfolio website "
ali_port="8111"

print_urls() {
  echo ""
  echo "Stable URLs"
  echo "- Ziyada Home:  http://$HOST:$ziyada_port/index.html"
  echo "- Ziyada Arabic: http://$HOST:$ziyada_port/ar.html"
  echo "- Ali Home:     http://$HOST:$ali_port/index.html"
}

start_one() {
  local name="$1"
  local dir="$2"
  local port="$3"

  if [[ ! -d "$dir" ]]; then
    echo "Skip $name: site directory not found"
    echo "Path: $dir"
    return 0
  fi

  bash "$SERVE_SCRIPT" "$dir" "$port" "$HOST"
}

stop_one() {
  local name="$1"
  local dir="$2"
  local port="$3"

  if [[ ! -d "$dir" ]]; then
    echo "Skip $name: site directory not found"
    echo "Path: $dir"
    return 0
  fi

  bash "$STOP_SCRIPT" "$dir" "$port" "$HOST"
}

status_one() {
  local name="$1"
  local port="$2"
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "$name: running on http://$HOST:$port/"
  else
    echo "$name: stopped"
  fi
}

case "$ACTION" in
  start)
    case "$TARGET" in
      ziyada)
        start_one "ziyada" "$ziyada_dir" "$ziyada_port"
        ;;
      ali)
        start_one "ali" "$ali_dir" "$ali_port"
        ;;
      all)
        start_one "ziyada" "$ziyada_dir" "$ziyada_port"
        start_one "ali" "$ali_dir" "$ali_port"
        ;;
      *)
        echo "Unknown target: $TARGET"
        echo "Use: ziyada | ali | all"
        exit 1
        ;;
    esac
    print_urls
    ;;
  stop)
    case "$TARGET" in
      ziyada)
        stop_one "ziyada" "$ziyada_dir" "$ziyada_port"
        ;;
      ali)
        stop_one "ali" "$ali_dir" "$ali_port"
        ;;
      all)
        stop_one "ziyada" "$ziyada_dir" "$ziyada_port"
        stop_one "ali" "$ali_dir" "$ali_port"
        ;;
      *)
        echo "Unknown target: $TARGET"
        echo "Use: ziyada | ali | all"
        exit 1
        ;;
    esac
    ;;
  status)
    status_one "ziyada" "$ziyada_port"
    status_one "ali" "$ali_port"
    print_urls
    ;;
  open)
    case "$TARGET" in
      ziyada)
        open "http://$HOST:$ziyada_port/ar.html"
        ;;
      ali)
        open "http://$HOST:$ali_port/index.html"
        ;;
      *)
        echo "Unknown target: $TARGET"
        echo "Use: ziyada | ali"
        exit 1
        ;;
    esac
    ;;
  *)
    echo "Unknown action: $ACTION"
    echo "Usage: bash shared/tools/site_shortcuts.sh {start|stop|status|open} {ziyada|ali|all}"
    exit 1
    ;;
esac
