# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: `94c0ddd` — "checkpoint: harness inicial", publicado em
  github.com/arthurparahyba/harness-creator (branch `main`, repo público)
- Testes: 249/249 passando (`pytest -q`); ruff e mypy strict limpos
- CI: run 30265616998 verde nos 8 steps do `harness-dod.yml`, no primeiro push
- Change/plano ativo: TASKS.md na raiz (Grupos 1, 2, 4, 6, 7, 8, 9, 10 concluídos)
- Em andamento: nada — fronteira limpa
- Não commitado: só o arquivo `-c` na raiz, lixo de execução manual antiga de
  teste (contém "FORMATADO" repetido, do formatador falso). Deixado fora do
  commit de propósito; remover com `rm ./-c` se confirmar que não serve.
- Maturidade: L4 · Self-correcting, 105/108 (`npx -y harness-score`);
  geração medida em 8 ecossistemas, +64 a +67 pontos (`python3 tests/medir.py`),
  inalterada pela revisão — como esperado, ela corrigiu defeitos, não mexeu
  na cobertura de artefatos

## O que mudou nesta sessão (revisão completa da skill, v2.2 → v2.3)
- Gate hook não depende mais de Python: extração do JSON com fallback em
  awk. Antes, em repo Go/.NET/Java sem Python, ele saía 2 para TODA entrada
  — o agente não conseguia rodar nem o `npm test` da própria DoD.
- Os hooks leem os dois formatos de entrada (`tool_input.command` e
  `command` no topo do JSON) e passou a existir `.cursor/hooks.json`: os
  três agentes-alvo (Claude Code, Devin CLI, Cursor) têm enforcement.
- Marcadores novos: `<branch-base>` (fim do `develop` fixo),
  `<como-propor-mudanca-de-plano>` (fim do `/opsx:propose` em repo sem
  OpenSpec), `<ferramentas-do-harness>`, `<checks-do-repo>`.
- Frontmatter do SKILL.md sem campos inertes; regras invioláveis no corpo.
- Manifesto `.claude/harness.json`: versão, data, arquivos gerados e itens
  recusados — base para atualizar ou remover o harness em execuções futuras.
- FASE 5 cronometra a DoD; FASE 4 propõe dividi-la quando passa de ~3 min.
- `PREENCHIVEIS` virou fonte única em `tests/gerar.py` (havia duas listas).

## Bloqueios / pendências fora de escopo
- `git init` + primeiro commit "checkpoint: harness inicial" (Grupo 1)
- **O harness DESTE repo está desatualizado em relação à skill**: o
  `AGENTS.md` da raiz ainda manda `git checkout develop` (não existe git
  aqui) e usar `/opsx:propose` (não existe `openspec/`) — exatamente os
  dois defeitos que o Grupo 7 corrigiu nos templates. Regenerar o harness
  local com a skill 2.3; não fiz porque está fora do escopo dos grupos.
- HYG-08 (interpolação `${VAR}` em config MCP) é inatingível: o repo não
  usa MCP. É o único check vermelho e vale 3 pts.
- Grupos 3 e 5 seguem abertos (fixtures Python/Rust/Ruby/PHP e recomendações
  do grupo B); os testes novos de paridade entre agentes ganham cobertura
  quando essas fixtures existirem.

- Próxima ação: `git init` e commitar tudo como checkpoint zero, ou
  regenerar o harness deste repositório com a skill 2.3.
