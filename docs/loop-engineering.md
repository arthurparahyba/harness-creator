# Loop Engineering — artigos de referência e glossário

> Pesquisa consolidada em 2026-07-31. Fontes primárias listadas no fim.
>
> **Aviso de maturidade.** Diferente de harness engineering, este vocabulário
> tem *dois meses*. O post de Steinberger que o disparou é de 07/06/2026, o
> ensaio "Loopcraft" saiu em 12/06/2026 e o AI Engineer World's Fair que o
> consolidou foi em junho de 2026. Não existe survey acadêmico do termo, não há
> consenso sobre a taxonomia, e boa parte do material é blog de fornecedor
> descrevendo o próprio produto. Tratar como campo em formação, não como
> disciplina assentada — as marcações de divergência abaixo são deliberadas.
>
> Nota de coleta: a keynote de swyx no AIEWF só foi lida por transcrições e
> recaps (o vídeo não foi assistido); os dois PDFs do arXiv entraram por resumo
> automático, não por leitura integral.

## Os artigos que importam

| # | Artigo | Por que é importante |
|---|---|---|
| 1 | **swyx — "Loopcraft: The Art of Stacking Loops"** (latent.space, 12/06/2026) | O texto que nomeou a coisa. Consolida Steinberger, Cherny e Karpathy numa tese só: a habilidade de maior alavancagem deixou de ser escrever um bom prompt. Origem de "stacking loops", "Salty Lesson" e do eixo subir/descer um loop. |
| 2 | **LangChain — "The Art of Loop Engineering"** | A taxonomia mais citada: os quatro loops empilhados (agente → verificação → evento → hill climbing). É o mapa que quase todo material posterior reusa. |
| 3 | **"Engineering Reliable Coding Agent Loops"** (todatabeyond) | O material mais técnico e menos hype. Modelo de dois loops (nativo × supervisor), loop contract tipado, classificação de falhas, failure fingerprinting, no-progress detection. É o que mais se parece com engenharia. |
| 4 | **Geoffrey Huntley — técnica "Ralph Wiggum"** (meados de 2025) | O loop mínimo que funcionou: `while :; do cat PROMPT.md \| claude-code; done`. Pré-data o termo e é a prova de existência que o resto racionalizou. Hoje é plugin oficial do Claude Code. |
| 5 | **Vercel AI SDK — "Agents: Loop Control"** | Onde a teoria vira API: `stopWhen`, `stepCountIs`, `prepareStep`, `activeTools`. Útil por mostrar que as "condições de parada" da literatura já são parâmetros nomeados. |
| 6 | **"Supervising Ralph Wiggum: Metacognitive Co-Regulation"** (arXiv 2603.24768) | O único tratamento acadêmico dos *modos de falha* do loop: drift, stagnation, fixation — e mecanismos de supervisão contra eles. |
| 7 | **"Self-Compacting Language Model Agents"** (arXiv 2606.23525) e **"Beyond Compaction"** (arXiv 2606.11213) | O problema que só aparece dentro de loops longos: a janela enche. Compaction, eviction estruturada, horizonte estendido. |
| 8 | **Cockroach Labs — "Why Agent Loops Fail in Production"** | O ângulo que ninguém mais cobre: durabilidade. Checkpointing, fronteiras de transação, blast radius, recovery gap. Loop que não sobrevive a restart não é produção. |
| 9 | **TrueFoundry — recap AIEWF 2026** | Fixa a relação entre as duas disciplinas: "loops geram saída em escala; harnesses governam essa saída". Traz o dado do evento: 27,6% dos PRs mergeados vieram de IA, ~48% tiveram revisão humana explícita. |

---

## Glossário

### Conceitos-raiz

