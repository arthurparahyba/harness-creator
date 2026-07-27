#!/bin/bash
# format-on-edit.sh — hook PostToolUse do agent loop.
# Roda o formatter do projeto no arquivo editado para manter formatacao
# consistente. UNIVERSAL: o formatter e preenchido pela skill via placeholder.
#
# Entrada (stdin): JSON com {tool_name, tool_input:{file_path}}.
# Saida: exit 0 (saida eh ignorada pelo agent loop em PostToolUse).
#
# Funciona em Claude Code (matcher: Edit|Write|MultiEdit) e Devin CLI
# (matcher: edit) pois o formato stdin e identico.
#
# PLACEHOLDER: ruff format deve ser substituido pela skill com o
# comando de formatacao da linguagem detectada, ex:
#   Python:  black --quiet
#   JS/TS:   prettier --write
#   Go:      gofmt -w
#   Rust:    rustfmt
#   Ruby:    rubocop -A
#   .NET:    dotnet format <sln> --include
#   Java:    google-java-format -i
#
# PLACEHOLDER: *.py deve ser substituido pelo padrao de arquivos
# da linguagem, ex:
#   Python:  *.py
#   JS/TS:   *.{js,ts,jsx,tsx}
#   Go:      *.go
#   Rust:    *.rs
#   .NET:    *.cs
#   Java:    *.java
set -euo pipefail

INPUT="$(cat)"
detect_python() {
  for cand in python3.12 python3 python; do
    p=$(command -v "$cand" 2>/dev/null || true)
    [ -z "$p" ] && continue
    if "$p" -c 'import sys' 2>/dev/null; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}
PY_BIN="$(detect_python || true)"
if [ -z "$PY_BIN" ]; then
  exit 0
fi
FILE_PATH="$(printf '%s' "$INPUT" | "$PY_BIN" -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || echo '')"

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# So formata arquivos que casam com o padrao da linguagem do projeto.
case "$FILE_PATH" in
  *.py)
    if command -v ruff >/dev/null 2>&1 && [ -f "$FILE_PATH" ]; then
      ruff format "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
esac

exit 0
