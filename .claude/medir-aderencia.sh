#!/bin/sh
# medir-aderencia.sh — mede se o PROTOCOLO do AGENTS.md foi seguido.
#
# NAO E O verificar-harness.sh, e a diferenca decide tudo o que vem abaixo:
#
#   verificar-harness.sh  o harness esta integro?   arquivos parados, agora
#   check-arch.sh         o codigo respeita regras?  arvore de trabalho, agora
#   medir-aderencia.sh    o protocolo foi seguido?   historico, ao longo do tempo
#
# Um harness perfeitamente instalado e integralmente ignorado passa no
# verificador com nota maxima. E essa lacuna que este script fecha.
#
# POR QUE O GIT, E NAO O SESSION_STATE
# O SESSION_STATE.md e escrito pelo mesmo agente cuja disciplina se quer
# medir: testemunha e reu. O historico do git e subproduto — o agente
# commita para trabalhar, nao para se avaliar —, o que o torna dificil de
# maquiar sem esforco deliberado.
#
# ISTO NAO E UM GATE
# O exit e 0 mesmo com todas as medidas em alerta. "Aderencia caiu de 80%
# para 60%" nao tem conserto no harness: tem conversa com o time. Atras de
# um exit 1 isso viraria "alguem quebrou alguma coisa", que e falso, e a
# reacao previsivel a um vermelho que ninguem causou e desligar o sensor.
# Exit 2 e reservado para "nao consegui medir", que e outra coisa.
#
# O QUE ELE NAO VE — declarado aqui porque um instrumento que nao declara
# seu limite e lido como se nao tivesse nenhum:
#   - Qualidade. Um `checkpoint:` impecavel sobre codigo ruim marca ok.
#     Qualidade e trabalho da DoD.
#   - Eficacia. Se o protocolo VALE A PENA e experimento A/B, nao leitura
#     de historico.
#   - Intencao. A medida 5 sabe que houve sessao com edicao e sem commit;
#     nao sabe se o agente desistiu, se o usuario interrompeu, ou se a
#     edicao foi descartada de proposito.
#
# ATE ONDE ELE VE
# As medidas 1 a 4 leem git, e git so registra o que virou commit: por elas,
# duas horas de agente rodando em circulos e desistindo eram invisiveis. A
# medida 5 fecha esse buraco lendo o trace do `registrar-sessao.sh`, gravado
# pelos hooks a cada chamada de ferramenta. Sem o trace (harness recem
# instalado, hooks nao registrados) ela se declara cega em vez de calar.
#
# POSIX sh, sem Python e sem jq: precisa rodar em repo Go, .NET ou Java, e
# vale igual nos tres agentes-alvo (Claude Code, Devin CLI, Cursor).
#
# Uso:
#   sh .claude/medir-aderencia.sh                 # tabela legivel
#   sh .claude/medir-aderencia.sh --json          # para consumo por script
#   sh .claude/medir-aderencia.sh --commits 100   # janela maior (padrao 30)
#   sh .claude/medir-aderencia.sh --raiz DIR      # mede outro diretorio
#
# Saida: 0 = mediu (com ou sem alerta), 2 = nao consegui medir.
set -u

FORMATO=texto
RAIZ=.
JANELA=30
while [ $# -gt 0 ]; do
  case "$1" in
    --json) FORMATO=json ;;
    --commits) shift; JANELA="${1:-30}" ;;
    --raiz) shift; RAIZ="${1:-.}" ;;
    -h|--help) sed -n '2,45p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
  shift
done

cd "$RAIZ" 2>/dev/null || { echo "diretorio inacessivel: $RAIZ" >&2; exit 2; }

case "$JANELA" in
  ''|*[!0-9]*) echo "--commits espera um numero, recebeu: $JANELA" >&2; exit 2 ;;
esac

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "sem repositorio git — nao ha historico para medir." >&2
  exit 2
fi

