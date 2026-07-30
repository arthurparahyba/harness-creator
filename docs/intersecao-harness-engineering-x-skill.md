# Interseção: o que um repo com harness precisa × o que a skill constrói

> Analisado em 2026-07-30, contra a skill `harness-creator` v2.5.
> As características vêm do glossário de [harness-engineering.md](harness-engineering.md);
> a coluna da skill foi verificada lendo `SKILL.md`, `references/` e `resources/`.
>
> **Revisado em 2026-07-30**, duas vezes:
>
> 1. Depois de duas imprecisões achadas ao tentar transformar as lacunas em
>    trabalho. As duas eram do mesmo tipo — eu marquei como ausência o que
>    era, num caso, medição que existe e mora noutro lugar; no outro, decisão
>    explícita do usuário. O registro de ambas ficou no texto em vez de ser
>    apagado: uma análise que esconde as próprias correções não serve para
>    decidir nada. Ver "Correções" no fim.
> 2. Depois de executados os **Grupos 40, 41 e 42**, que fecharam as lacunas
>    1, 3 e 4. As linhas afetadas trazem o número do grupo. O placar passou a
>    ser **contado** a partir das tabelas, não somado de cabeça — as duas
>    versões anteriores dele estavam erradas, o que é a mesma categoria de
>    descuido que a seção Correções documenta.

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
| **Progressive disclosure de contexto** | A própria skill lê uma fase por vez, e o harness gerado tira procedimento e escopo do arquivo sempre-lido. O que não existe é instrução ao agente do repo alvo para aplicar o princípio no trabalho dele | **Parcial** — aplicado no desenho, não ensinado |
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
| **Controles inferenciais** — revisão semântica por IA | O subagente `propor-regra-arch`: lê o diff do grupo, aplica julgamento semântico ("não o erro pontual — a *classe* dele") e devolve rascunhos de regra. Um revisor que emite **veredito** foi removido no Grupo 28, por decisão do usuário | **Parcial** — o controle existe, mas só para Claude Code (ver §5) |

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
| **Guardrails de ação destrutiva** | `gate-destructive.sh`, registrado nos três agentes-alvo. Os padrões saíram do script para `.harness/gate-rules.json` no Grupo 42 | **Coberto** |
| **Fail-closed** — gate quebrado não pode liberar | `failClosed` no Cursor; fallback em awk nos scripts; regras A01/A02 validam sintaxe; e o gate cai numa lista embutida se o registro sumir, ficar ilegível ou perder todas as regras de bloqueio | **Coberto** — é o tipo de detalhe que a maioria dos harnesses erra |
| **Higiene de segredos** | Credencial de MCP vira `${VAR}`; `.env` no `.gitignore`; rotação reportada como decisão humana. E o trace de sessão redige o comando por lista de permissão, para não gravar credencial em disco | **Coberto** |
| **Permissions / approval tiers** | Três níveis no `gate-rules.json`: `permitir` (exceção ancorada, precede `bloquear`), `bloquear` (exit 2 com WHAT/WHY/FIX), `avisar` (passa, mas grava `risco` no trace) | **Coberto** — Grupo 42 |
| **Proteção do próprio enforcement** | Regras `G01`/`G02`: a DoD **executa** o gate a cada grupo e exige exit 2 no destrutivo e 0 no seguro. Detecção, porque prevenção não é portátil — o Cursor não tem evento de pré-edição de arquivo | **Coberto** — Grupo 42; não estava na tabela original |
| **Sandbox / workspace isolado** | Nada | **Ausente** |
| **Human-in-the-loop** | Uma pausa de aprovação na FASE 4; no harness gerado, o "PARE após o commit" e o gate de proposta de plano | **Coberto** |
| **Observability / tracing do agente** | `registrar-sessao.sh`, Grupo 41: uma linha por chamada de ferramenta em `.harness/trace/`, nos três agentes. Sai 0 sempre e nunca com `failClosed` — observação não pode custar o enforcement | **Coberto** — para chamadas de ferramenta |
| **Telemetry-driven development** | O trace registra o que a sessão fez, mas nada consome isso para reproduzir bug | **Ausente** |
| **Evals do harness** | `medir-aderencia.sh`: quatro medidas sobre o git (Grupo 40), a quinta sobre o trace (Grupo 41) e a sexta sobre risco dos comandos (Grupo 42). Diagnóstico, não gate | **Parcial** — mede aderência e risco, não eficácia; para isso continua sendo preciso o A/B do nível C |

