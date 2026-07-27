#!/usr/bin/env bash
# score-harness.sh — Scorer semantico de prontidao de harness (L02-L12)
#
# Mede se um repositorio tem as CAPACIDADES ensinadas em
# https://walkinglabs.github.io/learn-harness-engineering/en/
# independente do NOME do arquivo que as implementa.
#
# Complementa (nao substitui) o tools/audit-harness.sh oficial do curso,
# que e literal por nome de arquivo. Aqui, SESSION_STATE.md conta como
# PROGRESS.md, TASKS.md/openspec conta como feature_list.json, e hooks +
# pre-commit + /dod contam como enforcement de verificacao.
#
# Uso:
#   ./eval/score-harness.sh [caminho/do/repo] [--json] [--quiet]
#
# Saida: score por subsistema, indice de prontidao (0-100), cobertura
# critica, e a lista separada de PASS (canonico), EQUIV (equivalente) e
# FAIL (lacuna real).
#
# Exit: 0 se toda capacidade CRITICA passa; 1 caso contrario.

set -o pipefail

REPO="${1:-.}"
[[ "$REPO" == --* ]] && REPO="."
REPO="${REPO%/}"
JSON=0
QUIET=0
for arg in "$@"; do
  [[ "$arg" == "--json" ]] && JSON=1
  [[ "$arg" == "--quiet" ]] && QUIET=1
done

if [[ ! -d "$REPO" ]]; then
  echo "erro: diretorio nao encontrado: $REPO" >&2
  exit 2
fi

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
if [[ ! -t 1 ]] || [[ $JSON -eq 1 ]]; then
  RED=''; GREEN=''; YELLOW=''; BLUE=''; CYAN=''; BOLD=''; RESET=''
fi

# ── Acumuladores ──────────────────────────────────────────────────────────────
PTS=0; MAX=0
CRIT_OK=0; CRIT_TOTAL=0
N_PASS=0; N_EQ=0; N_FAIL=0
ROWS=()          # linhas JSON
GAPS=()          # lacunas reais, com correcao
DIVERGENCES=()   # capacidades cobertas por artefato nao-canonico

# bash 3.2 (macOS) — sem arrays associativos: indice posicional 0..5
SUBS=("1-Instrucao" "2-Ambiente" "3-Estado" "4-Escopo" "5-Verificacao" "6-CicloDeVida")
SUB_PTS=(0 0 0 0 0 0)
SUB_MAX=(0 0 0 0 0 0)

json_escape() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/ /g'; }

# check <id> <indice-subsistema 0..5> <crit|rec> <descricao> <pass|eq|fail> <evidencia> <correcao>
check() {
  local id="$1" si="$2" sev="$3" desc="$4" res="$5" ev="${6:-}" fix="${7:-}"
  local w=1; [[ "$sev" == "crit" ]] && w=3
  MAX=$((MAX + w)); SUB_MAX[$si]=$(( ${SUB_MAX[$si]} + w ))
  [[ "$sev" == "crit" ]] && CRIT_TOTAL=$((CRIT_TOTAL + 1))

  local tag color
  case "$res" in
    pass) PTS=$((PTS + w)); SUB_PTS[$si]=$(( ${SUB_PTS[$si]} + w ))
          N_PASS=$((N_PASS + 1)); tag="PASS "; color="$GREEN"
          [[ "$sev" == "crit" ]] && CRIT_OK=$((CRIT_OK + 1)) ;;
    eq)   PTS=$((PTS + w)); SUB_PTS[$si]=$(( ${SUB_PTS[$si]} + w ))
          N_EQ=$((N_EQ + 1)); tag="EQUIV"; color="$BLUE"
          [[ "$sev" == "crit" ]] && CRIT_OK=$((CRIT_OK + 1))
          DIVERGENCES+=("$id  $desc  -> coberto por: $ev") ;;
    *)    N_FAIL=$((N_FAIL + 1)); tag="FAIL "; color="$RED"
          GAPS+=("[$( [[ $sev == crit ]] && echo CRITICO || echo recomendado )] $id $desc :: $fix") ;;
  esac

  if [[ $QUIET -eq 0 && $JSON -eq 0 ]]; then
    printf "  ${color}[%s]${RESET} %-3s %s%s\n" "$tag" "$id" "$desc" \
      "$( [[ -n "$ev" && "$res" != "fail" ]] && echo "  ${CYAN}(${ev})${RESET}" )"
  fi
  ROWS+=("{\"id\":\"$id\",\"subsystem\":\"${SUBS[$si]}\",\"severity\":\"$sev\",\"status\":\"$res\",\"description\":\"$(json_escape "$desc")\",\"evidence\":\"$(json_escape "$ev")\",\"fix\":\"$(json_escape "$fix")\"}")
}