- **Loop engineering** — projetar deliberadamente o ciclo em que o agente roda: o que ele faz entre chamadas de ferramenta, quando confere o próprio trabalho e como decide que terminou. Sucessor declarado do prompt engineering.
- **Loopcraft** — o nome de swyx para a mesma prática, com ênfase no *empilhamento*: a arte não é desenhar um loop, é escolher a pilha certa.
- **Stacking loops** — cercar um loop com outro, cada camada externa monitorando e corrigindo a interna. A tese é que a inteligência bruta do modelo importa menos que os loops em volta dele.
- **Subir / descer um loop** — descer para a camada de baixo quando algo quebra (confiabilidade); subir conforme os modelos melhoram (alavancagem). swyx aposta que subir vale mais no longo prazo.
- **Salty Lesson** — inversão da Bitter Lesson de Sutton: "não conserte as coisas você mesmo; foque em sistemas que escalam com mais agentes — metas e orquestração".
- **Agent loop** — o ciclo raciocinar → agir → observar, repetido até uma condição de parada. Base no ReAct; é o Loop 1 de toda taxonomia.
- **Loop vs. harness** — não são concorrentes nem sinônimos: o loop é o que *executa*, o harness é o que o *limita*. `Agent = Model + Harness`, e o loop é o que o harness cerca. Loop sem harness multiplica saída além do que humano inspeciona.

### A pilha de loops (taxonomia LangChain)

- **Loop 1 — Agent loop** — modelo chamando ferramentas até a tarefa acabar. Automatiza o trabalho.
- **Loop 2 — Verification loop** — um *grader* confere a saída contra uma rubrica e, se reprovar, devolve com feedback. Custa latência e dinheiro por execução; se paga quando precisão importa.
- **Loop 3 — Event-driven loop** — o gatilho deixa de ser humano: webhook, cron, mensagem. É o que faz o agente parecer infraestrutura em vez de brinquedo.
- **Loop 4 — Hill climbing loop** — traces de produção alimentam um agente de análise que melhora a configuração do harness. A seta de retorno não volta ao topo: ela **alcança dentro** do Loop 1 e o altera.
- **Modelo de dois loops** (variante técnica) — loop nativo do agente (Claude Code, Codex) dentro de um **loop supervisor** externo que mantém estado entre invocações e decide se a evidência representa progresso real.

### Anatomia de um loop

- **Trigger** — o que inicia (comando, agendamento, evento).
- **Verifiable goal** — definição de "pronto" checável por máquina. Meta vaga ("faça boa pesquisa") produz comportamento imprevisível.
- **Tools** — as ações disponíveis, e cujo resultado o agente observa.
- **State / memory** — registro do que já foi tentado e descoberto. Sem isso o loop repete tentativas.
- **Stop rules** — três saídas, não uma: sucesso, desistência (teto de tentativas) e escalada para humano.
- **Context accumulation** — resultados de ferramenta voltam para o histórico. É o mecanismo do loop e também sua bomba-relógio (ver *context rot*).
- **Loop contract** — especificação tipada do que uma execução pode fazer: objetivo, caminhos graváveis e protegidos, critérios de aceite, teto de iterações, máximo de arquivos alterados.

### Condições de parada e orçamento

- **`stopWhen` / `stepCountIs(n)` / `hasToolCall()`** — as condições de parada como parâmetro de API (AI SDK). O default de 20 passos existe como controle de custo, não de qualidade.
- **`prepareStep`** — callback antes de cada passo: troca modelo, ajusta parâmetros, restringe `activeTools`, compacta o histórico. É onde o loop deixa de ser homogêneo.
- **`--max-iterations`** — o teto duro. A documentação do Ralph Wiggum é explícita: a *completion promise* (casamento exato de string) é frágil; o teto é o mecanismo primário de segurança.
- **Acceptance predicate** — verificação determinística rodada pelo *controlador*, não pelo agente. Não se aceita a alegação de conclusão do agente; roda-se `pytest` e olha-se o resultado.
- **No-progress detection** — detectar que o agente produz o mesmo resultado apesar de mudanças de instrução ou ambiente.
- **Failure fingerprinting** — comparar tipo de exceção e mensagem entre execuções para identificar que a *mesma* falha está recorrendo sob alegação de progresso.
- **Escalation / surrender** — sair para o humano é resultado legítimo do loop, e precisa ser desenhado. Loop sem essa saída ou declara vitória cedo ou não para nunca.
- **Budget exhaustion** — teto de gasto por invocação e acumulado. O caso citado do Ralph: contrato de US$ 50k entregue com US$ 297 de API — e horas de execução sem supervisão.

### Padrões de loop

