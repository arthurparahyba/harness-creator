# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `dfe0413` na `main`, publicado, CI verde — Grupo 37.
- Testes: 623/623 + 4 skips explícitos; ruff e mypy strict limpos; score da
  geração **+67** em todos os ecossistemas (+52 no `sem-sensores`).
- Change/plano ativo: `TASKS.md` na raiz — **só o Grupo 26 aberto, e
  BLOQUEADO** (ver pendências). Grupos 25, 27 a 37 concluídos e publicados.
- Os três defeitos achados na rodada do PetClinic viraram os Grupos 34, 35 e
  36 — todos entregues. Rodar a skill num repo real pagou por si.
- Em andamento: nada — fronteira limpa.
- Não commitado: só o `-c` na raiz, lixo de execução manual antiga.
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

## Pendências
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
