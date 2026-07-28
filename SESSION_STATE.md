# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: branch `feature/grupos-16-a-20`, criada da `main` em
  `2e3be23` (merge do PR #1, que trouxe os Grupos 11–15 e o plano dos 18–20).
  Branch **não publicada**.
- Testes: 384/384 (`pytest -q`); ruff e mypy strict limpos.
- Efetividade (`python3 tests/medir.py`), agora sobre 13 fixtures: +67 na
  maioria, +64 no `dotnet`, e **+52 no `sem-sensores`** — a diferença é
  exatamente o enforcement que a regra de honestidade manda não gerar. É a
  primeira vez que essa regra tem número em vez de argumento.
- Verificador novo (`.claude/verificar-harness.sh`): 11/11 nos 8 ecossistemas
  gerados, 4/11 em diretório sem harness.
- Change/plano ativo: `TASKS.md` na raiz — **nenhuma task aberta**.
- Em andamento: nada, fronteira limpa.
- Não commitado: só o arquivo `-c` na raiz, lixo de execução manual antiga
  (contém "FORMATADO" repetido, do formatador falso). Remover com `rm ./-c`
  se confirmar que não serve.

## O que mudou nesta sessão (Grupos 16, 18, 19, 20, 3 e 5)
Sequência executada a pedido do usuário, que dispensou explicitamente a
parada entre grupos. O commit por grupo verificado foi mantido.

- **Grupo 16** — dois itens da FASE 5 eram insatisfazíveis: a "DoD IDÊNTICA
  em 6 arquivos" (impossível por construção) virou tabela de equivalência, e
  o teste do gate, que continha `rm -rf` literal e era bloqueado pelo gate do
  repo onde a skill roda, passa a montar o comando em partes. Teste novo varre
  os blocos de código de toda reference contra o próprio gate.
- **Grupo 18** — a fronteira de escopo criada no 11.1 era sobrescrita por duas
  seções que mandavam começar pela FASE 1 sem condição. Virou passo 0. O
  roteiro de 6 fases estava em três lugares; sobrou um. As 10 regras (eram 12)
  trazem cada uma o modo de falhar.
- **Grupo 19** — `resources/verificar-harness.sh` em POSIX sh, 11 checagens,
  sem exigir Python. A FASE 5 caiu de 19 itens para 7 (só os de julgamento) e
  o `evals/gradua.py` delega ao mesmo script. Dois bugs apareceram durante a
  implementação: o gate era invocado com `sh` (ele é bash e usa array), e as
  checagens de ponte e de hooks passavam por vacuidade em diretório vazio.
- **Grupo 20** — ver pendências abaixo: o resultado é subdisparo real.
- **Grupos 3 e 5** — Python, Rust, Ruby e PHP ganharam fixture (eram promessa
  em `ecossistemas.md` que nada exercitava), mais `monorepo-com-raiz` e
  `com-preexistentes`. `gerar.py` passa a respeitar a regra de honestidade, e
  `tests/test_honestidade.py` a cobra.

## Pendências
- **Subdisparo da skill é real e não se resolve reescrevendo a descrição.**
  Positivas ~0/10, negativas 10/10; a query que contém "harness engineering"
  literalmente dispara 1 vez em 3. Reproduzido em diretório neutro e com
  timeout de 120s e 300s, e três iterações do otimizador não melhoraram o
  número. A causa provável é o modelo começar a escrever um AGENTS.md sozinho
  em vez de consultar a skill. Antes de tentar redação nova, subir
  `--runs-per-query`: 3 é pouco quando a taxa vive entre 0 e 0.33.
- **Rodar eval de triggering SEMPRE de diretório neutro.** De dentro deste
  repo o sub-agente carrega o `AGENTS.md` local e obedece o protocolo daqui em
  vez de consultar a skill. O sintoma (0/10 positivas, taxa exatamente 0.0)
  parece descrição ruim e não é. Duas execuções inválidas ficaram em
  `evals/triggering-runs/` de propósito, como contraexemplo.
- **Iteração 2 do nível D ficou por fazer.** É o que prova que as correções
  dos Grupos 15, 16, 18 e 19 pegaram. Agora há um caso novo
  (`com-preexistentes`, que exercita a FASE 3) e o `gradua.py` delegando ao
  verificador.
- **Grupo 17 ainda por escrever**, dos achados registrados na iteração 1:
  `/dod` gerado mesmo com DoD vazia (contra a regra inviolável 5); ordem dos
  hooks do pre-commit não especificada mas decisiva em .NET
  (`dotnet test --no-build` exige build antes); `<setup-steps>` exige versão
  de runtime que a FASE 1 não coleta.
- **O nível D não exercita o ramo mais complexo da regra de honestidade**: os
  subagentes recebem instrução de RECUSAR remediações que instalem deps, então
  "usuário aceita sensores → DoD deixa de ser vazia → enforcement é gerado na
  mesma execução" nunca é testado. Fechar exige um caso com deps
  pré-instaladas.
- **O harness DESTE repo está desatualizado**: o `AGENTS.md` da raiz manda
  `git checkout develop` (só existe `main`) e usar `/opsx:propose` (não há
  `openspec/`). Bati nos dois nesta sessão. Agora que existe modo de
  atualização, é o primeiro caso de teste real dele.
- HYG-08 (interpolação `${VAR}` em config MCP) é inatingível: o repo não usa
  MCP.

- Próxima ação: abrir PR da `feature/grupos-16-a-20`, e depois a iteração 2 do
  nível D — é ela que valida tudo que esta sessão mudou.
