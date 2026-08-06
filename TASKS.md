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

## Grupo 3 - Ampliar a cobertura dos ecossistemas ✅
- [x] 3.1 Fixtures de Python, Rust, Ruby e PHP, com Stack registrada em
      `gerar.py`. As quatro linhas de `ecossistemas.md` eram promessa que nada
      exercitava; agora as parametrizações de geração rodam sobre 12 stacks
- [x] 3.2 `tests/test_honestidade.py`: `gerar.py` passa a respeitar a regra da
      FASE 2 (DoD vazia → sem pre-commit e sem CI), e o teste cobra isso mais
      a não-invenção de comando de teste. Antes não havia sensor nenhum
- [x] 3.3 Fixture `com-preexistentes` (AGENTS.md do usuário com convenções
      reais + `ci.yml`) e caso novo em `evals/evals.json`. A FASE 3 é conflito,
      não preenchimento: `gerar.py` não a implementa, então quem exercita é o
      nível D com um modelo real
Verificação: `pytest -q && ruff check . && mypy` — 364 testes

## Grupo 4 - Medir os ecossistemas com o scanner ✅
<!-- Só deste repositório: a skill entregue não depende de harness-score.
     Aqui ele serve para conferir se a geração continua eficaz. -->
- [x] 4.1 `tests/medir.py` gera o harness em cada fixture e mede
- [x] 4.2 Resultado por ecossistema em `tests/fixtures/README.md`
- [x] 4.3 CI do workflow gerado passou a rodar TODOS os comandos da DoD
Verificação: `python tests/medir.py` — 8 ecossistemas, +64 a +67 pontos

## Grupo 5 - Fechar as recomendações do grupo B ✅
- [x] 5.1 Fixture `monorepo-com-raiz`: mesma árvore do `monorepo`, só o
      `package.json` da raiz muda. O teste prova o contraste — sem o ponto de
      entrada a DoD precisa delegar (`--workspaces`), com ele usa os scripts
      reais do repo
- [x] 5.2 Teste de que a skill NÃO gera artefato estranho à stack — cobre o
      `package.json` em .NET pedido aqui, mais 7 combinações (Gemfile em PHP,
      composer.json em Ruby, requirements.txt em .NET...). Regra inviolável 8
Verificação: `pytest -q && python tests/medir.py` — 384 testes

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

## Grupo 16 - Checagens insatisfazíveis e fontes divergentes ✅
- [x] 16.1 FASE 5 item 8: "DoD IDÊNTICA em 6 arquivos" é impossível por
      construção (init.sh roda só teste, pre-commit é lista, CI é step por
      sensor). Virou tabela de equivalência: o que precisa bater é o
      conjunto de sensores e a ordem, não o texto
- [x] 16.2 FASE 5 item 5: o comando destrutivo passa a ser montado em partes
      (`RM=rm; FLAG=-rf`), que é a forma que não se auto-bloqueia. O teste
      novo varre os blocos de código de TODA reference contra o próprio gate
- [x] 16.3 Formatter de Python: `01-descoberta.md` apontava `black --quiet` e
      o comentário do `pre-commit-config.yaml` trazia black+pylint. Ambos
      passam a apontar para `ecossistemas.md`, com teste que proíbe a segunda
      resposta
- [x] 16.4 Lockfile saiu do grupo A para o B (gerar exige rede e fixa versões
      para o time), `git pull` ganhou guarda `git remote | grep -q .`, e a
      FASE 4 perdeu "pontos"/"nível que destrava"
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py`
— 264 testes (+6); medição inalterada (+64 a +67 nos 8 ecossistemas)

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

## Grupo 18 - Contradições e redundância na SKILL.md ✅
<!-- O 11.1 criou a fronteira "fluxo completo × edição pontual" mas não
     revisou as duas seções que mandam começar pela FASE 1 sem condição
     nenhuma. Para quem lê de cima para baixo, elas sobrescrevem a fronteira:
     a instrução mais específica vem primeiro e a mais genérica vem depois. -->
- [x] 18.1 "EXECUÇÃO IMEDIATA" e "Escopo" viraram uma seção só, com a triagem
      como passo 0 explícito. A ordem incondicional de começar pela FASE 1
      sumiu; a regra 1 agora manda não perguntar QUAL caminho seguir
- [x] 18.2 O roteiro de 6 fases estava em três lugares e "leia só a fase
      atual" em dois. Sobrou uma cópia de cada. A seção "Arquivos gerados"
      também duplicava a de Referências e foi absorvida por ela
- [x] 18.3 As 10 regras (eram 12) trazem cada uma o modo de falhar; as que
      duplicavam FASE 1/FASE 2 (credencial, remediação) passam a apontar para
      a fase, com teste que reprova regra curta demais para explicar o porquê
- [x] 18.4 Três exemplos pedido → ação na fronteira de escopo, incluindo o
      caso de diagnóstico, que não é nem fluxo nem edição de conteúdo
- [x] 18.5 (não planejado) A SKILL.md contradizia a FASE 5 recém-corrigida em
      dois pontos — prometia "DoD idêntica" e listava lockfile como
      enforcement gerado. Teste novo trava os dois
Verificação: `pytest -q && ruff check . && mypy` — 269 testes (+5).
SKILL.md: 169 → 181 linhas. Cresceu de propósito: saíram ~30 linhas de
repetição e entraram modos de falhar e exemplos, que é conteúdo novo.

## Grupo 19 - FASE 5 executável em vez de checklist ✅
<!-- Achado nº1 desta análise. Os 19 itens da FASE 5 são quase todos
     determinísticos, e as assertions U1-U12 do nível D são os mesmos checks
     escritos de novo. Hoje todo invocation reescreve esse shell do zero e o
     resultado depende de o modelo ter paciência com 19 itens em prosa. POSIX
     shell, não Python: o verificador roda no repo ALVO, mesmo motivo que fez
     o Grupo 6 tirar a dependência de Python do gate. Depende do 16 porque
     16.1 e 16.2 corrigem justamente dois dos itens a automatizar — script
     antes disso codifica uma regra insatisfazível e um teste que se
     auto-bloqueia. -->
- [x] 19.1 `resources/verificar-harness.sh` (POSIX shell) cobrindo os itens
      determinísticos: JSON parseia, CRLF, bit de execução, gate nos dois
      caminhos, wrapper `hooks`, caminhos do manifesto, ponte `@AGENTS.md`,
      marcadores da lista nominal, credencial literal
- [x] 19.2 FASE 5 passa a chamar o script e fica só com o que exige
      julgamento: por que cada check importa, o que fazer quando um falha, e
      os itens não automatizáveis (tempo da DoD, remediações aceitas rodando,
      AGENTS.md com escopo não duplicando o protocolo)
- [x] 19.3 `evals/gradua.py` passa a chamar o mesmo script nas assertions
      U1-U12, para skill e eval não poderem divergir
- [x] 19.4 O script entra em `references/arquivos-gerados.md` e no manifesto
      `.claude/harness.json` — é artefato entregue ao repo alvo junto com os
      hooks, não ferramenta interna da skill
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py`
— 275 testes (+6); verificador 11/11 nos 8 ecossistemas gerados e 4/11 em
diretório sem harness; medição inalterada

## Grupo 20 - Medir o disparo da skill ✅
<!-- Pendência mais antiga do SESSION_STATE: a `description` nunca foi
     otimizada para triggering, e a fronteira de escopo criada no 11.1 nunca
     foi medida. Depende do 18 porque é o 18 que fixa essa fronteira — medir
     antes é medir um comportamento que ainda vai mudar. Mede disparo, não
     execução: é trilha independente do nível D. -->
- [x] 20.1 `evals/triggering.json`: 20 queries, 10 near-miss (CI, README,
      eslint, MCP, git hook comum, explicação conceitual de WIP=1)
- [x] 20.2 `run_loop.py` rodado com opus-5, 3 iterações. **Descoberta de
      método**: rodar de dentro deste repo invalida a medição — o sub-agente
      carrega o `CLAUDE.md`/`AGENTS.md` daqui e obedece o protocolo local em
      vez de consultar a skill. Precisa de diretório neutro. Documentado em
      `evals/README.md` com as duas execuções inválidas preservadas
- [x] 20.3 Nada a aplicar: nenhuma das 3 candidatas bateu a original
      (treino 6/12, teste 4/8 em todas). A `description` só foi corrigida no
      ponto factual que o Grupo 16 tornou falso (lockfile → verificador)
- [x] 20.4 (não planejado) Diagnóstico do resultado: negativas 10/10,
      positivas ~0/10. É subdisparo real, reproduzido em 3 configurações. A
      causa provável não é redação — é o modelo achar que resolve sozinho
Verificação: `pytest -q && ruff check . && mypy` — resultado e método
registrados em `evals/README.md`

