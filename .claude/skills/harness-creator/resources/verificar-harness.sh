#!/bin/sh
# verificar-harness.sh — checagens deterministicas do harness instalado.
#
# A FASE 5 da skill tem 19 itens e a maioria e mecanica: JSON que parseia,
# script sem CRLF, gate devolvendo o codigo certo. Refazer isso a mao a cada
# geracao e lento e varia entre execucoes; aqui o resultado e o mesmo sempre.
#
# Fica no repositorio depois da geracao de proposito: quem recebeu o harness
# pode reconferir se ele continua integro sem gastar uma execucao da skill.
#
# POSIX sh, sem dependencia de Python nem jq: precisa rodar em repo Go, .NET
# ou Java, onde exigir Python transformaria a verificacao em erro de setup.
#
# Uso:
#   sh .claude/verificar-harness.sh            # tabela legivel
#   sh .claude/verificar-harness.sh --json     # para consumo por script
#   sh .claude/verificar-harness.sh --raiz DIR # verifica outro diretorio
#
# Saida: 0 = tudo passou, 1 = alguma checagem falhou, 2 = erro de uso.
set -u

FORMATO=texto
RAIZ=.
while [ $# -gt 0 ]; do
  case "$1" in
    --json) FORMATO=json ;;
    --raiz) shift; RAIZ="${1:-.}" ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
  shift
done

cd "$RAIZ" 2>/dev/null || { echo "diretorio inacessivel: $RAIZ" >&2; exit 2; }

TOTAL=0
FALHAS=0
SEP=""
BUFFER=""
if [ "$FORMATO" = json ]; then
  BUFFER=$(mktemp 2>/dev/null || printf '/tmp/verificar-harness.%s' $$)
  : > "$BUFFER"
  trap 'rm -f "$BUFFER"' EXIT INT TERM
fi

# Python quando existe (parser de verdade); senao, checagens mais fracas que
# se anunciam como tais. Mentir sobre a forca da checagem e pior que nao ter.
PY=""
for _cand in python3 python; do
  if command -v "$_cand" >/dev/null 2>&1 && "$_cand" -c 'import sys' 2>/dev/null; then
    PY="$_cand"
    break
  fi
done

escapar() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' '
}

resultado() {
  _nome="$1"; _ok="$2"; _ev="$3"
  TOTAL=$((TOTAL + 1))
  [ "$_ok" -eq 0 ] || FALHAS=$((FALHAS + 1))
  if [ "$FORMATO" = json ]; then
    if [ "$_ok" -eq 0 ]; then _b=true; else _b=false; fi
    printf '%s\n    {"check": "%s", "passed": %s, "evidence": "%s"}' \
      "$SEP" "$(escapar "$_nome")" "$_b" "$(escapar "$_ev")" >> "$BUFFER"
    SEP=","
  else
    if [ "$_ok" -eq 0 ]; then _st="OK   "; else _st="FALHA"; fi
    printf '%s  %s' "$_st" "$_nome"
    [ -n "$_ev" ] && printf ' — %s' "$_ev"
    printf '\n'
  fi
}

json_parseia() {
  if [ -n "$PY" ]; then
    "$PY" -c 'import json,sys; json.load(open(sys.argv[1]))' "$1" 2>/dev/null
    return $?
  fi
  # Sem Python: balanceamento de chaves fora de string. Pega o truncamento e a
  # virgula sobrando que quebram na pratica; nao e um parser.
  awk '
    { linha = $0
      for (i = 1; i <= length(linha); i++) {
        c = substr(linha, i, 1)
        if (esc) { esc = 0; continue }
        if (c == "\\") { esc = 1; continue }
        if (c == "\"") { str = !str; continue }
        if (str) continue
        if (c == "{" || c == "[") n++
        if (c == "}" || c == "]") n--
        if (n < 0) exit 1
      }
    }
    END { exit (n == 0 ? 0 : 1) }' "$1"
}

