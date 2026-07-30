# FASE 2 — Preenchimento VERBATIM dos templates

**Objetivo:** Ler cada template aplicável em `resources/` e gerar o arquivo
de destino exatamente como está no template.
**Precondições:** Fase 1 concluída, Relatório de Descoberta aprovado.

---

## Conteúdo

- REGRA PRINCIPAL
- REGRA DE HONESTIDADE (enforcement vazio não se gera)
- REGRA DE GRAVAÇÃO
- Camada de instrução
- Camada de enforcement
- ➡️ Fase 2 concluída — siga direto para a Fase 3

---

## REGRA PRINCIPAL

Não parafraseie, não resuma, não reordene, não "melhore" o texto do
protocolo. As ÚNICAS alterações permitidas são preencher os trechos
marcados com `<>`.

## REGRA DE HONESTIDADE (enforcement vazio não se gera)

Se a Fase 1 não encontrou NENHUM comando real de teste/lint/types, a
Definition of Done está vazia — e enforcement sem o que verificar é pior
que a ausência dele: passa verde sempre e dá confiança falsa de que
algo foi verificado.

Nesse caso, **não gerar** `.pre-commit-config.yaml` nem
`.github/workflows/harness-dod.yml`.

Mas não pare em "pendência": **proponha a correção**. Monte o item de
sensores do [catálogo de remediações](remediacoes.md) com os comandos
exatos da linguagem detectada, os arquivos de config prontos e os
primeiros testes propostos sobre funções puras reais do repositório —
para o usuário aceitar ou recusar na FASE 4. Diagnosticar sem receita
transfere ao usuário justamente o trabalho que a skill existe para fazer.

Se ele aceitar, os sensores passam a existir, a DoD deixa de ser vazia, e
`.pre-commit-config.yaml` e o workflow de CI **são gerados nesta mesma
execução** — refaça o preenchimento da DoD com os comandos novos antes de
gravar. Se recusar, nada de enforcement é gerado, e a consequência é
reportada sem insistir: o `/dod` fica sem o que executar e "concluído"
volta a ser julgamento do agente.

Gerar mesmo assim, com steps `# TODO`, seria a skill violando a própria
regra de que "concluído = comando passando". Vale também para a DoD do
AGENTS.md: `# TODO: definir comando de teste` é honesto; inventar
`pytest` num repo sem um único teste, não.

A diferença entre inventar e recomendar é o consentimento. Escrever
`pytest` na DoD de um repo sem testes é fabricar evidência. Propor
"instalar pytest, com esta config e estes três testes, aceita?" é a
skill fazendo seu trabalho — e só vira arquivo depois do sim.

## REGRA DE GRAVAÇÃO

Todo arquivo é gravado com quebra de linha **LF**, sem exceção. Um `\r`
num `.sh` transforma o shebang em `/bin/bash^M` e faz o script morrer com
exit 1 — no gate hook isso significa **falhar aberto**: a operação
destrutiva executa. O `.editorconfig` gerado declara `end_of_line = lf`;
os arquivos gerados têm de obedecer o que eles próprios prescrevem.

## Camada de instrução

- `<DoD>` / comandos da Definition of Done: comandos reais descobertos,
  encadeados com `&&`, priorizando o que o CI exige. Usar OS MESMOS
  comandos no AGENTS.md, no config.yaml e no passo de baseline do init.sh
  (redundância deliberada; nunca versões divergentes).
- `<MUST NOT>`: 3-6 restrições derivadas de convenções REAIS encontradas
  (ex.: padrão de acesso a dados, ferramenta de migration). Nunca inventar
  restrições genéricas sem evidência.
  - "Não alterar migrations já aplicadas — criar nova" é uma boa restrição
    **quando a Fase 1 encontrou ferramenta de migration**, e entra como uma
    das `<restrição N>`. Ela já esteve fixa no template, fora de placeholder:
    todo repositório recebia uma regra sobre um banco que muitos não têm, e
    o agente que transcrevia VERBATIM violava a regra de não inventar
    restrição. Restrição sem evidência ensina o leitor a ignorar a lista.
- Descrição do projeto e stack no topo do AGENTS.md, e comandos do
  init.sh: conforme a Fase 1, com a fonte citada.
