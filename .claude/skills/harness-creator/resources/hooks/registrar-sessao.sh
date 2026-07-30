#!/bin/sh
# registrar-sessao.sh — hook de OBSERVACAO do agent loop.
#
# Grava uma linha por chamada de ferramenta em .harness/trace/AAAA-MM-DD.jsonl.
# Existe para responder a pergunta que o `medir-aderencia.sh` declara nao
# conseguir responder: o que aconteceu numa sessao que NAO COMMITOU NADA.
# Git so registra o que virou commit; duas horas de agente rodando em circulos
# e desistindo nao deixam rastro nenhum.
#
# ELE SAI 0 SEMPRE. NAO E ENFORCEMENT.
# Esta e a propriedade que decide o desenho inteiro, e o motivo de isto ser um
# script SEPARADO em vez de umas linhas dentro do gate:
#   - No Claude Code e no Devin, hook que morre some em silencio — mas se
#     estivesse DENTRO do gate, mataria o gate junto, e gate morto falha
#     ABERTO: o comando destrutivo executa.
#   - No Cursor, hook registrado com `failClosed` que falha bloqueia o shell
#     inteiro. Por isso este NUNCA e registrado com `failClosed`.
# Observacao nao pode custar o enforcement. Falha de escrita (disco cheio,
# diretorio read-only, permissao) e engolida de proposito.
#
# POR QUE SO awk, SEM PYTHON
# O gate e o format-on-edit tentam Python antes do awk porque uma leitura
# errada ali significa gate falhando aberto ou formatter rodando no arquivo
# errado. Aqui uma leitura errada custa UMA LINHA DE TRACE IMPERFEITA, que nao
# quebra nada — e este hook dispara em TODA chamada de ferramenta, onde subir
# um interpretador Python a cada evento seria um imposto permanente sobre a
# sessao. Custo assimetrico, decisao diferente.
#
# O QUE NAO ENTRA NO ARQUIVO, e por que
# O comando completo NAO e gravado. `export TOKEN=...`,
# `curl -H "Authorization: ..."` e `mysql -pSENHA` sao comandos comuns, e um
# arquivo em disco com segredo em claro e pior que nao ter trace nenhum.
# A regra e LISTA DE PERMISSAO, nao lista de bloqueio: guarda-se o binario e,
# do segundo token, apenas o que parece subcomando (`npm test`, `git commit`).
# Qualquer coisa fora desse formato — maiuscula, `=`, `-`, string longa — e
# descartada. Lista de bloqueio erra por omissao; a de permissao erra por
# excesso de zelo, que aqui custa so diagnostico.
#
# O QUE ELE NAO VE — declarado porque instrumento que nao publica seu limite
# e lido como se nao tivesse nenhum:
#   - So o que os HOOKS veem: chamadas de ferramenta. Raciocinio do agente,
#     tokens consumidos e custo em dolar sao invisiveis.
#   - Sessao que nao roda ferramenta nenhuma nao deixa linha.
#   - O VEREDITO do gate. Contar bloqueios exigiria o gate escrever em disco,
#     e qualquer escrita dentro dele pode faze-lo falhar aberto. Nao vale a
#     troca.
#   - Nao e APM: sem spans, sem duracao por chamada, sem correlacao.
#
# Registrado nos tres agentes-alvo, ao lado do gate e nunca com failClosed:
#   Claude Code  .claude/settings.json   PreToolUse (Bash) + PostToolUse (Edit)
#   Devin CLI    .devin/hooks.v1.json    PreToolUse (exec) + PostToolUse (edit)
#   Cursor       .cursor/hooks.json      beforeShellExecution + afterFileEdit

TRACE_DIR="${HARNESS_TRACE_DIR:-.harness/trace}"
# Teto por arquivo. Acima dele o hook para de anexar em silencio, em vez de
# truncar: trace pela metade que se apresenta como completo engana mais que
# trace ausente, e um .jsonl de sessao que cresce sem limite acaba sendo
# apagado a mao junto com o diretorio.
TRACE_MAX_BYTES="${HARNESS_TRACE_MAX_BYTES:-2097152}"

INPUT="$(cat 2>/dev/null)"

# Extrai uma chave string do JSON, nos dois formatos em uso:
#   {"tool_input":{"command":...}}  Claude Code, Devin CLI
#   {"command":...}                 Cursor
# Le a primeira ocorrencia da chave, venha de onde vier — para trace, saber
# QUAL das duas posicoes trouxe o valor nao muda nada.
extrai() {
  printf '%s' "$INPUT" | awk -v k="$1" '
    { s = s $0 }
    END {
      p = index(s, "\"" k "\"")
      if (p == 0) exit 0
      rest = substr(s, p + length(k) + 2)
      q = index(rest, "\"")
      if (q == 0) exit 0
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
    }' 2>/dev/null
}

# Reducao do comando a binario + subcomando. Ver "O QUE NAO ENTRA" no topo.
reduz_comando() {
  printf '%s' "$1" | awk '
    {
      t1 = $1
      # `TOKEN=abc npm test`: a atribuicao vem ANTES do binario. Guarda-se a
      # chave e joga-se fora o valor.
      if (index(t1, "=") > 0) sub(/=.*/, "=***", t1)
      # Lista de permissao para o segundo token: subcomando e minusculo e
      # curto (`test`, `commit`, `run`, `spotless:apply`). O resto — flag,
      # caminho, atribuicao, base64 — nao entra.
      t2 = ($2 ~ /^[a-z][a-z0-9:._-]{0,29}$/) ? $2 : ""
      print (t2 == "" ? t1 : t1 " " t2)
    }' 2>/dev/null
}

escapa_json() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n\r' 2>/dev/null
}

registrar() {
  comando="$(extrai command)"
  arquivo="$(extrai file_path)"

  # Sessao vem do payload quando o agente a manda (o Claude Code manda
  # `session_id`); vazia quando nao manda. O leitor cai para agrupamento por
  # intervalo de tempo nesse caso — ver `medir-aderencia.sh`.
  sessao="$(extrai session_id)"

  if [ -n "$comando" ]; then
    evento=shell
    alvo="$(reduz_comando "$comando")"
  elif [ -n "$arquivo" ]; then
    evento=edit
    alvo="$arquivo"
  else
    # Outro evento, outra ferramenta: nada de util a registrar.
    return 0
  fi

  [ -d "$TRACE_DIR" ] || mkdir -p "$TRACE_DIR" 2>/dev/null || return 0

  dia="$(date -u +%Y-%m-%d 2>/dev/null)" || return 0
  arq="$TRACE_DIR/$dia.jsonl"

  if [ -f "$arq" ]; then
    tamanho="$(wc -c < "$arq" 2>/dev/null | tr -d ' ')"
    case "$tamanho" in
      ''|*[!0-9]*) ;;
      *) [ "$tamanho" -ge "$TRACE_MAX_BYTES" ] && return 0 ;;
    esac
  fi

  printf '{"ts":"%s","evento":"%s","alvo":"%s","sessao":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null)" \
    "$evento" \
    "$(escapa_json "$alvo")" \
    "$(escapa_json "$sessao")" \
    >> "$arq" 2>/dev/null || return 0
}

# Toda a saida e descartada: hook de observacao que imprime em stdout/stderr
# vira ruido no contexto do agente a cada chamada de ferramenta, e no Cursor
# stderr de hook e apresentado ao usuario.
registrar >/dev/null 2>&1

exit 0
