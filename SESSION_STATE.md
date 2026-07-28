# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `09e8e2e` (Grupo 21), branch `feature/bateria-nivel-c`,
  criada da `main` em `0cc6f7c`. Branch **não publicada**.
- Testes: 384/384 (`pytest -q`); ruff e mypy strict limpos.
- Change/plano ativo: `TASKS.md` na raiz — Grupos 21 (✅), 22 e 23 abertos.
- Em andamento: nada — Grupo 21 commitado, fronteira limpa.
- Não commitado: só o arquivo `-c` na raiz, lixo de execução manual antiga.

## O que mudou nesta sessão (Grupo 21)
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
- Herdadas das sessões anteriores: subdisparo da skill (nível E) não se
  resolve reescrevendo a `description`; iteração 2 do nível D por fazer;
  Grupo 17 por escrever; o `AGENTS.md` deste repo ainda manda
  `git checkout develop` (só existe `main`) e citar `/opsx:propose` (não há
  `openspec/`).
- Próxima ação: Grupo 22 — `eval/nivel-c/tarefas.json`, `roda.sh`,
  `preparar.sh` e `tests/test_nivel_c.py`.