- `<branch-base>`: o nome real descoberto no item 19 da Fase 1 — o default
  do remoto, não um palpite. `main`, `master`, `develop` e `trunk` são
  todos comuns, e o AGENTS.md gerado usa este nome num `git checkout` que o
  agente roda antes de qualquer funcionalidade nova: errado, ele falha com
  `pathspec did not match` logo na primeira sessão. Se a Fase 1 devolveu
  NÃO ENCONTRADO (repo sem git, sem remoto), preencher com
  `# TODO: definir branch base` e registrar como pendência — nunca chutar.
- `<como-propor-mudanca-de-plano>`: depende da fonte de trabalho detectada
  no item 8 da Fase 1, e as duas variantes são mutuamente exclusivas.
  - **Com `openspec/`**, transcrever:
    ```
    Para criar ou modificar planos (proposals, specs, tasks), use os comandos
    OpenSpec (`/opsx:propose`, `/opsx:apply`) — nunca edite artefatos de
    `openspec/` manualmente.
    ```
  - **Sem `openspec/`** (o repo recebeu `TASKS.md`), transcrever:
    ```
    Para criar ou modificar o plano, acrescente o grupo ao `TASKS.md` no
    formato descrito abaixo e confirme com o usuário antes de executá-lo.
    ```
  Mandar usar `/opsx:propose` num repo sem OpenSpec é instruir o agente a
  chamar um comando que não existe: ele para no meio do fluxo ou inventa
  um caminho. A skill `executar-grupo` já resolve essa bifurcação em tempo
  de execução; o AGENTS.md tem de concordar com ela.
- **Comandos do init.sh invocam a ferramenta pelo interpretador, não pelo
  executável solto**: `python3 -m pip`, `python3 -m pytest`, `npx tsc`.
  Em muitas instalações `pip` e `pytest` não existem no PATH, e como o
  init.sh roda com `set -e`, a sessão morre no passo 1 — antes de o
  agente ver qualquer estado. O mesmo vale para qualquer comando que
  dependa de um venv que talvez não esteja ativo.
- Comando NÃO ENCONTRADO → placeholder `# TODO: definir comando de teste`
  e registrar como pendência. Jamais alucinar um comando plausível.
- `<ferramentas-do-harness>`: ponteiros para a camada de enforcement, uma
  linha por artefato **efetivamente gerado**. Transcrever apenas as que se
  aplicam:
  ```
  - Para fechar um grupo do plano: skill `executar-grupo` (passo a passo).
  - Para verificar a Definition of Done: comando `/dod`.
  - Hooks de agent loop ativos: gate de comandos destrutivos e formatação
    automática a cada edição.
  - Para conferir se o protocolo vem sendo seguido:
    `sh .claude/medir-aderencia.sh` (diagnóstico, não gate).
  ```
  Sem esses ponteiros a corrente arrebenta no meio: a skill `executar-grupo`
  guarda o procedimento inteiro e só é carregada se o agente souber que ela
  existe. O AGENTS.md é o único arquivo que ele lê sempre — é dali que a
  camada de enforcement precisa ser alcançável. Se um artefato não foi
  gerado (o repo já tinha skills, já tinha subagente), a linha dele não
  entra: apontar para o que não existe é pior que não apontar.
- **AGENTS.md com escopo** (`resources/AGENTS-scoped.md` → `<dir-principal>/AGENTS.md`):
  gerar SEMPRE que a Fase 1 não tiver encontrado contexto com escopo. É o
  arquivo que leva o conhecimento para perto do código, em vez de manter
  tudo na raiz sendo carregado a cada request.
  - `<caminho>`: o diretório de código principal descoberto na Fase 1.
  - Restrições: AS MESMAS `MUST NOT` do AGENTS.md raiz que se aplicam a
    este diretório — não inventar restrições novas nem genéricas.
  - **NUNCA duplicar o protocolo** (grupos, WIP=1, DoD, handoff) aqui: ele
    vive só na raiz. Este arquivo é escopo, não protocolo.
  - Monorepo: um por pacote relevante, cada um com suas próprias regras.