# Repo sem commit nenhum nao e desobediencia, e ausencia de dados. Reportar
# 0% de aderencia num scaffold recem-criado seria um vermelho que acusa o
# usuario de algo que ele ainda nao teve chance de fazer.
if ! git rev-parse HEAD >/dev/null 2>&1; then
  echo "repositorio sem commits — nada para medir ainda." >&2
  exit 2
fi

TOTAL=0
ALERTAS=0
SEP=""
BUFFER=""
if [ "$FORMATO" = json ]; then
  BUFFER=$(mktemp 2>/dev/null || printf '/tmp/medir-aderencia.%s' $$)
  : > "$BUFFER"
  trap 'rm -f "$BUFFER"' EXIT INT TERM
fi

escapar() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' '
}

# Toda escrita em stdout passa por aqui, e o motivo e o `trap ... EXIT` que
# este script instala para limpar os temporarios. Com um trap de EXIT
# registrado, o shell SOBREVIVE ao SIGPIPE em vez de morrer calado, e o
# printf passa a reportar `write error: Broken pipe` no stderr. Quem faz
# `medir-aderencia.sh | head` — o uso mais natural de um relatorio — recebia
# um erro no terminal. Ferramenta de diagnostico nao pode sujar a saida de
# quem a usa do jeito obvio.
diz() {
  printf "$@" 2>/dev/null || exit 0
}

# Cada medida imprime WHAT/WHY/FIX quando alerta, no mesmo formato que o
# `arch-rules.json` usa. Numero solto ("aderencia: 43%") nao diz a ninguem o
# que fazer na segunda-feira; agente que ve numero ruim sem receita tende a
# atacar o medidor.
medida() {
  _nome="$1"; _alerta="$2"; _valor="$3"; _what="$4"; _why="$5"; _fix="$6"; _cego="$7"
  TOTAL=$((TOTAL + 1))
  [ "$_alerta" -eq 0 ] || ALERTAS=$((ALERTAS + 1))
  if [ "$FORMATO" = json ]; then
    if [ "$_alerta" -eq 0 ]; then _b=false; else _b=true; fi
    printf '%s\n    {"medida": "%s", "alerta": %s, "valor": "%s", "cego_para": "%s"}' \
      "$SEP" "$(escapar "$_nome")" "$_b" "$(escapar "$_valor")" "$(escapar "$_cego")" >> "$BUFFER"
    SEP=","
  else
    if [ "$_alerta" -eq 0 ]; then _st="[ok    ]"; else _st="[ALERTA]"; fi
    diz '%s %-38s %s\n' "$_st" "$_nome" "$_valor"
    if [ "$_alerta" -ne 0 ]; then
      diz '         WHAT: %s\n' "$_what"
      diz '         WHY:  %s\n' "$_why"
      diz '         FIX:  %s\n' "$_fix"
    fi
    diz '         (nao ve: %s)\n' "$_cego"
  fi
}