## Grupo 21 - Relatório da rodada petclinic e protocolo do nível C ✅
<!-- O nível C existia só como protocolo em prosa (`eval/protocolo-experimento.md`);
     nunca tinha sido executado. A rodada de 2026-07-28 sobre spring-petclinic
     produziu os primeiros números, e eles vivem hoje só no transcript de uma
     sessão — que é exatamente o que o harness existe para impedir. -->
- [x] 21.1 `eval/nivel-c/README.md`: o que a bateria mede, as decisões de
      método (rodar do repo alvo, `-p` headless, autorização de aprovação) e
      o que ela NÃO mede
- [x] 21.2 `eval/nivel-c/petclinic-2026-07-28.md`: relatório da rodada, com a
      tabela comparativa control × harness por métrica e por tarefa, e as
      citações literais que sustentam cada linha
- [x] 21.3 Registrar em `eval/README.md` que o nível C saiu do papel, com
      ponteiro para o relatório
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 22 - Bateria executável (depende: Grupo 21) ✅
- [x] 22.1 `eval/nivel-c/tarefas.json`: T1–T4 com prompt literal, benefício
      medido e o patch do bug plantado — hoje só existem no transcript
- [x] 22.2 `eval/nivel-c/roda.sh`: executa uma célula (condição × tarefa) com
      `claude -p` a partir do repo alvo, com `--resume` para tarefa na mesma
      sessão. O `cd` para o repo alvo é requisito de validade, não conforto
- [x] 22.3 `eval/nivel-c/preparar.sh`: clona o repo alvo, cria as cópias
      `control/` e `harness/` e roda o baseline antes de qualquer sessão
- [x] 22.4 `tests/test_nivel_c.py`: tarefas.json parseia, todo prompt não é
      vazio, scripts sem CRLF e executáveis, patch do bug aplica limpo
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 23 - Medição automática e comando (depende: Grupo 22) ✅
- [x] 23.1 `eval/nivel-c/mede.py`: lê os JSONs das células, o `git log` e o
      estado da árvore de cada repo, roda a DoD do alvo e calcula M1–M9
- [x] 23.2 Saída em tabela markdown comparativa, no formato do relatório do
      Grupo 21 — o relatório escrito à mão vira o formato de referência
- [x] 23.3 `.claude/commands/exp-nivel-c.md`: comando que dispara a bateria e
      cobra evidência de comando, como o `/dod`
- [x] 23.4 Testes de `mede.py` sobre saídas sintéticas das duas condições
Verificação: `pytest -q && ruff check . && mypy && python3 eval/nivel-c/mede.py --autoteste`

## Grupo 24 - Resultado do nível C no README da raiz ✅
<!-- O README hoje descreve o que a skill faz e como trabalhar no repo, mas
     não responde "isso funciona?". A rodada do nível C respondeu com número;
     o número está em eval/nivel-c/ e ninguém que abre o README o encontra. -->
- [x] 24.1 Seção no `README.md` com a comparação com/sem harness da rodada
      petclinic e ponteiro para o relatório e para o comando `/exp-nivel-c`
- [x] 24.2 Teste que amarra os números do README ao relatório: número que
      aparece num e não no outro é divergência, e divergência entre a vitrine
      e a evidência é pior do que não ter vitrine
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 25 - Ordem da description e custo permanente do corpo ⚠
<!-- Achado nº1 da auditoria contra as best practices oficiais. A doc do
     Claude Code manda pôr o caso de uso principal PRIMEIRO, porque o listing
     trunca pelo fim. A description gasta 323 dos seus 694 chars (47%) antes
     do primeiro gatilho, e 148 deles são a enumeração de artefatos entre
     parênteses — que não dispara nada: ninguém pede "me gera um
     SESSION_STATE.md". Sob qualquer truncamento, o que se perde primeiro é
     exatamente a lista de gatilhos. Isso é candidato a causa do subdisparo
     do nível E, junto com a hipótese do orçamento (Grupo 26). -->
- [x] 25.1 Reordenar a `description`: o que faz + gatilhos primeiro, a
      enumeração de artefatos por último, onde o corte a atinge antes de
      atingir o que faz a skill disparar
- [~] 25.2 **NÃO feito, deliberadamente.** `when_to_use` não existe no padrão
      aberto (agentskills.io define só `name`, `description`, `license`,
      `compatibility`, `metadata` e `allowed-tools`) — é extensão do Claude
      Code. Mover os gatilhos para lá os tornaria invisíveis em qualquer
      cliente que siga a spec, e este projeto tem compatibilidade com três
      agentes como requisito. O ganho já veio da reordenação (25.1); o custo
      seria portabilidade. Revertido do plano original com base na spec.
- [x] 25.3 Cortar as duas duplicações que sobreviveram ao Grupo 18: a ponte
      `CLAUDE.md` (linhas 89-90 vs Regra 9) e o Plano de Remediação (102-110
      vs Regra 6). A regra numerada é a forma acionável; a prosa paga custo
      em todo request e não instrui nada a mais. A terceira cópia da ponte,
      na tabela de diagnóstico, FICA — é outro caso de uso
- [x] 25.4 Remover o TL;DR (22-28): quando ele entra em contexto a decisão de
      usar a skill já foi tomada, e ele não muda nenhuma ação seguinte
- [!] 25.5 **BLOQUEADO: o instrumento não mede.** Teste de sanidade decisivo:
      skill `deploy-producao`, description dizendo "Use SEMPRE que o usuario
      pedir para rodar o deploy de producao", query "roda o deploy de producao
      pra mim agora" -> `trigger_rate 0.00`. Descrição não fica melhor que
      essa. A detecção de disparo do `run_eval.py` nunca acende. Registrado em
      `evals/README.md`; reabre a conclusão de que o subdisparo não é da
      description, e bloqueia o Grupo 26
Verificação: `pytest -q && ruff check . && mypy` — 498 testes (+3 sensores).
Gatilhos saíram de 47% para **10%** da description (char 323 -> 69), medido e
travado por teste. O antes/depois de triggering NÃO foi obtido: instrumento
quebrado (ver 25.5).

## Grupo 26 - Testar o orçamento do listing como causa do subdisparo
<!-- O nível E mediu subdisparo e as sessões anteriores concluíram que
     reescrever a description não resolve. A doc do Claude Code aponta uma
     causa que não é o texto: o listing de skills tem orçamento de 1% da
     janela de contexto e, ao estourar, corta descriptions começando pelas
     skills MENOS invocadas — o perfil exato desta. Os 694 chars não batem no
     cap de 1536 por entrada, mas podem ser cortados pelo orçamento global.
     Se for isso, nenhuma reescrita de description jamais resolveria. -->
- [ ] 26.1 Medir o listing real com `/doctor` e `claude --debug`, registrando
      se há aviso de overflow e se a description da skill chega inteira
- [ ] 26.2 Rerodar a bateria de triggering (`evals/triggering.json`) com
      `skillListingBudgetFraction` elevado, contra a mesma baseline
- [ ] 26.3 Registrar o resultado em `eval/` — inclusive se for negativo, que
      elimina a hipótese e é o que impede a próxima sessão de repeti-la
Verificação: `pytest -q && ruff check . && mypy` + tabela de triggering antes/depois

## Grupo 27 - Itens mecânicos de conformidade (depende: Grupo 25) ✅
<!-- Separados do 25 de propósito: são reais e baratos, mas nenhum deles muda
     a eficácia da skill. O que tem efeito é o índice — a doc manda pôr em
     arquivo de referência com mais de 100 linhas porque, em leitura parcial,
     o agente perde o resto sem saber que perdeu, e
     `02-preenchimento-templates.md` tem 285 linhas. -->
- [x] 27.1 Índice no topo dos 7 arquivos com mais de 100 linhas
      (`references/`: 01, 02, 05, `atualizacao.md`, `remediacoes.md`,
      `arquivos-gerados.md`; e `MUDANCAS-NO-REPOSITORIO.md`)
- [x] 27.2 Teste que reprova `.md` da skill com mais de 100 linhas sem índice:
      a regra só vale se um sensor a cobrar, senão o próximo nasce sem
- [x] 27.3 `compatibility` no frontmatter (três agentes-alvo, git, shell
      POSIX) e `invioláveis` → `inviolaveis` na linha 112, único acento de
      uma SKILL.md que no resto não usa nenhum
- [x] 27.4 `allowed-tools` cobrindo o que a FASE 5 executa
      (`verificar-harness.sh` e o gate hook): hoje a skill promete rodar
      "sem perguntar nada" e para num prompt de permissão que ela mesma causou
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
566 testes (+10). O sensor de índice nasceu largo demais e pegou `SKILL.md` e
`README.md`; foi escopado ao que o modelo lê SOB DEMANDA. Tirar o acento de
`invioláveis` quebrou um teste que ancorava no título — o harness pegou.