- **Ponte `CLAUDE.md`** (`resources/CLAUDE.md` → `/CLAUDE.md` e
  `<dir-principal>/CLAUDE.md`): copiar VERBATIM, sem placeholders — é só a
  linha `@AGENTS.md` sob um comentário. Gerar nos DOIS destinos, um ao lado
  de cada AGENTS.md gerado.
  - Motivo: **o Claude Code carrega `CLAUDE.md` e não carrega `AGENTS.md`**,
    nem na raiz nem em subdiretório. Sem a ponte, o AGENTS.md é gravado mas
    nunca entra no contexto — o harness fica completo no disco e ausente na
    sessão, que é o modo mais silencioso de falhar: nada quebra, o agente
    só ignora o protocolo.
  - O `@` é import, não cópia: o conteúdo continua num lugar só, e os
    agentes que leem `AGENTS.md` direto (Devin, Codex) não são afetados.
    NUNCA duplicar o conteúdo do AGENTS.md aqui — duas cópias divergem na
    primeira edição.
  - Caminho relativo ao arquivo que importa, então a MESMA linha
    `@AGENTS.md` resolve para o irmão em qualquer um dos dois destinos.
- **Skill `executar-grupo`** (`resources/skills/executar-grupo/SKILL.md` →
  `.claude/skills/executar-grupo/SKILL.md`): copiar VERBATIM, sem
  placeholders. Empacota o procedimento de fechar um grupo, que é
  conhecimento sob demanda — carregá-lo em todo request via AGENTS.md
  desperdiça contexto. Gerar só se a Fase 1 não encontrou skills.

## Camada de enforcement

- `<dod-command>` no `dod-command.md`: o MESMO comando da DoD do AGENTS.md.
- `<formatter_command>` no `format-on-edit.sh`: comando de formatação da
  linguagem detectada, **conforme a coluna Formatter de
  [ecossistemas.md](ecossistemas.md)** — ela é a fonte única (ex.: Python é
  `ruff format`; JS/TS é `prettier --write`).
- `<formatter_bin>` no `format-on-edit.sh`: nome do binário do formatter
  (ex.: `ruff`, `prettier`, `gofmt`, `rustfmt`). É testado com
  `command -v`, então precisa ser o executável, não a linha inteira.
- **Sem formatter detectado**, preencher os DOIS com `formatter-nao-definido`
  e registrar a pendência no relatório. O `command -v` falha, o hook vira um
  no-op e o script continua válido.
  Nunca preencher com `# TODO`: o marcador do binário fica dentro da linha
  `if command -v ... ; then`, e o `#` comenta o resto dela — inclusive o
  `then`. O resultado é um `format-on-edit.sh` com erro de sintaxe que morre
  a cada edição de arquivo, e nenhum item da FASE 5 acusa isso. O `# TODO`
  é honesto no AGENTS.md, onde é texto; dentro de shell ele é um bug.
- `<sln>` (somente .NET): caminho do `.sln` ou do `.csproj` principal
  descoberto na Fase 1. Aparece nos exemplos de DoD, de pre-commit e no
  `format-on-edit.sh` da stack .NET. Se sobreviver à geração, todo comando
  `dotnet` do harness falha na primeira execução.
- `<file_glob>` no `format-on-edit.sh`: padrão de arquivos da linguagem.
  Vira um padrão de `case`, que **não faz brace expansion** — `*.{js,ts}`
  não casa com nada e o hook para de formatar sem erro nenhum. Para várias
  extensões, use alternância: `*.js|*.ts|*.jsx|*.tsx`. Um por ecossistema,
  conforme [ecossistemas.md](ecossistemas.md).
- `<pre-commit-hooks>` no `pre-commit-config.yaml`: blocos de hooks
  derivados dos comandos de lint/format/types descobertos. Cada hook
  segue o padrão:
  ```
      - id: <nome>
        name: <descrição>
        entry: bash -c '<comando>'
        language: system
        pass_filenames: false
        files: <glob da linguagem>
        stages: [pre-commit]
  ```
