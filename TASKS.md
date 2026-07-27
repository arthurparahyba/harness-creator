# TASKS.md
<!-- Fonte de trabalho FALLBACK: usada quando o repo não tem OpenSpec.
     Mesmo contrato de formato definido no AGENTS.md: grupos de 2-5
     tasks, verificação por grupo, dependências entre grupos. -->

## Grupo 1 - Versionar o harness
- [ ] 1.1 `git init` e primeiro commit `checkpoint: harness inicial`
- [ ] 1.2 Confirmar que `.gitignore` cobre os caches de ferramenta
- [ ] 1.3 Confirmar que `harness-dod.yml` roda verde no primeiro push
Verificação: `pytest -q && ruff check . && mypy && npx -y harness-score --min-level 4 --quiet`

## Grupo 2 - Cobrir a geração, não só os templates ✅
- [x] 2.1 Fixtures de 8 ecossistemas em `tests/fixtures/`
- [x] 2.2 `tests/gerar.py` reproduz a FASE 2 e `test_geracao.py` valida o gerado
- [x] 2.3 Hook de formatação e gate executados contra código real de cada stack
Verificação: `pytest -q` — 165 testes

## Grupo 3 - Ampliar a cobertura dos ecossistemas (depende: Grupo 2)
- [ ] 3.1 Fixtures de Python, Rust, Ruby e PHP (hoje só documentados)
- [ ] 3.2 Teste de que o enforcement NÃO é gerado quando a DoD é vazia
- [ ] 3.3 Fixture com CI e AGENTS.md preexistentes, para cobrir a FASE 3
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 4 - Medir os ecossistemas com o scanner ✅
<!-- Só deste repositório: a skill entregue não depende de harness-score.
     Aqui ele serve para conferir se a geração continua eficaz. -->
- [x] 4.1 `tests/medir.py` gera o harness em cada fixture e mede
- [x] 4.2 Resultado por ecossistema em `tests/fixtures/README.md`
- [x] 4.3 CI do workflow gerado passou a rodar TODOS os comandos da DoD
Verificação: `python tests/medir.py` — 8 ecossistemas, +64 a +67 pontos

## Grupo 5 - Fechar as recomendações do grupo B (depende: Grupo 3)
- [ ] 5.1 Fixture de monorepo com o script raiz já aplicado, para provar
      que a recomendação vale os 6 pontos de SNS-01 sem intervenção manual
- [ ] 5.2 Teste de que a skill NÃO gera `package.json` em repo .NET
Verificação: `pytest -q && python tests/medir.py`

<!-- Grupos 6-10: revisão completa da skill (2026-07-27). Cada um fecha um
     bloco do relatório de melhorias; a ordem importa porque o 7 renomeia
     marcadores que o 10 reutiliza. -->

## Grupo 6 - Portabilidade do gate hook ✅
- [x] 6.1 `gate-destructive.sh` extrai o comando sem depender de Python
      (fallback em shell) e só bloqueia quando há comando ilegível
- [x] 6.2 `format-on-edit.sh` com a mesma extração, aceitando também o
      formato de entrada do Cursor (`command`/`file_path` no topo do JSON)
- [x] 6.3 Testes com `PATH` sem Python nas duas direções (destrutivo → 2,
      seguro → 0) e com o JSON no formato do Cursor
Verificação: `pytest -q && ruff check . && mypy` — 199 testes

## Grupo 7 - Marcadores sem instrução e valores fixos indevidos ✅
- [x] 7.1 `<branch-base>` no AGENTS.md + item de descoberta da branch padrão
      (hoje `develop` está fixo e falha na maioria dos repos)
- [x] 7.2 `<como-propor-mudanca-de-plano>`: o AGENTS.md gerado deixa de
      mandar usar `/opsx:propose` em repo sem OpenSpec
- [x] 7.3 `<setup-steps>` documentado na FASE 2 e teste exigindo instrução
      na fase que preenche, não em qualquer reference
Verificação: `pytest -q && ruff check . && mypy` — 203 testes

## Grupo 8 - Paridade entre os três agentes-alvo ✅
- [x] 8.1 `.cursor/hooks.json` gerado (`beforeShellExecution` + `afterFileEdit`,
      `failClosed` no gate) apontando para os mesmos scripts
- [x] 8.2 Regra de conflito, item de verificação e limite do Devin
      (skills/agents sem path documentado) registrados nas references
- [x] 8.3 Teste cross-agent: todo config de hook gerado referencia script
      existente e o script executa
Verificação: `pytest -q && ruff check . && mypy` — 227 testes

## Grupo 9 - Fonte única e frontmatter ✅
- [x] 9.1 Frontmatter do SKILL.md sem `execution-mode`, `phase-count`,
      `required-reading` e `critical-constraints`; conteúdo essencial no corpo
- [x] 9.2 `arquivos-gerados.md` como única fonte dos destinos; README e
      MUDANCAS passam a linkar, com teste que impede a lista de voltar
- [x] 9.3 Manifesto `.claude/harness.json` (versão da skill, data, arquivos)
      gerado e validado na FASE 5
Verificação: `pytest -q && ruff check . && mypy` — 239 testes

## Grupo 10 - Efetividade do harness gerado ✅
- [x] 10.1 `<ferramentas-do-harness>`: o AGENTS.md aponta para `/dod`,
      `executar-grupo` e `code-reviewer` (hoje a corrente não fecha)
- [x] 10.2 FASE 5 cronometra a DoD e a FASE 4 propõe divisão quando ela é
      lenta demais para rodar a cada grupo
- [x] 10.3 `<checks-do-repo>` no `code-reviewer`: checklist derivado das
      convenções reais, universais fixos
Verificação: `pytest -q && ruff check . && mypy` — 249 testes
