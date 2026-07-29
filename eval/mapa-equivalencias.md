# Mapa de equivalências — curso ↔ `harness-creator`

O curso e a skill implementam as mesmas capacidades com nomes diferentes.
Esta tabela é o contrato do scorer: define o que conta como `EQUIV` e por quê.
É também a lista de decisões a revisar se o objetivo for interoperar com as
ferramentas do walkinglabs.

## De/para

| Capacidade (lecture) | Canônico no curso | Gerado pela skill | Status |
|---|---|---|---|
| Manual de operação | `AGENTS.md` / `CLAUDE.md` | `AGENTS.md` (raiz) | idêntico |
| Divulgação progressiva (L04) | links para `docs/*.md` | `AGENTS.md` com escopo no dir de código + skill `executar-grupo` + `/dod` | EQUIV |
| Inicialização (L06) | `init.sh` | `init.sh` | idêntico |
| Estado de sessão (L05) | `PROGRESS.md` / `claude-progress.md` | `SESSION_STATE.md` | EQUIV |
| Registro de decisões (L03) | `DECISIONS.md`, `docs/decisions/` | propostas do OpenSpec (`openspec/changes/*/proposal.md`) — ausente se o repo não usa OpenSpec | EQUIV / lacuna |
| Fonte de trabalho (L08) | `feature_list.json` | `TASKS.md` em grupos, ou `openspec/changes/*/tasks.md` | EQUIV |
| Unidade de escopo (L07) | feature com `state` | **grupo** de 2–5 tasks com linha `Verificação:` | EQUIV |
| Transição de estado por verificação (L08) | `scripts/verify-feature.sh` + `make verify-feature` | linha `Verificação:` do grupo + regra "saída de comando é evidência" | EQUIV mais fraco |
| Comando único de verificação | `make check` | DoD encadeada em `AGENTS.md` + `/dod` + `init.sh` | EQUIV |
| Enforcement | CI | hooks de agent loop + pre-commit + workflow de CI + `.devin/hooks.v1.json` | mais forte |
| Regras arquiteturais (L10) | `.harness/arch-rules.json` + `scripts/check-arch.sh` | `.harness/arch-rules.json` + `.claude/check-arch.sh` na DoD | idêntico |
| Observabilidade (L11) | `scripts/session-trace.sh`, `.harness/traces/*.jsonl` | histórico em `SESSION_STATE.md` por checkpoint | EQUIV mais fraco |
| Rubrica de avaliação (L11) | `templates/evaluator-rubric.md` | `/dod` | EQUIV mais fraco |
| Estado limpo (L12) | `templates/clean-state-checklist.md` + `make clean-check` | regra "fronteira limpa" + "nunca commitar com verificação falhando" | EQUIV |
| Parada limpa (L05/L12) | aviso de context anxiety | "PARE. Contexto pode ser reiniciado." | idêntico em efeito |

### Onde "EQUIV mais fraco" importa

Quatro equivalências trocam **artefato executável por texto ou por
julgamento de outro agente**:

- `verify-feature.sh` → linha `Verificação:` — o curso torna impossível marcar
  passing sem rodar o comando; a skill pede que o agente rode e não minta.
- `arch-rules.json` → **idêntico** desde o Grupo 31: a skill passou a gerar o
  registro e o runner, ligados à cadeia da DoD. V6 saiu de `fail` para `pass` —
  cobertura melhor do que a de antes do Grupo 28, quando o subagente revisor
  contava só como `eq`: revisor julga caso a caso e esquece, registro acumula.
- `session-trace.jsonl` → `SESSION_STATE.md` — sinal estruturado por evento vs.
  resumo em prosa por checkpoint.
- `evaluator-rubric.md` → `/dod` — critério fixo vs. os comandos da DoD, que
  não avaliam qualidade, só passam ou falham.

Nos quatro, o scorer dá o ponto (a capacidade existe) mas registra a
divergência. Se o objetivo for atingir o nível 4 do curso de verdade, é
nessa lista que a skill precisa evoluir — e não em mais arquivos de
instrução.

## Impacto de não usar o vocabulário canônico

1. `tools/audit-harness.sh` do curso reprova o repo (crítico: `PROGRESS.md`
   ausente), mesmo com a capacidade presente.
2. Templates multilíngues e scripts do `harness-engineering-template` não
   encaixam sem adaptação.
3. Agentes de terceiros treinados na convenção do curso procuram
   `feature_list.json` e não acham.

## Duas saídas possíveis

**Adaptar** — gerar `PROGRESS.md` e `feature_list.json` como
arquivos-ponte, ou gerar os alvos `make check` / `make vcr` apontando para
a DoD já existente. Custo baixo, ganha interoperabilidade, mas duplica
fonte de verdade — o que o próprio protocolo da skill proíbe.

**Documentar** — manter o vocabulário e declarar o de/para no `AGENTS.md`
gerado, para que qualquer agente entenda que `SESSION_STATE.md` É o
`PROGRESS.md`. Custo quase zero, resolve o problema para agentes de IA
(que leem), não resolve para scripts (que não leem).

Recomendação: documentar, e reservar a adaptação para os repos onde alguém
de fato for rodar as ferramentas do curso.