- **Workflow de CI** (`resources/ci-workflow.yml` →
  `.github/workflows/harness-dod.yml`): gerar SOMENTE se a Fase 1 não
  encontrou nenhuma configuração de CI. Sem CI prévio não há pipeline nem
  runner corporativo com que conflitar, e sem enforcement remoto a DoD
  vale apenas na máquina de quem lembrar de rodá-la.
  - `<setup-steps>`: os steps que preparam o runtime antes da DoD —
    `uses:` da action de setup da linguagem e o comando de restore de
    dependências. A tabela por ecossistema está no cabeçalho do próprio
    `resources/ci-workflow.yml` (Python, JS/TS, Go, .NET, Java, Rust).
    Usar a MESMA versão de runtime descoberta na Fase 1: setup de Node 20
    num projeto que exige 22 falha no `npm ci`, não na DoD, e o erro
    aponta para o lugar errado. Indentação de 6 espaços, como os demais
    steps do job.
  - `<dod-steps>`: um `- run:` por comando da DoD, na mesma ordem do
    AGENTS.md. Um step por sensor — assim o step vermelho já diz qual
    sensor falhou.
  - `<runner>`: `ubuntu-latest`, **sinalizando na FASE 4** que precisa
    trocar se a organização usar runner self-hosted.
  - O passo "Hooks intactos" vai pronto, sem preenchimento: ele confere
    que os scripts de hook ainda existem e que o gate ainda bloqueia. É o
    que impede o harness de ser desfeito em silêncio, já que remover um
    hook não quebra build nenhum.
  - Se o repo JÁ tem CI: não gerar nada — ver regra da FASE 3.
- Lockfile: gerar com o comando apropriado da linguagem detectada
  (`pip freeze > requirements.txt`, `npm install --package-lock-only`,
  `cargo generate-lockfile`, `go mod tidy`, `composer install`,
  `bundle install`). Usar sempre o **nome convencional do ecossistema**
  (ver Fase 1, item 10): um arquivo com nome inventado não é instalado por
  nenhuma ferramenta e não conta como lockfile. Se o projeto usa uv ou
  poetry, o lockfile é `uv lock` / `poetry lock`, não `pip freeze`.
  **.NET e Java/Maven não têm
  lockfile convencional** — .NET pode usar `packages.lock.json` (opt-in)
  e Maven usa `mvn dependency:lock` (não padrão); registrar como
  pendência e deixar o usuário decidir.
- `.mcp.json`: se MCP detectado em path não-raiz, copiar o conteúdo
  para `/.mcp.json`. Se já estiver na raiz, não duplicar.
  **Se a Fase 1 encontrou credencial literal, NÃO copiar o valor.**
  Substituir por interpolação de ambiente (`"token": "${GITHUB_TOKEN}"`),
  listar na FASE 4 cada variável que o usuário precisa exportar, e avisar
  que o segredo continua no arquivo de origem e deve ser rotacionado se
  já foi commitado. Copiar um segredo para a raiz o torna mais visível e
  mais provável de vazar — exatamente o contrário do objetivo da cópia.
- `.editorconfig`: se não existir `.editorconfig`, copiar
  `resources/editorconfig-base` para `/.editorconfig` (regras universais).
  Para linguagens com regras específicas (ex: .NET/C# com
  `dotnet_naming_rule` e `dotnet_diagnostic.*`), mesclar as regras do
  template específico (`resources/editorconfig-dotnet` como exemplo) sobre
  o base. Se houver template específico para a linguagem detectada, usar;
  senão, usar apenas o base.
- `.gitignore`: se `.env` e `.env.*` não estiverem cobertos, fazer append
  das linhas:
  ```
  # Environment files (never commit credentials)
  .env
  .env.*
  !.env.example
  ```
  NUNCA sobrescrever o `.gitignore` existente — sempre append.
- **Fluxo de branches** no AGENTS.md da raiz:
  - `<prefixo-de-branch>`: o prefixo majoritário do histórico, COM o
    separador (`feature/`, `feat/`, `users/joao/`). Default `feature/` só
    quando não houver evidência — e nesse caso declare na FASE 4 que é
    default, não descoberta.
  - `<politica-de-entrega>`: uma linha por regra que a FASE 1 encontrou, no
    formato dos outros bullets da seção Commits. Exemplos do que sai daqui:
    "Após o commit do grupo, `git push` da feature branch e abra PR para
    `main` (`gh pr create`) — `CODEOWNERS` exige revisão." ou "Merges são
    diretos na `main`; não abrir PR." Sem evidência, escreva a linha que
    pede a decisão ao usuário em vez de inventar uma política.
