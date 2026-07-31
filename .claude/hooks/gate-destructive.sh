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

# ------------------------------------------------------------ registro de regras
# Os padroes vivem em `.harness/gate-rules.json`, nao aqui dentro, porque o
# gate binario errava dos dois lados. O falso bloqueio e o mais caro: ele
# ensina a driblar. Uma vez aprendido num caso obviamente errado (limpar um
# diretorio temporario), o drible passa por cima tambem dos bloqueios certos.
# Com registro, cada falso bloqueio vira uma excecao declarada UMA vez — a
# mesma catraca do `arch-rules.json`.
#
# "MAS O AGENTE PODE EDITAR O REGISTRO E SE LIBERAR"
# Pode — e ja podia editar este script, com o mesmo shell. Tirar os padroes
# daqui nao cria a capacidade. A defesa nao e o formato do arquivo: e a regra
# G01 do `arch-rules.json`, que EXECUTA este gate a cada rodada da DoD e exige
# exit 2 no destrutivo. Gate enfraquecido deixa de ser invisivel e vira build
# vermelho no proximo grupo.
#
# Este script NAO ESCREVE EM DISCO, por nada. Escrita pode falhar (disco
# cheio, volume read-only), falha mata o script, e script morto devolve exit
# 1 — que em PreToolUse significa "erro nao-bloqueante" e deixa o comando
# destrutivo passar. O gate falha ABERTO. Quem registra e o
# `registrar-sessao.sh`, que roda ao lado e pode falhar sem consequencia.
REGRAS="${HARNESS_GATE_RULES:-.harness/gate-rules.json}"

# Le o registro como TSV. Mesmo parser em awk do `check-arch.sh`: exigir jq
# transformaria o gate em bloqueio de tudo em maquina sem jq.
_le_registro() {
  [ -f "$REGRAS" ] || return 1
  awk '
    function limpa(s) {
      sub(/^[^:]*:[[:space:]]*"/, "", s)
      sub(/",?[[:space:]]*$/, "", s)
      gsub(/\\"/, "\"", s)
      gsub(/\\\\/, "\\", s)
      return s
    }
    /"nivel"[[:space:]]*:/  { nivel  = limpa($0) }
    /"padrao"[[:space:]]*:/ { padrao = limpa($0) }
    /"what"[[:space:]]*:/   { what   = limpa($0) }
    /"why"[[:space:]]*:/    { why    = limpa($0) }
    /"fix"[[:space:]]*:/ {
      fix = limpa($0)
      if (nivel != "" && padrao != "")
        printf "%s\t%s\t%s\t%s\t%s\n", nivel, padrao, what, why, fix
      nivel = ""; padrao = ""; what = ""; why = ""; fix = ""
    }
  ' "$REGRAS" 2>/dev/null
}

REGISTRO="$(_le_registro || printf '')"

# Fallback embutido. Registro ausente, ilegivel ou sem NENHUMA regra de
# bloqueio cai aqui: gate sem registro nao pode virar gate sem protecao, que
# seria transformar "alguem apagou um arquivo" em "o harness parou de
# proteger" sem nada acusando.
if ! printf '%s' "$REGISTRO" | grep -q '^bloquear'; then
  REGISTRO="$(printf '%s\n' \
    "bloquear	rm[[:space:]]+-rf?[[:space:]]	remocao recursiva forcada	Nao ha desfazer	Confirme com o humano" \
    "bloquear	git[[:space:]]+push[[:space:]].*(--force|[[:space:]]-f[[:space:]])	push forcado	Reescreve historico remoto	Use --force-with-lease" \
    "bloquear	git[[:space:]]+reset[[:space:]]+--hard	reset destrutivo	Descarta o nao commitado	Use git stash" \
    "bloquear	git[[:space:]]+clean[[:space:]]+-[a-z]*f	remocao de nao rastreados	Inclui .env sem copia	Use git clean -n" \
    "bloquear	git[[:space:]]+branch[[:space:]]+-D	remocao forcada de branch	Commit fica so no reflog	Use git branch -d" \
    "bloquear	(DROP[[:space:]]+(TABLE|SCHEMA|DATABASE)|TRUNCATE[[:space:]]+TABLE|drop[[:space:]]+database)	destruicao em banco	Nao ha desfazer	Peca ao humano" \
    "bloquear	(npm[[:space:]]+publish|(yarn|pnpm)[[:space:]]+publish|mvn[[:space:]]+.*(deploy|release:perform)|gradle(w)?[[:space:]]+.*publish|dotnet[[:space:]]+nuget[[:space:]]+push|cargo[[:space:]]+publish|gem[[:space:]]+push|twine[[:space:]]+upload)	publicacao de artefato	Versao publicada nao se despublica	Peca ao humano" \
    "bloquear	(terraform[[:space:]]+destroy|go[[:space:]]+clean[[:space:]]+.*-modcache|mkfs\\.|dd[[:space:]]+if=.*of=/dev/)	destruicao de infraestrutura	Efeito fora do repositorio	Peca ao humano")"
fi

# ---------------------------------------------------------------- decisao
# `permitir` ANTES de `bloquear`, e a ordem e o ponto: sem precedencia, uma
# excecao nunca conseguiria abrir buraco num padrao amplo como `rm -rf`, e o
# registro seria decorativo.
#
# Toda excecao e ANCORADA (`^...$`) e proibe `;`, `|`, `&`, `$` e crase no
# caminho. Sem isso, `rm -rf node_modules && rm -rf /` casaria a excecao pelo
# comeco e o gate liberaria a segunda metade junto. Ancorar e o que separa
# "excecao" de "buraco".
while IFS=$'\t' read -r nivel padrao _what _why _fix; do
  [ "$nivel" = "permitir" ] || continue
  [ -n "${padrao:-}" ] || continue
  if printf '%s' "$COMMAND" | grep -qE "$padrao"; then
    exit 0
  fi
done <<< "$REGISTRO"

while IFS=$'\t' read -r nivel padrao what why fix; do
  [ "$nivel" = "bloquear" ] || continue
  [ -n "${padrao:-}" ] || continue
  if printf '%s' "$COMMAND" | grep -qE "$padrao"; then
    echo "BLOCKED: $what" >&2
    echo "WHY:  $why" >&2
    echo "FIX:  $fix" >&2
    echo "Bloqueado pelo gate (.claude/hooks/gate-destructive.sh)." >&2
    echo "Se realmente necessario, peça confirmacao explicita ao usuario." >&2
    exit 2
  fi
done <<< "$REGISTRO"

exit 0
