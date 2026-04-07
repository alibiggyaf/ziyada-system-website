#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <project-name>"
  exit 1
fi

PROJECT_NAME="$1"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_DIR="$ROOT_DIR/projects/$PROJECT_NAME"

if [[ -d "$PROJECT_DIR" ]]; then
  echo "Project already exists: $PROJECT_DIR"
  exit 1
fi

mkdir -p "$PROJECT_DIR"/{scripts,tools,workflows,docs,assets,notebooks,outputs,.tmp,app}

cat > "$PROJECT_DIR/README.md" <<EOF
# ${PROJECT_NAME}

## Purpose
Describe what this project is for.

## Structure
- scripts/: Python automations
- tools/: Shell wrappers
- workflows/: SOP and execution flows
- docs/: Documentation and trackers
- assets/: Exports and references
- notebooks/: Research and experiments
- outputs/: Generated artifacts
- .tmp/: Disposable temporary files
- app/: Application code

## Baseline
Global baseline instructions are in:
- .github/CLAUDE skool Ai-automation society.md

Project-level instructions should extend baseline, not replace it.
EOF

echo "Created project: $PROJECT_DIR"
