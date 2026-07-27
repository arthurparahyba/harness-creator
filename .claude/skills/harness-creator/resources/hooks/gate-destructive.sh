#!/bin/bash
# gate-destructive.sh — hook PreToolUse do agent loop.
# Bloqueia comandos potencialmente destrutivos antes da execucao.
# UNIVERSAL: independe da linguagem do projeto.
#
# Entrada (stdin): JSON com o comando em {tool_input:{command}} ou {command}.
# Saida: exit 0 = allow, exit 2 = block (stderr vira feedback ao agente).
#
# Funciona nos tres agentes-alvo, pois o exit 2 significa "bloquear" nos tres:
#   Claude Code  .claude/settings.json      PreToolUse, matcher Bash
#   Devin CLI    .devin/hooks.v1.json       PreToolUse, matcher exec
#   Cursor       .cursor/hooks.json         beforeShellExecution (failClosed)
# O Cursor manda `command` no topo do JSON, os outros dois em `tool_input`.
set -euo pipefail

INPUT="$(cat)"

# ---8<--- extracao de JSON (copia identica em format-on-edit.sh) ---8<---
# Duplicado de proposito: um `source` de arquivo irmao introduz uma falha nova
# — lib ausente faz o script morrer com exit 1, que em PreToolUse significa
# "erro nao-bloqueante" e deixa o comando destrutivo passar. Hook e arquivo
# autocontido. `tests/test_skill.py` exige que as duas copias sejam iguais.
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

# Le uma chave string do JSON de entrada, aceitando os dois formatos em uso:
#   {"tool_input":{"command":...}}  Claude Code, Devin CLI, Cursor preToolUse
#   {"command":...}                 Cursor beforeShellExecution/afterFileEdit
# Python primeiro (parser de verdade); awk como fallback, porque exigir Python
# num repo Go/.NET/Java sem Python instalado transformava o gate em bloqueio
# de TODO comando — o harness deixava de proteger e passava a impedir o
# trabalho. awk e POSIX: existe onde bash existe.
extrai_json() {
  chave="$1"
  py="$(detect_python || true)"
  if [ -n "$py" ]; then
    valor="$(printf '%s' "$INPUT" | "$py" -c '
import json, sys
d = json.load(sys.stdin)
k = sys.argv[1]
ti = d.get("tool_input")
v = ti.get(k) if isinstance(ti, dict) else None
print(v if isinstance(v, str) else (d.get(k) if isinstance(d.get(k), str) else ""))
' "$chave" 2>/dev/null || printf '')"
    if [ -n "$valor" ]; then
      printf '%s' "$valor"
      return 0
    fi
  fi
  printf '%s' "$INPUT" | awk -v k="$chave" '
    { s = s $0 }
    END {
      p = index(s, "\"" k "\"")
      if (p == 0) exit 1
      rest = substr(s, p + length(k) + 2)
      q = index(rest, "\"")
      if (q == 0) exit 1
      rest = substr(rest, q + 1)
      i = 1
      while (i <= length(rest)) {
        c = substr(rest, i, 1)
        if (c == "\\") {
          e = substr(rest, i + 1, 1)
          out = out ((e == "n" || e == "t" || e == "r") ? " " : e)
          i += 2
          continue
        }
        if (c == "\"") break
        out = out c
        i++
      }
      print out
    }'
}
# ---8<--- fim da extracao de JSON ---8<---

COMMAND="$(extrai_json command || printf '')"

# Sem chave `command` no JSON nao ha o que inspecionar (outro tool, outro
# evento): liberar. Com a chave presente e valor ilegivel, bloquear — e a
# unica situacao em que falhar fechado e a resposta certa.
if [ -z "$COMMAND" ]; then
  if printf '%s' "$INPUT" | grep -q '"command"'; then
    echo "BLOCKED: comando ilegivel no JSON de entrada — gate nao pode inspecionar." >&2
    exit 2
  fi
  exit 0
fi

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
  # Publicacao de artefato: irreversivel em qualquer registry publico —
  # versao publicada nao se despublica. Universal de proposito: ter o
  # padrao de npm num repo Go nao custa nada e evita esquecer de ativar.
  'npm[[:space:]]+publish'
  '(yarn|pnpm)[[:space:]]+publish'
  'mvn[[:space:]]+.*(deploy|release:perform)'
  'gradle(w)?[[:space:]]+.*publish'
  'dotnet[[:space:]]+nuget[[:space:]]+push'
  'cargo[[:space:]]+publish'
  'gem[[:space:]]+push'
  'twine[[:space:]]+upload'
  # Destruicao de infraestrutura e de cache global de dependencias.
  'terraform[[:space:]]+destroy'
  'go[[:space:]]+clean[[:space:]]+.*-modcache'
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
