# Interseção: o que um repo com harness precisa × o que a skill constrói

> Analisado em 2026-07-30, contra a skill `harness-creator` v2.5.
> As características vêm do glossário de [harness-engineering.md](harness-engineering.md);
> a coluna da skill foi verificada lendo `SKILL.md`, `references/` e `resources/`.

Legenda de cobertura:

| Marca | Significado |
|---|---|
| **Coberto** | A skill gera o artefato, e ele é verificado na FASE 5 |
| **Parcial** | Existe alguma coisa, mas mais fraca que o padrão da literatura |
| **Proposto** | A skill não gera; ela diagnostica e recomenda no Plano de Remediação |
| **Ausente** | Nem gerado nem diagnosticado |
| **Fora de escopo** | Ausência deliberada, com motivo registrado na própria skill |

---

## 1. Camada de instrução (outer harness)

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **Arquivo de instrução na raiz** — protocolo permanente que o agente lê sempre | `AGENTS.md` na raiz, transcrito VERBATIM do template, com DoD, grupos, WIP=1 e regras MUST NOT | **Coberto** |
| **Ponte de carregamento** — o arquivo precisa efetivamente entrar em contexto | `CLAUDE.md` com `@AGENTS.md` ao lado de *cada* `AGENTS.md`. É regra inviolável nº 9, porque sem ela o protocolo é gravado e nunca lido | **Coberto** — e é um detalhe que quase nenhuma fonte da literatura cobre |
| **Instrução com escopo** — restrições locais que só carregam quando o caminho é relevante | `AGENTS-scoped.md` no diretório principal de código, separando escopo (local) de protocolo (raiz) | **Coberto** |
| **Ambient affordances** — ambiente legível sem instrução explícita | `.editorconfig`, `.gitignore`, README mínimo, `.mcp.json` normalizado na raiz | **Parcial** — cobre convenções de arquivo, não estrutura de código |
| **Skills / procedimento sob demanda** | Skill `executar-grupo` com os 8 passos do checkpoint | **Coberto** (só Claude Code — ver limite abaixo) |
| **Agent-first codebase** — documentação machine-readable como fonte única | Descoberta cita arquivo-fonte para toda afirmação (regra nº 3); DoD e comandos saem de manifesto/CI reais | **Parcial** — garante veracidade do que escreve, não reorganiza a doc do projeto |

---

## 2. Guides — controles feedforward

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **Plano como artefato** — o trabalho vive num arquivo, não no chat | Fonte de trabalho com precedência: `openspec/changes/<ativa>/tasks.md` → `TASKS.md`. Regra: "nunca invente tarefas fora da fonte ativa" | **Coberto** |
| **Plan-and-execute** — planejar separado de executar | Gate explícito: se o pedido não está coberto pela fonte de trabalho, o agente PARA e propõe antes de editar qualquer arquivo | **Coberto** |
| **Task decomposition com marcos** | Grupos de 2-5 tasks, cada um com linha `Verificação:` executável e dependências declaradas entre grupos | **Coberto** |
| **Progressive disclosure de contexto** | A própria skill lê uma fase por vez; o harness gerado tira procedimento e escopo do arquivo sempre-lido | **Coberto** no design; **Ausente** como instrução ao agente do repo alvo |
| **Restrições arquiteturais mecânicas** (as "camadas" do Codex) | `.harness/arch-rules.json` — regras com `check`, `expect`, `what`, `why`, `fix` — mais o subagente `propor-regra-arch` para adicionar novas | **Coberto** |

---

