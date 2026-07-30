# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: Grupo 41 na `feature/eval-aderencia` — **não publicado**
  (ninguém pediu push). Quatro commits acumulados nela. Antes: `c9bf6e2` na
  `main`, CI verde — Grupo 39.
- Testes: 751/751 + 4 skips explícitos; ruff e mypy strict limpos; score da
  geração **+67** em todos os ecossistemas (+52 no `sem-sensores`) — o
  `tests/medicao.json` saiu byte a byte idêntico ao baseline, sem regressão.
- Change/plano ativo: `TASKS.md` na raiz — **só o Grupo 26 aberto, e
  BLOQUEADO** (ver pendências). Grupos 25, 27 a 41 concluídos.
- Em andamento: nada — fronteira limpa. **Próximo: lacuna 4** (approval
  tiers) do `docs/intersecao-harness-engineering-x-skill.md`, proposta como
  grupo no `TASKS.md` antes de implementar. A lacuna 2 foi cancelada (era
  erro de documentação, ver abaixo); 5 e 6 o usuário decidiu não implementar.

## O que mudou nesta sessão (Grupo 41)
`registrar-sessao.sh`: hook de observação registrado nos três agentes, ao
lado do gate e nunca com `failClosed`. Grava uma linha por chamada de
ferramenta em `.harness/trace/`, com redação por lista de permissão. A medida
5 do `medir-aderencia.sh` lê esse trace e responde o que as medidas 1-4
declaravam não ver: sessão que editou arquivo e não commitou nada.

**Reduções de escopo declaradas, não silenciosas:**
- Contar bloqueios do gate ficou de fora. Exigiria o gate escrever em disco,
  e qualquer escrita dentro dele pode fazê-lo falhar aberto.
- O trace não vê raciocínio, custo, nem se a edição foi descartada depois.

**Dois defeitos achados pelos próprios testes**, ambos da mesma classe — os
dois lados escritos juntos, concordando por engano:
1. O teste de "sai 0 sempre" não mordia (a função interna já é total).
   Substituído por par comportamento + estrutura. `set -e` no hook quebraria
   o contrato sem nenhum teste de comportamento acusar.
2. O leitor da medida 5 quebrava com espaço depois dos dois-pontos e
   reportava "trace vazio" em vez de erro — quem lesse concluiria que não
   houve sessão.

## O que mudou nesta sessão (Grupo 40 + pesquisa)

## O que mudou nesta sessão (Grupo 40 + pesquisa)
Duas coisas, nesta ordem:

1. **`docs/` novo** — [harness-engineering.md](docs/harness-engineering.md)
   (pesquisa das fontes primárias: Böckeler/martinfowler, Anthropic, OpenAI,
   survey arXiv 2604.08224, awesome-list) e
   [intersecao-harness-engineering-x-skill.md](docs/intersecao-harness-engineering-x-skill.md)
   (42 características × o que a skill gera; placar 21 coberto / 8 parcial /
   2 proposto / 8 ausente / 3 fora de escopo, mais 6 lacunas priorizadas).
2. **Grupo 40** — `medir-aderencia.sh` no harness gerado.

**Correção registrada:** a lacuna 1 do doc de interseção estava larga demais
como escrita ("não há como medir se o harness melhora o comportamento"). É
falsa: este repo tem cinco níveis de eval (A/B em `eval/score-harness.sh`,
C em `eval/nivel-c/`, D em `evals/gradua.py`, E em `evals/triggering.json`).
A lacuna real é estreita — nenhum deles VIAJA com o harness; todos medem a
skill e rodam aqui. O Grupo 40 fecha só essa parte. **O doc ainda não foi
corrigido** para a forma estreita; está na lista de pendências.

**Achado do Grupo 40, medindo o próprio repositório:** a métrica de handoff
escrita como "SESSION_STATE no MESMO commit do checkpoint" dava 4 de 17 aqui.
Falso positivo — registrar o hash do checkpoint no arquivo obriga o commit
dele a existir antes. Aceitando também o commit seguinte: 17 de 17. O
medidor rodado contra este repo hoje dá 2 alertas de 4 (grupos concluídos
37 × 34 checkpoints, e 11 de 17 no handoff).
- Os três defeitos achados na rodada do PetClinic viraram os Grupos 34, 35 e
  36 — todos entregues. Rodar a skill num repo real pagou por si.
- Em andamento: nada — fronteira limpa.
- Não commitado: nada. O `-c` da raiz (lixo de execução manual antiga) foi
  apagado nesta sessão.
- Pendência achada e NÃO consertada (fora do escopo): o README da skill, em
  "O que você ganha concretamente", ainda anuncia "Review automatizado:
  subagente de code review" — o Grupo 28 removeu esse subagente, e
  `grep -r code-review .claude/skills/harness-creator/` não retorna nada.
- Execução em série foi autorizada pelo usuário nesta sessão: a regra "PARE
  após o grupo" do AGENTS.md ficou suspensa, com push e relatório por grupo.