## Grupo 28 - Remover o subagente code-reviewer do produto ✅
<!-- Decisão do usuário: a skill deixa de gerar o subagente. A ressalva foi
     apresentada e mantida — na rodada do nível C o agente delegou por conta
     própria em T1 e T2, e em T1 a revisão mudou o código (o teste passou a
     afirmar o código da mensagem, não só o campo). O custo medido é
     conhecido e não deve ser escondido: `V6 — Regras arquiteturais` usa
     `first_of .claude/agents/code-reviewer.md .claude/agents` como
     equivalência e, sem nenhum dos dois, cai de `eq` para `fail`. `X4` tem
     fallback para `dod.md` e sobrevive. A remoção é do produto: o órfão em
     `.claude/agents/` DESTE repo fica onde está, é outro escopo. -->
- [x] 28.1 Apagar `resources/agents/code-reviewer.md` e a escrita
      correspondente em `tests/gerar.py`, inclusive a linha do subagente em
      `<ferramentas-do-harness>`
- [x] 28.2 Tirar os ponteiros da corrente: passo 6 do `executar-grupo`
      (renumerando 7-9), o bloco `<ferramentas-do-harness>` e a seção
      "Subagente" da FASE 2, o item 16 da FASE 1 e a regra de conflito da
      FASE 3
- [x] 28.3 Atualizar os catálogos e a documentação de vitrine:
      `arquivos-gerados.md` (linha da tabela e o limite conhecido do Devin),
      `remediacoes.md` (grupo A), `README.md` e `MUDANCAS-NO-REPOSITORIO.md`
- [x] 28.4 `eval/score-harness.sh` e `eval/mapa-equivalencias.md`: V6 perde a
      equivalência e passa a `fail`. Registrar a queda como resultado, não
      remendar o scanner para preservar o número — scanner que se ajusta para
      manter a nota deixa de medir
- [x] 28.5 Rodar `python3 tests/medir.py` e gravar o score novo em
      `tests/fixtures/README.md`, ao lado do anterior
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
404 testes (-2: os do marcador `<checks-do-repo>`); score de +64~+67 para +62,
queda de 5 pontos do V6, registrada em `tests/fixtures/README.md`

## Grupo 29 - Descobrir o fluxo de branches, não só a branch base ✅
<!-- Pedido do usuário. A FASE 1 já descobre `<branch-base>` por git CLI
     (item 18, Grupo 7.1), mas para aí: o template segue fixando o prefixo
     `feature/`, e o que fazer DEPOIS do commit — push? PR? merge direto? —
     é conselho genérico ("muitos repos têm workflow que cria o PR"), não
     fato do repositório. Num repo que usa `feat/` ou IDs de ticket, o
     AGENTS.md gerado manda o agente criar uma branch fora do padrão do time
     na primeira execução.

     Design: descobrir, não perguntar. A Regra 1 proíbe perguntar qual
     caminho seguir e o fluxo tem UMA pausa; o fluxo inferido vai para
     confirmação dentro da FASE 4, junto com o resto, em vez de virar uma
     pergunta nova no meio. -->
- [x] 29.1 Item novo na FASE 1: padrão de nome de branch por evidência —
      `git branch -r` e `git log --format=%D` (prefixos realmente usados),
      `CONTRIBUTING.md`, template de PR. Sem evidência: NÃO ENCONTRADO, e o
      default `feature/` passa a ser escolha declarada, não silenciosa
- [x] 29.2 Item novo na FASE 1: política de entrega — existe
      `.github/PULL_REQUEST_TEMPLATE*`, `CODEOWNERS`, proteção de branch
      visível, workflow que abre PR? Deriva push-e-PR × commit direto
- [x] 29.3 Marcadores `<prefixo-de-branch>` e `<politica-de-entrega>` no
      template do AGENTS.md, substituindo o `feature/` fixo e o parágrafo
      genérico sobre PR
- [x] 29.4 O fluxo inferido entra no bloco de confirmação da FASE 4, com a
      evidência que o sustenta — é onde o usuário corrige antes de gravar
- [x] 29.5 Testes: marcadores documentados na fase que os preenche, geração
      sem marcador sobrevivente, e caso de fixture com prefixo não-`feature/`
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
530 testes (+32). Score por ecossistema inalterado (+62).

## Grupo 30 - Remover o code-reviewer órfão deste repositório ✅
<!-- O Grupo 28 tirou o subagente do produto e deixou de fora, de propósito,
     o arquivo órfão deste repo. O usuário pediu a remoção também. Órfão
     porque o `AGENTS.md` da raiz nunca o citou: nenhuma regra mandava
     revisar antes de commitar, então ele não estava sendo usado aqui. -->
- [x] 30.1 Apagar `.claude/agents/code-reviewer.md` e o diretório vazio
- [x] 30.2 Confirmar que o gate `--min-level 4` do `harness-dod.yml` continua
      passando: medido antes (L4 · 105/108) e depois (L4 · 100/108). Os 5
      pontos saem de "Skills & Commands"; o nível não cai
Verificação: `pytest -q && ruff check . && mypy && npx -y harness-score --min-level 4 --quiet`

## Grupo 31 - Regras arquiteturais executáveis no harness gerado ✅
<!-- Lacuna estrutural, exposta (não criada) pelo Grupo 28. A skill nunca
     cobriu regra arquitetural com sensor: o que existia era o subagente
     revisor, que produzia veredito descartável em vez de regra durável.

     O que entra aqui é a parte DETERMINÍSTICA, de propósito. A DoD só
     significa algo porque é reprodutível — "saída de comando é evidência".
     Um LLM nessa cadeia a tornaria não-reprodutível, cara e flaky no CI, e
     reintroduziria o modo de falha que o nível C mediu (3 de 4 sessões sem
     harness declararam "pronto" falsamente). Além disso `check-arch.sh` é
     shell e roda nos três agentes-alvo; subagente só roda no Claude Code.

     O agente propositor é o Grupo 32, e é incremento — não fundação. -->
- [x] 31.1 `resources/arch-rules.json` (semente de 3-5 invariantes derivados
      da stack detectada) e `resources/check-arch.sh`, o runner portátil que
      percorre as regras e imprime WHAT/WHY/FIX nas que falham. Os três
      campos existem para o agente não "consertar" apagando a regra
- [x] 31.2 Item na FASE 1: derivar as regras candidatas de evidência real do
      repo — camada onde vive o domínio, padrão de acesso a dados, artefatos
      que quebram em silêncio. Sem evidência, não entra: mesma regra dos
      `MUST NOT`
- [x] 31.3 Engate nos três pontos de verificação que já existem:
      `<dod-command>`, `<dod-steps>` do CI e `.pre-commit-config.yaml`. Regra
      sem cabo para execução automática é documento, não sensor
- [x] 31.4 Regra de conflito na FASE 3: `arch-rules.json` existente NUNCA é
      sobrescrito — é do usuário, como o `.gitignore`. Sobrescrever apagaria
      exatamente o que o arquivo existe para acumular
- [x] 31.5 Testes: geração por ecossistema, `check-arch.sh` executado de
      verdade (falha quando a regra é violada, passa quando não), e o teste
      de não-sobrescrita da FASE 3
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
495 testes (+52). `V6 — Regras arquiteturais` saiu de `fail` para **`pass`**
no scanner do curso: cobertura melhor do que antes do Grupo 28, quando o
subagente revisor contava só como `eq`. O `harness-score` externo não pontua
arch-rules, então os +62 por ecossistema não mudaram.

## Grupo 32 - Agente que PROPÕE regra arquitetural (depende: Grupo 31) ✅
<!-- A promoção review→regra automatizada: em vez de depender de alguém
     lembrar de escrever a regra depois de achar o problema, o agente redige
     o rascunho. Diferente do subagente removido no Grupo 28 — aquele
     produzia veredito (APPROVED/CHANGES REQUESTED) que evaporava no commit;
     este produz regra, que fica.

     A trava não é opcional: agente que pode EDITAR as regras pode
     ENFRAQUECÊ-LAS. Bloqueado pela regra A07, o caminho mais curto para o
     verde é reescrever a A07 — uma catraca que gira para os dois lados não
     é catraca. Propõe, não grava.

     Só Claude Code (subagente). Por isso é incremento e não fundação. -->
- [x] 32.1 Template do agente: lê o diff do grupo, compara com as camadas
      declaradas, e devolve rascunho de regra no formato de `arch-rules.json`
      (id, description, check, expect, what, why, fix) — nunca um veredito