## 3. Sensors — controles feedback

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **Controles computacionais** (testes, lint, tipos) | Não instala sensores. Descobre os existentes e os encadeia na DoD | **Proposto** — é o item nº 1 do grupo B do Plano de Remediação, com comandos do ecossistema detectado e nomes de funções puras concretas para testar |
| **DoD como gate executável** | Bloco `Definition of Done` no AGENTS.md com comandos reais `&&`-encadeados + comando `/dod` que os roda | **Coberto** |
| **Deterministic gate vs. probabilistic compliance** | Pre-commit portátil + workflow de CI (`harness-dod.yml`), ambos só gerados se houver comandos reais — regra nº 5, "não gere enforcement vazio" | **Coberto**, com honestidade explícita |
| **Architecture fitness functions** | `check-arch.sh` roda as regras do `arch-rules.json` e entra na cadeia da DoD. Shell puro, portátil aos três agentes | **Coberto** |
| **Maintainability harness** | `format-on-edit.sh` (hook de edição) + pre-commit | **Coberto**, com exceção documentada: formatter que não escopa por arquivo vira item do Plano em vez de hook |
| **Behaviour harness** — corretude funcional | Depende inteiramente dos testes do repo | **Proposto** — mesma lacuna que a literatura chama de "categoria menos madura" |
| **Controles inferenciais** — revisão semântica por IA | Nenhum revisor inferencial é gerado | **Ausente** |

---

## 4. Continuidade entre sessões

Este é o eixo mais forte da skill. É onde ela implementa quase literalmente
o padrão do artigo da Anthropic.

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **`init.sh`** — estado executável num comando | `init.sh` em 4 blocos: deps, sanity, baseline de testes, estado persistido (SESSION_STATE + fonte de trabalho + git log) | **Coberto** |
| **Progress file / handoff** | `SESSION_STATE.md` com commit verificado, testes X/Y, grupo em andamento, não commitado, bloqueios, próxima ação | **Coberto** |
| **Session startup protocol** | Seção "Início de nova funcionalidade" do AGENTS.md: init → ler estado → terminar grupo pendente → checar cobertura → branch → próximo grupo | **Coberto** |
| **Incremental progress** | WIP=1 e "PARE após o commit do grupo. Contexto pode ser reiniciado." | **Coberto** |
| **Git-based state management** | Um commit por grupo (`checkpoint: <nome>`), nunca com verificação falhando | **Coberto** |
| **Feature list** — requisitos granulares marcados como falhando | `TASKS.md` tem grupos e verificação, mas não o padrão "200 features todas falhando" | **Parcial** |
| **Initializer agent** — prompt distinto para a primeira janela | A skill *é* o initializer, executada uma vez pelo humano. Não gera um agente inicializador separado no repo alvo | **Fora de escopo** — resolvido por outro mecanismo |
| **Memória de longo prazo** além da sessão | Só `SESSION_STATE.md` + git | **Parcial** |

---

## 5. Runtime do agente

Aqui está a maior distância entre a literatura e a skill — e em boa parte
por construção: são características do *inner* harness, que vem do
fornecedor do agente, não do repositório.

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **Agent loop** (ReAct) | Nada — é do agente | **Fora de escopo** (inner harness) |
| **Compaction / context rot** | Nada | **Fora de escopo** (inner harness) |
| **Subagent isolation** | Gera um subagente (`propor-regra-arch`), mas não uma política de delegação | **Parcial** |
| **Tool design** — schemas e erros de ferramenta como interface | Nada sobre desenho de ferramentas | **Ausente** |
| **MCP** | Detecta config MCP existente e normaliza credencial para `${VAR}`; consolida em `.mcp.json` na raiz | **Parcial** — higieniza o que existe, não propõe servidores |
| **Progressive token budgeting** | Nada no repo alvo | **Ausente** |

---

## 6. Segurança e operação