- **Generate-and-verify** — gera, checa, repete até passar em critério objetivo.
- **Evaluator-optimizer** — pontua cada tentativa e itera rumo à nota maior, em vez de passa/não passa.
- **Plan-execute-replan** — revisa a estratégia quando aparece obstáculo inesperado.
- **Polling / monitoring loop** — ciclo ao longo do tempo, não dentro de uma tarefa.
- **Processing queue loop** — item por item, sequencial.
- **Event-response loop** — ação disparada por evento externo.
- **Ralph Wiggum** — realimentar o *mesmo* prompt indefinidamente. O prompt nunca muda entre iterações; o agente melhora porque **lê o próprio trabalho passado** nos arquivos e no git. No plugin do Claude Code, um hook `Stop` intercepta a tentativa de sair e devolve o prompt, sem loop externo de shell.
- **Bounded worker handoff** — contrato explícito do que uma execução isolada pode tentar: ferramentas permitidas, escopo de arquivos, limite de turnos.

### Contexto dentro do loop

- **Context rot** — a qualidade degrada conforme o contexto cresce, mesmo dentro do limite da janela. É o motivo de o loop longo ingênuo não funcionar.
- **Compaction** — sumarizar e reiniciar perto do limite. Na prática dispara bem antes de encher.
- **Self-compacting agents** — o agente reconhece a pressão de contexto e comprime o próprio histórico, sem intervenção externa.
- **Structured context eviction** — descartar seletivamente em vez de sumarizar tudo.
- **Note-taking** — externalizar para arquivo o que não cabe na janela (é o papel do `SESSION_STATE.md` deste repo).
- **Subagent isolation** — cada iteração com contexto novo, devolvendo só a conclusão.
- **Escala real** — sessões estilo SWE-bench passam de milhões de tokens e mais de cem turnos por problema. O loop longo é o caso normal, não o extremo.

### Modos de falha

- **Drift** — o agente se afasta progressivamente do objetivo declarado.
- **Stagnation** — cicla sobre soluções quase idênticas sem progresso.
- **Fixation** — trava numa abordagem cedo demais e não sai dela apesar da evidência.
- **Infinite loop** — ausência de teto ou de detecção de repetição.
- **Context overflow** — histórico cresce sem compactação.
- **Tool confusion** — ferramentas com nomes ou escopos sobrepostos.
- **Error propagation** — erro atravessa a cadeia sem verificação intermediária.
- **Idempotency failure** — retry de ferramenta com efeito colateral aplica o efeito duas vezes.
- **Blast radius** — uma única ação do agente com permissão excessiva destrói estado de produção.
- **Memory drift** — o estado histórico envelhece e corrompe o loop de hill climbing.
- **Recovery gap** — restaurar o banco não restaura a *posição* do fluxo nem os efeitos já emitidos.
- **Audit gap** — log de aplicação não reconstrói responsabilidade ao longo de milhares de iterações.

### Durabilidade e operação

- **Checkpointing** — o loop persiste o ponto de pausa; depois de qualquer restart, reencontra a posição.
- **Transaction boundaries** — sequência de escrita dentro de transação, para que uma chamada interrompida não deixe dado plausível e errado.
- **Append-only audit trail** — registro à prova de adulteração ligado a ação, credencial e versão do dado.
- **Role scoping** — permissão de escrita do agente limitada por papel, para conter blast radius.
- **Git worktree isolation** — cada tentativa em diretório próprio, sem contaminação cruzada.
- **Durable plan ledger** — registro que sobrevive às invocações: critérios de aceite originais, hipóteses que falharam, revisões.
- **Provider adapters** — normalizar saída de agentes diferentes num schema único (`changed_files`, `evidence`, `usage`, `stop_reason`).
- **Traces** — observação por passo; é o insumo do Loop 4 e a única forma de depurar por que uma execução descarrilhou.
- **Standing ownership / standing credentials** — o modelo de delegação apresentado pela Anthropic no AIEWF: agentes com posse permanente de parte da codebase. É o cenário que exige orçamento, gates de aprovação e trace por passo.

---

## Encaixe com este repositório

O protocolo do [AGENTS.md](../AGENTS.md) já é um loop engineered — só não estava
nomeado assim. A tradução termo a termo:

