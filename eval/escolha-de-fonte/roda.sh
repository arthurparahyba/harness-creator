#!/bin/sh
# roda.sh — bateria NAO deterministica da escolha de fonte.
#
# Roda o MESMO pedido de funcionalidade N vezes num repositorio alvo que ja
# tem o harness instalado, e reporta em quantas delas a resposta acendeu os
# seis sinais do `detecta.py`. Custa dolares e depende de rede: por isso vive
# fora da Definition of Done e nao e chamado por teste nenhum.
#
# O que ele produz e TAXA, nao veredito. Uma rodada verde nao prova
# confiabilidade e uma vermelha nao prova defeito — o detector tem falso
# negativo declarado (ver o docstring do detecta.py).
#
# Uso:
#   sh eval/escolha-de-fonte/roda.sh <repo-alvo> [N]
set -eu

AQUI=$(cd "$(dirname "$0")" && pwd)
ALVO=${1:?uso: roda.sh <repo-alvo> [N]}
N=${2:-5}
SAIDA="$ALVO/.harness-eval-escolha"
PEDIDO="Quero implementar agendamento de consultas para os pets: o dono escolhe um veterinario e um horario. Pode implementar?"

[ -f "$ALVO/AGENTS.md" ] || { echo "alvo sem AGENTS.md: $ALVO (instale o harness antes)" >&2; exit 2; }
mkdir -p "$SAIDA"

# SEM linha de autorizacao, de proposito: autorizar o agente a aprovar em nome
# do usuario contamina exatamente a decisao que esta sendo medida.
i=1
while [ "$i" -le "$N" ]; do
  echo "=== rodada $i de $N"
  ( cd "$ALVO" && claude -p "$PEDIDO" --output-format json --permission-mode bypassPermissions ) \
    > "$SAIDA/rodada-$i.json" 2> "$SAIDA/rodada-$i.err" || true
  i=$((i + 1))
done

ACESAS=0
i=1
while [ "$i" -le "$N" ]; do
  if python3 "$AQUI/detecta.py" "$SAIDA/rodada-$i.json" > "$SAIDA/rodada-$i.txt" 2>&1; then
    ACESAS=$((ACESAS + 1))
  fi
  i=$((i + 1))
done

echo
echo "=== $ACESAS de $N rodadas com os seis sinais. Detalhe por rodada em $SAIDA/"
echo "Taxa, nao veredito: o detector tem falso negativo declarado."