- **Hook de formatação**: só gere `format-on-edit.sh` se a FASE 1 achou um
  formatter que **escopa por arquivo**. Quando ela registrou
  `SEM HOOK DE FORMATAÇÃO`, não gere o script E remova o registro dele dos
  três configs de hook (`claude-settings.json`, `devin-hooks.json`,
  `cursor-hooks.json`) — registro apontando para script inexistente é falha
  silenciosa, e no Cursor com `failClosed` derruba o shell do agente inteiro.
  A formatação vai para o pre-commit e o CI.
- **Regras arquiteturais** (`resources/arch-rules.json` →
  `.harness/arch-rules.json`, e `resources/check-arch.sh` →
  `.claude/check-arch.sh`, `chmod +x`): a semente vai VERBATIM, e as regras
  candidatas achadas na FASE 1 entram como itens novos da lista, cada uma com
  `id`, `description`, `check`, `expect`, `what`, `why` e `fix`.
  - `check` é um comando de shell; `expect` é `exit-0` (padrão) ou
    `exit-nonzero`, este último para a regra que afirma a AUSÊNCIA de algo.
  - `what`/`why`/`fix` nomeiam arquivo, função ou comando. Um `grep` sozinho
    bastaria para um humano; para um agente, não: ele vê comando falhando e
    quer fazê-lo parar de falhar, e sem o `why` o caminho mais curto é apagar
    a regra.
  - Se `.harness/arch-rules.json` já existir, **não toque** — ver
    [FASE 3](03-resolucao-conflitos.md). Regra nova vira item do Plano de
    Remediação.
  - `bash .claude/check-arch.sh` entra na DoD, ao lado dos outros comandos.
    Regra sem cabo para execução automática é documento, não sensor. Repo sem
    sensores mantém a DoD vazia: os arquivos são gerados, mas inventar uma DoD
    que só roda o check-arch daria um verde que o repositório não merece.
- **Agente propositor** (`resources/agents/propor-regra-arch.md` →
  `.claude/agents/propor-regra-arch.md`): preencher `<branch-base>` no comando
  de diff. VERBATIM no resto — inclusive a seção "O que você NÃO faz", que é
  a trava do desenho: o agente propõe regra, não veredito, e não tem
  ferramenta de escrita. Agente que pode editar as regras pode enfraquecê-las,
  e uma catraca que gira para os dois lados não é catraca.
  - Só Claude Code, como `executar-grupo`. Registrar na FASE 4 quando o
    usuário usar Devin ou Cursor: a cobertura de regra arquitetural desses
    dois vem do `check-arch.sh`, que é shell e roda em qualquer lugar.
- **Manifesto** (`resources/harness-manifest.json` → `.claude/harness.json`):
  preencher `<versao-da-skill>` com a `metadata.version` do `SKILL.md`,
  `<data-iso>` com a data da geração, `<ecossistema>` com a linha detectada
  na Fase 1, `<dod-command>` com a MESMA DoD dos outros arquivos, e a lista
  `arquivos` com todo caminho efetivamente gravado nesta execução — só o que
  foi gravado, não a tabela inteira de possibilidades. Os itens do Plano de
  Remediação recusados ou adiados vão em `recusados`.
  - É o único arquivo que se sobrescreve sem perguntar: ele descreve a
    execução atual, então manter a versão anterior seria registrar mentira.
  - Um harness sem manifesto não tem como ser atualizado depois: a próxima
    execução não distingue o que a skill gerou do que o usuário escreveu.
- `README.md`: se não existir na raiz, gerar um mínimo (o que é o projeto,
  como instalar, como rodar os testes — reaproveitando a descoberta) e
  apresentar na FASE 4. É o primeiro documento de orientação que agente e
  humano leem; um repo sem README obriga a exploração que o harness existe
  para eliminar. Se já existir, NUNCA sobrescrever.

---

## ➡️ Fase 2 concluída — siga direto para a Fase 3

Continue imediatamente para a [Fase 3](03-resolucao-conflitos.md). Os
arquivos ainda estão apenas preenchidos em memória; nada foi gravado.
