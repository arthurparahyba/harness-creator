# Harness Engineering — artigos de referência e glossário

> Pesquisa consolidada em 2026-07-30. Fontes primárias listadas no fim.
> Nota: `openai.com/index/harness-engineering` e `unrolling-the-codex-agent-loop`
> retornaram 403 na coleta; o conteúdo do primeiro foi resumido pela cobertura
> do InfoQ, e o segundo entra apenas como ponteiro.

## Os artigos que importam

| # | Artigo | Por que é importante |
|---|---|---|
| 1 | **Birgitta Böckeler — "Harness engineering for coding agent users"** (martinfowler.com, 02/04/2026) | O texto canônico do lado do *usuário* de agentes. Introduz o vocabulário que todo mundo passou a usar: guides/sensors, controles computacionais vs. inferenciais, harnessability. |
| 2 | **Anthropic — "Effective harnesses for long-running agents"** (26/11/2025) | O experimento que fundou o padrão de continuidade entre sessões: initializer agent, `init.sh`, arquivo de progresso, protocolo de startup de sessão. É o desenho que este repo implementa. |
| 3 | **OpenAI — "Harness engineering: leveraging Codex in an agent-first world"** (fev/2026) | O caso interno mais radical: um serviço em produção 100% escrito por Codex. Origem do termo "agent-first codebase" e da ideia de restrições arquiteturais mecânicas. *(lido via InfoQ — original bloqueado)* |
| 4 | **OpenAI — "Unrolling the Codex agent loop"** | Desmonta o loop do agente componente a componente e mostra onde cada um pode ser melhorado. *(não acessível; citado consistentemente como referência do loop)* |
| 5 | **Anthropic — "Building Effective Agents"** (dez/2024) | Pré-data o termo, mas é a base: workflows vs. agentes, e os padrões de composição (prompt chaining, routing, orchestrator-workers, evaluator-optimizer). |
| 6 | **Zhou et al. — "Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering"** (arXiv 2604.08224, abr/2026) | O único survey acadêmico que trata harness como camada unificadora. Taxonomia "from weights to context to harness". |
| 7 | **awesome-harness-engineering** (GitHub) | Índice vivo — foundations, design primitives, evals, sandbox/permissions, templates. Melhor ponto de entrada para o resto. |
| 8 | **Wikipedia — "Agent harness"** | Útil por consolidar a distinção inner vs. outer harness e a fórmula `Agent = Model + Harness`. |

---

## Glossário

### Conceitos-raiz

- **Harness** — tudo em um agente de IA *exceto o modelo*: loop, ferramentas, contexto, memória, sandbox, guardrails, observabilidade. Definição de Böckeler.
- **Agent = Model + Harness** — a fórmula-síntese de 2026: capacidade bruta do modelo deixou de ser o gargalo; o gargalo é a infraestrutura determinística em volta dele.
- **Inner harness** — o que vem pronto do fornecedor (SDK, ferramentas de arquivo, loop, permissões do Claude Code / Codex).
- **Outer harness** — o que *você* monta por cima: AGENTS.md, servidores MCP, skills, hooks, scripts. É aqui que mora a harness engineering do usuário.
- **Externalization** — mover capacidade dos pesos do modelo para infraestrutura externa (memória, skills, protocolos). Tese do survey.
- **Harnessability** — o quanto uma codebase *permite* ser controlada: linguagem tipada, arquitetura modular, testes rápidos aumentam; um monolito dinâmico sem testes destrói.
- **Ambient affordances** — propriedades estruturais do ambiente que o tornam legível e navegável para o agente, sem instrução explícita (nomes consistentes, estrutura previsível, erros descritivos).
- **Agent-first codebase** — codebase projetada assumindo que o autor principal é um agente: documentação machine-readable, fronteiras explícitas, feedback executável.

### Controle (o eixo de Böckeler)

- **Guides / feedforward controls** — atuam *antes* da ação, aumentando a chance de acerto de primeira: instruções, specs, templates, exemplos, plano aprovado.
- **Sensors / feedback controls** — atuam *depois*, detectando problema e permitindo autocorreção antes do humano: testes, lint, type check, revisão por outro agente.
- **Controles computacionais** — determinísticos e rápidos (CPU): pytest, ruff, mypy, ArchUnit. Milissegundos, resultado confiável.
- **Controles inferenciais** — julgamento semântico feito por IA: lentos, caros, não determinísticos, mas capturam o que linter não captura.
- **Maintainability harness** — controles sobre qualidade interna e estrutura do código.
- **Architecture fitness harness** — fitness functions: checagens executáveis de características arquiteturais (camadas, dependências, performance).
- **Behaviour harness** — garantia de corretude funcional. Categoria admitidamente menos madura; ainda exige validação humana pesada.
- **Structural tests** — testes que falham quando a camada arquitetural é violada (na OpenAI: Types → Config → Repo → Service → Runtime → UI).
- **Deterministic gate vs. probabilistic compliance** — a distinção central da disciplina: pedir "siga o padrão" no prompt é probabilístico; um lint que bloqueia o commit é determinístico. Sempre prefira o segundo.

