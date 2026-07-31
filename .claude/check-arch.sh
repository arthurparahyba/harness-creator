#!/usr/bin/env bash
# check-arch.sh — runner das regras arquiteturais de .harness/arch-rules.json.
#
# Le o registro de regras, roda o `check` de cada uma e, nas que falham,
# imprime WHAT / WHY / FIX. Sai 1 se qualquer regra falhar, 0 se todas
# passarem, para entrar na cadeia de verificacao ao lado dos outros sensores.
#
# POR QUE UM REGISTRO, E NAO UMA REVISAO
# Uma regra arquitetural pode morar em quatro lugares, com forcas diferentes:
# na cabeca das pessoas (some com a rotatividade), na revisao (depende de
# quem revisou e do dia), num documento (nao falha — o agente le ou nao le) e
# num comando que quebra. So o ultimo impede a violacao. Este script e o
# ultimo degrau.
#
# A CATRACA
# Todo problema novo encontrado numa revisao vira uma regra aqui. O registro
# so cresce, e cada classe de erro e cometida UMA vez. Sem esse habito o
# arquivo vira uma lista congelada que perde relevancia conforme o projeto
# muda.
#
# POR QUE A MENSAGEM TEM TRES CAMPOS
# Um `grep` sozinho diria "violacao em X" — suficiente para um humano que
# conhece o projeto, insuficiente para um agente. Agente ve comando falhando
# e quer faze-lo parar de falhar; sem contexto, os caminhos mais curtos sao
# reescrever a regra ou driblar o check.
#   what  o que quebrou e onde   — sem ele, o agente procura no escuro
#   why   por que a regra existe — sem ele, o agente "conserta" apagando-a
#   fix   qual e a saida correta — sem ele, o agente inventa uma saida torta
#
# Uso:
#   bash .claude/check-arch.sh [caminho/do/repo]
set -uo pipefail

RAIZ="${1:-.}"
REGRAS="$RAIZ/.harness/arch-rules.json"

if [ ! -f "$REGRAS" ]; then
  echo "check-arch: $REGRAS nao encontrado — nenhuma regra para verificar."
  exit 0
fi

# jq quando existir; senao, um parser em awk. Exigir jq transformaria o
# sensor em bloqueio em toda maquina que nao o tem — o mesmo erro que os
# hooks ja cometeram exigindo Python. O formato e uma lista de objetos
# planos, sem aninhamento, o que torna o fallback viavel.
_campos() {
  if command -v jq >/dev/null 2>&1; then
    jq -r '.[] | [.id, .description, .check, (.expect // "exit-0"), .what, .why, .fix]
           | @tsv' "$REGRAS"
    return
  fi
  awk '
    function limpa(s) {
      sub(/^[^:]*:[[:space:]]*"/, "", s)
      sub(/",?[[:space:]]*$/, "", s)
      gsub(/\\"/, "\"", s)
      return s
    }
    /"id"[[:space:]]*:/          { id   = limpa($0) }
    /"description"[[:space:]]*:/ { desc = limpa($0) }
    /"check"[[:space:]]*:/       { chk  = limpa($0) }
    /"expect"[[:space:]]*:/      { exp  = limpa($0) }
    /"what"[[:space:]]*:/        { what = limpa($0) }
    /"why"[[:space:]]*:/         { why  = limpa($0) }
    /"fix"[[:space:]]*:/ {
      fix = limpa($0)
      if (exp == "") exp = "exit-0"
      printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n", id, desc, chk, exp, what, why, fix
      id = desc = chk = exp = what = why = fix = ""
    }
  ' "$REGRAS"
}

falhas=0
total=0

while IFS=$'\t' read -r id desc chk expect what why fix; do
  [ -z "${id:-}" ] && continue
  total=$((total + 1))

  ( cd "$RAIZ" && eval "$chk" ) >/dev/null 2>&1
  codigo=$?

  # `exit-0` (padrao) espera sucesso; `exit-nonzero` espera falha, para a
  # regra que afirma a AUSENCIA de algo sem depender de `!` dentro do JSON.
  if [ "$expect" = "exit-nonzero" ]; then
    ok=$([ "$codigo" -ne 0 ] && echo 1 || echo 0)
  else
    ok=$([ "$codigo" -eq 0 ] && echo 1 || echo 0)
  fi

  if [ "$ok" = "1" ]; then
    echo "  [ok  ] $id  $desc"
  else
    falhas=$((falhas + 1))
    echo "  [FAIL] $id  $desc"
    echo "         WHAT: $what"
    echo "         WHY:  $why"
    echo "         FIX:  $fix"
  fi
done < <(_campos)

echo
if [ "$falhas" -gt 0 ]; then
  echo "check-arch: $falhas de $total regra(s) violada(s)."
  exit 1
fi
echo "check-arch: $total regra(s), nenhuma violada."
exit 0
