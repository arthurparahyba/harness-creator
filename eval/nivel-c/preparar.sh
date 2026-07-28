#!/bin/sh
# preparar.sh — monta o painel de uma rodada do nivel C.
#
# Cria duas copias limpas do repositorio alvo a partir do MESMO commit:
#   <workdir>/control/   sem harness
#   <workdir>/harness/   onde a skill sera aplicada
# e roda a DoD no control para provar que o baseline esta verde. Baseline
# vermelho invalida T4 inteiro: um bug plantado nao se distingue do que ja
# estava quebrado.
#
# Uso:
#   sh eval/nivel-c/preparar.sh <workdir> [--repo URL] [--ref COMMIT] [--dod CMD]
#
# O passo de aplicar a skill em <workdir>/harness/ e MANUAL, de proposito:
# quem aplica a skill e um modelo lendo o SKILL.md, e e isso que o nivel D
# mede. Este script prepara o terreno e para ali.
set -eu

AQUI=$(cd "$(dirname "$0")" && pwd)
TAREFAS="$AQUI/tarefas.json"

le_alvo() {
  python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['alvo_padrao'][sys.argv[2]])" \
    "$TAREFAS" "$1"
}

[ $# -ge 1 ] || { sed -n '2,20p' "$0"; exit 2; }
WORKDIR="$1"; shift
REPO=$(le_alvo repo)
REF=""
DOD=$(le_alvo dod)
while [ $# -gt 0 ]; do
  case "$1" in
    --repo) shift; REPO="${1:?}" ;;
    --ref) shift; REF="${1:?}" ;;
    --dod) shift; DOD="${1:?}" ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
  shift
done

[ -e "$WORKDIR" ] && { echo "workdir ja existe: $WORKDIR (aponte para um caminho novo)" >&2; exit 2; }
mkdir -p "$WORKDIR/runs"

echo "=== [1/4] Clonando $REPO"
git clone --quiet "$REPO" "$WORKDIR/origem"
if [ -n "$REF" ]; then
  git -C "$WORKDIR/origem" checkout --quiet "$REF"
fi
BASE=$(git -C "$WORKDIR/origem" rev-parse --short HEAD)
echo "commit base: $BASE"

echo "=== [2/4] Duas copias do mesmo commit"
# Clone local em vez de copia de diretorio: cada celula precisa do proprio
# git limpo, sem herdar artefato de build nem o index da outra.
git clone --quiet "$WORKDIR/origem" "$WORKDIR/control"
git clone --quiet "$WORKDIR/origem" "$WORKDIR/harness"

echo "=== [3/4] Baseline no control: $DOD"
if ( cd "$WORKDIR/control" && eval "$DOD" >"$WORKDIR/runs/baseline.log" 2>&1 ); then
  echo "baseline VERDE (log em $WORKDIR/runs/baseline.log)"
else
  echo "baseline VERMELHO — interrompa: T4 nao mede nada com a suite ja quebrada." >&2
  tail -20 "$WORKDIR/runs/baseline.log" >&2
  exit 1
fi

printf '%s\n' "$BASE" > "$WORKDIR/runs/commit-base.txt"
printf '%s\n' "$DOD" > "$WORKDIR/runs/dod.txt"

echo "=== [4/4] Passo manual"
cat <<FIM

Agora aplique a skill harness-creator em:

    $WORKDIR/harness

e commite o resultado nesse repositorio (a celula precisa comecar de uma
arvore limpa, senao o estado do harness se mistura com o trabalho das
tarefas). Confira com:

    sh $WORKDIR/harness/.claude/verificar-harness.sh --raiz $WORKDIR/harness

Depois, para cada tarefa e cada condicao:

    sh eval/nivel-c/roda.sh $WORKDIR control T1
    sh eval/nivel-c/roda.sh $WORKDIR harness T1

e ao fim:

    python3 eval/nivel-c/mede.py $WORKDIR
FIM
