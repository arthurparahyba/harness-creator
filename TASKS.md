# TASKS.md
<!-- Fonte de trabalho FALLBACK: usada quando o repo não tem OpenSpec.
     Mesmo contrato de formato definido no AGENTS.md: grupos de 2-5
     tasks, verificação por grupo, dependências entre grupos. -->

## Grupo 1 - Versionar o harness ✅
- [x] 1.1 `git init` e primeiro commit `checkpoint: harness inicial`
- [x] 1.2 Confirmar que `.gitignore` cobre os caches de ferramenta
- [x] 1.3 Confirmar que `harness-dod.yml` roda verde no primeiro push
Verificação: `pytest -q && ruff check . && mypy && npx -y harness-score --min-level 4 --quiet`
— commit 94c0ddd, run 30265616998 verde nos 8 steps

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

<!-- Grupos 11-13: análise da skill sob a ótica do skill-creator (2026-07-27).
     Os três atacam a camada de instrução — o que o modelo lê para executar a
     skill. O 11 vem primeiro porque enxuga o arquivo que os outros dois
     editam. Segue aberto o achado nº1 da análise: nada mede a skill sendo
     EXECUTADA por um modelo (`tests/gerar.py` é uma reimplementação da FASE 2
     em Python, não a skill) — isso é o Grupo 14, ainda por planejar. -->

## Grupo 11 - Enxugar a SKILL.md e destravar os catálogos ✅
- [x] 11.1 Remover "Quando ativar esta skill" do corpo: duplica a
      `description` e só carrega DEPOIS do trigger, então não influencia
      disparo nenhum. No lugar, a fronteira fluxo completo × edição pontual
- [x] 11.2 Regra 5 passa a permitir os catálogos que a fase citar — hoje ela
      contradiz a FASE 1, que manda consultar `ecossistemas.md` e
      `remediacoes.md`
- [x] 11.3 Troubleshooting de 19 linhas vira diagnóstico de 5, restrito ao
      que nenhuma fase alcança: harness já instalado que falha em silêncio
Verificação: `pytest -q && ruff check . && mypy` — 251 testes

## Grupo 12 - Atualizar harness existente (depende: Grupo 11) ✅
<!-- O manifesto `.claude/harness.json` existe desde o Grupo 9 e ninguém o
     usa para atualizar: o fluxo continua sendo o de 6 fases do zero. A prova
     está no SESSION_STATE deste repo — o harness local está desatualizado e
     não foi regenerado porque regenerar custa uma execução inteira. -->
- [x] 12.1 `references/atualizacao.md` (catálogo, não fase): lê o manifesto,
      classifica cada arquivo em gerado/editado/do usuário e propõe só o delta
- [x] 12.2 FASE 1 (passo 0) e FASE 3 bifurcam para o catálogo quando
      `harness.json` existe, sem criar uma segunda pausa no fluxo
- [x] 12.3 Testes de alcançabilidade do catálogo a partir das duas fases que
      o usam e de que as recusas anteriores não são reprópostas
Verificação: `pytest -q && ruff check . && mypy` — 253 testes

## Grupo 13 - FASE 4 sem despejo de conteúdo (depende: Grupo 11) ✅
- [x] 13.1 Apresentar resumo por arquivo novo; diff completo para o que
      sobrescreve ou dá append em arquivo do usuário; AGENTS.md da raiz
      integral mesmo quando novo, porque governa todas as sessões
- [x] 13.2 Teste de que a FASE 4 exige o conteúdo integral justamente nos
      casos destrutivos, que são os que o usuário precisa auditar