---

## 7. O que a skill tem e a literatura não discute

Cinco coisas aparecem aqui e não no vocabulário estabelecido. Valem como
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
- **Enforcement que se prova a cada grupo** — as regras `G01`/`G02` executam
  o gate dentro da DoD. A literatura discute guardrails como coisa que se
  configura; aqui a configuração é verificada em toda rodada, porque quem
  pode enfraquecê-la é justamente quem ela vigia. O par importa: a G01
  sozinha é satisfeita por um gate que bloqueia tudo.
- **A distinção prevenção × detecção como decisão de portabilidade** — o
  Cursor não tem evento de pré-edição de arquivo, então proteger o gate
  contra edição não valeria nos três agentes. Em vez de entregar
  enforcement parcial, a skill previne no shell e detecta no resto. A
  literatura trata guardrail como capacidade uniforme; na prática ela é
  desigual entre agentes, e o desenho precisa dizer onde.

---

## Placar

Contado a partir das tabelas acima, não somado de cabeça — as duas versões
anteriores deste placar estavam erradas por aritmética minha, o que é a mesma
categoria de descuido que a seção Correções documenta. O comando abaixo
recontá-lo, e **reprova linha ambígua**: contar expôs uma característica
marcada como Coberto *e* Ausente ao mesmo tempo, que por isso não era
contável por ninguém — virou Parcial, que é o que ela sempre foi.

```
awk -F'|' '/^\|/ && NF==5 && $4 !~ /---|Cobertura/ {print $4}' \
  docs/intersecao-harness-engineering-x-skill.md | sed 's/\*\*//g'
```

| Cobertura | Nº de características |
|---|---|
| Coberto | 24 |
| Parcial | 9 |
| Proposto (diagnosticado, não gerado) | 2 |
| Ausente | 4 |
| Fora de escopo (deliberado) | 3 |
| **Total** | **42** |

**As quatro ausências restantes são todas de runtime**: sandbox, tool design,
progressive token budgeting e telemetry-driven development. As três primeiras
são inner harness — vêm do fornecedor do agente, não do repositório. Só a
última é outer harness de verdade.

Isso confirma a leitura original e a torna mais forte: a skill cobre o que é
harness *de repositório*, e o que sobra está do outro lado da fronteira entre
inner e outer harness. Não há mais nenhuma ausência do tipo "foi esquecido".

---

## Lacunas priorizadas

Ordenadas pelo que destrava outra coisa, seguindo a mesma regra do Plano de
Remediação da própria skill:

1. ~~**Evals do harness gerado**~~ — **fechada na forma estreita pelo Grupo
   40.** A forma larga que eu havia escrito era falsa (ver Correções). O que
   faltava era um eval que *viajasse* com o harness: `medir-aderencia.sh`
   agora vai no repo alvo. Continua fora: eficácia comportamental, que exige
   A/B com modelo real e não cabe num script de histórico.
2. ~~**Controles inferenciais**~~ — **não era lacuna** (ver Correções). O
   `propor-regra-arch` é gerado e é inferencial; o revisor com veredito foi
   removido por decisão do usuário no Grupo 28, com o custo medido.
   Resíduo legítimo, menor: a camada inferencial vale só para Claude Code.