## O que mudou nesta sessão (Grupos 33, 31, 25, 29, 32 e 27)
Seis grupos entregues na `main`, CI verde em todos. Testes: 406 → 566.

- **33** — `format-on-edit.sh` era inerte em Java/Maven e Java/Gradle. Eram
  QUATRO defeitos encadeados: o template anexava `"$FILE_PATH"` no fim
  (Maven lê como fase de ciclo de vida e aborta); `gerar.py` preenchia
  `<formatter_command>` só com o binário, então nenhum teste exercitava o
  comando real; cabeçalho do hook e `ecossistemas.md` divergiam; e o stub
  rigoroso revelou que o hook checava `command -v gradle` mas rodava
  `./gradlew` — no-op em todo projeto com wrapper.
- **31** — a skill passou a gerar `.harness/arch-rules.json` e
  `.claude/check-arch.sh` na cadeia da DoD. `V6` saiu de `fail` para `pass`.
- **25** — gatilhos da `description` saíram de 47% para 10% do texto; TL;DR e
  duas duplicações removidas do corpo.
- **29** — FASE 1 passou a descobrir prefixo de branch e política de entrega
  por evidência (`git branch -r`, `git log --merges`, PULL_REQUEST_TEMPLATE,
  CODEOWNERS), não mais presumidos.
- **32** — agente `propor-regra-arch`, sem ferramenta de escrita: propõe
  regra, não veredito. Score voltou a +67.
- **27** — índice nos 8 arquivos longos, `compatibility`, `allowed-tools`.

## O que mudou nesta sessão (Grupo 28)
A skill deixou de gerar o subagente `code-reviewer`, a pedido do usuário. A
ressalva foi apresentada antes e mantida: na rodada do nível C o agente
delegava por conta própria (T1 e T2), e em T1 a revisão mudou o código.

O custo está medido e registrado, não maquiado: `V6 — Regras arquiteturais`
usava `.claude/agents/code-reviewer.md` como equivalência e passou de `eq` para
`fail`. O score da geração caiu de +64~+67 para **+62** em todos os
ecossistemas. `tests/fixtures/README.md` mostra as duas colunas lado a lado e
`eval/mapa-equivalencias.md` registra regra arquitetural como SEM COBERTURA. O
scanner **não** foi remendado para preservar a nota.

Efeito colateral que os sensores pegaram: o marcador `<checks-do-repo>` ficou
documentado sem template que o preenchesse, e os dois testes de marcador
reprovaram. Removido junto.

## O que mudou nesta sessão (Grupos 21, 22, 23 e 24)
Primeira execução do **nível C**, que existia só como protocolo em prosa
desde que foi escrito. Alvo: `spring-projects/spring-petclinic` (Java 17,
Maven, Spring Boot 4.1), duas cópias — uma com o harness gerado pela skill,
outra sem —, quatro tarefas por célula, `claude -p` headless rodando de
dentro de cada repo alvo.

- Resultado: falso "pronto" em **3 de 4** sessões sem harness contra **0 de
  4** com; 0 commits e build vermelho no controle contra 4 commits e build
  verde com harness; +65% de custo (US$ 1,94 → US$ 3,20).
- Relatório em `eval/nivel-c/petclinic-2026-07-28.md`, protocolo de execução
  em `eval/nivel-c/README.md`, JSONs brutos das 8 sessões em
  `eval/nivel-c/runs/`.
- A bateria virou reexecutável: `preparar.sh` (painel + baseline), `roda.sh`
  (uma célula, com o bug plantado e a DoD medida DEPOIS da sessão),
  `tarefas.json` (T1–T4 com prompt literal) e `mede.py` (tabela comparativa).
  Comando `/exp-nivel-c` amarra os quatro. `pyproject.toml` passou a incluir
  `eval` no mypy.
- Dois defeitos do `mede.py` apareceram ao rodá-lo sobre os dados reais e
  foram corrigidos com teste: DoD não medida contava como verde (`0 de 4` lido
  como quatro sessões boas), e o commit de instalação do harness inflava a
  contagem de commits da célula `harness` em um.
- O `README.md` da raiz ganhou a seção "Isso funciona?" com o placar da
  rodada, e um teste que reprova se algum número dela não existir no
  relatório — a vitrine não anda sozinha.

## Execução real da skill no Spring PetClinic (2026-07-29)
Rodada de validação a pedido do usuário, num clone de
`spring-projects/spring-petclinic` (`f182358`, Java 17, Maven+Gradle).

- Resultado: **L0 · 39/108 -> L4 · 89/108**. Verificador 11/11, check-arch
  5/5, gate provado (exit 2 no destrutivo, 0 na DoD).
- Executada pelo próprio agente da sessão, não headless: o
  `claude -p --permission-mode bypassPermissions` foi bloqueado pelo
  classificador. **A medição é fraca** — quem executou escreveu a skill nesta
  mesma sessão, que é exatamente o viés que o `evals/README.md` alerta.