### Runtime do agente

- **Agent loop** — ciclo pensar → agir → observar, repetido até condição de parada. Base no paper ReAct.
- **Tool design** — nomes, schemas e mensagens de erro das ferramentas tratados como interface de produto: erro mal escrito custa iterações.
- **MCP (Model Context Protocol)** — protocolo padrão para expor ferramentas e dados a qualquer agente.
- **Skills** — expertise procedural empacotada e invocável (é o que este repo gera).
- **Context delivery / context engineering** — decidir o que entra na janela e quando; documentação estruturada como fonte única de verdade.
- **Compaction** — sumarização do histórico quando a janela enche, preservando o essencial.
- **Progressive token budgeting** — alocar orçamento de contexto por fase da tarefa em vez de despejar tudo de uma vez.
- **Context rot** — degradação de qualidade conforme o contexto cresce, mesmo dentro do limite da janela.
- **Subagent isolation** — delegar a um subagente com contexto reconstruído do zero, devolvendo só a conclusão ao pai.
- **Plan-and-execute** — separar planejamento de execução em passos/artefatos distintos (Plan.md / Implement.md no Codex).

### Continuidade entre sessões (padrão Anthropic)

- **Long-running agent** — trabalho que atravessa múltiplas janelas de contexto, em sessões discretas, cada uma nascendo sem memória.
- **Initializer agent** — agente da primeira sessão: prepara ambiente, cria `init.sh`, arquivo de progresso e commit inicial. Prompt diferente do das sessões seguintes.
- **`init.sh`** — script único que instala deps, roda testes e mostra o estado. Reduz descoberta de ambiente a um comando.
- **Progress file** (`claude-progress.txt`, o `SESSION_STATE.md` daqui) — mecanismo de handoff: o que foi feito, o que travou, qual a próxima ação.
- **Feature list** — expansão do pedido em requisitos granulares e testáveis, todos marcados como falhando no início, dando alvo explícito de conclusão.
- **Git-based state management** — commits descritivos como memória externa auditável e ponto de reversão.
- **Session startup protocol** — sequência fixa no início de cada sessão: verificar diretório, ler git log e progresso, escolher a próxima tarefa, rodar health check.
- **Incremental progress** — cada sessão avança um pedaço verificado, em vez de tentar a solução completa (o WIP=1 / checkpoint por grupo deste repo).

### Segurança e operação

- **Guardrails** — retries, timeouts, max-steps, teto de orçamento, condições de parada.
- **Permissions / approval tiers** — gradação de autorização por risco da ação, em vez de prompt de permissão para tudo.
- **Sandbox / workspace** — ambiente isolado onde o agente pode errar sem consequência.
- **Human-in-the-loop** — pontos de aprovação e intervenção explicitamente desenhados no fluxo.
- **Observability / tracing** — spans e logs da execução do agente; base para depurar por que uma sessão descarrilhou.
- **Telemetry-driven development** — agente usa logs e métricas para reproduzir bugs em isolamento, prática interna do OpenAI.
- **Evals** — medição sistemática do harness contra tarefas de referência; sem isso, mudanças no harness são achismo.

---

## Encaixe com este repositório

O AGENTS.md que a skill gera implementa quase literalmente o padrão Anthropic
(`init.sh`, `SESSION_STATE.md`, protocolo de startup, incremental progress) com
sensores computacionais no eixo de Böckeler (`pytest && ruff check . && mypy`).

A análise característica a característica — o que a literatura exige × o que a
skill `harness-creator` de fato gera, com placar e lacunas priorizadas — está em
[intersecao-harness-engineering-x-skill.md](intersecao-harness-engineering-x-skill.md).

---

## Fontes

- [Harness engineering for coding agent users — Böckeler](https://martinfowler.com/articles/harness-engineering.html)
- [Effective harnesses for long-running agents — Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [OpenAI harness engineering (cobertura InfoQ)](https://www.infoq.com/news/2026/02/openai-harness-engineering-codex)
- [Harness engineering: leveraging Codex in an agent-first world — OpenAI](https://openai.com/index/harness-engineering/)
- [Unrolling the Codex agent loop — OpenAI](https://openai.com/index/unrolling-the-codex-agent-loop/)
- [Externalization in LLM Agents (arXiv 2604.08224)](https://arxiv.org/abs/2604.08224)
- [awesome-harness-engineering](https://github.com/ai-boost/awesome-harness-engineering)
- [Agent harness — Wikipedia](https://en.wikipedia.org/wiki/Agent_harness)
- [What Is an Agent Harness? — Arize](https://arize.com/blog/what-is-an-agent-harness/)
- [Harness Engineering — Faros AI](https://www.faros.ai/blog/harness-engineering)
