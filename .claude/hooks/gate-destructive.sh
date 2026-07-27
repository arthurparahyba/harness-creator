#!/bin/bash
# gate-destructive.sh — hook PreToolUse do agent loop.
# Bloqueia comandos potencialmente destrutivos antes da execucao.
# UNIVERSAL: independe da linguagem do projeto.
#
# Entrada (stdin): JSON com {tool_name, tool_input:{command}}.
# Saida: exit 0 = allow, exit 2 = block (stderr vira feedback ao agente).
#
# Funciona em Claude Code (matcher: Bash) e Devin CLI (matcher: exec)
# pois o formato stdin e os exit codes sao identicos.
set -euo pipefail

INPUT="$(cat)"
detect_python() {
  for cand in python3.12 python3 python; do
    p=$(command -v "$cand" 2>/dev/null || true)
    [ -z "$p" ] && continue
    # Valida que o binario realmente roda (descarta stub da MS Store no Windows).
    if "$p" -c 'import sys' 2>/dev/null; then
      printf '%s' "$p"
      return 0
    fi
  done
  return 1
}
PY_BIN="$(detect_python || true)"
if [ -z "$PY_BIN" ]; then
  echo "BLOCKED: python nao encontrado — gate nao pode inspecionar o comando." >&2
  exit 2
fi
COMMAND="$(printf '%s' "$INPUT" | "$PY_BIN" -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null || echo '')"

# Padroes de risco — operacoes irreversiveis ou com efeito colateral real.
# Independem da linguagem: git, shell, SQL, filesystem.
RISKY_PATTERNS=(
  'rm[[:space:]]+-rf?[[:space:]]'
  'git[[:space:]]+push[[:space:]].*--force'
  'git[[:space:]]+push[[:space:]].*-f[[:space:]]'
  'git[[:space:]]+reset[[:space:]]+--hard'
  'git[[:space:]]+clean[[:space:]]+-fd'
  'git[[:space:]]+branch[[:space:]]+-D'
  'DROP[[:space:]]+(TABLE|SCHEMA|DATABASE)'
  'TRUNCATE[[:space:]]+TABLE'
  'drop[[:space:]]+database'
  ':(){.*};:'
  'mkfs\.'
  'dd[[:space:]]+if=.*of=/dev/'
)

for PATTERN in "${RISKY_PATTERNS[@]}"; do
  if printf '%s' "$COMMAND" | grep -qE "$PATTERN"; then
    echo "BLOCKED: comando corresponde a padrao de risco: $PATTERN" >&2
    echo "Operacao destrutiva bloqueada pelo gate hook (.claude/hooks/gate-destructive.sh)." >&2
    echo "Se realmente necessario, peça confirmacao explicita ao usuario." >&2
    exit 2
  fi
done

exit 0
