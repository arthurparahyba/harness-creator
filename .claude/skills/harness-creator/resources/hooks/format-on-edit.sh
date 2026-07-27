#!/bin/bash
# format-on-edit.sh — hook PostToolUse do agent loop.
# Roda o formatter do projeto no arquivo editado para manter formatacao
# consistente. UNIVERSAL: o formatter e preenchido pela skill via placeholder.
#
# Entrada (stdin): JSON com o arquivo em {tool_input:{file_path}} ou {file_path}.
# Saida: exit 0 (saida eh ignorada pelo agent loop em PostToolUse).
#
# Funciona nos tres agentes-alvo:
#   Claude Code  .claude/settings.json      PostToolUse, matcher Edit|Write|MultiEdit
#   Devin CLI    .devin/hooks.v1.json       PostToolUse, matcher edit
#   Cursor       .cursor/hooks.json         afterFileEdit
# O Cursor manda `file_path` no topo do JSON, os outros dois em `tool_input`.
#
# PLACEHOLDER: <formatter_command> deve ser substituido pela skill com o
# comando de formatacao da linguagem detectada, ex:
#   Python:  black --quiet
#   JS/TS:   prettier --write
#   Go:      gofmt -w
#   Rust:    rustfmt
#   Ruby:    rubocop -A
#   .NET:    dotnet format <sln> --include
#   Java:    google-java-format -i
#
# PLACEHOLDER: <file_glob> deve ser substituido pelo padrao de arquivos
# da linguagem. ATENCAO: isto vira um padrao de `case`, que NAO faz brace
# expansion — `*.{js,ts}` nunca casa com nada e o hook deixa de formatar em
# silencio. Para varias extensoes, use alternancia com `|`:
#   Python:  *.py
#   JS/TS:   *.js|*.ts|*.jsx|*.tsx|*.mjs|*.cjs
#   Angular: *.ts|*.html|*.scss
#   Go:      *.go
#   Rust:    *.rs
#   .NET:    *.cs
#   Java:    *.java
set -euo pipefail

INPUT="$(cat)"

# ---8<--- extracao de JSON (copia identica em gate-destructive.sh) ---8<---
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

FILE_PATH="$(extrai_json file_path || printf '')"

# PostToolUse nunca bloqueia: sem caminho legivel, sai em silencio.
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# So formata arquivos que casam com o padrao da linguagem do projeto.
case "$FILE_PATH" in
  <file_glob>)
    if command -v <formatter_bin> >/dev/null 2>&1 && [ -f "$FILE_PATH" ]; then
      <formatter_command> "$FILE_PATH" 2>/dev/null || true
    fi
    ;;
esac

exit 0