- [x] 32.2 A regra proposta entra pelo caminho que já existe para decisão do
      usuário: item do Plano de Remediação, com o `check` exato e o impacto,
      aceito um a um. O agente não escreve no arquivo
- [x] 32.3 Registrar na FASE 4 e em `arquivos-gerados.md` que é Claude-Code-
      only, como já se faz com `executar-grupo`
- [x] 32.4 Teste de que o agente gerado não tem permissão de escrita em
      `arch-rules.json` e de que o formato do rascunho é o do arquivo
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
556 testes (+26). Score voltou de +62 para **+67**, o mesmo de antes do
Grupo 28: `.claude/agents/` de volta recupera os 5 pontos. Mas agora a
cobertura de regra arquitetural é `pass` por sensor determinístico, não `eq`
por julgamento de LLM — mesma nota, cobertura melhor.

## Grupo 33 - format-on-edit.sh inerte em Java/Maven e Java/Gradle ✅
<!-- Pendência antiga, promovida a grupo. Investigando, são TRÊS defeitos
     encadeados, não um:

     1. ESTRUTURAL: o template faz `<formatter_command> "$FILE_PATH"`, o que
        obriga o caminho a ser o último argumento posicional. Formatter de
        plugin de build não aceita isso. Reproduzido com Maven real:
        [ERROR] Unknown lifecycle phase "src/main/java/Foo.java"
        e o `2>/dev/null || true` engole o erro — falha em silêncio.

     2. CEGUEIRA DO TESTE: `gerar.py` preenchia `<formatter_command>` com
        `stack.formatter_bin` (só o binário), gerando `mvn "$FILE_PATH"`. O
        gerador de teste divergia da skill, então nenhum teste jamais
        exercitou o comando real. O stub de binário aceitava qualquer argv e
        completava o encobrimento.

     3. FONTES DIVERGENTES: o cabeçalho do hook diz `Java: google-java-format
        -i`; `ecossistemas.md` diz `mvn spotless:apply`. A skill tem regra de
        fonte única e a violava aqui. -->
- [x] 33.1 `<formatter_command>` passa a conter `"$FILE_PATH"` na posição que
      cada ferramenta exige, e o template deixa de anexá-lo: Maven usa
      `-DspotlessFiles=`, Gradle usa `-PspotlessIdeHook=`, os demais seguem
      posicionais. Fonte única em `ecossistemas.md`; o cabeçalho do hook
      deixa de listar comando e passa a apontar para a tabela
- [x] 33.2 `gerar.py` passa a usar o comando REAL de cada ecossistema
      (campo novo em `Stack`), não o binário — é o que reaproxima o gerador
      de teste do que a skill gera
- [x] 33.3 Stub que VALIDA o argv em vez de aceitar tudo: só formata se
      encontrar o caminho alvo entre os argumentos, nas formas que as
      ferramentas reais usam. Stub permissivo foi o que deixou isso passar
- [x] 33.4 Teste que reprova `<formatter_command>` reduzido ao binário e
      teste que exige o caminho presente no comando de todo ecossistema
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
443 testes (+39). O stub rigoroso revelou um QUARTO defeito não previsto: o
hook checava `command -v gradle` mas rodava `./gradlew`, então em projeto com
wrapper (a maioria) era no-op. `formatter_bin` do Gradle passou a ser o
wrapper. Score por ecossistema inalterado.

## Grupo 34 - Semente de arch-rules tolerante a harness parcial ✅
<!-- Achado por rodar a skill num repo Java real (spring-petclinic). A regra
     A02 da semente faz `bash -n .claude/hooks/format-on-edit.sh` sem checar
     se o arquivo existe. O petclinic usa `spring-javaformat`, que NÃO escopa
     por arquivo: rodá-lo a cada edit formataria o módulo inteiro, e a própria
     skill manda não gerar enforcement que atrapalha. Sem o hook, A02 reprova.

     O efeito é o que a FASE 5 alerta: o primeiro contato do usuário com o
     registro de regras é um vermelho que ele não causou — e a reação natural
     a isso é apagar o arquivo, matando a catraca antes de ela girar. -->
- [x] 34.1 A01 e A02 passam a tolerar ausência do hook: `test ! -f X || bash -n X`
- [x] 34.2 Teste que gera um harness SEM o hook de formatação e exige que o
      check-arch continue aprovando
Verificação: `pytest -q && ruff check . && mypy`

## Grupo 35 - Verificador cega para a própria skill instalada no alvo ✅
<!-- Achado ao rodar a skill no spring-petclinic. O `verificar-harness.sh`
     varre o repositório inteiro procurando marcador sobrevivente e AGENTS.md
     sem ponte CLAUDE.md. Quando a skill está instalada como skill de projeto
     em `.claude/skills/harness-creator/` — que é um caminho de instalação
     legítimo e documentado — ele varre os próprios TEMPLATES da skill, que
     contêm marcadores por construção, e o `AGENTS.md` interno dela.

     Resultado: 4 falhas numa geração correta. O usuário lê "falha aqui é
     defeito da geração, não pendência do usuário" — que é o que o próprio
     verificador imprime — e vai caçar um defeito que não existe.

     Não é artefato do teste: instalar a skill no repo é como um time a
     compartilha via git. -->
- [x] 35.1 O verificador exclui `.claude/skills/*/resources/` e o `AGENTS.md`
      interno de skills instaladas das varreduras de marcador e de ponte
- [x] 35.2 Teste que instala a skill dentro de uma fixture gerada e exige
      11/11 — hoje daria 7/11
- [x] 35.3 A mesma exclusão vale para a FASE 5: o item que manda colar a
      saída precisa dizer o que NÃO conta
Verificação: `pytest -q && ruff check . && mypy` — 592 testes (+13). O teste
novo instala a skill inteira dentro de cada fixture gerada e exige 11/11;
sem a correção dava 7/11.