| Conceito da literatura | O que existe aqui |
|---|---|
| Loop supervisor (externo ao nativo) | O ciclo de grupo: `init.sh` → grupo → verificação → commit → handoff |
| Verifiable goal | A linha `Verificação:` de cada grupo — comando executável, não descrição |
| Acceptance predicate | A Definition of Done, rodada pelo humano/CI e não alegada pelo agente ("saída de comando é evidência") |
| Stop rule por escopo | WIP=1, `MUST NOT tocar em arquivos fora do escopo do grupo atual` |
| Durable plan ledger | `SESSION_STATE.md` + `TASKS.md` |
| Note-taking / handoff entre janelas | A obrigação de atualizar o `SESSION_STATE.md` a cada grupo |
| Checkpointing | Um commit por grupo — a posição do loop sobrevive ao reset de contexto |
| Bounded worker handoff | O subagente `propor-regra-arch`: escopo fechado, devolve rascunho, nunca veredito |
| Hill climbing (Loop 4) | `medir-aderencia.sh` e os evals — medição que realimenta o harness |

**O que a literatura tem e este repo não tem.** As lacunas são todas do mesmo
tipo — controles sobre *não terminar*:

1. **Nenhum teto de iteração.** Não existe equivalente a `--max-iterations`. Se
   um grupo não fecha, nada conta as tentativas.
2. **Nenhuma detecção de não-progresso.** O protocolo manda parar ao fim do
   grupo, mas nada percebe a *mesma* verificação falhando pela quarta vez —
   sem failure fingerprinting, stagnation é invisível.
3. **Escalada não é saída declarada.** Sucesso e bloqueio existem (bloqueios vão
   para o `SESSION_STATE.md`); "desistir depois de N tentativas" não.
4. **Sem orçamento.** Nenhum teto de tokens, tempo ou custo por grupo.

Isso é coerente com o desenho: aqui o loop é conduzido por humano a cada
checkpoint, e o humano é o teto de iteração. A pergunta aberta — que este
documento não responde — é se o harness gerado pela skill deveria embutir esses
controles para repositórios rodando em modo mais autônomo.

A análise equivalente do lado de harness, característica a característica com
placar, está em
[intersecao-harness-engineering-x-skill.md](intersecao-harness-engineering-x-skill.md).
O glossário irmão está em [harness-engineering.md](harness-engineering.md).

---

## Fontes

- [Loopcraft: The Art of Stacking Loops — swyx / Latent Space](https://www.latent.space/p/loopcraft)
- [AIEWF Daily Dispatch: Loops, Software Factories & Forward Deployed Engineers — Latent Space](https://www.latent.space/p/aiewf-daily-dispatch-loops)
- [The Art of Loop Engineering — LangChain](https://www.langchain.com/blog/the-art-of-loop-engineering)
- [Engineering Reliable Coding Agent Loops: Control Flow, Verification, Retries, and Stop Conditions](https://todatabeyond.substack.com/p/engineering-reliable-coding-agent)
- [ralph-wiggum plugin — anthropics/claude-code](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- ['Ralph Wiggum' loop prompts Claude to vibe-clone commercial software for $10 an hour — The Register](https://www.theregister.com/2026/01/27/ralph_wiggum_claude_loops/)
- [Agents: Loop Control — Vercel AI SDK](https://ai-sdk.dev/docs/agents/loop-control)
- [The Anatomy of an Agent Loop — Steve Kinney](https://stevekinney.com/writing/agent-loops)
- [Supervising Ralph Wiggum: Metacognitive Co-Regulation for Engineering Design (arXiv 2603.24768)](https://arxiv.org/pdf/2603.24768)
- [Self-Compacting Language Model Agents (arXiv 2606.23525)](https://arxiv.org/pdf/2606.23525)
- [Beyond Compaction: Structured Context Eviction for Long-Horizon Agents (arXiv 2606.11213)](https://arxiv.org/pdf/2606.11213)
- [Why Agent Loops Fail in Production — Cockroach Labs](https://www.cockroachlabs.com/blog/agent-loops-production-database-patterns/)
- [Loops, Harnesses, and 6,000 Engineers — AIEWF 2026 Recap, TrueFoundry](https://www.truefoundry.com/blog/aiewf-2026-loops-harness-engineering)
- [What Is Loop Engineering? — MindStudio](https://www.mindstudio.ai/blog/what-is-loop-engineering-autonomous-ai-agent-workflows)
- [Loop Engineering with Agents — Medium](https://dassum.medium.com/loop-engineering-with-agents-5e9b984e8d8a)
- [What is Loop Engineering: Four Levels of Agentic Loops — Medium](https://medium.com/@tahirbalarabe2/what-is-loop-engineering-four-levels-of-agentic-loops-ccc48b850002)