- [x] 13.3 Versão da skill 2.3 → 2.4 (o modo de atualização compara versões)
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py`
— 254 testes; medição +64 a +67 nos 8 ecossistemas, inalterada

## Grupo 14 - Medir a skill EXECUTADA por um modelo (depende: Grupo 13) ✅
<!-- Achado nº1 da análise: `tests/gerar.py` é uma reimplementação
     determinística da FASE 2 em Python. Os 254 testes validam essa cópia,
     não a skill. Se o modelo parafrasear um template, pular a ponte
     CLAUDE.md ou ignorar a FASE 5, nenhum teste reprova. Os 19 itens da
     FASE 5 já são a rubrica: viram assertions quase por transcrição. -->
- [x] 14.1 Fixture `sem-sensores`: repo Python sem test runner nem linter,
      com funções puras nomeáveis. É o caso mais informativo — mede a regra
      de honestidade (não gerar enforcement vazio), hoje sem sensor nenhum
- [x] 14.2 `evals/evals.json` com 3 casos (node, dotnet, sem-sensores) e
      16 assertions derivadas da FASE 5, mais `evals/gradua.py` que as checa
      programaticamente (validado: 5/16 num run parcial, discrimina certo)
- [x] 14.3 Rodar cada caso com a v2.4 e com a v2.3 (baseline em `4838f30`),
      graduar contra as assertions e registrar o resultado — 6 runs completos,
      97/100 assertions, resultados em `evals/iteracao-1/`. Delta entre versões
      = zero (o esperado: os Grupos 11-13 não mudam o artefato gerado)
- [x] 14.5 `evals/agrega.py`: consolida os gradings e destaca quais assertions
      discriminam as versões — a U10 oscila nos dois sentidos, então é
      variância entre agentes, não melhoria
- [x] 14.4 Registrar em `evals/README.md` o que este nível mede e o que ele
      NÃO mede, e a decisão de harness de aprovar a FASE 4 em nome do usuário
Verificação: `pytest -q && ruff check . && mypy` + relatório de grading
— 254 testes verdes; grading em `evals/iteracao-1/grading.json` (97/100)

## Grupo 15 - Contradições que só a execução revelou (depende: Grupo 14) ✅
<!-- Achados da iteração 1 do nível D. Seis agentes independentes, três
     ecossistemas, duas versões da skill — todos bateram nos mesmos pontos.
     Nenhum é detectável pelos 254 testes: só aparecem quando alguém tenta
     OBEDECER a instrução. Ordem: o 15.1 primeiro porque é o que faz a
     geração oscilar entre execuções. -->
- [x] 15.1 Marcador em cabeçalho de comentário: `format-on-edit.sh` traz
      `<formatter_command>`/`<file_glob>`/`<sln>` no comentário E no corpo.
      Regra 3 (VERBATIM) contra FASE 5 item 6 — decidir qual cede e aplicar
      a mesma defesa que o `ci-workflow.yml` já tem. O teste novo achou mais
      4 ocorrências além da relatada (`init.sh`, `.pre-commit-config.yaml`)
- [x] 15.2 `resources/AGENTS.md:59`: `MUST NOT: alterar migrations já
      aplicadas` vira `<restrição N>` ou some. Hoje é regra inventada
      transcrita verbatim em repo sem banco
- [x] 15.3 `# TODO: definir formatter` dentro de `if command -v ...; then`
      comenta o `then` e mata o hook com erro de sintaxe. Passa a preencher
      com `formatter-nao-definido`: o `command -v` falha e o hook vira no-op
Verificação: `pytest -q && ruff check . && mypy` — 258 testes; medição nas
8 fixtures inalterada (+64 a +67)

## Grupo 16 - Checagens insatisfazíveis e fontes divergentes (depende: Grupo 15)
- [ ] 16.1 FASE 5 item 8: "DoD IDÊNTICA em 6 arquivos" é impossível por
      construção (init.sh roda só teste, pre-commit é lista, CI é step por
      sensor). Reescrever para equivalência semântica, não igualdade literal
- [ ] 16.2 FASE 5 item 5: o comando de teste do gate contém `rm -rf` literal
      e é bloqueado pelo gate do repo onde a skill roda. Prescrever a forma
      que não se auto-bloqueia
- [ ] 16.3 Formatter de Python tem três respostas divergentes na skill
      (`black --quiet`, `ruff format`, `# TODO`). `ecossistemas.md` é a fonte
      única — as outras passam a apontar para ela, com teste
