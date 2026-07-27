# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Se a sessão terminou em fronteira limpa (grupo commitado), a maioria
     dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: Grupo 16 na branch `feature/grupos-16-a-20`, criada a
  partir da `main` em `2e3be23` (merge do PR #1, que trouxe os Grupos 11-15
  e o plano dos 18-20)
- Testes: 264/264 passando (`pytest -q`, +6 no Grupo 16); ruff e mypy strict
  limpos; medição inalterada (+64 a +67 nos 8 ecossistemas)
- Change/plano ativo: TASKS.md na raiz (Grupos 1, 2, 4, 6–16 concluídos)
- Em andamento: sequência 16 → 18 → 19 → 20 a pedido do usuário, que dispensou
  explicitamente a parada entre grupos. O commit por grupo verificado continua
  valendo
- Não commitado: só o arquivo `-c` na raiz, lixo de execução manual antiga de
  teste (contém "FORMATADO" repetido, do formatador falso). Deixado fora do
  commit de propósito; remover com `rm ./-c` se confirmar que não serve.
- Efetividade: geração medida em 8 ecossistemas, +64 a +67 pontos
  (`python3 tests/medir.py`), **inalterada** pela revisão — como esperado,
  os Grupos 11–13 mexem na camada de instrução que o modelo lê, não nos
  templates que ele grava. Nenhuma regressão nas fixtures.

## O que mudou nesta sessão (análise skill-creator, v2.3 → v2.4)
Origem: análise da skill sob a ótica do skill-creator. Os três grupos atacam
a camada de instrução — o que o modelo lê para executar a skill.

- **Grupo 11**: a seção "Quando ativar esta skill" repetia a `description`
  quase palavra por palavra, e o corpo só carrega DEPOIS do trigger — nove
  linhas que não influenciavam disparo nenhum. No lugar, a fronteira que
  faltava entre fluxo completo e edição pontual: "acrescente uma linha no
  AGENTS.md" não merece seis fases e uma pausa de aprovação. A regra 5
  ("leia SOMENTE o arquivo da fase") contradizia as FASES 1, 2 e 4, que
  mandam consultar os catálogos; agora permite os que a fase citar. O
  troubleshooting caiu de 19 para 5 linhas, restrito ao que nenhuma fase
  alcança: harness já instalado falhando em silêncio.
- **Grupo 12**: `references/atualizacao.md`. O manifesto existia desde a
  v2.3 e nenhuma fase o usava para atualizar — a prova estava aqui mesmo,
  neste arquivo, na sessão anterior. A FASE 1 passa a bifurcar no passo 0 e
  a FASE 3 deixa de congelar os arquivos que a própria skill gerou.
- **Grupo 13**: a FASE 4 despejava o conteúdo integral de ~20 arquivos.
  Agora é resumo para o que é novo e diff completo para o que sobrescreve ou
  dá append em arquivo do usuário — o único caso em que aprovar errado custa
  trabalho dele.

## Próximos grupos, já planejados no TASKS.md
- **Grupo 16** — checagens insatisfazíveis e fontes divergentes: o item 8 da
  FASE 5 ("DoD IDÊNTICA em 6 arquivos") é impossível por construção; o item 5
  se auto-bloqueia pelo gate; formatter de Python tem 3 respostas na skill
  (o 15 já apontou a FASE 2 para `ecossistemas.md`, falta `01-descoberta.md`
  que ainda diz `black --quiet`); lockfile no grupo A exige rede.
- **Iteração 2 do nível D**, depois do 16: é o que prova que as correções
  pegaram. Desta vez a U10 vira sinal limpo em vez de moeda.
- **Grupos 18, 19 e 20** (escritos, não iniciados) — segunda análise
  skill-creator, agora sobre COMO a SKILL.md diz, não o que diz. O 18 fecha a
  contradição que o 11.1 deixou aberta (a fronteira de escopo contra a regra
  que manda começar pela FASE 1 sem condição) e enxuga as três cópias do
  roteiro. O 19 é o maior: a FASE 5 vira `verificar-harness.sh` em POSIX
  shell — os 19 itens são quase todos determinísticos e as assertions U1-U12
  do nível D já são os mesmos checks escritos de novo. Shell e não Python
  pelo motivo do Grupo 6: roda no repo alvo. O 20 fecha a pendência da
  `description`. Os dois primeiros dependem do 16.
- **Grupo 17 (por escrever)**, dos achados ainda sem grupo: `/dod` gerado
  mesmo com DoD vazia (contra a regra inviolável 7); ordem dos hooks do
  pre-commit não especificada mas decisiva em .NET (`dotnet test --no-build`
  exige build antes); `<setup-steps>` exige versão de runtime que a FASE 1
  não coleta.
- **Testes baratos do 3.2 e 5.2**: a iteração 1 provou o comportamento
  (`sem-sensores` não gerou enforcement, `dotnet` não gerou `package.json`,
  nas duas versões). Converter em pytest — o eval descobre, o teste segura.

## Bloqueios / pendências fora de escopo
- ~~**Descrição nunca otimizada para triggering.**~~ Deixou de ser pendência
  solta: virou o Grupo 20, com dependência declarada no Grupo 18 (que é quem
  fixa a fronteira de escopo a ser medida).
- **A `description` do frontmatter anuncia lockfile como gerado**, e o Grupo
  16 o moveu para remediação. Não foi corrigido no 18 de propósito: mexer na
  description muda o disparo, e o Grupo 20 é quem mede isso. Corrigir lá,
  antes de rodar o otimizador — senão ele otimiza um texto que já se sabe
  errado.
- **O nível D não exercita o ramo mais complexo da regra de honestidade**:
  os subagentes recebem instrução de RECUSAR remediações que instalem deps,
  então "usuário aceita sensores → DoD deixa de ser vazia → enforcement é
  gerado na mesma execução" (FASE 2) nunca é testado. Documentado em
  `evals/README.md`; fechar exige um caso com deps pré-instaladas.
- ~~**PR não aberto**~~: resolvido — PR #1 mergeado em `main` em 2026-07-27.
  A lição fica: 9 commits num PR só é caro de revisar; abrir mais cedo.
- **O harness DESTE repo está desatualizado**: o `AGENTS.md` da raiz manda
  `git checkout develop` (só existe `main`) e usar `/opsx:propose` (não há
  `openspec/`). Agora que existe modo de atualização, é o primeiro caso de
  teste real dele.
- HYG-08 (interpolação `${VAR}` em config MCP) é inatingível: o repo não
  usa MCP.
- Grupos 3 e 5 seguem abertos (fixtures Python/Rust/Ruby/PHP e recomendações
  do grupo B). O 3.2 — enforcement NÃO gerado com DoD vazia — é o mais caro
  dos dois: cobre a regra de honestidade, o comportamento mais delicado da
  skill, hoje sem sensor nenhum.

- Próxima ação: **Grupo 16** (checagens insatisfazíveis e fontes
  divergentes), que é o próximo desmarcado e destrava os Grupos 18 e 19.
  Branch nova a partir de `main`.