# ---------------------------------------------------------------- JSON valido
JSONS=".claude/settings.json .devin/hooks.v1.json .cursor/hooks.json .mcp.json .claude/harness.json .harness/arch-rules.json .harness/gate-rules.json"
_ruins=""
_vistos=0
for f in $JSONS; do
  [ -f "$f" ] || continue
  _vistos=$((_vistos + 1))
  json_parseia "$f" || _ruins="$_ruins $f"
done
if [ -n "$PY" ]; then _como="parser"; else _como="balanceamento (sem Python)"; fi
if [ -n "$_ruins" ]; then
  resultado "JSON dos configs parseia" 1 "invalido:$_ruins"
else
  resultado "JSON dos configs parseia" 0 "$_vistos arquivo(s), via $_como"
fi

# ------------------------------------------------- scripts: LF e executaveis
SCRIPTS="init.sh"
[ -f .claude/check-arch.sh ] && SCRIPTS="$SCRIPTS .claude/check-arch.sh"
# O medidor de aderencia entra aqui e em lugar nenhum mais: o verificador
# garante que ele esta integro (LF, bit de execucao) e NUNCA o executa. Sao
# perguntas diferentes — integridade agora contra comportamento ao longo do
# tempo — e um repo recem-gerado, sem commit nenhum, reprovaria numa medida
# de aderencia que ainda nao teve chance de existir.
[ -f .claude/medir-aderencia.sh ] && SCRIPTS="$SCRIPTS .claude/medir-aderencia.sh"
for f in .claude/hooks/*.sh; do
  [ -f "$f" ] && SCRIPTS="$SCRIPTS $f"
done
_crlf=""
_naoexec=""
for f in $SCRIPTS; do
  [ -f "$f" ] || continue
  # CRLF mata o shebang: o script morre com exit 1, que em PreToolUse significa
  # "erro nao-bloqueante" — o comando destrutivo executa e o gate falha ABERTO.
  if od -c "$f" 2>/dev/null | grep -q '\\r  *\\n'; then _crlf="$_crlf $f"; fi
  [ -x "$f" ] || _naoexec="$_naoexec $f"
done
if [ -n "$_crlf" ]; then
  resultado "Scripts sem CRLF" 1 "CRLF em:$_crlf (gate falha ABERTO)"
else
  resultado "Scripts sem CRLF" 0 "todos com LF"
fi
if [ -n "$_naoexec" ]; then
  resultado "Scripts executaveis" 1 "sem bit de execucao:$_naoexec"
else
  resultado "Scripts executaveis" 0 "todos executaveis"
fi

# --------------------------------------------------------- gate nos 2 caminhos
GATE=.claude/hooks/gate-destructive.sh
if [ -f "$GATE" ]; then
  # O comando de risco e montado em partes: escrito por extenso, o gate do
  # repositorio onde isto roda bloquearia a propria verificacao.
  _rm=rm
  _flag=-rf
  # O alvo NAO pode ser sob /tmp: desde o gate graduado, caminho temporario e
  # excecao declarada em `.harness/gate-rules.json`, e o gate o libera com
  # razao. A sonda antiga passou a testar o caminho permitido e reportava
  # "gate nao bloqueia" numa geracao correta.
  _payload=$(printf '{"tool_name":"Bash","tool_input":{"command":"%s %s /alvo-inexistente"}}' "$_rm" "$_flag")
  # Executado pelo proprio shebang, nunca com `sh $GATE`: o gate e bash e usa
  # array. Forcar sh nele o faz morrer com erro de sintaxe, e um gate que
  # morre devolve exit != 2 — a verificacao acusaria falha onde nao ha.
  printf '%s' "$_payload" | "$GATE" >/dev/null 2>&1
  _cod=$?
  if [ "$_cod" -eq 2 ]; then
    resultado "Gate bloqueia comando destrutivo" 0 "exit 2"
  else
    resultado "Gate bloqueia comando destrutivo" 1 "exit $_cod (esperado 2; exit 1 = falha ABERTO)"
  fi

  printf '{"tool_name":"Bash","tool_input":{"command":"git status"}}' | "$GATE" >/dev/null 2>&1
  _cod=$?
  if [ "$_cod" -eq 0 ]; then
    resultado "Gate libera comando seguro" 0 "exit 0"
  else
    resultado "Gate libera comando seguro" 1 "exit $_cod (gate bloqueia tudo)"
  fi
else
  resultado "Gate bloqueia comando destrutivo" 1 "$GATE ausente"
  resultado "Gate libera comando seguro" 1 "$GATE ausente"
fi

# --------------------------------------------- settings.json com wrapper hooks
if [ -f .claude/settings.json ]; then
  # Sem o wrapper no nivel raiz nenhum scanner enxerga os hooks registrados.
  if grep -q '"hooks"' .claude/settings.json; then
    resultado "settings.json tem wrapper hooks" 0 "chave presente"
  else
    resultado "settings.json tem wrapper hooks" 1 "eventos no nivel raiz, sem wrapper"
  fi
else
  resultado "settings.json tem wrapper hooks" 1 ".claude/settings.json ausente"
fi

# -------------------------------- hooks registrados apontam para script real
_orfaos=""
_refs=0
for cfg in .claude/settings.json .devin/hooks.v1.json .cursor/hooks.json; do
  [ -f "$cfg" ] || continue
  for ref in $(grep -o '\.claude/hooks/[A-Za-z0-9_-]*\.sh' "$cfg" | sort -u); do
    _refs=$((_refs + 1))
    [ -x "$ref" ] || _orfaos="$_orfaos $cfg->$ref"
  done
done
# Zero referencia nao e sucesso: e enforcement que nenhum agente vai executar.
# Sem esta guarda a checagem passa em repo onde nada foi registrado.
if [ "$_refs" -eq 0 ]; then
  resultado "Hooks registrados existem e executam" 1 "nenhum hook registrado nos 3 agentes"
elif [ -n "$_orfaos" ]; then
  # No Claude Code e no Devin o hook morre em silencio; no Cursor o failClosed
  # transforma a referencia quebrada em bloqueio de todo comando.
  resultado "Hooks registrados existem e executam" 1 "referencia quebrada:$_orfaos"
else
  resultado "Hooks registrados existem e executam" 0 "todas as referencias resolvem"
fi

# ------------------------------------------------------- ponte CLAUDE.md
# Skill instalada no repositorio e conteudo DELA, nao harness gerado: os
# templates em `resources/` tem marcador por construcao e o `AGENTS.md`
# interno documenta a skill, sem ponte porque nao precisa de uma. Varrer isso
# fazia uma geracao correta reprovar em 4 checagens, e o usuario lia
# "defeito da geracao" e ia cacar um problema que nao existe. Instalar a
# skill no repo e caminho legitimo — e como um time a compartilha via git.
_sem_ponte=""
_agents=0
for agents in $(find . -name AGENTS.md -not -path './.git/*' -not -path '*/node_modules/*' \
                  -not -path './.claude/skills/*' 2>/dev/null); do
  _agents=$((_agents + 1))
  # Expansao de parametro em vez de `dirname`: menos um binario exigido.
  dir="${agents%/*}"
  [ "$dir" = "$agents" ] && dir="."
  irmao="$dir/CLAUDE.md"
  if [ ! -f "$irmao" ]; then
    _sem_ponte="$_sem_ponte $dir(sem CLAUDE.md)"
  elif ! grep -q '^@AGENTS\.md[[:space:]]*$' "$irmao"; then
    # Dentro de crase ou de bloco de codigo o import nao e parseado: vira texto.
    _sem_ponte="$_sem_ponte $irmao(import nao solto)"
  fi
done
# E a unica checagem que separa "harness gravado" de "harness carregado": sem
# ela nada falha, o agente apenas ignora o protocolo. Por isso zero AGENTS.md
# tambem reprova — nao ha nada para carregar.
if [ "$_agents" -eq 0 ]; then
  resultado "Ponte CLAUDE.md alcanca cada AGENTS.md" 1 "nenhum AGENTS.md no repositorio"
elif [ -n "$_sem_ponte" ]; then
  resultado "Ponte CLAUDE.md alcanca cada AGENTS.md" 1 "$_sem_ponte"
else
  resultado "Ponte CLAUDE.md alcanca cada AGENTS.md" 0 "todo AGENTS.md tem irmao importando"
fi

# ------------------------------------------------- manifesto confere com disco
MANIFESTO=.claude/harness.json
if [ -f "$MANIFESTO" ]; then
  _fantasmas=""
  for caminho in $(grep -o '"[^"]*"' "$MANIFESTO" | tr -d '"' | grep -E '^\.?[A-Za-z0-9_./-]+\.(sh|md|json|yaml|yml)$'); do
    [ -e "$caminho" ] || _fantasmas="$_fantasmas $caminho"
  done
  if [ -n "$_fantasmas" ]; then
    resultado "Manifesto so lista arquivo existente" 1 "nao existe(m):$_fantasmas"
  else
    resultado "Manifesto so lista arquivo existente" 0 "todos os caminhos resolvem"
  fi
else
  resultado "Manifesto so lista arquivo existente" 1 "$MANIFESTO ausente"
fi

# --------------------------------------------------------- .env no .gitignore
if [ -f .gitignore ] && grep -q '^\.env' .gitignore; then
  resultado ".gitignore cobre .env" 0 "coberto"
elif [ -f .gitignore ]; then
  resultado ".gitignore cobre .env" 1 "sem entrada para .env"
else
  resultado ".gitignore cobre .env" 1 ".gitignore ausente"
fi

# ------------------------------------------- credencial literal em .mcp.json
if [ -f .mcp.json ]; then
  # Valor de chave sensivel que nao seja interpolacao ${...} e segredo em claro.
  _vaz=$(grep -iE '"(token|key|secret|password|authorization)"[[:space:]]*:' .mcp.json \
         | grep -v '\${' | head -3)
  if [ -n "$_vaz" ]; then
    resultado "Sem credencial literal em .mcp.json" 1 "valor em claro encontrado"
  else
    resultado "Sem credencial literal em .mcp.json" 0 "so interpolacao"
  fi
fi

# ------------------------------------------------- marcadores nao preenchidos
# Os nomes sao montados com os delimitadores em runtime: escritos por extenso,
# a propria FASE 2 os substituiria dentro deste arquivo na hora de gerar.
MARCADORES="branch-base caminho como-propor-mudanca-de-plano
data-iso dod-command ecossistema ferramentas-do-harness dod-steps file_glob
formatter_bin formatter_command politica-de-entrega pre-commit-hooks
prefixo-de-branch runner setup-steps sln
versao-da-skill"
ABRE='<'
FECHA='>'
_sobrou=""
for m in $MARCADORES; do
  alvo="${ABRE}${m}${FECHA}"
  achados=$(grep -rl -- "$alvo" . \
            --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ \
            2>/dev/null | grep -v 'verificar-harness.sh' \
            | grep -v '^\./\.claude/skills/[^/]*/' | head -2)
  [ -n "$achados" ] && _sobrou="$_sobrou $m"
done
if [ -n "$_sobrou" ]; then
  resultado "Nenhum marcador preenchivel sobrou" 1 "sobrou:$_sobrou"
else
  resultado "Nenhum marcador preenchivel sobrou" 0 "nenhum"
fi

# ---------------------------------------------------------------------- saida
if [ "$FORMATO" = json ]; then
  printf '{\n  "total": %s,\n  "falhas": %s,\n  "checks": [' "$TOTAL" "$FALHAS"
  cat "$BUFFER"
  printf '\n  ]\n}\n'
else
  printf '\n%s de %s checagens passaram.\n' "$((TOTAL - FALHAS))" "$TOTAL"
  if [ "$FALHAS" -gt 0 ]; then
    printf 'Falha aqui e defeito da geracao, nao pendencia do usuario.\n'
  fi
fi

[ "$FALHAS" -eq 0 ] || exit 1
exit 0