3. ~~**Observability do agente**~~ — **fechada pelo Grupo 41.** O
   `registrar-sessao.sh` grava uma linha por chamada de ferramenta,
   independente de o agente commitar, cooperar ou chegar ao fim; a medida 5
   do `medir-aderencia.sh` lê isso e detecta sessão que editou e não
   commitou. Continua fora: raciocínio, custo, e se a edição foi descartada
   depois — o trace vê chamada de ferramenta, não intenção.
4. ~~**Approval tiers**~~ — **fechada pelo Grupo 42.** Três níveis em
   `.harness/gate-rules.json`, exceções ancoradas, e as regras `G01`/`G02`
   executando o gate na cadeia da DoD. Prevenção onde é portátil, detecção
   onde não é.
5. **Progressive disclosure no repo alvo** — a skill aplica o princípio em
   si mesma, mas não o ensina ao harness que gera. **Em aberto por decisão
   do usuário**, que quis entender melhor antes.
6. **Sandbox** — é do runtime, então provavelmente fora de escopo de verdade;
   mas isso não está registrado como decisão em lugar nenhum, e ausência sem
   motivo escrito é indistinguível de esquecimento. **Em aberto.**

A sequência 1–4 foi executada. As lacunas 1 e 2 não viraram código pelo
motivo esperado: a 1 foi reduzida à forma estreita e a 2 cancelada — as duas
por erro de análise, não por mudança de escopo (ver Correções).

---

## Correções

Duas linhas deste documento estavam erradas, e as duas erravam do mesmo
jeito: marcavam como **ausência** o que era outra coisa. Ficam registradas
porque uma análise que apaga os próprios erros não serve para decidir nada
— e porque o modo de errar se repete, o que é informação sobre como ler o
resto da tabela.

**Lacuna 1, forma larga (errada):** *"não há como responder se este harness
melhorou o comportamento do agente"*. Falso. Este repositório tem cinco
níveis de eval: A e B em [`eval/score-harness.sh`](../eval/score-harness.sh)
(36 capacidades), C em [`eval/nivel-c/`](../eval/nivel-c/README.md) (A/B no
Spring PetClinic: falso "pronto" em 3 de 4 sessões sem harness contra 0 de 4
com), D em `evals/gradua.py` e E em `evals/triggering.json`. A pergunta *é*
respondida, com evidência. A lacuna estreita e correta: nenhum deles viaja
junto com o harness — todos medem a skill, rodam aqui, e são operados por
quem a escreve.

**Lacuna 2, como escrita (errada):** *"nenhum revisor semântico é gerado; é
a metade do eixo de Böckeler que está totalmente vazia"*. Duas falhas. O
`propor-regra-arch` é gerado e é um controle inferencial — e o próprio
documento o registrava como existente na §5, contradizendo a §3. E o revisor
com veredito não está ausente por esquecimento: foi removido no Grupo 28 a
pedido do usuário, com a ressalva apresentada antes e o custo medido sem
maquiagem (`V6` de `eq` para `fail`, score de +67 para +62). Os Grupos 31 e
32 devolveram o `V6` a `pass` pelo registro de regras, com cobertura melhor
que a anterior — [`mapa-equivalencias.md`](../eval/mapa-equivalencias.md):
"revisor julga caso a caso e esquece, registro acumula". A classificação
correta é **Fora de escopo (decisão explícita)**, não Ausente.

**O padrão:** as duas linhas foram escritas olhando só para o repositório
alvo e para o `resources/` da skill. Nenhuma consultou `eval/`, `evals/` nem
o histórico de decisões no `TASKS.md`. Uma tabela de cobertura montada assim
enxerga ausência onde há trabalho que mora fora do recorte — vale conferir
as demais linhas marcadas **Ausente** contra as mesmas fontes antes de
transformá-las em plano.

---

Este documento é análise, não plano. Cada lacuna vira grupo no `TASKS.md`
antes de qualquer implementação.
