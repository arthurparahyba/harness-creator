# Avaliação da skill `harness-creator`

Como medir se a skill realmente deixa um repositório pronto para colher os
benefícios de [Learn Harness Engineering](https://walkinglabs.github.io/learn-harness-engineering/en/)
(walkinglabs) — e não apenas se ela gera arquivos.

O curso promete seis benefícios concretos: menos retrabalho, escopo
controlado, conclusão verificável, progresso contínuo entre sessões,
execução observável e handoff seguro. Nenhum deles é um arquivo. Todos são
comportamento do agente. Por isso a avaliação tem três níveis, e cada um
responde uma pergunta diferente.

| Nível | Pergunta | Instrumento | Custo |
|---|---|---|---|
| **A — Conformidade literal** | O repo passa na régua oficial do curso? | `tools/audit-harness.sh` do curso | segundos |
| **B — Prontidão semântica** | As *capacidades* dos 5 subsistemas existem, sob qualquer nome? | [`score-harness.sh`](score-harness.sh) | segundos |
| **C — Eficácia comportamental** | O agente de fato se comporta melhor? | [`protocolo-experimento.md`](protocolo-experimento.md) | horas |

Os três são necessários. A só mede vocabulário; B mede capacidade; C mede
benefício. Uma skill pode ir bem em B e mal em C — é exatamente o risco de
gerar harness que ninguém obedece.

---

## Nível A — Conformidade literal (régua do curso)

```bash
curl -fsSL https://raw.githubusercontent.com/walkinglabs/learn-harness-engineering/main/tools/audit-harness.sh \
  | bash -s -- /caminho/do/repo
```

70 checks, casados **por nome de arquivo** (`PROGRESS.md`, `feature_list.json`,
alvos `make check` / `make vcr` / `make e2e`, `.harness/arch-rules.json`,
`templates/clean-state-checklist.md`).

**Para que serve:** é um juiz externo, escrito por terceiros, que a skill não
controla. Mede interoperabilidade: quanto do ecossistema de ferramentas do
curso funciona out-of-the-box no repo gerado.

**O que ele *não* mede:** capacidade. `SESSION_STATE.md` cumpre o papel de
`PROGRESS.md` e mesmo assim reprova.

## Nível B — Prontidão semântica (este scorer)

```bash
./eval/score-harness.sh /caminho/do/repo          # relatório legível
./eval/score-harness.sh /caminho/do/repo --json   # para pipeline / diff
```

36 capacidades derivadas das lectures L02–L12, agrupadas nos 6 subsistemas.
Cada capacidade aceita **múltiplas implementações**. Três status:

- `PASS` — implementada com o artefato canônico do curso;
- `EQUIV` — implementada por artefato equivalente (conta ponto, mas registra
  a divergência de nomenclatura — ver [mapa-equivalencias.md](mapa-equivalencias.md));
- `FAIL` — lacuna real, com a correção exata impressa junto.

Peso 3 para as 8 capacidades **críticas**, peso 1 para as demais. Exit 0 só
quando todas as críticas passam.

Saída: `Índice de Prontidão 0–100`, percentual por subsistema, e nível de
maturidade (0 sem harness → 4 loop autônomo).

### Medindo a skill, não o repo

O número absoluto de um repo diz pouco. A eficácia da skill é o **delta**:

```bash
./eval/score-harness.sh /repo --json > antes.json
# rode a skill harness-creator no /repo
./eval/score-harness.sh /repo --json > depois.json
./eval/compare-harness.sh antes.json depois.json
```

Métricas que saem daí:

| Métrica | Definição | Meta |
|---|---|---|
| **Lift** | `score_depois − score_antes` | ≥ +50 em repo sem harness |
| **Taxa de fechamento de lacunas** | lacunas fechadas / lacunas iniciais | ≥ 80% |
| **Fechamento de críticas** | críticas fechadas / críticas iniciais | **100%** — é o mínimo operável |
| **Lacuna residual** | FAILs que sobram depois da skill | ≤ 4, e todas listadas no Plano de Remediação |
| **Regressão** | capacidade que existia e sumiu | **0** — a skill não pode destruir harness pré-existente |
| **Divergência** | quantidade de EQUIV | reportar; alto = pouca interoperabilidade |

Rode em uma amostra, não em um repo. Sugestão de painel mínimo (um por
ecossistema, já que a skill detecta ecossistema e não linguagem): Python/uv,
Node/pnpm, .NET, Java/Maven, Go. Mais três casos de borda que costumam
quebrar geradores: monorepo, repo **sem test runner**, e repo que **já tem**
AGENTS.md e CI.

O caso "sem test runner" é o mais informativo: lá a skill não pode gerar DoD
real. O comportamento correto é lacuna declarada + item de remediação com
comando exato — não enforcement vazio. O scorer marca `V1`/`V5` como FAIL;
a avaliação da skill nesse repo é se ela **admitiu** isso, o que é um check
manual (ver critério R1 no protocolo).

## Nível C — Eficácia comportamental

Arquivo existir não é o benefício; o agente obedecer é. O
[protocolo de experimento](protocolo-experimento.md) descreve o A/B: mesma
tarefa, mesmo modelo, repo com e sem harness, medindo aderência ao protocolo,
falsos "pronto", retrabalho entre sessões e recuperação de contexto perdido.

---

## Primeira medição (2026-07-26, repo `harness-creator`)

| Instrumento | Resultado |
|---|---|
| Nível A (audit oficial) | **11/70** componentes; críticos **5/7**; exit 1 |
| Nível B (scorer semântico) | **96/100**; críticas **8/8**; nível 4; 25 PASS, 9 EQUIV, 2 FAIL |

A distância entre 11/70 e 96/100 é o achado central e **não** é margem de
erro de um dos dois. São dois recortes diferentes:

1. **Divergência de nomenclatura (9 capacidades).** `SESSION_STATE.md` no
   lugar de `PROGRESS.md`, `TASKS.md`/OpenSpec no lugar de
   `feature_list.json`, hooks + pre-commit + `/dod` no lugar de alvos de
   `Makefile`. A capacidade existe; a ferramenta oficial não a enxerga. Custo
   real: nenhuma ferramenta de terceiros do ecossistema do curso funciona
   sobre o repo gerado.
2. **Lacunas reais.** O audit oficial cobra L10/L11/L12 em profundidade
   (registro de regras arquiteturais, trace por sessão, documento de
   qualidade) e a skill cobre isso de forma mais rasa — o scorer semântico
   registra como EQUIV, não como PASS, justamente para não esconder o
   déficit: um agente revisor não é o mesmo que uma regra executável.

Os dois FAILs genuínos deste repo (registro durável de decisões; regra de
remoção de artefato de debug) são baratos e cabem nos templates.

**Leitura honesta:** a skill entrega com folga os subsistemas 1–5 (instrução,
ambiente, estado, escopo, verificação) e entrega o subsistema 6 (ciclo de
vida/observabilidade) na metade da profundidade que o curso pede. E entrega
tudo com vocabulário próprio, o que a isola das ferramentas do curso.

---

## Arquivos

- [`score-harness.sh`](score-harness.sh) — scorer semântico, zero dependência, bash 3.2+
- [`compare-harness.sh`](compare-harness.sh) — delta antes/depois, requer `python3`
- [`mapa-equivalencias.md`](mapa-equivalencias.md) — de/para entre o vocabulário do curso e o da skill
- [`protocolo-experimento.md`](protocolo-experimento.md) — nível C, medição comportamental
