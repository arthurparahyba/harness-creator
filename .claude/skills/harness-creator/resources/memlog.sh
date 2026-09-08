#!/bin/sh
# memlog.sh — caderno de bordo append-only da funcionalidade em andamento.
#
# Escreve a JORNADA de uma funcionalidade (o que aconteceu, o que se decidiu),
# uma entrada por chamada. O estado ATUAL fica no SESSION_STATE.md; o que virou
# conhecimento duravel, em knowledge/. Aqui e so o registro cronologico.
#
# Invariantes — nao mude sem entender por que existem:
#  1. append-only e cronologico: so acrescenta no fim. NAO ha subcomando de
#     editar ou apagar. A ordem das linhas E a estrutura; historico nao se
#     reescreve.
#  2. write-only / cego: cada chamada ecoa {"entries":N} e nada mais. Quem
#     chama NUNCA rele o arquivo durante a sessao — so no resume, e ai quem le
#     e o agente. Registrar 40 achados custa 40 escritas e zero releituras.
#  3. sem status de ciclo de vida: "sessao concluida" e uma ENTRADA
#     (append event "..."), nunca um campo de cabecalho que teria de mutar. O
#     estado se descobre lendo as ultimas entradas.
#
# Escrita atomica: monta o novo conteudo num temp no mesmo diretorio e faz `mv`
# (atomico no mesmo filesystem). Um crash nunca deixa meia entrada. Uso serial.
set -eu

usage() {
  echo 'uso: memlog.sh init   <arquivo> [campo=valor ...]' >&2
  echo '     memlog.sh append <arquivo> <tipo> <texto>' >&2
  exit 2
}

[ $# -ge 2 ] || usage
cmd=$1
file=$2
shift 2

_atomic() { # le o novo conteudo do stdin e grava em "$file" de forma atomica
  _dir=$(dirname "$file")
  mkdir -p "$_dir"
  _tmp=$(mktemp "$_dir/.memlog.XXXXXX")
  cat >"$_tmp"
  mv "$_tmp" "$file"
}

_frontmatter() { # imprime um cabecalho a partir dos campos passados
  echo '---'
  for _kv in "$@"; do
    printf '%s: %s\n' "${_kv%%=*}" "${_kv#*=}"
  done
  printf 'updated: %s\n' "$(date -u +%Y-%m-%dT%H:%M)"
  echo '---'
  echo
}

case "$cmd" in
  init)
    _frontmatter "$@" | _atomic
    ;;
  append)
    [ $# -ge 2 ] || usage
    _type=$1
    shift
    _text=$*
    if [ -f "$file" ]; then
      { cat "$file"; printf -- '- (%s) %s\n' "$_type" "$_text"; } | _atomic
    else
      # auto-init com cabecalho minimo: append nunca falha por falta de init
      { _frontmatter; printf -- '- (%s) %s\n' "$_type" "$_text"; } | _atomic
    fi
    ;;
  *)
    usage
    ;;
esac

entries=$(grep -c '^- (' "$file" 2>/dev/null || true)
[ -n "$entries" ] || entries=0
printf '{"ok":true,"memlog":"%s","entries":%s}\n' "$file" "$entries"
