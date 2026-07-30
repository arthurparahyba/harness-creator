# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: Grupo 43 na `feature/janela-do-medidor`, publicado.
  Antes: `58ef747` na `main` — merge dos Grupos 40, 41 e 42, CI verde.
- Testes: 794/794 + 4 skips explícitos; ruff e mypy strict limpos; score da
  geração **+67** em todos os ecossistemas (+52 no `sem-sensores`) — o
  `tests/medicao.json` saiu byte a byte idêntico ao baseline, sem regressão.
- Change/plano ativo: `TASKS.md` na raiz — **só o Grupo 26 aberto, e
  BLOQUEADO** (ver pendências). Grupos 25, 27 a 43 concluídos.
- Em andamento: nada — fronteira limpa. A sequência de lacunas terminou:
  1 (Grupo 40), 2 (cancelada — erro de documentação), 3 (Grupo 41), 4
  (Grupo 42). As lacunas 5 e 6 o usuário decidiu não implementar por ora.
  O Grupo 43 veio depois, de um defeito achado ao validar no PetClinic.
- **`feature/janela-do-medidor` publicada e NÃO mergeada** — o merge dos
  Grupos 40-42 foi pedido explicitamente; este não. Decisão do usuário.

## O que mudou nesta sessão (Grupo 43)
Dois defeitos do `medir-aderencia.sh`, os dois achados ao rodar o harness no
clone real do spring-petclinic depois do merge — mesma fonte de valor da
rodada anterior: repo de verdade encontra o que fixture não encontra.

1. **Alarme falso em repositório preexistente.** A medida 1 perguntava "que
   fração dos commits segue o protocolo?" e aplicava isso a commits feitos
   antes de o protocolo existir. A janela do `git log` passou a começar em
   `gerado_em`, e sem commit posterior à instalação a medida se declara cega
   — como a medida 5 já fazia. Eram duas medidas do mesmo script tratando a
   mesma situação de formas opostas; era isso que tornava o caso um defeito.
2. **SIGPIPE.** A causa não era óbvia: sem trap, o shell morre calado no
   `head`; é o `trap ... EXIT` do próprio script que o faz sobreviver, e aí
   o `printf` reporta. `trap '' PIPE` PIORA — testado.

Revalidado no PetClinic: **0 de 6 medidas em alerta** num harness
recém-instalado, contra 2 de 6 antes.

**Armadilha de método:** `tests/gerar.py` grava `gerado_em` com a constante
fixa `2026-07-27`, anterior ao commit do PetClinic. Com ela, o alerta
persistia mesmo com o conserto certo, e por um momento pareceu que a correção
não funcionava. Fixture com data congelada mede outra coisa que não a
realidade — vale para o próximo grupo que mexer em janela de tempo.

## O que mudou nesta sessão (Grupo 42)
Gate deixou de ser binário. `.harness/gate-rules.json` com `permitir` /
`bloquear` / `avisar`; exceções ancoradas em `^...$`; `avisar` grava `risco`
no trace e vira a medida 6 do `medir-aderencia.sh`; regras `G01`/`G02`
executam o gate na cadeia da DoD.

**A decisão de arquitetura foi do usuário**, apresentada com o contra: mover
padrões de segurança de código para dado permite ao agente editá-los. O
contra-argumento aceito foi que ele já podia editar o script, e que a defesa
real é a detecção na DoD, não o formato do arquivo.

**Prevenção onde é portátil, detecção onde não é.** O Cursor não tem evento
de pré-edição de arquivo (só `beforeReadFile` e `afterFileEdit`,
https://cursor.com/docs/hooks.md), então bloquear a edição do gate antes que
ela ocorra violaria a regra 10. Daí a G01.

**Interações que só apareceram rodando:**
- A sonda do `verificar-harness.sh` usava `/tmp/sonda-gate`, que virou
  exceção declarada. Uma exceção nova redefine o que as sondas antigas medem.
- O primeiro ataque testado (trocar todo `bloquear` por `permitir`) falha
  sozinho: sem regra de bloqueio, o gate cai no fallback. O ataque que
  funciona é manter os bloqueios e abrir uma exceção larga por cima.

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

## Validação no spring-petclinic real (2026-07-30, após o merge)
Clone raso de `spring-projects/spring-petclinic` (`88e37c1`), harness gerado
por `tests/gerar.py`. **Ressalva de método:** é a reimplementação
determinística da FASE 2, não a skill executada por um modelo — o nível D
existe para medir essa diferença. E **não há JDK nesta máquina** (Maven sim,
runtime não), então o build do PetClinic não foi executado; o que foi
validado é a maquinaria do harness, que é toda shell.

Resultado: verificador **11/11**; check-arch **7/7** incluindo as regras
`G01`/`G02` novas; gate graduado correto contra caminhos reais (`target` e
`build` liberados, `src/main/java` e `/` bloqueados, e a exceção não abriu
buraco em `target && /`); trace classificando risco; e a senha de teste
`SPRING_DATASOURCE_PASSWORD=s3nh4-real` **não chegou ao disco**. Geração sem
`format-on-edit.sh`, que é o correto para `spring-javaformat`.

### DEFEITO ENCONTRADO E CORRIGIDO no Grupo 43 — medida 1 alarme falso
Num repositório que acabou de receber o harness, TODO o histórico é anterior
a ele e portanto não tem como conter commits `checkpoint:`. A medida 1
reporta **0% e ALERTA**, acusando o time de indisciplina por um período em
que o protocolo não existia.

É a mesma classe de problema que a medida 5 já trata bem (sem trace, ela se
declara cega em vez de alertar) e exatamente o modo de falha contra o qual o
próprio Grupo 42 argumenta: alarme falso é o que faz o sensor ser ignorado.

**Corrigido no Grupo 43**: a janela do `git log` passou a começar em
`gerado_em`, e sem commit posterior à instalação a medida se declara cega.
Revalidado no PetClinic: **0 de 6 medidas em alerta**, contra 2 de 6 antes.

Armadilha de método que quase escondeu o conserto: `tests/gerar.py` grava
`gerado_em` com a constante fixa `2026-07-27`, anterior ao commit do
PetClinic. Com ela o alerta persistia mesmo com a correção certa. Fixture com
data congelada mede outra coisa que não a realidade.

### Defeito menor, também corrigido no Grupo 43
`printf: write error: Broken pipe` no stderr ao truncar com `head`. A causa
não era óbvia: sem trap o shell morre calado; é o `trap ... EXIT` do próprio
script que o faz sobreviver ao SIGPIPE, e aí o printf reporta. E `trap '' PIPE`
PIORA — produz o erro em vez de evitá-lo.

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