header() { [[ $QUIET -eq 0 && $JSON -eq 0 ]] && echo -e "\n${CYAN}${BOLD}$1${RESET}"; return 0; }

# ── Primitivas de deteccao ────────────────────────────────────────────────────
has() { [[ -e "$REPO/$1" ]]; }

first_of() { for f in "$@"; do [[ -e "$REPO/$f" ]] && { echo "$f"; return; }; done; echo ""; }

glob_first() {
  for pat in "$@"; do
    for m in $REPO/$pat; do
      [[ -e "$m" ]] && { echo "${m#"$REPO"/}"; return; }
    done
  done
  echo ""
}

# grep em um conjunto de arquivos; ecoa o primeiro arquivo que casa
grep_in() {
  local pat="$1"; shift
  local f
  for f in "$@"; do
    [[ -f "$REPO/$f" ]] || continue
    grep -qiE "$pat" "$REPO/$f" 2>/dev/null && { echo "$f"; return; }
  done
  echo ""
}

# ── Corpus: todo arquivo que carrega protocolo de harness ────────────────────
CORPUS=()
while IFS= read -r f; do
  [[ -n "$f" ]] && CORPUS+=("${f#"$REPO"/}")
done < <(
  find "$REPO" -maxdepth 5 \
    -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' \
    -not -path '*/venv/*' -not -path '*/target/*' -not -path '*/dist/*' \
    \( -name 'AGENTS.md' -o -name 'CLAUDE.md' -o -name 'SESSION_STATE.md' \
       -o -name 'PROGRESS.md' -o -name 'claude-progress.md' -o -name 'TASKS.md' \
       -o -name 'DECISIONS.md' -o -name 'feature_list.json' \) 2>/dev/null \
  | grep -v '/skills/[^/]*/\(resources\|references\)/' | sort
)
while IFS= read -r f; do
  [[ -n "$f" ]] && CORPUS+=("${f#"$REPO"/}")
done < <(find "$REPO/.claude" "$REPO/openspec" "$REPO/.devin" -type f \
           \( -name '*.md' -o -name '*.json' -o -name '*.yaml' -o -name '*.yml' \) \
           2>/dev/null \
         | grep -v '/skills/[^/]*/\(resources\|references\)/' \
         | sort)
