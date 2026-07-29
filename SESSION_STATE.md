# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `d630d45` na `main`, publicado, CI verde — Grupo 33.
- Testes: 443/443 (`pytest -q`); ruff e mypy strict limpos; `harness-score`
  em L4; score da geração +62 em todos os ecossistemas.
- Change/plano ativo: `TASKS.md` na raiz — **Grupos 25, 26, 27, 29, 31 e 32
  abertos**. Grupos 28, 30 e 33 concluídos.
- Execução em série autorizada pelo usuário: a regra "PARE após o grupo" do
  AGENTS.md está suspensa nesta sessão, com push e relatório por grupo.
- Em andamento: nada — fronteira limpa.
- Não commitado: `TASKS.md` (propostas dos Grupos 31 e 32) e este arquivo;
  mais o `-c` na raiz, lixo de execução manual antiga.

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

## Pendências
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
