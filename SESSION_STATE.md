# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `f0566bb` na `main` — merge da `feature/bateria-nivel-c`
  (Grupos 21 a 24). DoD verde depois do merge. **Nada publicado ainda**: a
  `main` local está à frente da `origin/main`.
- Testes: 406/406 (`pytest -q`); ruff e mypy strict limpos; `mede.py --autoteste` OK.
- Change/plano ativo: `TASKS.md` na raiz — **Grupos 25 e 26 abertos**,
  propostos e ainda não iniciados (Grupos 21 a 24 concluídos).
- Em andamento: nada — Grupo 24 commitado, fronteira limpa. Os Grupos 25 e 26
  são plano, nenhum arquivo da skill foi tocado.
- Não commitado: `TASKS.md` (proposta dos Grupos 25/26) e este arquivo; mais
  o `-c` na raiz, lixo de execução manual antiga.

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
- **`format-on-edit.sh` é inerte em Java/Maven e em Java/Gradle.** O template
  faz `<formatter_command> "$FILE_PATH"`, e formatter de plugin
  (`spotless:apply`, `spring-javaformat:apply`, `spotlessApply`) não aceita
  caminho de arquivo — o Maven lê como fase de ciclo de vida e aborta, e o
  `2>/dev/null || true` engole o erro. Reproduzido com Maven real. Não
  corrigido: precisa de grupo próprio, e a correção tem duas partes — o
  comando certo por ecossistema e um teste que não use stub de binário, que é
  o que deixou isso passar (`test_formatter_alcanca_o_codigo_da_stack` põe um
  `mvn` falso no PATH que aceita qualquer argumento).
- O nível C ficou em **n=1 por célula**; o protocolo pede 3. Subir para 3 é o
  próximo passo antes de tratar qualquer número como estável.
- **O `code-reviewer` é órfão NESTE repo.** `.claude/agents/code-reviewer.md`
  existe, mas o `AGENTS.md` da raiz não o cita — nenhuma regra manda revisar
  antes de commitar um grupo. É o sintoma que a própria tabela de diagnóstico
  da SKILL.md descreve (ponteiro ausente no arquivo que é lido sempre). No
  harness GERADO ele funciona: a rodada do nível C tem o agente delegando por
  conta própria em T1 e T2, e em T1 a revisão mudou o código. O defeito é só
  do `AGENTS.md` deste repo, que foi escrito à mão. Junta-se às outras duas
  incoerências dele (`git checkout develop` e `/opsx:propose`) — os três
  cabem num grupo só de correção do harness próprio.
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