[[ ${#CORPUS[@]} -eq 0 ]] && CORPUS=(".__nada__")

grep_corpus() { grep_in "$1" "${CORPUS[@]}"; }

INSTR="$(first_of AGENTS.md CLAUDE.md)"
STATE="$(first_of SESSION_STATE.md PROGRESS.md claude-progress.md .harness/state.md)"
WORK="$(first_of feature_list.json features.json TASKS.md FEATURES.md)"
[[ -z "$WORK" ]] && WORK="$(glob_first 'openspec/changes/*/tasks.md')"
INIT="$(first_of init.sh scripts/init.sh scripts/setup.sh bootstrap.sh)"

LOCKFILES=(package-lock.json yarn.lock pnpm-lock.yaml bun.lockb requirements.txt
           poetry.lock uv.lock Pipfile.lock Cargo.lock go.sum Gemfile.lock mix.lock
           composer.lock packages.lock.json gradle.lockfile pubspec.lock)
PINFILES=(.tool-versions .nvmrc .node-version .python-version .ruby-version
          .java-version global.json go.mod rust-toolchain.toml .sdkmanrc)

VERIF_TOKENS='(pytest|npm (run )?test|yarn test|pnpm test|jest|vitest|go test|cargo test|dotnet test|mvn (verify|test)|gradlew? (test|check)|mix test|rspec|phpunit|ruff|eslint|mypy|tsc|flake8|black|prettier|dotnet format|spotless|golangci-lint|clippy)'

[[ $JSON -eq 0 && $QUIET -eq 0 ]] && {
  echo -e "${BOLD}Prontidao para Harness Engineering — scorer semantico${RESET}"
  echo -e "Repo: $REPO"
  echo -e "Ref:  https://walkinglabs.github.io/learn-harness-engineering/en/"
}

# ══ Subsistema 1: Instrucao (L02, L03, L04) ══════════════════════════════════
S=0; header "Subsistema 1 — Instrucao (L02/L03/L04)"

check I1 "$S" crit "Arquivo de instrucao na raiz" \
  "$( [[ -n "$INSTR" ]] && echo pass || echo fail )" "$INSTR" \
  "Criar AGENTS.md na raiz com: o que e o sistema, comando de verificacao, restricoes, onde vive o estado."

check I2 "$S" crit "Descreve o sistema nas primeiras 12 linhas" \
  "$( [[ -n "$INSTR" ]] && head -12 "$REPO/$INSTR" 2>/dev/null | grep -qiE '(projeto|project|sistema|system|servico|service|app|overview|vis[aã]o geral|stack)' && echo pass || echo fail )" \
  "$INSTR" "Abrir $INSTR com 2-3 linhas descrevendo a aplicacao e a stack com versoes exatas."

_lines=$( [[ -n "$INSTR" ]] && wc -l < "$REPO/$INSTR" 2>/dev/null || echo 9999 )
check I3 "$S" rec "Entrada e roteador, nao enciclopedia (<= 200 linhas)" \
  "$( [[ ${_lines:-9999} -le 200 ]] && echo pass || echo fail )" "$INSTR: ${_lines} linhas" \
  "$INSTR tem ${_lines} linhas — mover detalhe para docs/ ou AGENTS.md com escopo e deixar links."

_pd_canon="$(grep_in '\]\((docs|doc)/[^)]+\.md\)' "$INSTR")"
_pd_scoped=""
while IFS= read -r f; do
  rel="${f#"$REPO"/}"; [[ "$rel" != "AGENTS.md" && "$rel" != "CLAUDE.md" ]] && { _pd_scoped="$rel"; break; }
done < <(find "$REPO" -maxdepth 4 -not -path '*/.git/*' -not -path '*/node_modules/*' \
           \( -name 'AGENTS.md' -o -name 'CLAUDE.md' \) 2>/dev/null \
         | grep -v '/skills/[^/]*/\(resources\|references\)/' | sort)
_pd_skill="$(glob_first '.claude/skills/*/SKILL.md' '.claude/commands/*.md')"
check I4 "$S" rec "Divulgacao progressiva (contexto fatiado, carregado sob demanda)" \
  "$( [[ -n "$_pd_canon" ]] && echo pass || { [[ -n "$_pd_scoped$_pd_skill" ]] && echo eq || echo fail; } )" \
  "${_pd_canon:-${_pd_scoped:-$_pd_skill}}" \
  "Fatiar $INSTR: protocolo na raiz, escopo num AGENTS.md do diretorio de codigo, procedimento numa skill/comando."

check I5 "$S" rec "Restricoes duras explicitas (MUST NOT / nunca)" \
  "$( [[ -n "$(grep_in '(MUST NOT|MUST|nunca|never|proibido|forbidden|n[aã]o pode)' "$INSTR")" ]] && echo pass || echo fail )" \
  "$INSTR" "Adicionar secao de restricoes a $INSTR com regras MUST NOT derivadas de convencoes reais do repo."

check I6 "$S" rec "Aponta onde vive o estado e o plano de trabalho" \
  "$( [[ -n "$(grep_in '(PROGRESS\.md|SESSION_STATE|claude-progress|feature_list|TASKS\.md|openspec)' "$INSTR")" ]] && echo pass || echo fail )" \
  "$INSTR" "Citar em $INSTR os arquivos de estado e de plano, para o agente saber onde ler e onde escrever."

check I7 "$S" rec "Regra de atomicidade de commit" \
  "$( [[ -n "$(grep_corpus '(atomic|um commit por|one commit per|commit por grupo|mesmo commit|same commit|nunca commitar com)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(atomic|um commit por|one commit per|commit por grupo|mesmo commit|same commit|nunca commitar com)')" \
  "Declarar: um commit por unidade concluida; repo consistente depois de todo commit."

# ══ Subsistema 2: Ambiente / Inicializacao (L06) ═════════════════════════════
S=1; header "Subsistema 2 — Ambiente e inicializacao (L06)"

_mk_setup="$( [[ -f "$REPO/Makefile" ]] && grep -qE '^setup[[:space:]]*:' "$REPO/Makefile" 2>/dev/null && echo Makefile:setup )"
check E1 "$S" crit "Fase de inicializacao com um comando" \
  "$( [[ -n "$INIT" ]] && echo pass || { [[ -n "$_mk_setup" ]] && echo eq || echo fail; } )" \
  "${INIT:-$_mk_setup}" \
  "Criar init.sh executavel que instala deps, roda a baseline de testes e imprime o estado do repo."

_init_inst=""; _init_test=""
if [[ -n "$INIT" ]]; then
  grep -qiE '(install|restore|npm ci|pip install|uv sync|poetry install|bundle install|go mod|mvn|gradle|composer)' "$REPO/$INIT" 2>/dev/null && _init_inst=1
  grep -qiE "$VERIF_TOKENS" "$REPO/$INIT" 2>/dev/null && _init_test=1
fi
check E2 "$S" rec "Init instala E roda a verificacao (baseline antes de editar)" \
  "$( [[ -n "$_init_inst" && -n "$_init_test" ]] && echo pass || echo fail )" "$INIT" \
  "Fazer o init.sh rodar tambem a suite de verificacao, para o agente comecar de uma baseline conhecida."

_lock="$(first_of "${LOCKFILES[@]}")"
check E3 "$S" crit "Lockfile de dependencias versionado" \
  "$( [[ -n "$_lock" ]] && echo pass || echo fail )" "$_lock" \
  "Commitar o lockfile convencional do ecossistema para tornar a instalacao reproduzivel."

_pin="$(first_of "${PINFILES[@]}")"
_pin_eq="$(grep_in '(requires-python|"engines"|python_requires|<TargetFramework|languageVersion)' pyproject.toml setup.cfg package.json)"
check E4 "$S" rec "Versao de runtime fixada" \
  "$( [[ -n "$_pin" ]] && echo pass || { [[ -n "$_pin_eq" ]] && echo eq || echo fail; } )" "${_pin:-$_pin_eq}" \
  "Fixar a versao do runtime (.python-version / .nvmrc / .tool-versions / global.json)."

check E5 "$S" rec "Instrucao manda inicializar antes de tocar em codigo" \
  "$( [[ -n "$(grep_in '(init\.sh|make setup|npm ci|antes de qualquer a[cç][aã]o|before touching|session start)' "$INSTR")" ]] && echo pass || echo fail )" \
  "$INSTR" "Colocar em $INSTR o passo 1 obrigatorio: rodar o init antes de qualquer edicao."

# ══ Subsistema 3: Estado / Continuidade (L03, L05) ═══════════════════════════
S=2; header "Subsistema 3 — Estado e continuidade entre sessoes (L03/L05)"

check S1 "$S" crit "Arquivo de estado de sessao persistido no repo" \
  "$( [[ "$STATE" == "PROGRESS.md" || "$STATE" == "claude-progress.md" ]] && echo pass || { [[ -n "$STATE" ]] && echo eq || echo fail; } )" \
  "$STATE" "Criar SESSION_STATE.md (ou PROGRESS.md) versionado com estado atual, bloqueios e proxima acao."

check S2 "$S" rec "Estado registra commit verificado + status dos testes" \
  "$( [[ -n "$(grep_in '(commit)' "$STATE")" && -n "$(grep_in '(test|teste|passando|passing)' "$STATE")" ]] && echo pass || echo fail )" \
  "$STATE" "Incluir no estado os campos 'commit verificado' e 'testes X/Y' atualizados a cada checkpoint."

check S3 "$S" rec "Estado registra a proxima acao concreta" \
  "$( [[ -n "$(grep_in '(pr[oó]xima a[cç][aã]o|next step|next action|proxima acao)' "$STATE")" ]] && echo pass || echo fail )" \
  "$STATE" "Incluir campo 'Proxima acao' — a primeira coisa que a proxima sessao deve fazer."

check S4 "$S" rec "Estado registra bloqueios / pendencias fora de escopo" \
  "$( [[ -n "$(grep_in '(bloqueio|blocker|pend[eê]ncia|blocked|fora de escopo)' "$STATE")" ]] && echo pass || echo fail )" \
  "$STATE" "Incluir campo de bloqueios para o que foi descoberto e nao tratado (preserva WIP=1 sem perder o achado)."

check S5 "$S" rec "Rotina de entrada de sessao documentada (clock-in)" \
  "$( [[ -n "$(grep_corpus '(clock.?in|in[ií]cio de (nova )?(sess|funcionalidade)|antes de qualquer a[cç][aã]o|before touching|session start|leia .{0,20}(SESSION_STATE|PROGRESS))')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(clock.?in|in[ií]cio de (nova )?(sess|funcionalidade)|antes de qualquer a[cç][aã]o|before touching|leia .{0,20}(SESSION_STATE|PROGRESS))')" \
  "Documentar a sequencia de abertura: rodar init, ler o estado, retomar o trabalho em andamento antes de aceitar pedido novo."

check S6 "$S" rec "Rotina de saida de sessao documentada (clock-out)" \
  "$( [[ -n "$(grep_corpus '(clock.?out|ao concluir cada|fim de sess|session end|before closing|atualize .{0,20}(SESSION_STATE|PROGRESS))')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(clock.?out|ao concluir cada|fim de sess|atualize .{0,20}(SESSION_STATE|PROGRESS))')" \
  "Documentar o fechamento: atualizar estado, rodar verificacao, commitar checkpoint."

_dec="$(first_of DECISIONS.md docs/decisions docs/adr adr)"
[[ -z "$_dec" ]] && _dec="$(glob_first 'openspec/changes/*/proposal.md' 'openspec/changes/*/design.md')"
check S7 "$S" rec "Registro durave de decisoes (por que, nao so o que)" \
  "$( [[ "$_dec" == DECISIONS.md || "$_dec" == docs/* ]] && echo pass || { [[ -n "$_dec" ]] && echo eq || echo fail; } )" \
  "$_dec" "Criar DECISIONS.md (ou usar propostas do OpenSpec) para o racional das decisoes sobreviver ao fim do contexto."

# ══ Subsistema 4: Escopo / Lista de features (L07, L08) ══════════════════════
S=3; header "Subsistema 4 — Escopo e unidade de trabalho (L07/L08)"

check C1 "$S" crit "Fonte de trabalho legivel por maquina" \
  "$( [[ "$WORK" == feature_list.json || "$WORK" == features.json ]] && echo pass || { [[ -n "$WORK" ]] && echo eq || echo fail; } )" \
  "$WORK" "Criar feature_list.json (ou TASKS.md/openspec) enumerando as unidades de trabalho e o estado de cada uma."

check C2 "$S" rec "Regra WIP=1 (uma unidade ativa por vez)" \
  "$( [[ -n "$(grep_corpus '(WIP ?=? ?1|um grupo por vez|uma .{0,12}por vez|one .{0,20}at a time|only one active|single active)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(WIP ?=? ?1|um grupo por vez|one .{0,20}at a time|only one active)')" \
  "Declarar WIP=1: nada novo antes de a unidade atual estar verificada e commitada."

check C3 "$S" rec "Cada unidade tem comando de verificacao proprio" \
  "$( [[ -n "$(grep_in '(Verifica[cç][aã]o:|Verification:|"verification"|"cmd"|Verify:)' "$WORK")" ]] && echo pass || echo fail )" \
  "$WORK" "Terminar cada unidade em $WORK com uma linha 'Verificacao: <comando executavel>'."

check C4 "$S" rec "Regra de granularidade (unidade cabe em uma sessao)" \
  "$( [[ -n "$(grep_corpus '(2-5 tasks|uma sess[aã]o|one session|completable in one|checkpoint DENTRO|grupos coesos)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(2-5 tasks|uma sess[aã]o|one session|completable in one|checkpoint DENTRO|grupos coesos)')" \
  "Definir o tamanho da unidade: se nao cabe numa sessao, quebrar antes de comecar."

check C5 "$S" rec "Estado da unidade so muda por verificacao, nunca por autodeclaracao" \
  "$( [[ -n "$(grep_corpus '(verify-feature|nunca .{0,30}passing|sa[ií]da de comando|parece funcionar|not when the agent is confident|runtime evidence|evid[eê]ncia)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(verify-feature|sa[ií]da de comando|parece funcionar|runtime evidence|evid[eê]ncia)')" \
  "Declarar que so a saida do comando marca a unidade como feita — confianca do agente nao conta."

check C6 "$S" rec "Proibicao de trabalho fora da fonte de trabalho" \
  "$( [[ -n "$(grep_corpus '(nunca invente|fonte de trabalho|fora do escopo|outside .{0,15}scope|n[aã]o implemente direto|MUST NOT: implementar)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(nunca invente|fonte de trabalho|fora do escopo|outside .{0,15}scope|MUST NOT: implementar)')" \
  "Proibir implementar pedido que nao esteja na fonte de trabalho: primeiro planeja, depois executa."

# ══ Subsistema 5: Verificacao / DoD (L09, L10) ═══════════════════════════════
S=4; header "Subsistema 5 — Verificacao e Definition of Done (L09/L10)"

check V1 "$S" crit "Definition of Done com comandos reais" \
  "$( [[ -n "$(grep_in '(definition of done|concluído =|concluido =|DoD)' "$INSTR")" && -n "$(grep_in "$VERIF_TOKENS" "$INSTR")" ]] && echo pass || echo fail )" \
  "$INSTR" "Adicionar secao Definition of Done a $INSTR com os comandos reais do repo, encadeados, iguais aos do CI."

check V2 "$S" rec "Regra explicita de 'evidencia, nao confianca'" \
  "$( [[ -n "$(grep_corpus '(evid[eê]ncia|evidence|parece funcionar|looks fine|not .{0,20}confident)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(evid[eê]ncia|evidence|parece funcionar|looks fine)')" \
  "Escrever a regra: saida de comando e evidencia; 'parece funcionar' nao e."

# DoD replicada: mesmo token de verificacao aparece na instrucao e em >= 2 sensores
_dod_files=(); _dod_hits=0
for f in "$INIT" .claude/commands/dod.md .pre-commit-config.yaml Makefile \
         $(cd "$REPO" 2>/dev/null && ls .github/workflows/*.y*ml 2>/dev/null); do
  [[ -n "$f" && -f "$REPO/$f" ]] || continue
  if grep -qiE "$VERIF_TOKENS" "$REPO/$f" 2>/dev/null; then
    _dod_hits=$((_dod_hits + 1)); _dod_files+=("$f")
  fi
done
check V3 "$S" rec "DoD replicada em >= 2 sensores executaveis (nao so em prosa)" \
  "$( [[ $_dod_hits -ge 2 ]] && echo pass || echo fail )" "$(IFS=,; echo "${_dod_files[*]:-}")" \
  "Repetir os MESMOS comandos da DoD em init.sh, comando /dod, pre-commit e CI — texto sozinho o agente ignora."

_layers=0
[[ -n "$(grep_corpus '(lint|ruff|eslint|format|mypy|tsc|--verify-no-changes|clippy|golangci)')" ]] && _layers=$((_layers+1))
[[ -n "$(grep_corpus '(pytest|npm test|jest|vitest|go test|cargo test|dotnet test|mvn (verify|test)|mix test|rspec)')" ]] && _layers=$((_layers+1))
[[ -n "$(grep_corpus '(e2e|end.to.end|playwright|cypress|smoke|ready state|app .{0,10}start|integra[cç][aã]o)')" ]] && _layers=$((_layers+1))
check V4 "$S" rec "Verificacao em camadas (estatica -> testes -> runtime/e2e)" \
  "$( [[ $_layers -ge 3 ]] && echo pass || { [[ $_layers -eq 2 ]] && echo eq || echo fail; } )" \
  "$_layers/3 camadas" \
  "Cobrir as 3 camadas de L09/L10: estatica, comportamento em runtime, e confirmacao ponta a ponta."

_enf=()
[[ -n "$(grep_in '"hooks"' .claude/settings.json)" ]] && _enf+=(".claude/settings.json")
has .pre-commit-config.yaml && _enf+=(".pre-commit-config.yaml")
[[ -n "$(glob_first '.github/workflows/*.yml' '.github/workflows/*.yaml' '.gitlab-ci.yml' 'azure-pipelines.yml' 'Jenkinsfile')" ]] && _enf+=("CI")
has .devin/hooks.v1.json && _enf+=(".devin/hooks.v1.json")
[[ -n "$(glob_first '.husky/pre-commit' '.git/hooks/pre-commit')" ]] && _enf+=("git-hook")
check V5 "$S" crit "Enforcement executavel (a DoD roda sozinha, nao depende de boa vontade)" \
  "$( [[ ${#_enf[@]} -ge 1 ]] && echo pass || echo fail )" "$(IFS=,; echo "${_enf[*]:-}")" \
  "Instalar ao menos um sensor que bloqueia: hook de agent loop, pre-commit ou workflow de CI rodando a DoD."

_arch="$(first_of .harness/arch-rules.json scripts/check-arch.sh docs/architecture.md ARCHITECTURE.md)"
_arch_eq="$(first_of .claude/agents/code-reviewer.md .claude/agents)"
check V6 "$S" rec "Regras arquiteturais verificaveis / achado de review vira regra" \
  "$( [[ -n "$_arch" ]] && echo pass || { [[ -n "$_arch_eq" ]] && echo eq || echo fail; } )" \
  "${_arch:-$_arch_eq}" \
  "Criar .harness/arch-rules.json (ou script check-arch) e promover cada achado recorrente de review a regra automatica."

# ══ Subsistema 6: Ciclo de vida / estado limpo (L11, L12) ════════════════════
S=5; header "Subsistema 6 — Ciclo de vida da sessao (L11/L12)"

_clean="$(first_of templates/clean-state-checklist.md scripts/clean-state-check.sh)"
_clean_eq="$(grep_corpus '(fronteira limpa|estado limpo|clean.?state|nunca commitar com verifica|sess[aã]o (nao|não) (esta|está) completa)')"
check X1 "$S" rec "Protocolo de estado limpo no fim da sessao" \
  "$( [[ -n "$_clean" ]] && echo pass || { [[ -n "$_clean_eq" ]] && echo eq || echo fail; } )" \
  "${_clean:-$_clean_eq}" \
  "Definir o checklist de saida: build ok, testes ok, plano atualizado, sem artefato de debug, caminho de restart valido."

check X2 "$S" rec "Regra de remocao de artefato de debug" \
  "$( [[ -n "$(grep_corpus '(debug artifact|artefato de debug|console\.log|remover .{0,15}debug|print de debug|c[oó]digo morto)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(debug artifact|artefato de debug|console\.log|remover .{0,15}debug)')" \
  "Exigir a limpeza de logs e codigo temporario antes do commit de checkpoint."

_obs="$(first_of scripts/session-trace.sh .harness/traces)"
_obs_eq="$( [[ -n "$STATE" && -n "$(grep_corpus '(atualize .{0,20}(SESSION_STATE|PROGRESS)|ao concluir cada)')" ]] && echo "$STATE atualizado por checkpoint" )"
check X3 "$S" rec "Observabilidade: sinal de execucao gravado a cada sessao" \
  "$( [[ -n "$_obs" ]] && echo pass || { [[ -n "$_obs_eq" ]] && echo eq || echo fail; } )" \
  "${_obs:-$_obs_eq}" \
  "Gravar sinal por sessao (JSONL em .harness/traces/ ou historico no arquivo de estado) para o problema ficar visivel."

_qual="$(first_of docs/quality-document.md templates/evaluator-rubric.md)"
_qual_eq="$(first_of .claude/agents/code-reviewer.md .claude/commands/dod.md)"
check X4 "$S" rec "Rubrica de qualidade / revisao estruturada por sessao" \
  "$( [[ -n "$_qual" ]] && echo pass || { [[ -n "$_qual_eq" ]] && echo eq || echo fail; } )" \
  "${_qual:-$_qual_eq}" \
  "Adicionar rubrica de avaliacao (A/B/C/D por dimensao) ou agente revisor com criterio fixo."

check X5 "$S" rec "Regra de parada limpa (nao acelerar o fim, entregar handoff)" \
  "$( [[ -n "$(grep_corpus '(PARE|contexto pode ser reiniciado|do not rush|running low|n[aã]o prossiga automaticamente|stop.{0,20}commit)')" ]] && echo pass || echo fail )" \
  "$(grep_corpus '(PARE|contexto pode ser reiniciado|do not rush|n[aã]o prossiga automaticamente)')" \
  "Instruir: ao fechar a unidade, parar e avisar que o contexto pode ser reiniciado — nao emendar a proxima."

# ══ Resultado ════════════════════════════════════════════════════════════════
SCORE=0
[[ $MAX -gt 0 ]] && SCORE=$(( PTS * 100 / MAX ))
CRIT_PCT=0
[[ $CRIT_TOTAL -gt 0 ]] && CRIT_PCT=$(( CRIT_OK * 100 / CRIT_TOTAL ))

NIVEL="0 — sem harness"
[[ $SCORE -ge 25 ]] && NIVEL="1 — instrucao apenas"
[[ $SCORE -ge 45 && $CRIT_OK -eq $CRIT_TOTAL ]] && NIVEL="2 — sessao continua"
[[ $SCORE -ge 65 && $CRIT_OK -eq $CRIT_TOTAL ]] && NIVEL="3 — verificacao aplicada"
[[ $SCORE -ge 85 && $CRIT_OK -eq $CRIT_TOTAL ]] && NIVEL="4 — loop autonomo"

if [[ $JSON -eq 1 ]]; then
  {
    printf '{\n  "repo": "%s",\n' "$(json_escape "$REPO")"
    printf '  "score": %d,\n  "points": %d,\n  "max": %d,\n' "$SCORE" "$PTS" "$MAX"
    printf '  "critical_ok": %d,\n  "critical_total": %d,\n  "critical_pct": %d,\n' "$CRIT_OK" "$CRIT_TOTAL" "$CRIT_PCT"
    printf '  "level": "%s",\n' "$(json_escape "$NIVEL")"
    printf '  "counts": {"pass": %d, "equiv": %d, "fail": %d},\n' "$N_PASS" "$N_EQ" "$N_FAIL"
    printf '  "subsystems": {\n'
    for si in 0 1 2 3 4 5; do
      _p=0
      [[ ${SUB_MAX[$si]} -gt 0 ]] && _p=$(( ${SUB_PTS[$si]} * 100 / ${SUB_MAX[$si]} ))
      printf '    "%s": {"points": %d, "max": %d, "pct": %d}%s\n' \
        "${SUBS[$si]}" "${SUB_PTS[$si]}" "${SUB_MAX[$si]}" "$_p" \
        "$( [[ $si -lt 5 ]] && echo , )"
    done
    printf '  },\n  "checks": [\n'
    for i in "${!ROWS[@]}"; do
      printf '    %s%s\n' "${ROWS[$i]}" "$( [[ $i -lt $(( ${#ROWS[@]} - 1 )) ]] && echo , )"
    done
    printf '  ]\n}\n'
  }
else
  echo
  echo -e "${BOLD}────────────────────────────────────────────────────────${RESET}"
  echo -e "${BOLD}Indice de Prontidao: ${SCORE}/100${RESET}   (${PTS}/${MAX} pontos ponderados)"
  echo -e "  Capacidades criticas: ${CRIT_OK}/${CRIT_TOTAL} (${CRIT_PCT}%)"
  echo -e "  Nativo: ${N_PASS}   Equivalente: ${N_EQ}   Lacuna: ${N_FAIL}"
  echo -e "  Nivel de maturidade: ${BOLD}${NIVEL}${RESET}"
  echo -e "${BOLD}────────────────────────────────────────────────────────${RESET}"
  for si in 0 1 2 3 4 5; do
    _p=0; [[ ${SUB_MAX[$si]} -gt 0 ]] && _p=$(( ${SUB_PTS[$si]} * 100 / ${SUB_MAX[$si]} ))
    _bar=""; _n=$(( _p / 10 ))
    for ((i=0;i<10;i++)); do [[ $i -lt $_n ]] && _bar="${_bar}#" || _bar="${_bar}."; done
    printf "  %-16s [%s] %3d%%  (%d/%d)\n" "${SUBS[$si]}" "$_bar" "$_p" "${SUB_PTS[$si]}" "${SUB_MAX[$si]}"
  done

  if [[ ${#DIVERGENCES[@]} -gt 0 ]]; then
    echo -e "\n${BLUE}${BOLD}Capacidade coberta por artefato nao-canonico (${#DIVERGENCES[@]})${RESET}"
    echo -e "${BLUE}O curso espera outro nome; a capacidade existe. Custo: ferramenta"
    echo -e "literal do curso marca como ausente.${RESET}"
    for d in "${DIVERGENCES[@]}"; do echo "  - $d"; done
  fi

  if [[ ${#GAPS[@]} -gt 0 ]]; then
    echo -e "\n${YELLOW}${BOLD}Lacunas reais (${#GAPS[@]})${RESET}"
    for g in "${GAPS[@]}"; do echo "  - $g"; done
  fi

  echo
  if [[ $CRIT_OK -eq $CRIT_TOTAL ]]; then
    echo -e "${GREEN}${BOLD}Todas as capacidades criticas presentes.${RESET}"
  else
    echo -e "${RED}${BOLD}Faltam capacidades criticas — nao rode sessoes longas de agente aqui.${RESET}"
  fi
fi

[[ $CRIT_OK -eq $CRIT_TOTAL ]] && exit 0 || exit 1