| Característica esperada | O que a skill constrói | Cobertura |
|---|---|---|
| **Guardrails de ação destrutiva** | `gate-destructive.sh` — exit 2 bloqueia. Registrado nos três agentes-alvo (`.claude/settings.json`, `.devin/hooks.v1.json`, `.cursor/hooks.json` com `failClosed`) | **Coberto** |
| **Fail-closed** — gate quebrado não pode liberar | `failClosed` no Cursor; fallback em awk nos scripts para não depender de Python; regra A01/A02 valida sintaxe do hook | **Coberto** — é o tipo de detalhe que a maioria dos harnesses erra |
| **Higiene de segredos** | Credencial literal de MCP vira `${VAR}` (regra nº 4); `.env` no `.gitignore`; `.env.example` recomendado; rotação do segredo exposto reportada como decisão humana | **Coberto** |
| **Permissions / approval tiers** | Só o binário do gate destrutivo | **Parcial** — não há gradação por risco |
| **Sandbox / workspace isolado** | Nada | **Ausente** |
| **Human-in-the-loop** | Uma pausa de aprovação na FASE 4; no harness gerado, o "PARE após o commit" e o gate de proposta de plano | **Coberto** |
| **Observability / tracing do agente** | Nada | **Ausente** |
| **Telemetry-driven development** | Nada | **Ausente** |
| **Evals do harness** | Nada no repo alvo. (Existe a skill `exp-nivel-c` *neste* repositório, mas ela não é gerada para o alvo) | **Ausente** — a lacuna mais cara |

---

## 7. O que a skill tem e a literatura não discute

Três coisas aparecem aqui e não no vocabulário estabelecido. Valem como
contribuição própria:

- **Meta-harness verificado** — `verificar-harness.sh` (316 linhas) checa o
  harness recém-gravado: JSON e YAML que parseiam, scripts executáveis com
  LF, DoD equivalente entre os arquivos que a declaram, e o gate executado
  de verdade para provar exit 2 no destrutivo e 0 no seguro. A literatura
  fala em verificar o *código*; ninguém fala em verificar o *harness*.
- **Manifesto de atualização** — `.claude/harness.json` registra versão,
  data, ecossistema, DoD, arquivos gerados e o campo `recusados`. Torna o
  harness atualizável e auditável, e impede repropor o que o usuário já
  negou. A literatura trata harness como coisa que se escreve uma vez.
- **Portabilidade entre agentes-alvo** — os mesmos scripts registrados em
  três formatos de hook, com leitura dos dois layouts de JSON. Quase toda
  a literatura assume um agente só.

---

## Placar

| Cobertura | Nº de características |
|---|---|
| Coberto | 21 |
| Parcial | 8 |
| Proposto (diagnosticado, não gerado) | 2 |
| Ausente | 8 |
| Fora de escopo (deliberado) | 3 |

O padrão é nítido: **a skill é forte onde o harness é de repositório**
(instrução, guides, sensors, continuidade, guardrails) e vazia onde o
harness é de runtime (loop, contexto, tracing) — o que é a divisão correta
entre inner e outer harness. As ausências que *não* seguem esse padrão são
as que valem discutir.

---

## Lacunas priorizadas

Ordenadas pelo que destrava outra coisa, seguindo a mesma regra do Plano de
Remediação da própria skill:

1. **Evals do harness gerado** — hoje não há como responder "este harness
   melhorou o comportamento do agente?" para o repo alvo. Sem isso, toda
   mudança na skill é achismo. É a lacuna que torna as outras difíceis de
   priorizar.
2. **Controles inferenciais** — nenhum revisor semântico é gerado. É a
   metade do eixo de Böckeler que está totalmente vazia, e é justamente a
   que pega o que linter não pega.
3. **Observability do agente** — sem trace, um grupo que descarrilha só
   deixa o `SESSION_STATE.md`, que é escrito pelo próprio agente que
   descarrilhou.
4. **Approval tiers** — o gate é binário. Uma gradação por risco reduziria
   tanto o falso bloqueio quanto o falso verde.
5. **Progressive disclosure no repo alvo** — a skill aplica o princípio em
   si mesma, mas não o ensina ao harness que gera.
6. **Sandbox** — provavelmente fora de escopo de verdade (é do runtime),
   mas hoje isso não está registrado como decisão em lugar nenhum.

Nenhuma destas está na fonte de trabalho ativa. Este documento é análise,
não plano — virar plano exige `/opsx:propose`.