# ------------------------------------------------------------- janela de log
# A JANELA COMECA QUANDO O HARNESS CHEGOU, e este e o ponto do arquivo que
# mais custou para descobrir. Sem isso, a medida 1 pergunta "que fracao dos
# commits segue o protocolo?" e aplica a pergunta a commits feitos ANTES de o
# protocolo existir. Rodando no spring-petclinic — anos de historico do time
# do Spring — ela reportava `0 de 1 (0%)` e ALERTA, sobre um commit que trata
# de um bug de PostgreSQL e nunca teve como se chamar `checkpoint: Grupo N`.
#
# E instalar um relogio de ponto hoje e emitir relatorio dizendo que os
# funcionarios nao bateram ponto nos ultimos tres anos: o numero esta
# aritmeticamente certo e a conclusao e absurda. E o custo e concreto — a
# primeira coisa que alguem le depois de instalar o harness passa a ser um
# vermelho acusando o time de algo que ele nao teve como fazer. Alarme falso
# e o que faz o sensor ser ignorado, e sensor ignorado leva o relatorio junto.
#
# A data sai do manifesto, que a skill grava na geracao.
INSTALADO_EM=""
if [ -f .claude/harness.json ]; then
  INSTALADO_EM=$(awk '
    match($0, /"gerado_em"[ \t]*:[ \t]*"[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"/) {
      campo = substr($0, RSTART, RLENGTH)
      sub(/^.*"[ \t]*:[ \t]*"/, "", campo)
      sub(/"$/, "", campo)
      print campo
      exit
    }' .claude/harness.json 2>/dev/null)
fi

LOG=$(mktemp 2>/dev/null || printf '/tmp/medir-aderencia-log.%s' $$)
if [ -n "$INSTALADO_EM" ]; then
  git log -n "$JANELA" --no-merges --since="$INSTALADO_EM" \
    --format='%H%x09%s' > "$LOG" 2>/dev/null
else
  git log -n "$JANELA" --no-merges --format='%H%x09%s' > "$LOG" 2>/dev/null
fi
trap 'rm -f "$LOG" ${BUFFER:-}' EXIT INT TERM

N_COMMITS=$(awk 'END {print NR}' "$LOG")
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")

# Sem manifesto legivel a janela volta a ser o historico inteiro. Isso e
# DECLARADO em cada medida que depende dela, nao silencioso: trocar um alarme
# falso conhecido por um numero que ninguem sabe interpretar nao e conserto.
if [ -n "$INSTALADO_EM" ]; then
  JANELA_DESC="desde a instalacao do harness ($INSTALADO_EM)"
  CEGO_JANELA="commit de merge, e commit anterior a $INSTALADO_EM — de proposito"
else
  JANELA_DESC="historico completo (sem .claude/harness.json legivel)"
  CEGO_JANELA="QUANDO o harness foi instalado: sem manifesto, commits anteriores a ele entram na conta e derrubam a proporcao"
fi

if [ "$FORMATO" != json ]; then
  diz 'ADERENCIA AO PROTOCOLO — %s commit(s) em %s, %s\n\n' \
    "$N_COMMITS" "$BRANCH" "$JANELA_DESC"
fi

# --------------------------------------------- 1. proporcao de checkpoints
# O protocolo manda "um commit por grupo concluido: checkpoint: <nome>".
# A proporcao e a leitura mais direta de quanto do trabalho passou pela
# fronteira de grupo — e a fronteira e o que torna o reset de contexto
# seguro. Sem ela o WIP=1 vira texto.
N_CHECK=$(awk -F'\t' '$2 ~ /^checkpoint:/ {n++} END {print n+0}' "$LOG")
if [ "$N_COMMITS" -eq 0 ]; then
  # Zero commit na janela nao e indisciplina, e ausencia de dados — e a
  # medida 5 ja tratava o caso equivalente assim desde o Grupo 41 (sem
  # trace, ela imprime "sem trace" e se declara cega). Eram duas medidas do
  # mesmo script tratando a mesma situacao de formas opostas; agora nao sao.
  if [ -n "$INSTALADO_EM" ]; then
    _valor="nenhum commit desde $INSTALADO_EM"
    _cego="tudo: o harness foi instalado e ainda nao houve commit para julgar"
  else
    _valor="repositorio sem commit na janela"
    _cego="tudo: nao ha commit nos ultimos $JANELA"
  fi
  medida "Commits de checkpoint" 0 "$_valor" "" "" "" "$_cego"
else
  PCT=$(( N_CHECK * 100 / N_COMMITS ))
  # 50% e um limiar declarado, nao descoberto: abaixo dele a maior parte do
  # trabalho nao passou por checkpoint, e a fronteira deixou de ser a regra.
  if [ "$PCT" -lt 50 ]; then _a=1; else _a=0; fi
  medida "Commits de checkpoint" "$_a" "$N_CHECK de $N_COMMITS ($PCT%)" \
    "a maioria dos commits nao segue 'checkpoint: <nome do grupo>'" \
    "sem a fronteira de grupo nao ha ponto limpo para reiniciar contexto — o beneficio central do WIP=1 nao esta acontecendo" \
    "feche o proximo grupo com a DoD e commite com o prefixo 'checkpoint: '" \
    "$CEGO_JANELA"
fi

# ------------------------------- 2. grupo concluido sem commit de checkpoint
# Fonte de trabalho na precedencia do AGENTS.md: change ativa do OpenSpec
# primeiro, TASKS.md depois. Medir a fonte errada produziria zero grupos e
# um falso ok.
FONTE=""
if [ -d openspec/changes ]; then
  for d in openspec/changes/*/; do
    [ -d "$d" ] || continue
    case "$d" in */archive/) continue ;; esac
    [ -f "$d/tasks.md" ] && FONTE="$FONTE $d/tasks.md"
  done
fi
if [ -z "$FONTE" ] && [ -f TASKS.md ]; then FONTE="TASKS.md"; fi

if [ -z "$FONTE" ]; then
  medida "Grupos concluidos com checkpoint" 1 "sem fonte de trabalho" \
    "nao ha TASKS.md nem change ativa em openspec/changes/" \
    "sem fonte de trabalho o agente inventa tarefas, que e o que o protocolo proibe — e nao ha o que comparar com o historico" \
    "crie TASKS.md com ao menos um grupo no formato '## Grupo N - <objetivo>'" \
    "plano que vive fora do repositorio (issue tracker, documento)"
else
  # Um grupo esta concluido quando TODAS as suas tasks estao marcadas. E a
  # definicao que sai do proprio template (`- [ ]` / `- [x]`), e nao do
  # simbolo de status no titulo, que e convencao de cada repo.
  CONCLUIDOS=$(awk '
    function fecha() {
      if (nome == "") return
      if (feitas > 0 && abertas == 0) print nome
      nome = ""; feitas = 0; abertas = 0
    }
    /^##[[:space:]]+Grupo[[:space:]]/ { fecha(); nome = $0; next }
    /^[[:space:]]*-[[:space:]]*\[[ xX]\]/ {
      if (nome == "") next
      if ($0 ~ /\[[xX]\]/) feitas++; else abertas++
    }
    END { fecha() }
  ' $FONTE | awk 'END {print NR}')
  # Historico INTEIRO, nao a janela: grupos se acumulam ao longo da vida do
  # projeto, e comparar o total deles com uma amostra de 30 commits acusaria
  # todo repositorio maduro.
  CHECK_TOTAL=$(git log --no-merges --format='%s' 2>/dev/null \
                | awk '/^checkpoint:/ {n++} END {print n+0}')
  if [ "$CONCLUIDOS" -gt "$CHECK_TOTAL" ]; then _a=1; else _a=0; fi
  medida "Grupos concluidos com checkpoint" "$_a" \
    "$CONCLUIDOS concluido(s), $CHECK_TOTAL checkpoint(s)" \
    "ha grupo marcado como concluido sem commit de checkpoint correspondente" \
    "marcar a caixinha sem fechar o checkpoint faz 'concluido' voltar a ser opiniao, que e exatamente o que a DoD existe para impedir" \
    "confira se o trabalho de cada grupo marcado esta commitado antes de marca-lo" \
    "QUAL grupo ficou sem checkpoint — a comparacao e de contagem, nao de nome"
fi

# ----------------------------------------- 3. SESSION_STATE nos checkpoints
# O protocolo manda atualizar o SESSION_STATE.md ao concluir cada grupo.
# Checkpoint sem handoff deixa a proxima sessao comecando cega, que e o modo
# de falha que o arquivo existe para evitar.
#
# O HANDOFF PODE VIR NO COMMIT SEGUINTE, e a medida aceita os dois casos. O
# protocolo diz "atualize o SESSION_STATE" ao concluir o grupo, sem exigir
# que seja no mesmo commit — e registrar o hash do checkpoint no arquivo
# obriga o commit dele a existir antes. Exigir o mesmo commit acusaria de
# desobediencia quem seguiu o protocolo ao pe da letra: medido contra o
# proprio repositorio da skill, era 4 de 17 pela regra estrita e 17 de 17
# pela regra correta. Uma medida com falso positivo desse tamanho e
# desligada na primeira semana, e leva o resto do relatorio junto.
if [ "$N_CHECK" -gt 0 ]; then
  COM_ESTADO=0
  # Para cada checkpoint, o par (ele, seu sucessor cronologico). O log vem do
  # mais novo para o mais antigo, entao o sucessor e a LINHA ANTERIOR.
  PARES=$(awk -F'\t' '$2 ~ /^checkpoint:/ {print $1 "\t" prev} {prev = $1}' "$LOG")
  printf '%s\n' "$PARES" | while IFS="$(printf '\t')" read -r sha seguinte; do
    [ -n "${sha:-}" ] || continue
    _achou=0
    for _c in "$sha" "${seguinte:-}"; do
      [ -n "$_c" ] || continue
      if git show --name-only --format='' "$_c" 2>/dev/null \
         | grep -q '^SESSION_STATE\.md$'; then
        _achou=1
        break
      fi
    done
    echo "$_achou"
  done > "$LOG.estado"
  COM_ESTADO=$(awk '/^1$/ {n++} END {print n+0}' "$LOG.estado")
  rm -f "$LOG.estado"
  if [ "$COM_ESTADO" -lt "$N_CHECK" ]; then _a=1; else _a=0; fi
  medida "SESSION_STATE nos checkpoints" "$_a" "$COM_ESTADO de $N_CHECK" \
    "ha checkpoint sem atualizacao do SESSION_STATE.md nele nem no commit seguinte" \
    "sem o handoff a proxima sessao comeca sem saber o que foi feito, o que travou nem qual e a proxima acao — o custo aparece so na sessao seguinte" \
    "atualize o SESSION_STATE.md ao fechar o grupo (hash, testes X/Y, bloqueios, proxima acao)" \
    "se o conteudo do handoff e util — so que o arquivo foi tocado"
else
  medida "SESSION_STATE nos checkpoints" 0 "sem checkpoint na janela" \
    "" "" "" \
    "nada: nao houve checkpoint nos ultimos $JANELA commits"
fi

# ------------------------------------------------ 4. escopo dos checkpoints
# "MUST NOT: tocar em arquivos fora do escopo do grupo atual". Um checkpoint
# com dezenas de arquivos nao e um grupo de 2-5 tasks. E SINAL, nao prova:
# renomear um diretorio move dezenas de arquivos legitimamente. Por isso o
# limiar e alto e a medida diz o que e.
if [ "$N_CHECK" -gt 0 ]; then
  CONTAGENS=$(mktemp 2>/dev/null || printf '/tmp/medir-aderencia-esc.%s' $$)
  : > "$CONTAGENS"
  while IFS="$(printf '\t')" read -r sha assunto; do
    case "$assunto" in
      checkpoint:*) ;;
      *) continue ;;
    esac
    git show --name-only --format='' "$sha" 2>/dev/null \
      | sed '/^$/d' | awk 'END {print NR}' >> "$CONTAGENS"
  done < "$LOG"
  ESC=$(sort -n "$CONTAGENS" | awk '
    { v[NR] = $1 }
    END {
      if (NR == 0) { print "0 0"; exit }
      m = (NR % 2) ? v[(NR + 1) / 2] : int((v[NR / 2] + v[NR / 2 + 1]) / 2)
      print m, v[NR]
    }')
  rm -f "$CONTAGENS"
  MEDIANA=$(echo "$ESC" | cut -d' ' -f1)
  MAXIMO=$(echo "$ESC" | cut -d' ' -f2)
  if [ "$MAXIMO" -gt 40 ]; then _a=1; else _a=0; fi
  medida "Escopo dos checkpoints" "$_a" "mediana $MEDIANA arquivo(s), maximo $MAXIMO" \
    "ha checkpoint alterando mais de 40 arquivos" \
    "grupo de 2-5 tasks nao costuma tocar tantos arquivos; o padrao provavel e varios grupos fechados num commit so, o que anula a fronteira de reset" \
    "confira o commit maior: se ele juntou grupos, divida os proximos; se foi renomeacao em massa, ignore este alerta" \
    "a diferenca entre escopo estourado e refatoracao legitima — isto e sinal, nao prova"
else
  medida "Escopo dos checkpoints" 0 "sem checkpoint na janela" \
    "" "" "" \
    "nada: nao houve checkpoint nos ultimos $JANELA commits"
fi

# ------------------------------------------- 5. sessoes que nao commitaram
# A medida que as quatro acima declaram nao ver. Todas leem git, e git so
# registra o que virou commit: duas horas de agente rodando em circulos e
# desistindo eram invisiveis aqui.
#
# A fonte e o trace do `registrar-sessao.sh`, gravado pelos hooks a cada
# chamada de ferramenta — independente de o agente commitar, cooperar ou
# chegar ao fim. Mesma epistemologia do git: subproduto, nao auto-relato.
#
# Sessao com trace e sem commit NAO E, por si, desobediencia: sessao de
# leitura, de investigacao ou interrompida pelo usuario e legitima. O alerta
# so acende quando isso e a MAIORIA, que e o padrao de agente que trabalha
# sem fechar grupo.
TRACE_DIR="${HARNESS_TRACE_DIR:-.harness/trace}"
if [ ! -d "$TRACE_DIR" ]; then
  medida "Sessoes sem commit" 0 "sem trace" "" "" "" \
    "tudo: o hook registrar-sessao.sh nao gravou nada ainda (harness recem-instalado, ou agente sem hooks registrados)"
else
  # Agrupamento por `sessao` quando o agente manda o id no payload; senao,
  # por DIA, que e a granularidade que o nome do arquivo ja garante. O
  # intervalo de tempo entre eventos seria mais preciso e exigiria aritmetica
  # de data em sh — precisao que nao paga o custo aqui.
  # A leitura tolera espaco depois dos dois-pontos e nao depende de offset
  # fixo. O hook escreve compacto, mas um leitor que quebra com um espaco
  # falha do pior jeito possivel: reportando "trace vazio" em vez de erro —
  # e quem le conclui que nao houve sessao, que e o oposto da verdade.
  # Sem intervalos `{n}` no regex: nem todo awk os suporta.
  SESSOES=$(cat "$TRACE_DIR"/*.jsonl 2>/dev/null | awk '
    function valor(linha, chave,   campo) {
      if (!match(linha, "\"" chave "\"[ \t]*:[ \t]*\"[^\"]*\"")) return ""
      campo = substr(linha, RSTART, RLENGTH)
      sub(/^"[^"]*"[ \t]*:[ \t]*"/, "", campo)
      sub(/"$/, "", campo)
      return campo
    }
    {
      sid = valor($0, "sessao")
      ts  = valor($0, "ts")
      dia = (ts ~ /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/) ? substr(ts, 1, 10) : ""
      chave = (sid != "") ? sid : dia
      if (chave == "") next
      visto[chave] = 1
      if (valor($0, "evento") == "edit") escreveu[chave] = 1
    }
    END {
      n = 0; e = 0
      for (k in visto) { n++; if (k in escreveu) e++ }
      print n, e
    }')
  N_SESSOES=$(echo "$SESSOES" | cut -d' ' -f1)
  N_ESCREVEU=$(echo "$SESSOES" | cut -d' ' -f2)

  if [ "${N_SESSOES:-0}" -eq 0 ]; then
    medida "Sessoes sem commit" 0 "trace vazio" "" "" "" \
      "tudo: ha diretorio de trace, mas nenhuma linha legivel nele"
  else
    # Sessao que EDITOU arquivo e nao produziu commit e a que interessa:
    # houve trabalho, e ele nao passou por fronteira nenhuma.
    COMMITS_HOJE=$(git log --since=midnight --oneline 2>/dev/null | awk 'END {print NR+0}')
    if [ "$N_ESCREVEU" -gt 0 ] && [ "$COMMITS_HOJE" -eq 0 ]; then _a=1; else _a=0; fi
    medida "Sessoes sem commit" "$_a" \
      "$N_SESSOES sessao(oes) no trace, $N_ESCREVEU com edicao, $COMMITS_HOJE commit(s) hoje" \
      "houve sessao que editou arquivo e nao produziu commit nenhum" \
      "trabalho fora de fronteira de grupo nao entra no historico: some no proximo reset de contexto e nao aparece em nenhuma das medidas acima" \
      "feche o grupo com a DoD e commite, ou registre em SESSION_STATE.md por que a sessao terminou sem checkpoint" \
      "o que o agente PENSOU, quanto custou, e se a edicao foi descartada depois — o trace ve chamada de ferramenta, nao intencao"
  fi
fi

# ------------------------------------------------- 6. comandos de risco medio
# O nivel `avisar` do `.harness/gate-rules.json` so existe se alguem LE o que
# ele produz. Sem esta medida, o gate graduado teria um terceiro nivel que
# grava um campo no trace e morre ali — pior que nao ter nivel nenhum, porque
# parece cobertura.
#
# Risco `medio` e o que o gate deixou passar de proposito: nao e destrutivo o
# bastante para bloquear, e nao deveria sumir em silencio. O caso que motivou
# o nivel: `git commit --no-verify` e o agente desligando o pre-commit do
# proprio harness.
if [ ! -d "$TRACE_DIR" ]; then
  medida "Comandos de risco medio" 0 "sem trace" "" "" "" \
    "tudo: sem trace nao ha como saber o que passou pelo gate"
else
  RISCOS=$(cat "$TRACE_DIR"/*.jsonl 2>/dev/null | awk '
    { if ($0 ~ /"risco"[ \t]*:[ \t]*"medio"/) m++; if ($0 ~ /"risco"[ \t]*:[ \t]*"alto"/) a++ }
    END { print m+0, a+0 }')
  N_MEDIO=$(echo "$RISCOS" | cut -d' ' -f1)
  N_ALTO=$(echo "$RISCOS" | cut -d' ' -f2)
  if [ "${N_MEDIO:-0}" -gt 0 ]; then _a=1; else _a=0; fi
  medida "Comandos de risco medio" "$_a" \
    "$N_MEDIO de risco medio, $N_ALTO tentativa(s) barrada(s) pelo gate" \
    "houve comando que o gate deixou passar e marcou como digno de nota" \
    "sao os comandos que nao merecem bloqueio e nao deveriam sumir: pular o pre-commit, abrir permissao 777, executar script baixado da rede. Nenhum quebra nada sozinho; juntos descrevem uma sessao que contornou o harness em vez de usa-lo" \
    "abra o trace e veja quais foram; se algum for rotina legitima neste repo, mova para 'permitir' em .harness/gate-rules.json com o motivo escrito" \
    "se o comando de risco medio de fato rodou — o trace registra a tentativa, e outro hook pode te-la barrado depois"
fi

# ---------------------------------------------------------------------- saida
if [ "$FORMATO" = json ]; then
  printf '{\n  "commits_analisados": %s,\n  "medidas": %s,\n  "alertas": %s,\n  "resultado": [' \
    "$N_COMMITS" "$TOTAL" "$ALERTAS"
  cat "$BUFFER"
  printf '\n  ]\n}\n'
else
  diz '\n%s de %s medida(s) em alerta.\n' "$ALERTAS" "$TOTAL"
  diz 'Diagnostico, nao gate: o exit e 0 mesmo com alerta.\n'
  diz 'Medidas 1-4 leem o historico do git; a 5 le o trace dos hooks.\n'
fi

exit 0