- A geração legítima ali é SEM `format-on-edit.sh`: o PetClinic usa
  `spring-javaformat`, que não escopa por arquivo.
- Três defeitos da skill apareceram. Um virou o Grupo 34 (já entregue); os
  outros dois viraram os Grupos 35 e 36.
- Alvo em `<scratchpad>/javatest/alvo` — some com a sessão; a rodada é
  reproduzível pelos passos acima.

## Integração com OpenSpec — provada de ponta a ponta (2026-07-29)
Verificada contra o CLI real: `npx @fission-ai/openspec@latest`, versão 1.7.0
([Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec)).

- A ferramenta LÊ o `openspec/config.yaml` gerado: corrompendo-o de propósito,
  o `doctor` avisa `could not parse ...; ignoring it`; com o gerado, silêncio.
- `openspec validate --all` na fixture: `1 passed, 0 failed`.
- O validador exige estrutura em INGLÊS (`## Why`, `## What Changes`,
  `MUST`/`SHALL`) mesmo com conteúdo em português — registrado na FASE 1.
- Instalação global do CLI falhou por permissão nesta máquina; tudo foi feito
  via `npx`. Se quiser o binário fixo: `npm install -g @fission-ai/openspec`.

## Pendências
- **A lacuna 2 do doc de interseção foi CANCELADA, não implementada.** Era
  erro de documentação: `propor-regra-arch` já é um controle inferencial
  gerado, e o revisor com veredito foi removido no Grupo 28 por decisão do
  usuário, com custo medido. Reclassificada como "Fora de escopo (decisão
  explícita)" no commit `2e559ed`. Resíduo real e NÃO tratado: a camada
  inferencial vale só para Claude Code, porque a doc do Devin não publica os
  paths de subagente.
- **Conferir as 6 linhas ainda marcadas "Ausente" no doc de interseção**
  contra `eval/`, `evals/` e o histórico do `TASKS.md` antes de virarem
  plano. As duas que já viraram estavam erradas pelo mesmo motivo: foram
  escritas olhando só o repo alvo e o `resources/` da skill.
- **BLOQUEADOR: o instrumento do nível E não detecta disparo nenhum.** Teste
  de sanidade: skill `deploy-producao`, description "Use SEMPRE que o usuario
  pedir para rodar o deploy de producao", query "roda o deploy de producao
  pra mim agora" → `trigger_rate 0.00`. O `run_eval.py` cria o command file e
  o `claude -p` responde; a detecção é que nunca acende, provavelmente por
  formato de evento do `stream-json` que mudou de versão. **Consequência:** o
  "subdisparo" medido no nível E pode ser artefato, e a conclusão de que ele
  "não se resolve reescrevendo a description" precisa ser reaberta. O Grupo
  26 está bloqueado por isto. Registrado em `evals/README.md`.
- O nível C ficou em **n=1 por célula**; o protocolo pede 3. Subir para 3 é o
  próximo passo antes de tratar qualquer número como estável.
- **O `AGENTS.md` deste repo está desatualizado em dois pontos, e a causa é
  uma só: ele foi escrito à mão e nunca regenerado.** Manda
  `git checkout develop` (a skill corrigiu isso no Grupo 7.1 com
  `<branch-base>` descoberto por git) e cita `/opsx:propose` sem haver
  `openspec/` (corrigido no 7.2 com `<como-propor-mudanca-de-plano>`). O
  terceiro item, o `code-reviewer` órfão, saiu no Grupo 30. A correção mais
  barata talvez não seja editar à mão de novo, e sim rodar a própria skill
  neste repositório — que é também o teste real do catálogo `atualizacao.md`,
  hoje exercitado só por fixture.
- **Descoberta da FASE 1 como script bundled — decisão de design em aberto.**
  O `skill-creator` oficial manda procurar trabalho que se repete a cada
  invocação e empacotá-lo em `scripts/`; a FASE 1 refaz a investigação de
  stack/comandos/lockfile à mão toda vez, e este repo já tem o código que faz
  isso programaticamente (`tests/gerar.py`). Não virou task: trocar raciocínio
  por script muda o que a skill é, e o ganho precisa ser medido (custo e
  variância entre execuções) antes de valer um grupo.
- Herdadas das sessões anteriores: subdisparo da skill (nível E) não se
  resolve reescrevendo a `description`; iteração 2 do nível D por fazer;
  Grupo 17 por escrever; o `AGENTS.md` deste repo ainda manda
  `git checkout develop` (só existe `main`) e citar `/opsx:propose` (não há
  `openspec/`).
- Próxima ação: `git push origin main` (não feito — ninguém pediu para
  publicar). Depois, a rodada com n=3 usando o `/exp-nivel-c`, ou o grupo de
  correção do `format-on-edit.sh` em Java.
