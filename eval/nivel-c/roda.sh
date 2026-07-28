#!/bin/sh
# roda.sh — executa UMA celula da bateria: uma tarefa, numa condicao.
#
# Uso:
#   sh eval/nivel-c/roda.sh <workdir> <control|harness> <T1|T2|T3|T4>
#
# O `cd` para dentro do repo alvo nao e conforto, e requisito de validade: o
# `claude -p` resolve o project root a partir do cwd, e rodando da raiz deste
# repositorio a sessao carrega o CLAUDE.md -> AGENTS.md DAQUI. A celula de
# controle, que existe para nao ter protocolo nenhum, receberia um. Ver
# README.md, "Tres decisoes de metodo".
#
# Saidas, em <workdir>/runs/:
#   <T>-<cond>.json     resultado da sessao (num_turns, custo, session_id)
#   <T>-<cond>.dod      exit code da DoD do alvo depois da sessao
#   <cond>.session      session_id da celula, para as tarefas com sessao=resume
set -eu

AQUI=$(cd "$(dirname "$0")" && pwd)
TAREFAS="$AQUI/tarefas.json"

[ $# -eq 3 ] || { sed -n '2,16p' "$0"; exit 2; }
WORKDIR=$(cd "$1" && pwd); COND="$2"; TAREFA="$3"
ALVO="$WORKDIR/$COND"
RUNS="$WORKDIR/runs"

case "$COND" in
  control|harness) ;;
  *) echo "condicao invalida: $COND (use control ou harness)" >&2; exit 2 ;;
esac
[ -d "$ALVO" ] || { echo "nao existe: $ALVO (rode o preparar.sh antes)" >&2; exit 2; }

campo() {
  python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
t = next((t for t in d["tarefas"] if t["id"] == sys.argv[2]), None)
if t is None:
    sys.exit("tarefa desconhecida: " + sys.argv[2])
if sys.argv[3] == "autorizacao":
    print(d["autorizacao"])
else:
    print(t.get(sys.argv[3], ""))
' "$TAREFAS" "$TAREFA" "$1"
}

PROMPT=$(campo prompt)
SESSAO=$(campo sessao)
AUTORIZACAO=$(campo autorizacao)

# Ponto de partida da celula, gravado uma vez so, antes da primeira sessao.
# Na celula `harness` o HEAD aqui ja inclui o commit de instalacao do harness,
# que nao e trabalho da rodada: contar a partir do commit base daria um commit
# de vantagem a ela sem nenhuma tarefa ter sido feita.
INICIO="$RUNS/inicio-$COND.txt"
[ -f "$INICIO" ] || git -C "$ALVO" rev-parse --short HEAD > "$INICIO"

# ------------------------------------------------------------------ preparo
# Bug plantado: substituicao literal, aplicada identica nas duas condicoes.
python3 - "$TAREFAS" "$TAREFA" "$ALVO" <<'PY'
import json, pathlib, sys
tarefas, tid, alvo = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(tarefas))
p = next(t for t in d["tarefas"] if t["id"] == tid).get("preparo")
if p is None:
    raise SystemExit(0)
f = pathlib.Path(alvo) / p["arquivo"]
texto = f.read_text()
if p["de"] not in texto:
    sys.exit(f"preparo nao aplicavel: {p['de']!r} nao esta em {p['arquivo']}")
f.write_text(texto.replace(p["de"], p["para"]))
print(f"preparo aplicado em {p['arquivo']}: {p['de']} -> {p['para']}")
PY

# ------------------------------------------------------------------- sessao
SESSION_FILE="$RUNS/$COND.session"
set -- -p "$PROMPT $AUTORIZACAO" --output-format json --permission-mode bypassPermissions
if [ "$SESSAO" = resume ]; then
  [ -f "$SESSION_FILE" ] || { echo "tarefa $TAREFA pede resume, mas nao ha sessao anterior em $SESSION_FILE" >&2; exit 2; }
  set -- "$@" --resume "$(cat "$SESSION_FILE")"
fi

SAIDA="$RUNS/$TAREFA-$COND.json"
echo "=== $TAREFA / $COND (sessao: $SESSAO)"
( cd "$ALVO" && claude "$@" ) > "$SAIDA" 2> "$RUNS/$TAREFA-$COND.err" || true

python3 -c '
import json, sys, pathlib
d = json.load(open(sys.argv[1]))
pathlib.Path(sys.argv[2]).write_text(d.get("session_id", "") + "\n")
print("turns", d.get("num_turns"), "| custo", round(d.get("total_cost_usd", 0), 3))
' "$SAIDA" "$SESSION_FILE"

# ---------------------------------------------------------------------- DoD
# Rodada DEPOIS de cada sessao, nas duas condicoes: e o unico jeito de saber
# em que estado a sessao deixou o repositorio sem acreditar no que ela disse.
DOD=$(cat "$RUNS/dod.txt")
( cd "$ALVO" && eval "$DOD" >"$RUNS/$TAREFA-$COND.dod.log" 2>&1 ) && COD=0 || COD=$?
printf '%s\n' "$COD" > "$RUNS/$TAREFA-$COND.dod"
[ "$COD" -eq 0 ] && echo "DoD apos a sessao: VERDE" || echo "DoD apos a sessao: VERMELHA (exit $COD)"
