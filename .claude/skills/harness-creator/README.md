# Harness Creator

Skill que gera o harness completo de um repositório para agentes de IA de
código — combinando descoberta automática de stack com templates de
protocolo fixo. **Funciona com qualquer linguagem**: Python, JavaScript/
TypeScript, .NET/C#, Java, Go, Rust, Ruby, PHP e outras.

> **Quer só saber o que ela mexe no seu repositório?**
> [MUDANCAS-NO-REPOSITORIO.md](MUDANCAS-NO-REPOSITORIO.md) lista, de forma
> objetiva, tudo que ela cria, modifica, propõe e nunca faz.

---

## Conteúdo

**Por que usar**
- [Para desenvolvedores: o que muda no seu dia a dia com IA](#para-desenvolvedores-o-que-muda-no-seu-dia-a-dia-com-ia)

**Como funciona**
- [Como a skill funciona](#como-a-skill-funciona) — as duas camadas e as 6 fases
- [O fluxo inteiro em três exemplos reais](#o-fluxo-inteiro-em-três-exemplos-reais) — Python, Java/Maven e React
- [Etapa 0 — Ativação e triagem](#etapa-0--ativação-e-triagem)
- [FASE 1 — Descoberta](#fase-1--descoberta-somente-leitura-nenhuma-escrita)
- [FASE 2 — Preenchimento VERBATIM](#fase-2--preenchimento-verbatim-dos-templates)
- [FASE 3 — Resolução de conflitos](#fase-3--resolução-de-conflitos-com-o-repositório-existente)
- [FASE 4 — Saída e aprovação ⏸️](#fase-4--saída-e-aprovação-️-a-única-pausa-do-fluxo)
- [FASE 5 — Verificação pós-geração](#fase-5--verificação-pós-geração)
- [FASE 6 — Fechamento do gate de CI](#fase-6--fechamento-do-gate-de-ci)
- [Catálogos consultados sob demanda](#catálogos-consultados-sob-demanda)
- [As 10 regras invioláveis](#as-10-regras-invioláveis)

**Referência**
- [Ecossistemas suportados](#ecossistemas-suportados)
- [Benefícios por conceito de Harness Engineering](#benefícios-por-conceito-de-harness-engineering)

---

## Para desenvolvedores: o que muda no seu dia a dia com IA

Se você nunca ouviu falar de harness engineering, aqui está o que essa
skill faz pelo seu repositório — em termos práticos.

### Antes (sem harness)

Você abre o Claude Code, Cursor ou Devin no seu repo e pede: "implementa
login com JWT". O agente:

1. Explora o repo por 10 minutos tentando entender a stack
2. Cria arquivos em lugares errados (não sabe sua convenção de pastas)
3. Não roda testes (não sabe o comando)
4. Faz `git push --force` sem pedir (ninguém bloqueou)
5. Commita código sem formatar — diff cheio de ruído
6. Você descobre 3 dias depois que quebrou algo que o agente não verificou
7. Na próxima sessão, o agente não lembra de nada e recomeça do zero

### Depois (com harness gerado por esta skill)

Você abre o agente no mesmo repo. Ele roda `./init.sh` automaticamente
e em 3 minutos sabe: stack, comandos de teste, lint, build, estado atual
do trabalho. Quando você pede "implementa login com JWT":

1. O agente lê SESSION_STATE.md e vê que há um grupo em andamento —
   termina antes de começar algo novo
2. Confirma que o pedido está coberto pelo plano de trabalho (não inventa
   tarefas fora do escopo)
3. Implementa em **grupos de 2-5 tasks**, verificando cada grupo antes de
   avançar (WIP=1 — nada fica meio-feito)
4. Toda vez que edita um arquivo, o hook de auto-formatação roda
   automaticamente — diff limpo
5. Se tenta rodar `rm -rf` ou `git push --force`, o gate hook **bloqueia**
   antes de executar
6. Antes de commitar, o pre-commit roda lint e build (segundos)
7. Para concluir, roda a Definition of Done — os comandos reais do seu
   repo (ex: `dotnet test`, `pytest`, `mvn verify`, `npm test`) — e só
   commita se tudo passar
8. Atualiza SESSION_STATE.md com o hash do commit, testes (X/Y), próxima
   ação
9. PARE e diz "Grupo concluído. Contexto pode ser reiniciado."

### O que você ganha concretamente

- **Menos tempo de setup**: o agente começa trabalhando, não explorando
- **Zero operações destrutivas**: hooks bloqueiam antes de executar
- **Diff limpo**: formatação automática a cada edit
- **Evidência de conclusão**: "passou" = comando passou, não "parece funcionar"
- **Continuidade entre sessões**: estado persistido, não recomeça do zero
- **Escopo controlado**: agente não avança sem verificar, não inventa tarefas
- **Sensores rodando**: testes, lint e build como gate antes de commitar
- **Review automatizado**: subagente de code review antes de commitar
- **Multi-linguagem**: mesma skill funciona em Python, .NET, Java, JS/TS,
  Go, Rust, Ruby e PHP — sem adaptação manual

### Como ela prova que funcionou

Nada é declarado pronto sem execução. Depois de gravar, a skill valida cada
artefato e **executa o gate hook de verdade** — ele precisa devolver exit 2
para um `rm -rf` simulado e exit 0 para um comando seguro. Se qualquer
verificação falhar, isso é defeito da geração, não pendência sua.

O detalhe de cada checagem está na [FASE 5](#fase-5--verificação-pós-geração).

### Em uma frase

**A skill transforma um repositório "aberto" num repositório "harnessado" —
onde o agente de IA trabalha dentro de regras, sensores e fronteiras que
garantem qualidade, segurança e continuidade, em vez de operar livremente
e causar danos.**

---

## Como a skill funciona

**O que ela faz, em uma frase:** lê um repositório qualquer, descobre como
aquele projeto se testa e se organiza, e escreve nele um conjunto de arquivos
que fazem um agente de IA trabalhar com disciplina — seguindo um plano,
verificando o próprio trabalho e deixando o estado registrado para a próxima
sessão.

Ela gera **duas camadas**, e a diferença entre elas explica quase todas as
decisões do fluxo:

| Camada | O que é | Exemplo | O que acontece sem ela |
|---|---|---|---|
| **Instrução** | Texto que o agente lê | `AGENTS.md`, `SESSION_STATE.md`, `init.sh` | O agente não sabe as regras do projeto |
| **Enforcement** | Código que roda e bloqueia | hooks, pre-commit, `/dod`, CI, `check-arch.sh` | O agente sabe as regras e pode ignorá-las — "concluído" volta a ser opinião dele |

O fluxo tem **6 fases** e **uma única pausa** (a FASE 4, antes de gravar
qualquer arquivo). Antes e depois dessa pausa, a skill executa tudo sozinha.

| # | Etapa | Arquivo que direciona | Grava em disco? | Em uma frase |
|---|---|---|---|---|
| 0 | Ativação e triagem | [SKILL.md](SKILL.md) | não | "Esse pedido merece o fluxo inteiro ou é uma edição de uma linha?" |
| 1 | FASE 1 — Descoberta | [references/01-descoberta.md](references/01-descoberta.md) | não | "Como este projeto funciona de verdade?" |
| 2 | FASE 2 — Preenchimento | [references/02-preenchimento-templates.md](references/02-preenchimento-templates.md) | não, só em memória | "Copiar os templates trocando só os `<marcadores>`" |
| 3 | FASE 3 — Conflitos | [references/03-resolucao-conflitos.md](references/03-resolucao-conflitos.md) | não | "O que já existe no repo e não pode ser destruído?" |
| 4 | FASE 4 — Aprovação ⏸️ | [references/04-saida-aprovacao.md](references/04-saida-aprovacao.md) | **sim, após o "ok"** | "Isto é o que vou escrever. Posso?" |
| 5 | FASE 5 — Verificação | [references/05-verificacao-pos-geracao.md](references/05-verificacao-pos-geracao.md) | não, só executa | "Provar que o que gravei realmente funciona" |
| 6 | FASE 6 — Gate de CI | [references/06-lembrete-ci.md](references/06-lembrete-ci.md) | não | "Fechar o único enforcement que ninguém consegue pular" |

**Regra de carregamento:** a skill lê **apenas o arquivo da fase que está
executando**, um por vez. Carregar os seis de uma vez gastaria justamente o
contexto que a divisão em seis arquivos existe para poupar.

Nas seções seguintes, os caminhos da coluna "Arquivo que direciona" são
relativos a este diretório, e "repo alvo" é o repositório que está recebendo
o harness. `<assim>` é um marcador de template — o único trecho que a skill
pode alterar.

---

## O fluxo inteiro em três exemplos reais

Antes do detalhamento fase a fase, o caminho completo em três repositórios
diferentes. Eles foram escolhidos porque **cada um exercita ramificações
distintas** do fluxo — o caminho feliz, o repo que já tem CI e o monorepo com
config prévia. Ao final há uma tabela comparando qual decisão cada um dispara.

### Caso 1 — Python, repo limpo (o caminho mais direto)

`pyproject.toml`, sem CI, sem hooks e sem harness anterior:

```
Usuário:  "prepara esse repo aqui pra eu usar com agente"

FASE 1    Lê pyproject.toml         → ecossistema Python
          Lê [tool.pytest], [tool.ruff] → pytest, ruff check ., mypy
          Não acha .github/workflows/   → NÃO ENCONTRADO (vira remediação)
          git symbolic-ref ...          → branch base = main
          git log --format=%D --all     → 12 de 15 branches usam feat/
          Não acha CLAUDE.md            → a ponte precisa ser gerada
          → Relatório de Descoberta + Plano de Remediação

FASE 2    DoD = "pytest && ruff check . && mypy"
          Preenche <branch-base>=main, <prefixo-de-branch>=feat/
          <formatter_command> = ruff format "$FILE_PATH"
          <file_glob>          = *.py
          Monta ~20 arquivos EM MEMÓRIA — nada gravado ainda

FASE 3    Acha um AGENTS.md antigo → preserva o descritivo, o protocolo
          do template prevalece nas seções sobrepostas

FASE 4  ⏸️ Mostra relatório + arquivos + plano e ESPERA
          Usuário: "ok, mas recusa o lockfile"
          → grava tudo, chmod +x nos scripts

FASE 5    sh .claude/verificar-harness.sh   → 11 checagens, cola a saída
          bash .claude/check-arch.sh        → nenhuma violada
          time pytest && ruff check . && mypy → 47s (abaixo dos 3 min, ok)

FASE 6    Repo não tinha CI → confirma que ubuntu-latest serve
          Avisa: hook apagado não quebra build nenhum
          ✅ Harness gerado
```

### Caso 2 — Java / Maven, estilo Spring (CI existente e formatter que não escopa)

`pom.xml` com `spring-javaformat-maven-plugin`, pipeline já configurado em `.github/`,, `CODEOWNERS` na raiz. Três coisas mudam de rota:

```
Usuário:  "configura o harness aqui"

FASE 1    Lê pom.xml                    → Java/Maven, NÃO só "Java"
          Acha spring-javaformat-...    → formata o MÓDULO INTEIRO
                                        → registra "SEM HOOK DE FORMATAÇÃO"
          Lê .github/workflows/ci.yml   → mvn verify já roda lá
          Lê runs-on: [self-hosted]     → NÃO é ubuntu-latest
          Acha CODEOWNERS               → entrega = PR com revisão
          git branch -r                 → branch base = develop (não main!)

FASE 2    DoD = "mvn verify" (o que o CI já exige é a base prioritária)
          <formatter_command>  → NÃO preenche: o hook não é gerado
          E REMOVE o registro dele dos 3 configs de hook — senão o
          Cursor, com failClosed, derruba o shell do agente
          Workflow de CI       → NÃO gera: o repo já tem pipeline
          Só gate-destructive.sh entra na camada de hooks

FASE 3    CI existente → não edita o pipeline, não gera por cima
          Respeita runs-on: [self-hosted]

FASE 4  ⏸️ Branch base: develop  (fonte: git branch -r)
          Prefixo:     feature/ (sem evidência — usando o default)
          Entrega:     push + PR (fonte: CODEOWNERS exige revisão)
          Plano: "o hook de formatação não foi gerado porque o plugin
          formata o módulo inteiro; a formatação está coberta pelo
          pre-commit e pelo CI"          ← senão parece esquecimento
          Usuário: "ok"

FASE 5    verificar-harness.sh → passa (não cobra hook que não existe)
          time mvn verify      → 19m42s   ⚠️ acima dos ~3 min
          → volta à FASE 4 e propõe dividir a DoD em duas:
            rápida por grupo (mvn -q test -pl <módulo>) e
            completa antes do push (mvn verify)

FASE 6    Repo JÁ tinha CI → confere se a DoD roda lá: roda
          Apresenta só o step de integridade dos hooks como sugestão
          ✅ Harness gerado
```

### Caso 3 — React em monorepo pnpm (config prévia e credencial exposta)

`package.json` com `react` nas dependências, `pnpm-workspace.yaml`, um
`.cursor/hooks.json` que o time já tinha escrito e um `mcp.json` do Cursor
com token literal:

```
Usuário:  "esse repo tá pronto pra agente?"        ← pedido vago = fluxo completo

FASE 1    Acha react em dependencies    → React, não "Node genérico"
          Acha pnpm-workspace.yaml      → monorepo
          Scripts de teste vivem só em packages/*  → NÃO há comando
          que valide o repo inteiro     → a DoD não tem como existir
          Acha .cursor/hooks.json       → hooks custom do time
          Não acha .claude/ nem .devin/ → 2 dos 3 agentes sem enforcement
          Acha "token": "ghp_A1b2..."   → CREDENCIAL LITERAL

FASE 2    DoD = "pnpm -r test && pnpm -r lint && npx tsc --noEmit"
          ...mas só DEPOIS de o usuário aceitar o script raiz (ver FASE 4)
          <formatter_command> = npx prettier --write "$FILE_PATH"
          <file_glob>         = *.js|*.jsx|*.ts|*.tsx    ← alternância,
                                não *.{js,ts}, que em case não casa nada
          /.mcp.json com "token": "${GITHUB_TOKEN}"      ← nunca o literal
          Um AGENTS.md com escopo POR PACOTE: as restrições de
          apps/web não são as de apps/api

FASE 3    .cursor/hooks.json existe → MESCLA, preserva os hooks custom
          .claude/settings.json e .devin/hooks.v1.json não existem
          → gerados normalmente (cada agente é avaliado separadamente)

FASE 4  ⏸️ Plano de Remediação, ordenado pelo que destrava outra coisa:
          [1] Script raiz que delega (pnpm -r test) — sem ele a DoD
              não tem um comando que valide o repositório inteiro
          [2] Rotacionar o token do GitHub: ele continua no arquivo de
              origem e, se foi commitado, está no histórico do git
          Usuário: "aceito o [1]"
          → refaz a DoD com o comando novo ANTES de gravar, e só então
            gera .pre-commit-config.yaml e o workflow de CI

FASE 5    verificar-harness.sh → 11 checagens, cola a saída
          pnpm -r test         → executa os sensores de verdade
          time <DoD>           → 1m12s (ok)

FASE 6    Repo não tinha CI → confirma ubuntu-latest
          ✅ Harness gerado + pendência: token a rotacionar
```

### O que os três casos mostram

A mesma skill, três resultados diferentes — e nenhuma diferença veio de
opinião, todas vieram de evidência lida no repositório:

| Decisão do fluxo | Python | Java / Maven | React monorepo |
|---|---|---|---|
| Gera `format-on-edit.sh`? | sim | **não** — plugin formata o módulo inteiro | sim |
| Gera workflow de CI? | sim | **não** — o repo já tem pipeline | sim, após a remediação |
| Gera `.pre-commit-config.yaml`? | sim | sim | **só depois** de a DoD deixar de ser vazia |
| Hooks: quantos agentes? | os 3 | os 3 | 2 gerados + 1 mesclado |
| AGENTS.md com escopo | 1 | 1 | **um por pacote** |
| Precisou de remediação antes da DoD? | não | não | **sim** — script raiz que delega |
| Fase que mudou de rota | — | 2, 3 e 6 | 2, 3 e 4 |

---

## Etapa 0 — Ativação e triagem

**O que acontece aqui:** antes de qualquer coisa, a skill decide se o pedido
realmente pede o harness inteiro. Um fluxo de 6 fases com pausa de aprovação
é caro; responder com ele a um pedido de uma linha gasta a sessão do usuário
num ritual que ele não pediu.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 0.1 | Disparar pelos gatilhos da `description` | `SKILL.md` (frontmatter) | Ser invocada mesmo quando o usuário **não usa a palavra "harness"** — ele pode dizer "cria um AGENTS.md", "prepara pra IA", "quero checkpoint por grupo de tasks" |
| 0.2 | **Passo 0 — dimensionar o pedido** | `SKILL.md`, "O fluxo — e o passo 0" | Aplicar um critério objetivo, não um julgamento novo a cada invocação: *o pedido nomeia a edição **e** o arquivo já existe?* → só a edição. Qualquer outro caso → fluxo completo |
| 0.3 | Decidir sozinha, nunca perguntar qual caminho seguir | `SKILL.md`, Regra 1 | Perguntar "você quer o fluxo completo ou só uma edição?" devolve ao usuário exatamente a triagem que a skill existe para fazer |
| 0.4 | Se o sintoma for de harness já instalado que não funciona, pular para a tabela de diagnóstico | `SKILL.md`, "Diagnóstico" | Cobrir o caso que nenhuma fase alcança: o harness está gravado, mas falha em silêncio |
| 0.5 | Carregar só o arquivo da fase corrente | `SKILL.md`, "O fluxo" | Economizar contexto para a fase que grava |

### Exemplos práticos

O critério do passo 0.2, aplicado:

| Pedido do usuário | Decisão | Por quê |
|---|---|---|
| "acrescente no AGENTS.md que usamos pnpm" | Edição pontual + uma frase dizendo que o fluxo completo existe | Nomeia a edição *e* o AGENTS.md já existe |
| "prepare este repo para agentes" | Fluxo completo, da FASE 1 | Não aponta linha nenhuma — quem pede isso está pedindo o harness |
| "configura o harness aqui" | Fluxo completo | Idem |
| "no Cursor o gate não bloqueia nada" | Tabela de diagnóstico + edição pontual | É harness já instalado falhando, não geração |

E o diagnóstico do passo 0.4 — todos os sintomas são de falha **silenciosa**,
que é o que os torna difíceis de achar sem uma lista:

| Sintoma | Causa provável |
|---|---|
| O agente ignora o protocolo, e o AGENTS.md está lá | Falta a ponte `CLAUDE.md` — o Claude Code carrega `CLAUDE.md` e **não** carrega `AGENTS.md` |
| O gate bloqueia até `npm test` | Hook de versão antiga, que exigia Python, em repo sem Python |
| No Cursor o gate não bloqueia nada | O Cursor manda `command` no topo do JSON; hook que lê só `tool_input` recebe string vazia |
| O agente nunca usa `/dod` nem `executar-grupo` | `<ferramentas-do-harness>` ficou vazio — sem o ponteiro no AGENTS.md, nada mais é alcançável |
| Nenhum scanner enxerga os hooks | `.claude/settings.json` sem o wrapper `"hooks"` na raiz |

---

## FASE 1 — Descoberta (somente leitura, nenhuma escrita)

**O que acontece aqui:** a skill investiga o repositório como um
desenvolvedor novo faria no primeiro dia — só que citando a fonte de cada
coisa que descobre. Nada é escrito nesta fase.

**A regra que governa tudo:** toda informação precisa vir de evidência num
arquivo do repo, com o arquivo-fonte citado. Sem evidência, escreve-se
`NÃO ENCONTRADO`. Nunca presumir, nunca preencher de memória.

> **Por que isso é tão rígido:** o produto da descoberta vira a Definition of
> Done, que vira o pre-commit e o CI. Se a skill "achar" que o comando de
> teste é `pytest` num repo que usa `pytest -c config/pytest.ini`, ela não
> gera um documento errado — ela gera um **pre-commit que bloqueia todo
> commit do time**.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 1.0 | Verificar se `.claude/harness.json` já existe | `01-descoberta.md`, Passo 0 → `atualizacao.md` | Se existir, o repo **já recebeu um harness desta skill**: a descoberta vira reduzida e a FASE 4 vira um diff. Descobrir isso no fim, e não no começo, faria a skill reinvestigar do zero e reapresentar 20 arquivos dos quais 18 não mudaram |
| 1.1 | Identificar o **ecossistema**, não a linguagem | `01-descoberta.md`, item 0 → `ecossistemas.md` | "Java" não decide nada: Maven e Gradle divergem em todos os comandos. Acertar a linguagem e errar o ecossistema gera uma DoD que não roda |
| 1.2 | Ler os manifestos | `01-descoberta.md`, item 1 | Descobrir linguagem, versões e dependências com fonte citada |
| 1.3 | Extrair os **comandos reais** de teste, lint, build e run | `01-descoberta.md`, item 2 | A tabela de ecossistemas diz onde procurar; o que está escrito no repo é que vale. Se o `package.json` define `"test": "jest --runInBand"`, a DoD usa isso |
| 1.4 | Ler o CI e inspecionar o `runs-on:` | `01-descoberta.md`, item 3 | Os comandos do CI são a **base prioritária** da DoD — é o que um merge já exige hoje. E o runner precisa ser lido, não presumido: `ubuntu-latest` chutado numa org com runner self-hosted faz o workflow nunca ser agendado |
| 1.5 | Achar o **diretório de código principal** e detectar monorepo/workspace | `01-descoberta.md`, item 4 | É onde vai o AGENTS.md com escopo. Em workspace, se os scripts vivem só nos pacotes, não existe um comando único que valide o repo inteiro — e a DoD precisa de um |
| 1.6 | Ler convenções já documentadas | `01-descoberta.md`, item 5 | Respeitar o que o time já escreveu, em vez de duplicar com texto genérico |
| 1.7 | Identificar banco, ORM e ferramenta de migration | `01-descoberta.md`, item 6 | Só com essa evidência a restrição sobre migrations pode entrar nos `MUST NOT` |
| 1.8 | Classificar o tipo de aplicação (API, frontend, CLI, lib) | `01-descoberta.md`, item 7 | Muda o que significa "verificado" naquele projeto |
| 1.9 | Checar OpenSpec: `openspec/` existe? tem `config.yaml` ou `project.md` legado? | `01-descoberta.md`, item 8 | Define a **fonte de trabalho** do agente: OpenSpec ou `TASKS.md`. As duas são mutuamente exclusivas |
| 1.10 | Determinar o formatter **e se ele escopa por arquivo** | `01-descoberta.md`, item 9 → `ecossistemas.md` (coluna Formatter, fonte única) | Formatter que formata o módulo inteiro não pode virar hook de edição — cada tecla dispararia um build completo. Um hook que atrapalha é um hook que o time desliga, levando o resto do enforcement junto |
| 1.11 | Identificar o gerenciador de dependências e o lockfile | `01-descoberta.md`, item 10 | Só nomes convencionais contam: um `requirements.lock` inventado não é instalado por ferramenta nenhuma nem reconhecido por scanner |
| 1.12 | Localizar MCP servers e **procurar credencial literal** | `01-descoberta.md`, item 11 + Regra 4 | Antes de propor copiar qualquer config para a raiz, saber se há segredo dentro dele |
| 1.13 | Verificar hooks existentes nos **três** agentes | `01-descoberta.md`, item 12 | Olhar só `.claude/settings.json` deixaria Devin e Cursor sem enforcement — e ninguém descobre, porque o agente desprotegido simplesmente funciona até causar o dano |
| 1.14 | Procurar config de linter/formatter e `.editorconfig` | `01-descoberta.md`, item 13 | Decidir se gera o `.editorconfig` base e se mescla template específico da linguagem |
| 1.15 | Conferir se `.gitignore` cobre `.env` | `01-descoberta.md`, item 14 | Preparar o append que evita commit de credencial |
| 1.16 | Verificar `LICENSE` e `README.md` | `01-descoberta.md`, item 15 | O README é o primeiro documento que agente e humano leem; a ausência vira oferta na FASE 4 |
| 1.17 | Verificar se o repo já empacota procedimentos como skill | `01-descoberta.md`, item 16 | Se já houver skills, a skill `executar-grupo` não é gerada — não competir com o que o time já tem |
| 1.18 | Levantar **regras arquiteturais candidatas**, só com evidência e só se verificáveis por um comando | `01-descoberta.md`, item 17 | Transformar invariantes que hoje vivem em prosa (README, ARCHITECTURE.md) em sensores executáveis |
| 1.19 | Procurar contexto com escopo (AGENTS.md aninhado, regras com escopo do Cursor) | `01-descoberta.md`, item 18 | Sem ele, todo o conhecimento vive na raiz e é carregado em **todo request**, inclusive nos que não tocam aquele código |
| 1.20 | Descobrir a **branch base** por evidência | `01-descoberta.md`, item 19 | O AGENTS.md gerado manda o agente rodar `git checkout <branch-base>` antes de toda funcionalidade nova. Nome errado = falha na primeira execução, antes de o agente escrever uma linha |
| 1.21 | Derivar o **prefixo de branch** contando ocorrências no histórico | `01-descoberta.md`, item 20 | Prefixo errado faz o agente criar branch fora do padrão do time — e o time só descobre no PR |
| 1.22 | Derivar a **política de entrega** (o que se faz depois do commit) | `01-descoberta.md`, item 21 | Mandar abrir PR num repo que faz merge direto trava o agente esperando uma aprovação que ninguém vai dar |
| 1.23 | Verificar a **ponte `CLAUDE.md`** | `01-descoberta.md`, item 22 + Regra 9 | É a diferença entre "harness gravado" e "harness carregado" |
| 1.24 | Se faltarem sensores, achar **funções puras** pelo nome e checar imports de sistema no entrypoint | `01-descoberta.md`, Passo 0.1 | "Escreva testes" não é acionável. "Teste `centro_logico()` e `extrair_json()`, que são puras" é |
| 1.25 | Montar o **Relatório de Descoberta** no formato fixo | `01-descoberta.md`, "Formato do Relatório" | Entregar ao usuário, linha a linha e com fonte, tudo que a skill viu — auditável antes de qualquer gravação |
| 1.26 | Transformar cada `NÃO ENCONTRADO` em item do **Plano de Remediação** | `01-descoberta.md`, Passo 0.1 → `remediacoes.md` + Regra 6 | O usuário termina a sessão sabendo **tudo** que falta — inclusive o que a skill não sabe gerar sozinha. Diagnosticar sem receita devolveria a ele o trabalho da skill |
| 1.27 | Apresentar o relatório e **seguir direto** para a FASE 2 | `01-descoberta.md`, fecho | A única pausa é a FASE 4; aqui nada foi escrito ainda, então não há o que aprovar |

### Exemplo 1 — Ecossistema, não linguagem (ação 1.1)

Dois repositórios Java, mesma linguagem, comandos **totalmente** diferentes:

```
pom.xml com spotless-maven-plugin
  Teste:     mvn test
  Formatter: mvn -q spotless:apply -DspotlessFiles="$FILE_PATH"   → vira hook

pom.xml com spring-javaformat-maven-plugin   (toda a família Spring)
  Teste:     mvn test
  Formatter: formata o MÓDULO INTEIRO         → NÃO vira hook
             registra-se "SEM HOOK DE FORMATAÇÃO" e a formatação
             vai para o pre-commit e o CI
```

Não basta ver que existe um plugin de formatação: é preciso ler **qual**
`artifactId` está no `pom.xml`. A mesma lógica vale para JS/TS — `package.json`
com `angular.json` ao lado usa `ng test --watch=false`, com `react` nas
dependências usa `vitest run`.

### Exemplo 2 — O que "citar a fonte" quer dizer na prática (ação 1.25)

O Relatório de Descoberta não é uma lista de conclusões; é uma lista de
conclusões **com o arquivo que as sustenta**:

```
- Ecossistema:                Python            (fonte: pyproject.toml)
- Comando de teste:           pytest            (fonte: [tool.pytest.ini_options])
- Comando de lint/format:     ruff check .      (fonte: [tool.ruff] + .pre-commit)
- Comandos exigidos pelo CI:  NÃO ENCONTRADO    (não há .github/workflows/)
- Runner de CI:               NÃO ENCONTRADO
- Branch base do fluxo:       main              (fonte: git symbolic-ref)
- Lockfile:                   NÃO ENCONTRADO
- Credencial literal em MCP:  "token" em .cursor/mcp.json — valor literal
```

Cada `NÃO ENCONTRADO` acima já é um candidato do Plano de Remediação
(ação 1.26).

### Exemplo 3 — Inferir o fluxo de branches por evidência (ações 1.20 a 1.22)

Nada aqui é presumido; tudo sai de um comando ou de um arquivo:

```
Branch base:  develop     ← git symbolic-ref refs/remotes/origin/HEAD
Prefixo:      feat/       ← git log --format=%D --all: 12 de 15 usam feat/
Entrega:      push + PR   ← .github/PULL_REQUEST_TEMPLATE.md + CODEOWNERS
```

Se não houver evidência nenhuma, o default é `feature/` — mas ele é
**declarado como default** na FASE 4, nunca apresentado como descoberta.

### Exemplo 4 — Regra arquitetural: o que entra e o que não entra (ação 1.18)

| Frase encontrada no repo | Vira regra? | Por quê |
|---|---|---|
| "O código deve ser limpo e coeso" | ❌ | É desejo — não há comando que verifique |
| "Nenhum arquivo em `domain/` importa o driver do banco" | ✅ | Vira `grep -r "import psycopg" domain/` com `expect: exit-nonzero` |
| "Use nomes descritivos" | ❌ | Vira item do Plano de Remediação, não regra silenciosamente fraca |

Toda regra precisa de `what`, `why` e `fix` nomeando arquivo, função ou
comando. **O `why` é o que impede o agente de "consertar" a violação apagando
a regra** — ele vê um comando falhando e quer fazê-lo parar de falhar.

---

## FASE 2 — Preenchimento VERBATIM dos templates

**O que acontece aqui:** a skill abre cada template de `resources/` e
preenche **somente** os trechos marcados com `<>`. Não parafraseia, não
resume, não reordena, não "melhora" o texto. Os arquivos ficam prontos em
memória — nada é gravado ainda.

> **Por que essa rigidez:** o princípio central da skill é que *o que precisa
> ser consistente não se deixa para o modelo redigir — se transcreve do
> template*. Se cada geração reescrevesse o protocolo com outras palavras,
> cada repositório receberia uma regra ligeiramente diferente, e a
> inconsistência só apareceria meses depois, quando duas equipes comparassem
> os próprios AGENTS.md.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 2.0 | **Regra de honestidade**: sem nenhum comando real de teste/lint/types, não gerar pre-commit nem workflow de CI | `02-preenchimento-templates.md` + Regra 5 | Enforcement sem o que verificar passa verde sempre. Isso é **pior** que não ter enforcement, porque parece ter |
| 2.1 | Nesse caso, montar a proposta de sensores com comandos exatos, configs prontas e primeiros testes sobre funções reais | `02-preenchimento-templates.md` → `remediacoes.md` | A diferença entre inventar e recomendar é o **consentimento**: escrever `pytest` na DoD de um repo sem testes é fabricar evidência; propor "instalar pytest, com esta config e estes três testes, aceita?" é o trabalho da skill |
| 2.2 | Gravar tudo em **LF**, sem exceção | `02-preenchimento-templates.md`, "REGRA DE GRAVAÇÃO" | Um único `\r` num `.sh` desliga o gate de segurança — ver exemplo abaixo |
| 2.3 | Preencher a `<DoD>` com os comandos reais encadeados por `&&`, iguais em AGENTS.md, `/dod`, config.yaml e init.sh | `02-preenchimento-templates.md` | A redundância é deliberada: cada consumidor declara a mesma DoD no formato que ele entende. Versões divergentes fariam cada um verificar coisa diferente |
| 2.4 | Preencher 3–6 `<MUST NOT>` derivados de convenções **reais** | `02-preenchimento-templates.md` + Regra 3 | Restrição inventada ensina o leitor a ignorar a lista inteira — inclusive as verdadeiras |
| 2.5 | Preencher `<branch-base>`; sem evidência, `# TODO: definir branch base` | `02-preenchimento-templates.md` | `main`, `master`, `develop` e `trunk` são todos comuns. Chutar trava o agente no primeiro `git checkout` com `pathspec did not match` |
| 2.6 | Escolher a variante de `<como-propor-mudanca-de-plano>`: OpenSpec **ou** TASKS.md | `02-preenchimento-templates.md` | Mandar usar `/opsx:propose` num repo sem OpenSpec é instruir o agente a chamar um comando que não existe — ele para no meio ou inventa um caminho |
| 2.7 | Escrever os comandos do `init.sh` chamando o interpretador (`python3 -m pip`, `npx tsc`) | `02-preenchimento-templates.md` | O `init.sh` roda com `set -e`. Em muitas instalações `pip` e `pytest` não estão no PATH: a sessão morre no passo 1, antes de o agente ver qualquer estado |
| 2.8 | Preencher `<ferramentas-do-harness>` **só com o que foi realmente gerado** | `02-preenchimento-templates.md` | O AGENTS.md é o único arquivo que o agente lê sempre — é dali que o resto precisa ser alcançável. Apontar para o que não existe é pior que não apontar |
| 2.9 | Gerar o **AGENTS.md com escopo** no diretório principal, sem repetir o protocolo | `AGENTS-scoped.md` | Leva o conhecimento para perto do código. Protocolo duplicado diverge da raiz na primeira edição |
| 2.10 | Gerar a **ponte `CLAUDE.md`** ao lado de **cada** AGENTS.md | `resources/CLAUDE.md` + Regra 9 | Sem ela o harness fica completo no disco e ausente na sessão — o modo mais silencioso de falhar: nada quebra, o agente só ignora o protocolo |
| 2.11 | Gerar a skill `executar-grupo`, se não houver skills | template da skill `executar-grupo` | Empacota o procedimento de fechar um grupo como conhecimento **sob demanda**, em vez de pesar o contexto de todo request |
| 2.12 | Preencher `<dod-command>` no `/dod` com a MESMA cadeia | `dod-command.md` | Dar ao usuário um comando único que roda a DoD inteira |
| 2.13 | Preencher `<formatter_command>`, `<formatter_bin>` e `<file_glob>` no hook de formatação | `02-preenchimento-templates.md` → `ecossistemas.md` | Três marcadores, três modos de o hook virar um no-op silencioso — ver exemplos abaixo |
| 2.14 | Derivar os `<pre-commit-hooks>` dos comandos descobertos | `pre-commit-config.yaml` | Um hook por sensor, para o commit local já barrar o que o CI barraria |
| 2.15 | Gerar o workflow de CI **só se não houver CI** | `ci-workflow.yml` | Sem CI prévio não há pipeline nem runner corporativo com que conflitar. E sem enforcement remoto, a DoD só vale na máquina de quem lembrar de rodá-la |
| 2.16 | Copiar `.mcp.json` para a raiz **trocando credencial literal por `${VAR}`** | `02-preenchimento-templates.md` + Regra 4 | Copiar um segredo para a raiz o torna mais visível e mais provável de ser commitado — exatamente o contrário do objetivo da cópia |
| 2.17 | Gerar `.editorconfig` (base + específico da linguagem, se houver) | `editorconfig-base`, `editorconfig-dotnet` | Regras universais, incluindo o `end_of_line = lf` que os próprios arquivos gerados precisam obedecer |
| 2.18 | Fazer **append** de `.env` no `.gitignore` | `02-preenchimento-templates.md` | Nunca sobrescrever: o `.gitignore` do time tem regras que a skill não conhece |
| 2.19 | Preencher `<prefixo-de-branch>` e `<politica-de-entrega>` | `02-preenchimento-templates.md` | Fazer o agente seguir o fluxo real do time, não um genérico |
| 2.20 | Se o formatter não escopa por arquivo: não gerar o hook **e remover o registro dele dos três configs** | `02-preenchimento-templates.md` | Registro apontando para script inexistente falha em silêncio no Claude Code e no Devin — e no Cursor, com `failClosed`, derruba o shell do agente inteiro |
| 2.21 | Gerar `.harness/arch-rules.json` + `.claude/check-arch.sh` e pôr `bash .claude/check-arch.sh` na DoD | `arch-rules.json`, `check-arch.sh` | Regra sem cabo para execução automática é documento, não sensor. É o degrau que falta a uma revisão: revisor julga caso a caso e esquece; regra fica, e cada classe de erro é cometida **uma vez só** |
| 2.22 | Gerar o agente `propor-regra-arch`, VERBATIM inclusive na seção "O que você NÃO faz" | `propor-regra-arch.md` | Ele propõe regra, não veredito, e **não tem ferramenta de escrita**. Um agente que pode editar as regras pode enfraquecê-las — e uma catraca que gira para os dois lados não é catraca |
| 2.23 | Preencher o **manifesto** `.claude/harness.json` | `harness-manifest.json` | É o que torna o harness atualizável depois — ver exemplo abaixo |
| 2.24 | Gerar um `README.md` mínimo, se não existir | `02-preenchimento-templates.md` | Um repo sem README obriga a exploração que o harness existe para eliminar. Se já existir, **nunca** sobrescrever |
| 2.25 | Seguir direto para a FASE 3 | `02-preenchimento-templates.md`, fecho | Os arquivos existem só em memória |

### Exemplo 1 — O que "preencher só os `<>`" significa

Trecho real do template `resources/AGENTS.md`, antes:

```markdown
## Definition of Done
Concluído = TODOS passam:

    <comandos reais do repo, encadeados com &&, priorizando o que o CI exige>

## Regras de trabalho
- MUST NOT: <restrição 1 — derivada de convenção real do repo>
- MUST NOT: <restrição 2>
```

Depois, num repo Python:

```markdown
## Definition of Done
Concluído = TODOS passam:

    pytest && ruff check . && mypy --strict src/

## Regras de trabalho
- MUST NOT: alterar migrations já aplicadas — criar uma nova
- MUST NOT: acessar o banco fora da camada repository/
```

Todo o resto do arquivo — WIP=1, o protocolo de grupos, o handoff de
sessão — foi copiado caractere a caractere.

Repare no segundo `MUST NOT`: ele só entra porque a FASE 1 **encontrou** uma
ferramenta de migration no repo. Essa restrição já esteve fixa no template,
fora de placeholder, e todo repositório recebia uma regra sobre um banco que
muitos nem tinham.

### Exemplo 2 — Por que LF importa tanto (ação 2.2)

A cadeia completa, do detalhe invisível ao dano real:

```
1. Arquivo gravado com CRLF
2. O shebang #!/bin/bash vira, para o kernel, "/bin/bash\r"
3. Esse interpretador não existe → o script morre com exit 1
4. Em PreToolUse, exit 1 significa "erro NÃO-bloqueante"
5. O agente executa o comando destrutivo assim mesmo
```

O gate **falha aberto**: continua instalado, continua registrado, e não
protege nada. Por isso a FASE 5 tem uma checagem dedicada a CRLF.

### Exemplo 3 — Os três marcadores do hook de formatação (ação 2.13)

Cada um tem um jeito próprio de virar um no-op silencioso:

```bash
# ❌ <file_glob> preenchido com brace expansion
case "$FILE_PATH" in *.{js,ts})       # case NÃO faz brace expansion:
                                      # não casa com nada, e nada acusa
# ✅
case "$FILE_PATH" in *.js|*.ts|*.jsx|*.tsx)

# ❌ <formatter_command> com o caminho posicional no fim
mvn spotless:apply "$FILE_PATH"       # Maven lê o caminho como fase de
                                      # ciclo de vida → "Unknown lifecycle
                                      # phase" → engolido pelo 2>/dev/null
# ✅
mvn -q spotless:apply -DspotlessFiles="$FILE_PATH"

# ❌ <formatter_bin> preenchido com # TODO
if command -v # TODO ; then           # o # comenta o resto da linha,
                                      # INCLUSIVE o "then" → erro de sintaxe
# ✅ sem formatter detectado:
if command -v formatter-nao-definido ; then    # command -v falha,
                                               # o hook vira no-op limpo
```

A lição da terceira: `# TODO` é honesto no AGENTS.md, onde é texto. Dentro de
um shell script, é um bug.

### Exemplo 4 — Credencial em config MCP (ação 2.16)

```jsonc
// .cursor/mcp.json encontrado na FASE 1
{ "github": { "token": "ghp_A1b2C3d4E5f6G7h8" } }

// /.mcp.json gerado pela FASE 2
{ "github": { "token": "${GITHUB_TOKEN}" } }
```

E, na FASE 4, três avisos que acompanham a conversão: exportar
`GITHUB_TOKEN`, o segredo **continua** no arquivo de origem, e se já foi
commitado ele está no histórico do git e **precisa ser rotacionado**.

### Exemplo 5 — Para que serve o manifesto (ação 2.23)

```json
{
  "harness": {
    "skill": "harness-creator",
    "versao": "2.5",
    "gerado_em": "2026-07-29",
    "ecossistema": "Python",
    "dod": "pytest && ruff check . && mypy",
    "arquivos": ["AGENTS.md", "CLAUDE.md", ".claude/hooks/gate-destructive.sh"],
    "recusados": ["lockfile (uv.lock)"]
  }
}
```

Ele responde três perguntas que nenhum outro arquivo responde:

| Pergunta | Campo | O que acontece sem a resposta |
|---|---|---|
| Este harness é de qual versão? | `versao` | A segunda execução não distingue o que a skill escreveu do que o usuário escreveu depois |
| O que exatamente foi gerado? | `arquivos` | Auditar ou remover o harness vira caça arquivo por arquivo |
| O que o usuário já recusou? | `recusados` | A skill repropõe na sessão seguinte algo que ele já decidiu |

É o **único** arquivo que a skill sobrescreve sem perguntar — ele descreve a
execução atual, então manter a versão anterior seria registrar mentira.

---

## FASE 3 — Resolução de conflitos com o repositório existente

**O que acontece aqui:** os arquivos estão prontos em memória, e agora a
skill compara com o que já existe no repo. Quase toda regra desta fase é uma
variação de **"não destrua o que o usuário escreveu"** — porque o custo dos
dois erros é assimétrico: gerar de menos o usuário resolve depois; sobrescrever
o `AGENTS.md` que o time enriqueceu ao longo de um ano é irreversível.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 3.0 | Se houver manifesto, **lê-lo antes** de tudo e classificar cada arquivo | `03-resolucao-conflitos.md` → `atualizacao.md` | Numa atualização, a regra de "não sobrescrever" sozinha congelaria justamente os arquivos que a skill deveria atualizar |
| 3.1 | `AGENTS.md` existente: preservar o descritivo útil; o protocolo do template prevalece nas seções sobrepostas; mostrar o diff | `03-resolucao-conflitos.md` | Ficar com o melhor dos dois: os comandos e convenções que o time escreveu, e o protocolo consistente entre repos |
| 3.2 | `CLAUDE.md` existente: **nunca sobrescrever**; se ele não alcança o AGENTS.md, propor o append de uma linha | `03-resolucao-conflitos.md` | Sobrescrever apagaria instrução do usuário; não fazer nada deixaria o protocolo fora do contexto do Claude Code. O append de `@AGENTS.md` resolve os dois |
| 3.3 | Bloco `<!-- OPENSPEC:START/END -->`: preservar intacto, inserir o protocolo depois | `03-resolucao-conflitos.md` | É um bloco gerenciado por outra ferramenta — editá-lo quebraria o `openspec update` |
| 3.4 | Conteúdo descritivo extenso: mover para AGENTS.md com escopo | `03-resolucao-conflitos.md` | Tirar da raiz o que só interessa a um diretório. **O protocolo nunca sai da raiz** |
| 3.5 | AGENTS.md com escopo já existente: não sobrescrever, não criar um segundo; propor append | `03-resolucao-conflitos.md` | Dois arquivos de escopo no mesmo lugar competem, e o agente não sabe qual vale |
| 3.6 | Skills já existentes: não gerar `executar-grupo`; oferecer na FASE 4 | `03-resolucao-conflitos.md` | Não competir com o procedimento que o time já empacotou |
| 3.7 | CI já existente: **nunca** gerar por cima nem editar o pipeline; respeitar o `runs-on:` | `03-resolucao-conflitos.md` | Runners variam, pipelines reusáveis podem já cobrir lint e teste, e schemas diferem entre GitHub, GitLab e Jenkins. A skill propõe o step; quem aplica é quem conhece o pipeline |
| 3.8 | Hooks já existentes: mesclar preservando os custom, avaliando os três agentes **separadamente** | `03-resolucao-conflitos.md` | O repo pode ter config de um agente e nenhuma dos outros — os que faltam são gerados normalmente |
| 3.9 | `.pre-commit-config.yaml`, `.editorconfig`, lockfile existentes: mostrar como sugestão | `03-resolucao-conflitos.md` | São escolhas de ferramenta do time |
| 3.10 | `.gitignore` existente: só append das linhas `.env` que faltarem | `03-resolucao-conflitos.md` | Nunca destruir regras de ignore que a skill não conhece |
| 3.11 | `.harness/arch-rules.json` existente: **nunca sobrescrever**, nem quando o manifesto o lista como gerado pela skill | `03-resolucao-conflitos.md` | Cada regra ali nasceu de um problema real que alguém encontrou. Regerar por cima apagaria exatamente o aprendizado que o arquivo existe para acumular |
| 3.12 | `README.md` e `LICENSE` existentes: não sobrescrever | `03-resolucao-conflitos.md` | Mesmo pobres, são do usuário |
| 3.13 | `TASKS.md` sem grupos: propor o agrupamento, não reescrever sozinha | `03-resolucao-conflitos.md` | O agrupamento muda o plano de trabalho do time — é decisão humana |
| 3.14 | Seguir direto para a FASE 4 | `03-resolucao-conflitos.md`, fecho | Nada foi escrito ainda |

### Exemplo — Atualização de um harness já existente (ação 3.0)

Quando existe `.claude/harness.json`, cada arquivo cai numa de cinco
situações, e o tratamento é diferente em cada uma:

| Situação | O que a skill faz |
|---|---|
| Listado em `arquivos` e **idêntico** ao que ela geraria hoje | Nada. Nem entra no plano de aprovação |
| Listado e a skill de hoje geraria **diferente** | Atualiza, mostrando o diff na FASE 4 |
| Listado, mas divergente **também** do template antigo | O usuário editou → **não sobrescrever**, mostrar o diff e perguntar |
| **Não** listado em `arquivos` | É do usuário → regra normal da FASE 3 |
| Listado e **ausente** do disco | Foi removido → perguntar antes de recriar; a remoção pode ter sido deliberada |

A terceira linha é a que exige mais cuidado: um `AGENTS.md` que a skill gerou
e o time depois enriqueceu com convenções reais é **mais valioso** que o
template. Sobrescrevê-lo destruiria trabalho humano para instalar texto
genérico.

E é isso que a FASE 4 apresenta numa atualização — um resumo, não vinte
arquivos:

```
ATUALIZAÇÃO DE HARNESS
Instalado: versão 2.2, gerado em 2026-05-14, ecossistema Python
Skill atual: versão 2.5

Atualiza (3)      arquivos que a skill gerou e hoje geraria diferente
Preserva (14)     idênticos ou editados por você — nenhum toque
Novo (2)          artefatos que a versão 2.2 ainda não gerava
Não repropõe (2)  itens recusados na geração anterior
```

---

## FASE 4 — Saída e aprovação ⏸️ (a única pausa do fluxo)

**O que acontece aqui:** tudo que foi decidido nas três fases anteriores é
apresentado de uma vez, e a skill **para** e espera. Recebido o "ok", ela
grava — e esse é o único momento do fluxo em que algo é escrito em disco.

> **Por que a pausa é aqui, e só aqui:** este é o momento anterior a gravar.
> Depois de gravar, uma confirmação já não protege nada; e uma confirmação
> por fase transformaria um fluxo autônomo em seis interrupções. É onde o
> usuário corrige de graça.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 4.1 | Apresentar o **Relatório de Descoberta** com as fontes | `04-saida-aprovacao.md` | O usuário audita o que a skill entendeu do projeto dele antes que isso vire arquivo |
| 4.2 | Apresentar o **fluxo de branches** em três linhas, com a evidência de cada uma, marcando o que é default | `04-saida-aprovacao.md` | Default apresentado como descoberta é **pior que uma pergunta**: o usuário aprova achando que a skill viu algo que ela não viu |
| 4.3 | Apresentar os arquivos com **profundidade proporcional ao risco** | `04-saida-aprovacao.md` | São ~20 artefatos: despejar todos por inteiro produz uma parede de texto que ninguém lê — e aprovação não lida é a pausa virando formalidade. Ver a regra abaixo |
| 4.4 | Apresentar o **Plano de Remediação**, ordenado pelo que **destrava** outra coisa | `04-saida-aprovacao.md` → `remediacoes.md` | Sensores vêm primeiro porque habilitam a DoD, o pre-commit e o CI de uma vez |
| 4.5 | Transformar cada rascunho do `propor-regra-arch` em item do Plano, com o `check` e a evidência do diff | `04-saida-aprovacao.md` | O agente propõe, o usuário decide, um a um |
| 4.6 | Listar as pendências que **só o humano resolve** | `04-saida-aprovacao.md`, item 4 | Runner self-hosted, segredo a rotacionar, step de DoD em CI existente, DoD lenta demais, migração de `project.md` |
| 4.7 | Oferecer `LICENSE`, se não existir | `04-saida-aprovacao.md`, item 5 | Escolha jurídica — sempre do usuário |
| 4.8 | Colher a decisão do Plano **item a item**, numa resposta só | `04-saida-aprovacao.md` | É a mesma pausa, não uma segunda rodada de perguntas |
| 4.9 | **Aguardar aprovação explícita** | `04-saida-aprovacao.md`, "⏸️ ÚNICA PAUSA" | Nada é gravado antes disso |
| 4.10 | Se um item aceito criar sensores: **refazer** o preenchimento da DoD e gerar o enforcement que passou a ter o que verificar | `04-saida-aprovacao.md` | Na mesma execução, a DoD deixa de ser vazia e o pre-commit e o CI passam a existir |
| 4.11 | **Gravar**, `chmod +x` no `init.sh` e nos `.claude/hooks/*.sh`, e sugerir `checkpoint: harness inicial` | `04-saida-aprovacao.md` | Sem o bit de execução, o agente registra um hook que nunca roda |
| 4.12 | Registrar os adiados em `SESSION_STATE.md`; não repropor os recusados | `04-saida-aprovacao.md` | Decisão tomada não volta à mesa na mesma sessão |
| 4.13 | Seguir direto para a FASE 5 | `04-saida-aprovacao.md` | As fases 5 e 6 só verificam e relatam |

### Exemplo 1 — Quanto mostrar de cada arquivo (ação 4.3)

A regra é o **risco de aprovar sem ler**:

| Tipo de arquivo | Como é apresentado | Por quê |
|---|---|---|
| Novo, que só existe por causa do harness (hooks, `/dod`, `SESSION_STATE.md`, manifesto) | **Uma linha** com o destino e os valores preenchidos | Nada é destruído se estiver errado, e a FASE 5 verifica cada um |
| Que sobrescreve, dá append ou altera conteúdo do usuário (`AGENTS.md` preexistente, `.gitignore`, `.editorconfig`) | **Diff completo, sempre** | É o único caso em que aprovar errado custa trabalho do usuário |
| `AGENTS.md` da raiz, quando é novo | **Conteúdo integral**, mesmo assim | É o arquivo que passa a governar todas as sessões de agente no repo, e os `MUST NOT` dele saíram de inferência — se algum ficou errado, é agora que se vê |

O resto fica disponível sob demanda, oferecido numa linha: quem quiser ler
tudo continua podendo; quem não quiser não paga por isso.

### Exemplo 2 — Um item do Plano de Remediação (ação 4.4)

Cada item declara o **custo**, não só o ganho:

```
PLANO DE REMEDIAÇÃO

[1] Instalar sensores de teste e lint
    Por que:   sem eles o agente não verifica o próprio trabalho, e a
               DoD, o pre-commit e o CI não podem ser gerados
    Muda:      pyproject.toml (novas dev-deps), tests/ (diretório novo)
    Comando:   pip install pytest ruff  +  a config abaixo
    Testes propostos: centro_logico(), extrair_json()  [funções puras]
    Atenção:   o entrypoint importa pyautogui/PIL — precisa de conftest
    Risco:     nenhum código de produção é alterado
    [ ] aceitar   [ ] recusar   [ ] adiar
```

Três regras de redação que esse formato aplica:

- **Agrupar por ação, não por arquivo faltante.** "Instalar sensores" é um
  item, não quatro.
- **Declarar o que a aceitação modifica.** O usuário está aprovando uma
  mudança no projeto dele, não um arquivo de configuração de agente.
- **Nunca usar vocabulário de pontuação** ("+6 pontos", "nível 4"). É o placar
  de uma ferramenta externa que o usuário não roda e que não existe em lugar
  nenhum do harness entregue.

### Exemplo 3 — A fronteira entre o que a skill faz e o que ela propõe

O critério é: *o artefato é só do harness, ou muda o contrato do projeto?*

| Grupo | O que é | Exemplo | Decisão |
|---|---|---|---|
| **A — Gerado** | Só afeta quem usa agente | Criar `.claude/hooks/gate-destructive.sh` | Aprovação única da FASE 4 |
| **B — Recomendado** | Muda dependências, config ou código | Adicionar `pytest` ao `pyproject.toml` | Confirmação item a item |
| **C — Informativo** | Só o humano pode decidir | Licença, segredo vazado, runner corporativo | Só reportar |

Adicionar `pytest` parece inofensivo, mas muda o que o time instala, o que o
CI roda e o que "quebrado" significa. Por isso é B, não A.

---

## FASE 5 — Verificação pós-geração

**O que acontece aqui:** os arquivos já estão no disco, e agora a skill
**executa o que acabou de escrever** para provar que funciona. Ela roda o
verificador, dispara o gate com um comando destrutivo de mentira para ver se
ele bloqueia, e cronometra a DoD.

> **Por que ela verifica a si mesma:** a skill cobra evidência de comando do
> agente que vai usar o harness — "saída de comando é evidência; 'parece
> funcionar' não é". Seria incoerente ela mesma declarar sucesso sem executar
> o que gerou.

E há uma distinção importante nesta fase: **falha aqui é defeito da geração,
não pendência do usuário.** Se uma checagem reprova, a skill corrige antes de
seguir — não reporta para o usuário resolver.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 5.1 | Rodar `sh .claude/verificar-harness.sh` e **colar a saída** | `05-verificacao-pos-geracao.md`, item 1 → `verificar-harness.sh` | 11 checagens mecânicas, com o mesmo resultado a cada execução — detalhadas na tabela abaixo |
| 5.2 | Rodar `bash .claude/check-arch.sh` e colar a saída | `05-verificacao-pos-geracao.md`, item 1.1 | A semente de regras precisa terminar em `nenhuma violada`. Se o primeiro contato do usuário com o registro for um vermelho que ele não causou, a reação natural é apagar o arquivo — e isso mata a catraca antes de ela girar uma vez |
| 5.3 | Validar o YAML do pre-commit e do workflow | `05-verificacao-pos-geracao.md`, item 1 | Já quebrou uma vez: um marcador que aparece **também** num comentário do template faz a substituição vazar para fora do comentário e corromper o arquivo |
| 5.4 | **Cronometrar a DoD** (`time <comando>`) e reportar o número | `05-verificacao-pos-geracao.md`, item 2 | Ver exemplo abaixo — é uma verificação sobre o protocolo, não sobre o código |
| 5.5 | Conferir a **equivalência da DoD** entre os arquivos que a declaram | `05-verificacao-pos-geracao.md`, item 3 | Equivalência de sensores e ordem, **não** de texto — ver exemplo abaixo |
| 5.6 | Conferir o frontmatter do subagente e da skill | `05-verificacao-pos-geracao.md`, item 4 | `description` precisa dizer **quando** usar, não só o que é: descrição vaga nunca dispara, e a skill fica no disco sem nunca ser invocada |
| 5.7 | Conferir que o AGENTS.md com escopo **não duplica o protocolo** | `05-verificacao-pos-geracao.md`, item 5 | Protocolo em dois lugares diverge na primeira edição, e aí o agente tem duas regras conflitantes |
| 5.8 | Conferir o nome convencional do lockfile, se a remediação foi aceita | `05-verificacao-pos-geracao.md`, item 6 | Recusa não é falha da geração — entra na lista de recusados, não na de erros |
| 5.9 | **Executar os sensores aceitos** uma vez e colar a saída | `05-verificacao-pos-geracao.md`, item 7 | Instalar a ferramenta e escrever a config **não é** entregar o sensor; entregar é ele executando. É aqui que aparece o `ImportError` por falta de stub, ou as 40 violações pré-existentes do linter |
| 5.10 | Emitir o **relatório final** com duas listas separadas | `05-verificacao-pos-geracao.md` | Ver exemplo abaixo |

### As 11 checagens do verificador (ação 5.1)

Todas existem porque o modo de falhar correspondente é **silencioso**:

| Checagem | O que ela impede |
|---|---|
| JSON dos configs parseia | JSON quebrado desliga o hook sem avisar ninguém |
| Scripts sem CRLF | O `\r` faz o shebang virar `/bin/sh^M`, o script morre com exit 1, e em `PreToolUse` isso significa "erro não-bloqueante": **o comando destrutivo executa** |
| Scripts executáveis | Sem o bit `+x`, o agente registra um hook que nunca roda |
| Gate bloqueia destrutivo (**exit 2**) | Testar só isto esconderia um gate que bloqueia *tudo* |
| Gate libera comando seguro (**exit 0**) | Testar só isto esconderia um gate que não bloqueia *nada* |
| `settings.json` tem o wrapper `hooks` | Sem o wrapper na raiz, nenhum scanner enxerga os hooks |
| Hooks registrados existem e executam | O pior caso silencioso: no Claude Code e no Devin o hook morre e o comando passa; no Cursor o `failClosed` transforma isso em bloqueio de tudo |
| Ponte `CLAUDE.md` alcança cada `AGENTS.md` | É a única checagem que separa "harness gravado" de "harness carregado" |
| Manifesto só lista arquivo existente | Manifesto mentiroso faz a atualização futura agir sobre ficção |
| `.gitignore` cobre `.env` | Credencial commitada |
| Nenhum marcador `<>` sobrou | Marcador vivo é template entregue pela metade |

O verificador **não exige Python**: onde existe, valida JSON com o parser de
verdade; onde não existe, cai para balanceamento de chaves e **diz isso na
saída**. Exigir Python transformaria a verificação em erro de setup
justamente nos repos Go, .NET e Java que a skill precisa atender.

### Exemplo 1 — O par de checagens do gate

Duas checagens, não uma, porque cada uma sozinha esconde o defeito oposto:

```
echo '{"tool_input":{"command":"rm -rf /"}}'  | gate  → espera exit 2  (bloqueou)
echo '{"tool_input":{"command":"npm test"}}'  | gate  → espera exit 0  (liberou)
```

Um gate que retorna sempre 2 passa no primeiro teste e é inutilizável na
prática — bloqueia `npm test`, o time desliga o hook, e o enforcement inteiro
vai junto. Os padrões que o gate realmente barra incluem `rm -rf`,
`git push --force` e `DROP TABLE|SCHEMA|DATABASE`.

### Exemplo 2 — Cronometrar a DoD é verificar o protocolo (ação 5.4)

O AGENTS.md manda rodar a DoD **a cada grupo**. Então o tempo dela não é
curiosidade — é o que decide se a regra vai ser cumprida:

```
$ time mvn verify
...
real    19m42s
```

Uma DoD de 20 minutos (suíte grande de Gradle, .NET, monorepo) não é rodada a
cada grupo por ninguém: o agente pula, o humano pula, e o WIP=1 vira texto sem
gate que o sustente. Acima de ~3 minutos, a skill leva à FASE 4 a proposta de
dividir em duas — a rápida por grupo e a completa antes do push — **dizendo
quais sensores ficariam em cada uma**.

Quem decide é o usuário: tirar um sensor da verificação por grupo é abrir mão
de detecção precoce, e o custo dessa troca depende do projeto.

### Exemplo 3 — Equivalência ≠ igualdade (ação 5.5)

Cada arquivo declara a mesma DoD no formato que o **seu** consumidor entende.
Exigir texto idêntico seria impossível por construção — e item impossível é
pior que item nenhum, porque o agente marca como ok sem ter verificado:

| Arquivo | Forma | Cobertura esperada |
|---|---|---|
| `AGENTS.md` | cadeia com `&&` | completa — **é a fonte** |
| `.claude/commands/dod.md` | a mesma cadeia | completa |
| `.github/workflows/harness-dod.yml` | um `- run:` por sensor | completa, mesma ordem |
| `openspec/config.yaml` (se gerado) | a mesma cadeia | completa |
| `.pre-commit-config.yaml` | um hook por sensor | só os que rodam sem rede |
| `init.sh` | passo de baseline | subconjunto: o runner de teste |

**É divergência:** sensor presente na fonte e ausente num consumidor de
cobertura completa, ou ordem trocada.
**Não é divergência:** o CI ter três `- run:` onde o AGENTS.md tem uma linha
com `&&`.

### Exemplo 4 — O relatório final tem duas listas, não uma (ação 5.10)

Porque o usuário age de forma diferente em cada uma:

```
RECUSADO OU ADIADO POR VOCÊ
  - Lockfile (uv.lock)
    Consequência: o init.sh pode instalar versões diferentes a cada
    execução, e o baseline verde de hoje não vale para amanhã

NINGUÉM PODE FECHAR AQUI
  - LICENSE: escolha jurídica, ainda por decidir
  - O token do GitHub em .cursor/mcp.json precisa ser rotacionado
```

Sem essa separação, um harness incompleto parece falha da skill quando na
verdade é uma escolha informada do usuário.

---

## FASE 6 — Fechamento do gate de CI

**O que acontece aqui:** a última fase cuida do único enforcement que ninguém
consegue pular.

> **A hierarquia do enforcement:** pre-commit e hooks de agent loop são
> **locais** — valem na máquina de quem instalou, e `git commit --no-verify`
> os contorna. O CI é **remoto**: roda em todo push, para todo mundo, sem
> depender de setup local. Sem ele, a DoD é opcional na prática.

| Ordem | Ação | Arquivo que direciona | Objetivo |
|---|---|---|---|
| 6.1 | Repo **sem** CI (workflow foi gerado): confirmar que `runs-on: ubuntu-latest` serve | `06-lembrete-ci.md` | Numa org com runner self-hosted, `ubuntu-latest` faz o workflow falhar em silêncio ou nunca ser agendado — e é preciso trocar **antes** do primeiro push |
| 6.2 | Repo **com** CI (nada gerado): verificar se a DoD já roda no pipeline; se não, apresentar o step proposto e onde ele entraria | `06-lembrete-ci.md` | Fechar o gate sem editar pipeline alheio: runners, schemas e pipelines reusáveis variam, e quem conhece o pipeline é o time |
| 6.3 | Avisar que **o harness pode ser desfeito sem ninguém notar** e sugerir as duas proteções mais baratas | `06-lembrete-ci.md` | Ver exemplo abaixo |
| 6.4 | Emitir a tabela final de sucesso | `06-lembrete-ci.md`, "✅ SUCESSO" | Fechamento explícito, com o que foi entregue em cada camada |

### Exemplo — O risco que fecha o fluxo (ação 6.3)

Um hook apagado, um sensor removido do manifesto, um `AGENTS.md` com escopo
que sumiu num merge: **nada disso quebra o build**. Ninguém descobre até um
agente causar exatamente o dano que o harness existia para evitar.

As duas proteções mais baratas, ambas sugeridas ao usuário e nenhuma imposta:

```
1. Fazer o CI falhar se os scripts referenciados em .claude/settings.json
   não existirem no repositório
   → hook apontando para arquivo ausente falha aberto e passa despercebido

2. Rodar o próprio gate com um comando destrutivo simulado e exigir exit 2,
   do mesmo jeito que a FASE 5 faz
   → é o teste que prova que a proteção continua ligada
```

A skill descreve o que precisa ser protegido e deixa a implementação com quem
conhece o pipeline — ela não escolhe ferramenta de auditoria pelo usuário.

---

## Catálogos consultados sob demanda

Não são fases: são tabelas lidas **quando uma fase as cita por link**. É o que
permite as seis fases serem curtas.

| Catálogo | Quem consulta | Para quê |
|---|---|---|
| [references/ecossistemas.md](references/ecossistemas.md) | FASE 1 (itens 0 e 9), FASE 2 | Comandos, formatter, lockfile e glob por stack. É **fonte única** — existe para o mesmo repo não receber um formatter na descoberta e outro no preenchimento |
| [references/remediacoes.md](references/remediacoes.md) | FASE 1, FASE 2, FASE 4 | O que recomendar, com o comando exato, e de quem é a decisão (grupos A/B/C) |
| [references/atualizacao.md](references/atualizacao.md) | FASE 1 (passo 0), FASE 3 | Como agir quando o repo já tem `.claude/harness.json` |
| [references/arquivos-gerados.md](references/arquivos-gerados.md) | FASE 2 | Mapa template → destino → condição, e como cada um dos três agentes registra os hooks |
| [references/conceitos-protocolo.md](references/conceitos-protocolo.md) | qualquer fase | Glossário: grupo, WIP=1, DoD, handoff |
| [MUDANCAS-NO-REPOSITORIO.md](MUDANCAS-NO-REPOSITORIO.md) | ao explicar ao usuário | O que a skill cria, modifica, propõe e nunca faz — escrito para quem vai aprovar |

### Os três agentes-alvo

O harness precisa funcionar em **Claude Code, Devin CLI e Cursor**. Os
scripts de hook são os mesmos nos três; o que muda é onde eles são
registrados e como o evento se chama:

| Agente | Onde registra | Comando de shell | Edição de arquivo |
|---|---|---|---|
| Claude Code | `.claude/settings.json` | `PreToolUse` + matcher `Bash` | `PostToolUse` + matcher `Edit\|Write\|MultiEdit` |
| Devin CLI | `.devin/hooks.v1.json` | `PreToolUse` + matcher `exec` | `PostToolUse` + matcher `edit` |
| Cursor | `.cursor/hooks.json` | `beforeShellExecution` (`failClosed`) | `afterFileEdit` |

`exit 2` significa "bloquear" nos três. O Cursor manda `command`/`file_path`
no topo do JSON e os outros dois em `tool_input` — por isso os scripts leem os
dois formatos. E o `failClosed` existe porque o padrão do Cursor, quando um
hook falha, é **prosseguir**: sem essa chave, um gate quebrado libera o
comando.

**Limite conhecido:** skills e subagentes (`executar-grupo`,
`propor-regra-arch`) valem hoje só para o Claude Code — a documentação do
Devin descreve `.devin/` com skills e agents, mas não publica os paths, e
inventar um geraria arquivo que nenhuma ferramenta lê. A camada de instrução e
o `check-arch.sh`, que é shell puro, os três leem e executam. É por isso que a
cobertura de regra arquitetural mora no **runner** e não no agente: o runner é
portátil, o agente é um incremento.

---

## As 10 regras invioláveis

Valem em todas as fases. Cada uma vem com o modo de falhar que a originou —
sem ele não há como julgar os casos que a regra não previu.

| # | Regra | O que acontece quando é quebrada |
|---|---|---|
| 1 | Não perguntar qual caminho seguir | Devolve ao usuário a triagem que a skill existe para fazer |
| 2 | Templates são transcritos VERBATIM | Cada repo recebe uma regra ligeiramente diferente, e a inconsistência só aparece meses depois, quando duas equipes comparam os próprios AGENTS.md |
| 3 | Toda informação da descoberta cita o arquivo-fonte | Uma DoD com o comando errado passa a bloquear todo commit do time |
| 4 | Nunca copiar credencial literal de MCP — converter para `${VAR}` | Copiar o segredo para a raiz o torna mais visível e mais provável de ser commitado |
| 5 | Não gerar enforcement vazio | Pre-commit sem hook e CI que passa sem rodar nada dão um verde que ninguém mereceu — pior que não ter, porque parece ter |
| 6 | Toda lacuna vira item do Plano de Remediação | Diagnosticar sem receita devolve ao usuário o trabalho da skill |
| 7 | Detectar **ecossistema**, não linguagem | Maven ≠ Gradle, Angular ≠ React: o resultado é uma DoD que não roda |
| 8 | Nunca gerar artefato estranho à stack | Um `package.json` num repo .NET é o sinal visível de que a descoberta errou — e o usuário perde a confiança no resto do harness, com razão |
| 9 | `CLAUDE.md` com `@AGENTS.md` ao lado de **cada** `AGENTS.md` | Nada falha, nada quebra — o agente apenas ignora o protocolo |
| 10 | O harness vale para os três agentes-alvo | Registrar hooks só de um deixa os outros dois sem enforcement, e ninguém percebe até alguém rodar um comando destrutivo no agente errado |

---

## Ecossistemas suportados

A unidade de detecção é o **ecossistema**, não a linguagem: Maven e Gradle
são Java e divergem em todos os comandos que a skill preenche, e Angular,
React e Node são JS/TS e também. Cada um destes foi verificado gerando o
harness num repositório real da stack e executando o resultado.

| Ecossistema | Detectado por |
|---|---|
| Node / TypeScript | `package.json` |
| React | `react` em `dependencies` |
| Angular | `angular.json` |
| Java / Maven | `pom.xml` |
| Java / Gradle | `build.gradle` |
| .NET / C# | `.sln`, `.csproj` |
| Go | `go.mod` |
| Python | `pyproject.toml`, `setup.py` |
| Rust | `Cargo.toml` |
| Ruby | `Gemfile` |
| PHP | `composer.json` |
| Monorepo JS | `workspaces`, `pnpm-workspace.yaml`, `nx.json`, `turbo.json` |

Nenhum template é específico de uma linguagem: todos usam placeholders
`<>` preenchidos via descoberta. Os comandos de teste, lint, tipos e
formatação de cada ecossistema, os nomes de lockfile e o padrão de arquivo
do hook de formatação vivem numa única tabela, em
[references/ecossistemas.md](references/ecossistemas.md) — de propósito,
para não haver duas fontes da mesma verdade divergindo com o tempo.

---

## Benefícios por conceito de Harness Engineering

A tabela abaixo explica o valor de cada peça. A lista canônica de arquivos,
destinos e condições está em
[references/arquivos-gerados.md](references/arquivos-gerados.md).

| Conceito | O que a skill gera | Benefício |
|----------|-------------------|-----------|
| **AGENTS.md** (contexto) | Arquivo raiz com descrição do projeto, comandos reais, convenções | O agente sabe o que é o projeto e como trabalhar nele sem explorar o repo |
| **AGENTS.md com escopo** | Arquivo no diretório de código com as restrições daquele diretório | Conhecimento perto do código; a raiz não vira um arquivo gigante carregado a cada request |
| **Skill `executar-grupo`** | `.claude/skills/executar-grupo/SKILL.md` com o procedimento de fechar um grupo | Procedimento carregado sob demanda, não em todo request |
| **Workflow de CI** | `.github/workflows/harness-dod.yml` com um step por comando da DoD (só se o repo não tiver CI) | Enforcement remoto: `--no-verify` não contorna. Um step por sensor faz o build vermelho já dizer qual falhou |
| **Gate de integridade** | Step no CI que confere os hooks e executa o gate | O harness não é desfeito em silêncio — apagar um hook deixa o CI vermelho |
| **Verificação pós-geração** | FASE 5 valida cada artefato e executa o gate hook | O resultado é evidência de comando, não afirmação — a mesma regra que a skill impõe ao agente |
| **Plano de Remediação** | Lista do que a skill **não** gera sozinha (instalar pytest/ruff, primeiros testes, `.env.example`), com comando exato e impacto | Você fica sabendo tudo que falta, não só o que a skill sabe escrever; instalar dependência é decisão sua, então confirma item a item |
| **Definition of Done (DoD)** | Os MESMOS comandos reais no AGENTS.md, no `/dod`, no init.sh, no pre-commit e no CI | "Concluído" é evidência de comando passando. A redundância é deliberada: DoD divergente faz o agente verificar uma coisa e o CI cobrar outra |
| **Grupos / Checkpoints** | Estrutura de tasks em grupos coesos de 2-5 unidades com `Verificação:` | Escopo, verificação e commit alinhados numa fronteira física |
| **WIP=1** | Regra no AGENTS.md que proíbe avançar antes do grupo atual estar verificado e commitado | Evita código meio-feito e overreach do agente |
| **init.sh** (ritual de abertura) | Script que instala deps, roda baseline de testes e mostra estado persistido | Sessão começa em <3 min com estado executável, sem exploração |
| **SESSION_STATE.md** (continuidade) | Arquivo de estado atualizado a cada commit de grupo | Agente retoma trabalho de onde parou após reset de contexto |
| **Hooks de agent loop** (enforcement) | `gate-destructive.sh` bloqueia o irreversível — `rm -rf`, `git push --force`, `DROP TABLE`, publicação de pacote (`npm publish`, `mvn deploy`, `dotnet nuget push`) e `terraform destroy` — e `format-on-edit.sh` formata a cada edit | O comando destrutivo não chega a executar; `npm test` e `mvn test` passam sem atrito, porque gate que atrapalha é gate que o time desliga |
| **Mesmos hooks nos três agentes** | Um registro por agente (Claude Code, Devin CLI e Cursor) apontando para os mesmos scripts, que leem os dois formatos de entrada e não dependem de Python instalado | A proteção não fica valendo só no agente que o autor do harness usava; trocar de ferramenta não desliga o gate |
| **Pre-commit portátil** | `.pre-commit-config.yaml` com lint/format/build da linguagem detectada | Sensores baratos rodam antes do commit existir — feedback mais cedo possível |
| **Comando `/dod`** | `.claude/commands/dod.md` com o mesmo comando da DoD | Agente verifica conclusão com um comando, sem relembrar os passos |
| **Registro de regras arquiteturais** | `.harness/arch-rules.json` + `.claude/check-arch.sh` na cadeia da DoD, e o agente `propor-regra-arch` que sugere regras novas sem poder escrevê-las | Cada classe de erro é cometida uma vez só: revisor julga caso a caso e esquece, regra fica. E o agente não pode enfraquecer a regra que o está reprovando |
| **OpenSpec config** | `openspec/config.yaml` com regras de execução (se `openspec/` existir) | Spec-Driven Development com workflow integrado ao harness |
| **Lockfile** | Geração do lockfile apropriado à linguagem detectada, se não existir | Instalações reproduzíveis — sensores testam a mesma árvore de deps em todo lugar |
| **`.editorconfig`** (universal) | `editorconfig-base` com regras universais + mescla de regras específicas (ex: .NET analyzers) | Linter e formatter configurados via um arquivo, para qualquer linguagem |
| **`.gitignore` + `.env`** | Append de `.env` / `.env.*` se não estiverem cobertos | Credenciais nunca commitadas por acidente |
| **LICENSE** | Oferta de licença apropriada se não existir | Repo pronto para distribuição |
| **MCP hygiene** | `.mcp.json` na raiz se detectado em outro path, com credencial literal convertida para `${VAR}` | Config centralizada, e um segredo nunca é copiado para um lugar mais visível do que já estava |
| **Degradação graciosa** | Fonte de trabalho com precedência (OpenSpec → TASKS.md), respeitada também pela skill `executar-grupo` | Harness funciona com ou sem OpenSpec; removida a ferramenta, tudo continua operando |