## Grupo 36 - Java/Maven não é só spotless ✅
<!-- A coluna Formatter de `ecossistemas.md` dá `mvn -q spotless:apply
     -DspotlessFiles=` como resposta única para Java/Maven. Toda a família
     Spring usa `spring-javaformat-maven-plugin`, e o PetClinic é o exemplo
     canônico. A FASE 1 manda confirmar contra o que está commitado ("o que
     está commitado ganha da tabela") e foi isso que salvou a geração — mas
     depender da regra geral para corrigir a tabela específica é frágil.

     E há um agravante que a tabela não tem como expressar hoje:
     `spring-javaformat` NÃO escopa por arquivo. Rodá-lo no hook de edição
     formataria o módulo inteiro a cada tecla — enforcement que atrapalha, que
     a skill manda não gerar. A resposta certa para esse caso não é um comando
     na tabela, é "não gere o hook; mande para o pre-commit e o CI". -->
- [x] 36.1 Linha de Java/Maven vira duas, escolhidas por evidência no
      `pom.xml`: `spotless-maven-plugin` -> comando escopado;
      `spring-javaformat-maven-plugin` -> SEM hook de edição
- [x] 36.2 Coluna ou nota nova em `ecossistemas.md` para "formatter que não
      escopa por arquivo", com a regra de não gerar o hook e mandar o item
      para o Plano de Remediação
- [x] 36.3 Item da FASE 1 passa a inspecionar QUAL plugin de formatação o
      manifesto declara, não só se existe algum
- [x] 36.4 Fixture `java-spring` (pom com spring-javaformat) e teste de que a
      geração NÃO produz `format-on-edit.sh` nela — o Grupo 34 tornou o
      check-arch tolerante a isso, falta o gerador respeitar
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
622 testes (+29) e 4 skips explícitos (os testes de forma do comando não se
aplicam onde não há comando). Fixture `java-spring` marca **+67**, o mesmo
dos outros: não gerar o hook não custa pontuação.

## Grupo 37 - README que lidera com a evidência, não com a definição ✅
<!-- O README tem 76 linhas e a prova começa na 37. Antes dela: o que o repo
     é, onde a skill vive, links para dois documentos, e como rodar os testes
     DESTE repositório. Quem abre está decidindo "isso resolve um problema
     meu?" e as primeiras 36 linhas respondem "como contribuo com este
     projeto?".

     É a mesma inversão que o Grupo 25 corrigiu na `description`: o que faz
     alguém agir fica abaixo do que a coisa é.

     A seção de evidência sobe para o topo — e continua sendo a seção que o
     teste do Grupo 24 vigia, então os números seguem com lastro obrigatório
     no relatório. -->
- [x] 37.1 `## Isso funciona?` vira a primeira seção, abrindo com o caso do
      javadoc (cena concreta) antes da tabela. O custo de +65% e o n=1 ficam
      onde estão, ditos por nós: é o que torna o resto crível
- [x] 37.2 As features viram consequências. "AGENTS.md com protocolo" não diz
      nada a quem decide; "o agente para de inventar tarefa fora do plano",
      sim. Regra: se a linha descreve um arquivo, é feature; se descreve algo
      que deixa de dar errado, é benefício
- [x] 37.3 "Trabalhar neste repositório" desce para o fim — é outra audiência
- [x] 37.4 Teste que reprova README cuja primeira seção não seja a evidência
Verificação: `pytest -q && ruff check . && mypy` — 623 testes (+1). O teste
do Grupo 24 continua exigindo lastro no relatório para cada número, e a seção
de evidência segue sob ele mesmo tendo subido para o topo.

## Grupo 38 - Ramo OpenSpec exercitado, não só especificado ✅
<!-- Achado ao testar a integração a pedido do usuário. A capacidade está
     inteira no papel — template `openspec-config.yaml`, destino no catálogo,
     item 8 da FASE 1 (inclusive o caso legado `project.md`), e a bifurcação
     do `<como-propor-mudanca-de-plano>` na FASE 2. Mas NENHUMA fixture tem
     `openspec/`, então `gerar.py` só executa a variante `TASKS.md`: o ramo
     "com OpenSpec" é prosa sem sensor. Mesma classe do `code-reviewer`
     órfão, que só apareceu quando alguém foi olhar.

     E há um buraco específico: o template usa placeholders em PROSA
     (`<stack e ferramentas...>`, `<comandos reais do repo...>`), que não
     estão em `PREENCHIVEIS`. Se o modelo não os preencher, o
     `config.yaml` gerado sai com o placeholder e nenhuma checagem acusa —
     o mesmo modo de falha do `<ferramentas-do-harness>` vazio. -->
- [x] 38.1 Fixture `node-openspec`: mesma árvore do `node` com `openspec/` e
      uma change ativa, para a bifurcação ter os dois lados exercitados
- [x] 38.2 `gerar.py` respeita a condição do catálogo: com `openspec/`, grava
      `openspec/config.yaml` e NÃO grava `TASKS.md`; sem, o inverso
- [x] 38.3 Sensor de placeholder em prosa: `config.yaml` gerado não pode
      conter `<...>` com espaços dentro (o `<objetivo>` do formato de grupo é
      texto do protocolo e fica)
- [x] 38.4 Teste da bifurcação: com OpenSpec o AGENTS.md manda usar
      `/opsx:propose`; sem, manda editar `TASKS.md`. Instrução trocada faz o
      agente chamar um comando que não existe
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
686 testes (+63: a fixture nova entra em todas as parametrizações de geração).
`node-openspec` marca **+67**, igual ao `node`.

## Grupo 39 - OpenSpec provado contra o CLI real ✅
<!-- O Grupo 38 provou que a skill gera o arquivo; faltava provar que a
     ferramenta o lê. Feito com o CLI 1.7.0
     (`npx @fission-ai/openspec@latest`). -->
- [x] 39.1 Prova de leitura: com o `config.yaml` corrompido de propósito, o
      `openspec doctor` emite `could not parse .../openspec/config.yaml;
      ignoring it`. Com o gerado, silêncio. A ferramenta lê o nosso arquivo
- [x] 39.2 A change da fixture passou a ser válida (`validate --all` →
      `1 passed, 0 failed`). Antes era inválida e seria uma armadilha: quem
      rodasse o validador acharia que a skill produz artefato quebrado
- [x] 39.3 Achado registrado na FASE 1: o validador exige **estrutura em
      inglês** — `## Why`, `## What Changes`, `MUST`/`SHALL` — mesmo com o
      conteúdo em português. `## Por que` e `DEVE` reprovam
- [x] 39.4 A skill passou a IDENTIFICAR a ferramenta (link e comando do CLI)
      na FASE 1 e no MUDANCAS-NO-REPOSITORIO: gerava config para uma
      ferramenta que nunca nomeava
Verificação: `pytest -q && ruff check . && mypy` — 686 testes; a validação
com o CLI é documentada em `tests/fixtures/README.md` e não é teste do
pytest porque depende de rede, mesma razão do `medir.py`.

## Grupo 40 - Eval de aderência dentro do harness gerado ✅
<!-- Origem: docs/intersecao-harness-engineering-x-skill.md, lacuna 1.

     A lacuna precisa ser dita com precisão, porque a versão larga ("faltam
     evals") é FALSA neste repositório: existem cinco níveis (A/B em
     `eval/score-harness.sh`, C em `eval/nivel-c/`, D em `evals/gradua.py`,
     E em `evals/triggering.json`). O que nenhum deles faz é viajar junto
     com o harness. Todos medem A SKILL, rodam AQUI, e são operados por
     quem escreve a skill.

     O repo alvo recebe `verificar-harness.sh`, que prova que o harness
     EXISTE — JSON parseia, script é executável, gate devolve exit 2. Nada
     prova que ele é OBEDECIDO. É exatamente a fronteira que o
     `eval/README.md` traça entre o nível B (capacidade) e o nível C
     (comportamento): o alvo hoje herda só o lado B.

     Consequência concreta: um time que instala o harness e seis semanas
     depois pergunta "isso está sendo seguido?" não tem instrumento. O
     `SESSION_STATE.md` não serve de resposta — é escrito pelo mesmo agente
     cuja aderência se quer medir.

     LIMITE, a declarar no próprio script e no README para não ser vendido
     como o que não é: git só enxerga o que foi commitado. Sessão que
     descarrilhou e não commitou nada é invisível. Isto mede aderência do
     histórico, não das sessões — é um sensor barato e determinístico, não
     o nível C. Quem quiser eficácia comportamental continua precisando do
     A/B. -->
- [x] 40.1 `resources/medir-aderencia.sh` — lê `git log`, a fonte de
      trabalho ativa e o `SESSION_STATE.md`, e reporta aderência ao
      protocolo do AGENTS.md. POSIX sh, sem rede e sem modelo, mesma
      restrição de portabilidade dos hooks (roda igual nos três
      agentes-alvo). Sem Python e sem jq, com teste que roda num `PATH`
      reduzido a 9 binários para provar isso
- [x] 40.2 As quatro métricas, cada uma com `what`/`why`/`fix` no formato do
      `arch-rules.json` e com uma linha declarando o que ela NÃO vê:
      proporção de `checkpoint:`; grupo concluído na fonte de trabalho sem
      checkpoint correspondente; `SESSION_STATE.md` ausente no checkpoint;
      escopo do checkpoint. **Achado ao medir o próprio repositório:** a
      terceira métrica, escrita como "no MESMO commit", dava 4 de 17 aqui —
      falso positivo, porque registrar o hash do checkpoint no arquivo
      obriga o commit dele a existir antes. Aceitando o commit seguinte,
      17 de 17. Medida com falso positivo desse tamanho é desligada na
      primeira semana e leva o resto do relatório junto
- [x] 40.3 Ligação ao harness: entrada em `arquivos-gerados.md` (com a
      tabela das três perguntas — íntegro / regras / protocolo), geração em
      `gerar.py`, ponteiro no `<ferramentas-do-harness>` da FASE 2, e item
      **1.2 da FASE 5 mandando NÃO executá-lo**: repo recém-gerado não tem
      histórico, e 0% de aderência ali acusa o usuário de algo que ele não
      teve chance de fazer. O verificador cobre o script por LF e bit de
      execução, e nunca o roda
- [x] 40.4 `tests/test_aderencia.py`, 17 testes com histórico git sintético
      construído commit a commit. O teste central é a separação
      obediente × desobediente — medidor que aprova os dois não mede nada.
      Provado por mutação: desligar o limiar de checkpoint reprova 2 testes;
      neutralizar a comparação de grupos reprova outros 2
- [x] 40.5 Regressão medida: `python3 tests/medir.py` nos 16 ecossistemas —
      `tests/medicao.json` saiu **byte a byte idêntico** ao baseline
      commitado. +67 em todos, +64 no dotnet, +52 no `sem-sensores`
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
706 testes (+20), ruff e mypy limpos, medição sem diff. Fora do escopo mas
corrigido porque quebrava a DoD: o hook de formatação deste repo colapsou o
bloco `openspec/config.yaml` do `gerar.py` em linhas de 159 chars, e o
`ruff check` reprovou — `ruff format` e `ruff check` discordando, com o hook
aplicando a metade que quebra. Resolvido parentetizando os valores.

## Grupo 41 - Trace de sessão: o que aconteceu quando nada foi commitado ✅
<!-- Origem: docs/intersecao-harness-engineering-x-skill.md, lacuna 3.

     Antes de propor, as três fontes que a Correção do doc manda conferir:
     `eval/` tem trace de sessão, mas só das 8 sessões headless do nível C,
     neste repositório, produzido pelo `claude -p --output-format json`.
     `evals/` mede a skill. Nada disso viaja com o harness. O repo alvo não
     ganha observabilidade nenhuma hoje.

     O Grupo 40 fechou metade do problema e DECLAROU a outra metade no
     próprio script: "sessao que descarrilhou e nao commitou nada e
     invisivel". Duas horas de agente rodando em circulos e desistindo nao
     deixam rastro. Este grupo cobre exatamente esse buraco.

     POR QUE OS HOOKS, E NAO OUTRO MECANISMO
     Eles já disparam a cada comando de shell e a cada edição, nos três
     agentes-alvo, e já estão registrados. É a única superfície de
     observação que a skill controla e que roda independentemente de o
     agente commitar, cooperar ou sequer chegar ao fim. Mesma epistemologia
     do git no Grupo 40 — subproduto, não auto-relato.

     O RISCO QUE DECIDE O DESENHO
     Hook de trace quebrado NAO PODE derrubar o gate. No Claude Code e no
     Devin um hook que morre some em silêncio; no Cursor, com `failClosed`,
     ele bloqueia o shell inteiro. Por isso o trace é um script SEPARADO que
     sai 0 sempre — nunca embutido no `gate-destructive.sh`, e nunca
     registrado com `failClosed`. Enforcement e observação não podem
     compartilhar destino.

     LIMITES, a declarar no script como o Grupo 40 fez:
       - Vê o que os HOOKS veem: chamadas de ferramenta. Raciocínio do
         agente, tokens e custo são invisíveis.
       - Sessão que não roda ferramenta nenhuma não deixa linha.
       - Não é APM: sem spans, sem correlação entre eventos. -->
- [x] 41.1 `resources/hooks/registrar-sessao.sh` — sai 0 sempre, registrado
      nos três agentes ao lado do gate e **nunca** com `failClosed`. Só awk,
      sem Python: os outros dois hooks tentam Python antes porque leitura
      errada ali é gate falhando aberto; aqui custa uma linha de trace
      imperfeita, e este dispara em TODA chamada de ferramenta — subir um
      interpretador por evento seria imposto permanente sobre a sessão
- [x] 41.2 Redação por **lista de permissão**, não de bloqueio: binário mais
      o segundo token só quando parece subcomando. Lista de bloqueio erra
      por omissão — basta uma forma não prevista para o segredo ir a disco.
      Coberto por 7 formas reais de passar credencial (`export TOKEN=`,
      `VAR=x cmd`, `-H "Authorization:"`, `mysql -pSENHA`, `aws configure
      set`, `user:token@github`, `postgres://user:senha@`). Teto por arquivo
      para em silêncio em vez de truncar: trace pela metade que se apresenta
      como completo engana mais que trace ausente
- [x] 41.3 `.harness/trace/` no `.gitignore`, e o teste prova a fronteira nos
      dois sentidos — `git check-ignore` tem de pegar o trace e **não** pegar
      o `arch-rules.json`. Ignorar `.harness/` inteiro mataria a catraca
      junto com o log
- [x] 41.4 Medida 5 do `medir-aderencia.sh`. Sessão com edição e sem commit
      é o alvo; sessão só de leitura não alerta — medida que grita sem motivo
      é a primeira a ser ignorada. Sem trace, ela se declara cega em vez de
      calar. **Reduzido de propósito:** contar bloqueios do gate exigiria o
      gate escrever em disco, e qualquer escrita dentro dele pode fazê-lo
      falhar aberto. Não vale a troca; registrado no cabeçalho do script
- [x] 41.5 51 testes novos (`test_trace.py` 26, `test_aderencia.py` +5,
      `test_geracao.py` +15 do gitignore parametrizado). Provados por mutação
      em quatro pontos: desligar a redação reprova 9; `set -e` no hook
      reprova 2; remover a guarda final reprova 1. Regressão: `medicao.json`
      byte a byte idêntico
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
751 testes (+45), limpos, medição sem diff, verificador 11/11 no alvo gerado.

Dois defeitos achados pelos próprios testes, ambos onde os dois lados foram
escritos juntos e concordaram por engano:
- O teste de exit 0 **não mordia**: trocar a guarda final por `|| exit 1` não
  reprovava nada, porque todo caminho interno já devolve 0. Substituído por
  um par — `PATH` vazio (comportamento) e checagem textual da guarda e da
  ausência de `set -e` (estrutura). É o único lugar onde essa proteção é
  observável, e `set -e` sozinho quebraria o contrato sem nenhum teste acusar.
- O leitor da medida 5 quebrava com espaço depois dos dois-pontos, e falhava
  do pior jeito: reportando "trace vazio" em vez de erro. Quem lesse
  concluiria que não houve sessão — o oposto da verdade.

## Grupo 42 - Gate graduado: exceção declarada e o degrau do falso verde ✅
<!-- Origem: docs/intersecao-harness-engineering-x-skill.md, lacuna 4.

     Conferido antes de propor, como a Correção do doc manda: `eval/` e
     `evals/` não têm nenhuma capacidade de permissão; o `score-harness.sh`
     não mede isso; o único grupo que tocou o gate foi o 6, de
     portabilidade. A lacuna está genuinamente aberta.

     O gate hoje é binário: casa um padrão -> exit 2; não casa -> exit 0
     silencioso. Isso erra dos dois lados.

     FALSO BLOQUEIO, com evidência desta sessão. Ao montar a demonstração do
     Grupo 41 eu rodei `rm -rf` num diretório de scratchpad e o gate
     bloqueou. A saída foi CONTORNAR — usei outro diretório. Esse é
     exatamente o caminho pelo qual um gate perde autoridade: ele erra, a
     pessoa aprende a driblar, e o drible vira hábito que também passa por
     cima dos bloqueios corretos.

     FALSO VERDE. Tudo fora da lista passa em silêncio, inclusive
     `git commit --no-verify`, que desliga o pre-commit do próprio harness.
     O agente pode enfraquecer o enforcement e nada acusa.

     POR QUE A PREVENÇÃO PARA NO SHELL
     O Cursor tem `beforeShellExecution` e `afterFileEdit`, e NÃO tem evento
     de pré-edição de arquivo (a lista publicada traz `beforeReadFile` e
     `afterFileEdit`) — https://cursor.com/docs/hooks.md. Bloquear a edição
     do próprio gate antes que ela ocorra não vale nos três agentes, e a
     regra 10 da skill não admite enforcement que só funciona em um. Por
     isso: prevenção onde é portátil (shell), DETECÇÃO onde não é (42.4).

     A TENSÃO QUE PRECISA DE DECISÃO SUA — ver 42.1. Tirar os padrões de
     dentro do script e pô-los num JSON torna o gate configurável por repo,
     que é o que resolve o falso bloqueio. Mas um registro que o agente pode
     editar é um registro que ele pode enfraquecer: bastaria acrescentar uma
     exceção para liberar o que o gate existe para barrar. O contra-argumento
     é que isso não é capacidade nova — o agente já pode editar o script
     hoje, com shell. A mitigação real não é o formato do arquivo, é a 42.4:
     a DoD passa a EXECUTAR o gate e exigir exit 2. Se você preferir manter
     os padrões no script e aceitar menos configurabilidade, é a 42.1 que
     muda. -->
- [x] 42.1 `.harness/gate-rules.json` com três níveis. `permitir` tem
      precedência sobre `bloquear`, senão a exceção nunca abriria caminho num
      padrão amplo e o registro seria decorativo. Fallback embutido quando o
      arquivo some, fica ilegível **ou perde todas as regras de bloqueio** —
      este último caso não estava previsto e é o drible mais curto que existe
- [x] 42.2 Exceções ancoradas em `^...$`, proibindo `;`, `|`, `&`, `$` e
      crase no caminho. **Isto é o grupo inteiro:** sem âncora,
      `rm -rf node_modules && rm -rf /` casa a exceção pelo começo e o gate
      libera a segunda metade. Ancorar é o que separa exceção de buraco
- [x] 42.3 Nível `avisar` grava `risco` no trace, não em stderr. A
      classificação roda sobre o comando **inteiro**, antes da redação —
      `--no-verify` é exatamente o que a redação joga fora, e classificar
      depois faria o nível inteiro ser decorativo. Uma chamada de awk, não um
      grep por regra: o hook dispara em toda chamada de ferramenta
- [x] 42.4 Regras `G01`/`G02` no `arch-rules.json`, executando o gate na
      cadeia da DoD. Vêm em par porque a G01 sozinha é satisfeita por um gate
      que bloqueia TUDO — passa na checagem e torna o agente inútil
- [x] 42.5 63 testes novos (`test_gate.py` 29, `test_trace.py` +11, mais o
      ajuste dos existentes). Provados por mutação: tirar a âncora final das
      exceções reprova 5; abrir uma exceção `^rm.*$` reprova 11
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
789 testes (+38), limpos, `medicao.json` byte a byte idêntico.

Três coisas que só apareceram ao rodar:

- **A sonda do `verificar-harness.sh` usava `/tmp/sonda-gate`** — e `/tmp/`
  virou exceção declarada nesta mudança. O gate passou a liberá-la com razão,
  e o verificador reportava "gate não bloqueia" numa geração correta. Uma
  exceção nova redefine o que as sondas antigas medem; alvo trocado para
  `/alvo-inexistente`.
- **O primeiro ataque que testei falhou sozinho.** Trocar todo `bloquear` por
  `permitir` deixa o registro sem regra de bloqueio, o gate cai no fallback e
  continua barrando. A G01 passou — corretamente, porque o gate não foi
  enfraquecido. Foi o que motivou testar o ataque que funciona: manter os
  bloqueios e abrir uma exceção larga por cima.
- **O gate deste repositório bloqueou a prova do gate.** Montar a bateria
  exigiu construir `rm -rf` em partes, como o `verificar-harness.sh` já fazia
  — o mesmo modo de falha registrado no defeito 5 do nível D.

## Grupo 43 - A janela do medidor começa quando o harness chega ✅
<!-- Achado ao rodar o harness no clone real do spring-petclinic, depois do
     merge dos Grupos 40-42. Mesma fonte de valor da rodada anterior: repo de
     verdade encontra o que fixture não encontra.

     O DEFEITO. A medida 1 pergunta "que fração dos commits segue o
     protocolo?" e aplica isso a commits feitos ANTES de o protocolo existir.
     No PetClinic — anos de histórico do time do Spring — ela reportou
     `0 de 1 (0%)` e ALERTA, sobre um commit que trata de um bug de
     PostgreSQL e nunca teve como se chamar `checkpoint: Grupo N`.

     É instalar um relógio de ponto hoje e emitir relatório dizendo que os
     funcionários não bateram ponto nos últimos três anos. O número está
     aritmeticamente certo e a conclusão é absurda.

     POR QUE ISSO NÃO É FRESCURA. A primeira coisa que alguém lê depois de
     instalar o harness passa a ser um alerta vermelho acusando o time de
     algo que ele não teve como fazer. É exatamente o argumento do Grupo 42
     sobre o falso bloqueio: alarme falso é o que faz o sensor ser ignorado,
     e sensor ignorado leva o resto do relatório junto.

     POR QUE É DEFEITO E NÃO TRADE-OFF. A medida 5 tem o mesmo problema em
     potencial e o resolve: sem trace, ela imprime "sem trace" e se declara
     cega em vez de alertar. Duas medidas do mesmo script tratando a mesma
     situação de formas opostas.

     O dado já existe: `.claude/harness.json` tem `gerado_em`. -->
- [x] 43.1 `git log --since=<gerado_em>`, com a data lida do
      `.claude/harness.json`. Uma linha resolve as medidas 1, 3 e 4 de uma
      vez, porque as três leem o mesmo log
- [x] 43.2 Sem commit desde a instalação, a medida 1 **se declara cega**, no
      mesmo formato da medida 5 — que já fazia isso desde o Grupo 41. Eram
      duas medidas do mesmo script tratando a mesma situação de formas
      opostas; era isso que tornava o caso um defeito, e não um trade-off
- [x] 43.3 Sem manifesto, sem `gerado_em` ou com data ilegível: mantém a
      janela antiga e **declara** no campo "não vê". Degradar em silêncio
      trocaria um alarme falso conhecido por um número que ninguém sabe ler
- [x] 43.4 SIGPIPE. **A causa não era óbvia:** sem trap, o shell morre calado
      no `head`; é o `trap ... EXIT` que este script instala para limpar os
      temporários que o faz SOBREVIVER, e aí o `printf` reporta o erro. E
      `trap '' PIPE` piora — testei, e ele produz o erro em vez de evitá-lo.
      Toda escrita em stdout passou por um `diz()` que sai quieto
- [x] 43.5 5 testes novos, ambos os consertos provados por mutação: zerar
      `INSTALADO_EM` reprova o teste do histórico preexistente; voltar o
      `diz()` para `printf` cru reprova o do SIGPIPE
Verificação: `pytest -q && ruff check . && mypy && python3 tests/medir.py` —
794 testes (+5), limpos, `medicao.json` sem diff. Revalidado no clone do
spring-petclinic: **0 de 6 medidas em alerta** num harness recém-instalado,
contra 2 de 6 antes, e stderr limpo ao truncar com `head`.

Um detalhe de método que quase escondeu o defeito: `tests/gerar.py` grava
`gerado_em` com a constante fixa `2026-07-27`. Com ela, o commit do PetClinic
(30/07) cai DENTRO da janela e o alerta persistia mesmo com o conserto certo.
Só ajustando o manifesto para a data real de instalação o comportamento
correto apareceu. Fixture com data congelada mede outra coisa que não a
realidade — vale para o próximo grupo que mexer em janela de tempo.

## Grupo 44 - Rodar a skill no próprio repositório ✅
<!-- Pedido do usuário, e a origem é a pendência registrada há várias
     sessões: o `AGENTS.md` daqui foi escrito à mão e nunca regenerado, e por
     isso manda `git checkout develop` (só existe `main`) e citar
     `/opsx:propose` (não há `openspec/`). Consertar à mão de novo repetiria a
     causa.

     CORREÇÃO DA PREMISSA. O SESSION_STATE dizia que isto seria "o teste real
     do catálogo `atualizacao.md`". NÃO É: `atualizacao.md` só vale quando há
     `.claude/harness.json`, e aqui não há — o harness deste repo é anterior
     ao manifesto. O que a rodada exercita de verdade é a **FASE 3**,
     resolução de conflito com repo existente, hoje coberta só pela fixture
     `com-preexistentes`. Continua valendo a pena, só não pelo motivo escrito.

     O QUE A DESCOBERTA JÁ MOSTROU. Este repositório, que constrói o gerador,
     roda um harness bem atrás do que a skill entrega: sem `.cursor/hooks.json`
     (o Cursor está sem enforcement nenhum), sem `registrar-sessao.sh`, sem
     verificador, sem medidor, sem `check-arch.sh`, sem os dois registros em
     `.harness/`, sem manifesto e sem `AGENTS.md` com escopo. O gate instalado
     é a versão de padrões embutidos, anterior ao Grupo 42.

     O RISCO QUE GOVERNA O GRUPO. O `AGENTS.md` daqui tem convenções REAIS
     que não estão em nenhum template: proibição de CRLF, transcrição verbatim
     de `resources/`, a definição de grupo como checkpoint. Regeneração que as
     perca troca um harness desatualizado por um harness errado. A FASE 3
     existe para isso, e é exatamente ela que esta rodada põe à prova. -->
- [x] 44.1 Skill rodada do início ao fim. 10 artefatos novos, 3 hooks
      substituídos, 4 arquivos do usuário alterados por merge/diff
- [x] 44.2 Convenções preservadas: os 4 `MUST NOT` (CRLF e verbatim
      inclusive), descrição do projeto, "Fontes de trabalho", "Estrutura do
      plano" e "Ao concluir cada grupo" saíram intactos
- [x] 44.3 Corrigidos POR DESCOBERTA: `main` veio de
      `git symbolic-ref refs/remotes/origin/HEAD`, o prefixo `feature/` de 23
      ocorrências no histórico, e a política de entrega (merge direto, sem
      PR) de `git log --merges` + ausência de PULL_REQUEST_TEMPLATE. Esta
      última **contradizia** o AGENTS.md, que mandava conferir se o CI abre
      PR — nenhum workflow daqui faz isso
- [x] 44.4 **Quatro defeitos**, os três primeiros corrigidos aqui porque
      deixavam a DoD vermelha:
      1. `tests/test_skill.py` rodava o gate sem fixar `HARNESS_GATE_RULES`.
         O veredito dependia de o repositório ter um registro instalado —
         17 testes reprovaram ao instalar o harness. Não estavam certos
         antes e errados depois: **nunca estiveram testando o que diziam**.
         E a expectativa em si estava velha: `rm -rf /tmp/x` virou exceção no
         Grupo 42 e ninguém atualizou, porque o fallback mascarava
      2. `A04` do `arch-rules.json` não tinha a exclusão de
         `.claude/skills/` que o `verificar-harness.sh` ganhou no Grupo 35 —
         correção aplicada a uma das duas checagens irmãs e não à outra.
         Ao consertar, apareceu um segundo defeito embutido: **campo `check`
         não pode conter barra invertida**, porque o `@tsv` do jq re-escapa
         `\` e o fallback em awk não desfaz. Regra com `\.` falha em
         silêncio, que é pior que não existir — parece que está verificando
      3. `test_geracao.py` testava só o lado que bloqueia. Ganhou o par que
         faltava: exceção declarada tem de passar, senão um gate que bloqueia
         TUDO aprova nos testes e torna o agente inútil
      4. **PENDÊNCIA, não corrigido**: o verificador é cego para o
         repositório DA skill. Acusa a fixture `com-preexistentes` (repo de
         entrada — não ter ponte é o ponto dela) e marcadores em
         `tests/gerar.py`, `TASKS.md` e `evals/`, que legitimamente falam
         sobre eles. Exige desenho, não conserto
- [x] 44.5 `check-arch` 7/7, gate provado nos dois caminhos, medidor
      funcionando. O `verificar-harness.sh` fica em 9/11 pelo defeito 4 —
      NÃO remendado para ficar verde, pela mesma razão registrada no Grupo
      28: scanner que se ajusta para preservar a nota deixa de medir
Verificação: `pytest -q && ruff check . && mypy && bash .claude/check-arch.sh`
— 843 testes (+49), ruff e mypy limpos, check-arch 7/7. O
`verificar-harness.sh` ficou FORA da linha de verificação de propósito: os
dois falsos positivos dele são o defeito 4, e pôr um vermelho conhecido na
cadeia treina o time a ignorá-la.

## Grupo 45 - Sensor para a barra invertida, e o README que mente ✅
<!-- Dois itens pequenos, e o primeiro fecha uma classe inteira.

     ITEM 1. O Grupo 44 descobriu que o campo `check` do `arch-rules.json`
     nao carrega barra invertida: o `@tsv` do jq re-escapa `\` e o fallback
     em awk nao desfaz. A regra chega ao shell quebrada e PASSA SEMPRE.

     Eu documentei isso em prosa dentro do proprio JSON. Prosa nao reprova
     nada. Quem escrever `"check": "grep -q '\.py$' src/"` — que e a coisa
     mais natural do mundo em regex — recebe uma regra que imprime `[ok]` em
     toda execucao e nunca verificou nada. Regra que sempre passa e pior que
     regra ausente: ocupa a linha e compra confianca.

     E o padrao que este repositorio ja puniu varias vezes: documentado e
     nao sensoreado. O Grupo 33 (formatter inerte em Java), o Grupo 35
     (verificador cego) e o proprio Grupo 44 (teste que media o ambiente)
     sao todos a mesma forma — a regra existia no texto e nao existia em
     comando.

     ITEM 2. O README da skill anuncia, na linha 89, "Review automatizado:
     subagente de code review antes de commitar". O Grupo 28 removeu esse
     subagente a pedido do usuario, com o custo medido e registrado. A
     vitrine vende ha varias sessoes uma funcionalidade que nao existe. Esta
     pendencia esta no SESSION_STATE desde entao. -->
- [x] 45.1 **O conserto planejado estava errado, e a 45.2 é que revelou.**
      Em vez de PROIBIR barra invertida, o `check-arch.sh` ganhou a paridade
      que o parser do gate já tinha: `jq` passou a usar `join("\t")` no lugar
      de `@tsv` (que re-escapa), e o awk passou a desfazer `\\`. A `A04`
      voltou a usar ponto literal, que é o que ela sempre quis dizer
- [x] 45.2 Verificado, não presumido — e a resposta foi **NÃO**: o
      `gate-rules.json` não sofre. O `_le_registro` do gate (Grupo 42) desfaz
      o escape; o `_campos` do check-arch (mais antigo) não desfazia.
      Assimetria entre irmãos pela terceira vez nesta sessão
- [x] 45.3 README da skill parou de anunciar o subagente de code review
      removido no Grupo 28. As duas menções restantes na skill são ao
      CONCEITO de revisão (contrastando registro vs. revisor), corretas
- [x] 45.4 Pendência do README baixada do `SESSION_STATE.md`
- [x] 45.5 **NÃO PLANEJADO — o fallback em awk do `check-arch.sh` nunca
      funcionou.** Apareceu ao escrever o teste que força o caminho sem
      `jq`: `awk: illegal statement`. A variável se chamava `exp`, que é
      função embutida do awk. Desde o Grupo 31, que criou o arquivo.
      Em máquina sem `jq` o runner imprimia `check-arch: 0 regra(s),
      nenhuma violada` e saía 0 — verde total, zero regras executadas. E o
      fallback existe exatamente para quem não tem jq: era essa pessoa, e
      só ela, que recebia o falso verde. Ninguém viu porque `jq` está
      instalado aqui e no CI — **o caminho que existe para o ambiente que
      não temos era justamente o que nunca era exercitado**
Verificacao: `pytest -q && ruff check . && mypy && bash .claude/check-arch.sh`
— 850 testes (+7), limpos, check-arch 7/7 nos DOIS caminhos do parser.
Provado por mutação: voltar o `@tsv` reprova 2, tirar o desfaz-escape do awk
reprova 2, e voltar o nome `exp` reprova 3.

## Grupo 46 - Onde a skill esta e como instala-la
<!-- Pedido do usuario: quem chega neste repositorio nao identifica de cara
     onde a skill vive, e instalar a skill no proprio projeto e o que ele
     precisa saber primeiro.

     O QUE EXISTE HOJE. Uma secao "Como usar" na linha 59 do README, com
     `cp -r .claude/skills/harness-creator <seu-repo>/.claude/skills/`. Ela
     tem tres problemas somados:

     1. O comando so funciona de DENTRO de um clone deste repo, e nada diz
        isso. Quem achou o projeto no GitHub nao tem de onde copiar.
     2. O README da SKILL nao tem secao de instalacao nenhuma -- e ele e
        justamente o que viaja junto quando alguem copia o diretorio.
     3. A instrucao termina em "peca o harness". O nivel E mediu SUBDISPARO
        real desta skill (positivas ~0/10, reproduzido em 3 configuracoes,
        Grupo 20.4). Quem seguir o README instala certo e a skill nao
        dispara. A instrucao esta incompleta contra evidencia que este
        repositorio ja tem.

     ORDEM NO README, decidida com o usuario. `## Isso funciona?` continua
     sendo a PRIMEIRA secao -- o teste do Grupo 37 (test_nivel_c.py) exige
     isso, e a razao dele continua valendo: quem abre esta decidindo se o
     projeto resolve um problema dele. A instalacao vem imediatamente
     depois, porque e a pergunta seguinte de quem se convenceu. -->
- [x] 46.1 Secao de instalacao no README da raiz, logo apos `## Isso
      funciona?`, com os tres caminhos reais e o comando exato: clone raso
      do repo publico, instalacao pessoal em `~/.claude/skills/`, e copia de
      dentro de um clone existente (o caso de hoje). Uma linha no topo diz
      onde a skill vive
- [x] 46.2 Como INVOCAR, com a razao dita: pedido explicito pelo nome da
      skill, porque o subdisparo esta medido. Instrucao que termina em "peca
      o harness" ja foi medida e nao basta
- [x] 46.3 A mesma secao no README da skill -- quem recebe so o diretorio
      copiado nao tem o README da raiz
- [x] 46.4 Fronteira declarada: a SKILL e artefato do Claude Code; o HARNESS
      GERADO e que vale nos tres agentes. Verificar como o `compatibility` do
      frontmatter esta escrito e corrigir o texto se induzir a ler que a
      skill se instala nos tres
- [x] 46.5 Sensor: teste que reprova README sem secao de instalacao e que
      exige que o caminho citado nela exista no repositorio. Renomear ou
      mover a skill passa a quebrar o build. Documentado-e-nao-sensoreado e
      o padrao que os Grupos 33, 35, 44 e 45 ja puniram aqui
Verificacao: `pytest -q && ruff check . && mypy && bash .claude/check-arch.sh`
— 859 testes (+9) e 4 skips, ruff e mypy limpos, check-arch 7/7.
Provado por mutacao: renomear a secao para `## Como usar` reprova 3, tirar
o caminho da abertura do README reprova 1, e voltar o `compatibility` para
a forma antiga reprova 1.

Duas decisoes tomadas na execucao, e nenhuma e cosmetica:

- **A secao antiga `## Como usar` foi REMOVIDA, nao mantida ao lado.** Ela
  dizia a mesma coisa pior (um `cp -r` que so funciona de dentro de um
  clone). Duas instrucoes de instalacao no mesmo arquivo divergem na
  primeira mudanca -- e assimetria entre irmaos foi o achado dos Grupos 44
  e 45.
- **O texto admite que o instrumento do subdisparo esta sob suspeita.** A
  tentacao era vender "medimos, use o nome"; o numero vem de uma bateria
  cujo detector nao acende no teste de sanidade (Grupo 25.5). O README diz
  as duas coisas: o que foi medido e que a medicao esta em aberto.

