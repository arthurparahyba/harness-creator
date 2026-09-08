# memoria-do-harness

Adicionar ao harness GERADO um sistema de memória de 3 camadas, traduzindo o
modelo do BMAD para a realidade do harness-creator (vale nos 3 agentes,
portátil). Design consolidado em `docs/memoria-do-harness.md`.

Camadas: (1) ESTADO atual — SESSION_STATE, sobrescrito [reuso, encolhe];
(2) memlog — jornada append-only por funcionalidade [novo];
(3) `knowledge/` — conhecimento de componente, revisável, com prova [novo];
(4) regra executável — catraca → arch-rules [reuso, ganha o memlog de input].

Decisões travadas: memlog commitado; `knowledge/` na raiz; hierarquia de prova
(prova re-rodável > proveniência > suspeita); sem `how-it-works` (investigação
tool-agnóstica); estado no SESSION_STATE.

## Grupo 1 - Design persistido + memlog
- [x] 1.1 Persistir o design consolidado em `docs/memoria-do-harness.md`.
- [x] 1.2 Script do memlog (`resources/memlog.sh`: `init`/`append`, escrita
      atômica, write-only-cego que ecoa o contador, auto-init no append) +
      `gerar.py` o emite em `.claude/memlog.sh`, com a convenção
      `tasks/<funcionalidade>/memlog.md`.
- [x] 1.3 Protocolo: `executar-grupo` (passo 4) e `AGENTS.md` (Ferramentas)
      mandam apendar a jornada no memlog; o SESSION_STATE guarda só o estado.
- [x] 1.4 Sensores: append-only (sem subcomando de editar/apagar), append
      preserva entradas e incrementa o contador, auto-init; `gerar.py` emite
      `.claude/memlog.sh` executável e com LF.
Verificação: pytest -q && ruff check . && mypy && bash .claude/check-arch.sh

## Grupo 2 - Base knowledge/ (método, formato, fontes) + wiring (depende: G1)
- [x] 2.1 Templates: `knowledge/README.md` (como investigar + formato + lista
      de fontes) e o frontmatter de proveniência + seção Prova.
- [x] 2.2 `AGENTS.md`: seção "Conhecimento do repositório" (ponteiro) + passo 3
      checa `knowledge/` primeiro; `gerar.py` cria o scaffolding.
- [x] 2.3 Sensores: `knowledge/README` existe, o AGENTS aponta (não inline —
      `derivado_de` fica no README), formato (proveniência + Prova) documentado.
Verificação: pytest -q && ruff check . && mypy && bash .claude/check-arch.sh

## Grupo 3 - Curadoria: catraca lê o memlog + promoção (depende: G2)
- [x] 3.1 `executar-grupo`: a catraca (passo 6) passa a ler o memlog além do
      diff; passo de promoção (durável → `knowledge/`; regra → `arch-rules`).
- [x] 3.2 O espectro de durabilidade (memlog → prosa/knowledge → arch-rule)
      escrito no passo 6.
- [x] 3.3 Sensores: a curadoria lê o memlog, promove aos dois destinos, e nomeia
      a régua de durabilidade.
Verificação: pytest -q && ruff check . && mypy && bash .claude/check-arch.sh

## Grupo 4 - Validação no PetClinic (depende: G3)
- [x] 4.1 Gerar o harness novo num clone do `spring-petclinic` (818c413).
- [x] 4.2 Tarefa A: investiguei a troca de banco (Spring profiles), gerei
      `knowledge/database-profiles.md` com Prova re-rodável, registrei no memlog
      GERADO. A Prova roda.
- [x] 4.3 Tarefa B (headless `claude -p`, sessão limpa): LEU o `knowledge/`,
      RODOU a Prova, não reinvestigou, leu o memlog, e ainda achou a receita
      incompleta e propôs corrigir o próprio `knowledge/`. Relatório em
      `docs/memoria-do-harness.md`. Ressalva: sem JDK a build não roda; n=1.
Verificação: relatório em docs + artefatos presentes + Tarefa B leu o knowledge (provado no transcript)