- [ ] 16.4 Lockfile sai do grupo A para o B (exige rede), `git pull` ganha
      guarda para repo sem remoto, e a FASE 4 perde o vocabulário de
      pontuação que não existe em lugar nenhum
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py`

<!-- O número 17 está reservado para os achados já registrados no
     SESSION_STATE e ainda sem grupo escrito (`/dod` gerado com DoD vazia,
     ordem dos hooks do pre-commit em .NET, `<setup-steps>` pedindo versão de
     runtime que a FASE 1 não coleta). Não é lacuna acidental. -->

<!-- Grupos 18-20: segunda análise sob a ótica do skill-creator (2026-07-27),
     agora comparando a SKILL.md contra o guia de escrita de skills. A
     primeira análise (Grupos 11-13) atacou o que o corpo dizia; esta ataca
     como ele diz. Três achados da primeira rodada NÃO voltam aqui de
     propósito: a tabela de diagnóstico já foi dimensionada no 11.3, a regra 5
     já foi destravada no 11.2, e a `description` já é o ponto mais forte do
     arquivo — só nunca foi medida, que é o Grupo 20. -->

## Grupo 18 - Contradições e redundância na SKILL.md (depende: Grupo 16)
<!-- O 11.1 criou a fronteira "fluxo completo × edição pontual" mas não
     revisou as duas seções que mandam começar pela FASE 1 sem condição
     nenhuma. Para quem lê de cima para baixo, elas sobrescrevem a fronteira:
     a instrução mais específica vem primeiro e a mais genérica vem depois. -->
- [ ] 18.1 A triagem de escopo vira passo 0 explícito do fluxo. "EXECUÇÃO
      IMEDIATA" e a regra 1 deixam de mandar começar pela FASE 1 sem condição
      e passam a mandar não perguntar QUAL DOS DOIS caminhos seguir — com
      teste que impede a contradição de voltar
- [ ] 18.2 O roteiro de 6 fases aparece três vezes (EXECUÇÃO IMEDIATA, regras
      1/2/5, Roteiro das fases) e "leia só a fase atual" duas vezes com a
      mesma justificativa: ~25 das 169 linhas repetindo dois fatos. Uma seção
      só, com os links
- [ ] 18.3 "Regras invioláveis" promete que cada regra existe porque a falha
      aconteceu, mas 1, 2, 6, 7 e 10 não dizem qual foi. Cada uma ganha o modo
      de falhar em uma linha ou sai; 6 e 8 duplicam FASE 2 e FASE 1 e passam a
      apontar para a fase, em vez de serem a segunda fonte que diverge
- [ ] 18.4 Par de exemplos pedido-a → ação na fronteira de escopo. É o ponto
      onde a skill mais erra de tamanho, e dois exemplos de duas linhas
      resolvem melhor que um critério em prosa
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 19 - FASE 5 executável em vez de checklist (depende: Grupo 16)
<!-- Achado nº1 desta análise. Os 19 itens da FASE 5 são quase todos
     determinísticos, e as assertions U1-U12 do nível D são os mesmos checks
     escritos de novo. Hoje todo invocation reescreve esse shell do zero e o
     resultado depende de o modelo ter paciência com 19 itens em prosa. POSIX
     shell, não Python: o verificador roda no repo ALVO, mesmo motivo que fez
     o Grupo 6 tirar a dependência de Python do gate. Depende do 16 porque
     16.1 e 16.2 corrigem justamente dois dos itens a automatizar — script
     antes disso codifica uma regra insatisfazível e um teste que se
     auto-bloqueia. -->
- [ ] 19.1 `resources/verificar-harness.sh` (POSIX shell) cobrindo os itens
      determinísticos: JSON parseia, CRLF, bit de execução, gate nos dois
      caminhos, wrapper `hooks`, caminhos do manifesto, ponte `@AGENTS.md`,
      marcadores da lista nominal, credencial literal
- [ ] 19.2 FASE 5 passa a chamar o script e fica só com o que exige
      julgamento: por que cada check importa, o que fazer quando um falha, e
      os itens não automatizáveis (tempo da DoD, remediações aceitas rodando,
      AGENTS.md com escopo não duplicando o protocolo)
- [ ] 19.3 `evals/gradua.py` passa a chamar o mesmo script nas assertions
      U1-U12, para skill e eval não poderem divergir
- [ ] 19.4 O script entra em `references/arquivos-gerados.md` e no manifesto
      `.claude/harness.json` — é artefato entregue ao repo alvo junto com os
      hooks, não ferramenta interna da skill
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py`

## Grupo 20 - Medir o disparo da skill (depende: Grupo 18)
<!-- Pendência mais antiga do SESSION_STATE: a `description` nunca foi
     otimizada para triggering, e a fronteira de escopo criada no 11.1 nunca
     foi medida. Depende do 18 porque é o 18 que fixa essa fronteira — medir
     antes é medir um comportamento que ainda vai mudar. Mede disparo, não
     execução: é trilha independente do nível D. -->
- [ ] 20.1 ~20 queries de triggering em `evals/`, metade near-miss — pedidos
      concretos, com caminho de arquivo e contexto, não abstrações. As
      negativas úteis são as que compartilham vocabulário com a skill e ainda
      assim pedem outra coisa (ex.: "cria um CI pra esse repo")
- [ ] 20.2 Rodar `scripts/run_loop.py` do skill-creator com o model id da
      sessão, sobre o eval set revisado
- [ ] 20.3 Aplicar `best_description` (a selecionada por score de teste, não
      de treino) e registrar score antes/depois em `evals/`
Verificação: `pytest -q && ruff check . && mypy` — score antes/depois
registrado em `evals/`
