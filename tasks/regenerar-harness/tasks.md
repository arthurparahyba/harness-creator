# regenerar-harness

Regenerar (atualizar) o harness DESTE repositório para os templates atuais da
skill, e migrar a fonte de trabalho do `TASKS.md` único para o formato de
pastas `tasks/<funcionalidade>/tasks.md`.

Contexto: o harness deste repo foi gerado no Grupo 44 (manifesto 2.5,
2026-07-31) e ficou atrás do produto — os templates mudaram nos grupos
seguintes, mas o repo nunca foi regenerado. A consequência concreta era o
`executar-grupo` instalado sem o passo da catraca: o repositório que constrói o
gerador não dogfoodava a própria catraca. Caminho de ATUALIZAÇÃO
(`references/atualizacao.md`), não geração limpa — manifesto íntegro,
ecossistema `python-pip` inalterado.

## Grupo 1 - Atualizar a maquinaria do harness (instrução + enforcement)
<!-- Primeiro a maquinaria porque o formato de pastas depende dela: init.sh que
     lê o plano ativo, AGENTS.md que descreve as duas fontes, executar-grupo
     que aponta a fonte pelo SESSION_STATE. Update atômico — não deixa harness
     meio-atualizado. -->
- [x] 1.1 Classificar cada arquivo do manifesto (disco × template de hoje):
      atualiza / preserva / editado-pelo-usuário. PRESERVA: `dod-command.md`
      (só o `-q` deste repo), o CI (gate `harness-score` é só deste repo; step
      check-arch está em `recusados`), `SESSION_STATE.md`, o AGENTS.md de
      escopo da skill.
- [x] 1.2 Instrução: AGENTS.md (Fontes de trabalho sem precedência fixa, passo
      3 "estude antes de propor", ferramenta `propor-regra-arch`),
      `executar-grupo` (passo da catraca + fontes folder-aware), init.sh (lista
      todos os planos, lê o ativo), `propor-regra-arch` (honestidade das
      ferramentas).
- [x] 1.3 Enforcement: check-arch.sh, arch-rules.json (A05 folder-aware, sem
      campos de contexto de dev), medir-aderencia.sh, pre-commit (cabeçalho
      final), gate-destructive.sh, format-on-edit.sh, editorconfig.
- [x] 1.4 FASE 5: rodar a DoD (o gate deste repo). O `verificar-harness.sh` é
      informativo e dá 9/11 aqui por design — cego para o repositório DA skill
      (acusa a fixture `com-preexistentes` e os marcadores dos templates em
      `resources/`), pendência documentada desde o Grupo 44.
Verificação: pytest -q && ruff check . && mypy && bash .claude/check-arch.sh

## Grupo 2 - Arquivar o histórico e fechar o manifesto (depende: Grupo 1)
<!-- Decisão do usuário (o atualizacao.md diz que migrar o histórico é dele):
     mover o TASKS.md legado para o formato de pastas, arquivando os 54 grupos
     verbatim numa pasta só — ordem intacta, que é o que os commits checkpoint:
     referenciam. -->
- [x] 2.1 Mover `TASKS.md` → `tasks/historico/tasks.md` verbatim (via `git mv`,
      rename rastreado); remover `TASKS.md` da raiz.
- [x] 2.2 Reescrever o manifesto (`.claude/harness.json`): data nova, lista com
      `tasks/README.md` e sem `TASKS.md` na raiz, `recusados` mantidos. Os
      arquivos de plano (`tasks/*/tasks.md`) ficam FORA — não listá-los é o que
      protege o histórico de um update futuro.
- [x] 2.3 Rodar `./init.sh` e `medir-aderencia.sh`: confirmam que enxergam as
      duas pastas (`tasks/historico`, `tasks/regenerar-harness`) e o plano
      ativo declarado no `SESSION_STATE.md`.
Verificação: pytest -q && ruff check . && mypy && bash .claude/check-arch.sh
