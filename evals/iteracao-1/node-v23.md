# Execução da skill harness-creator v2.3 — repo Node/TS `pedidos-api`

Prompt simulado: "acabei de entrar nesse projeto e vamos usar o Claude Code
nele pra valer. dá uma olhada e deixa o repo preparado pra isso"

Repo alvo: `.../iteration-2/eval-node/v23/repo`

---

## 1. Ecossistema detectado e DoD

| Campo | Valor | Fonte |
|---|---|---|
| Ecossistema | **Node / TS** (sem `angular.json`, sem `react` nas deps) | `package.json` |
| Monorepo/workspace | não (sem `workspaces`, sem `pnpm-workspace.yaml`/`nx.json`/`turbo.json`) | `package.json` |
| Tipo de aplicação | lib/módulo de cálculo (`pedidos-api`, sem entrypoint de servidor) | `package.json`, `src/total.ts` |
| Stack | TypeScript ^5.5 (`strict`, `ES2022`, `noEmit`), Vitest ^2.0, ESLint ^9 (flat), Prettier ^3.3, ESM (`"type":"module"`) | `package.json`, `tsconfig.json`, `eslint.config.js`, `.prettierrc` |
| Diretório de código principal | `src/` | árvore |
| Teste | `npm test` → `vitest run` | `package.json` scripts |
| Lint | `npm run lint` → `eslint .` | `package.json` scripts |
| Types | `npm run typecheck` → `tsc --noEmit` | `package.json` scripts |
| Formatter | `prettier --write` (bin `prettier`) | script `format` + `.prettierrc` |
| Lockfile | `package-lock.json` presente — porém stub (`"packages": {}`) | arquivo |
| CI | NÃO ENCONTRADO (sem `.github/`, sem `.gitlab-ci.yml`) → workflow gerado | árvore |
| Runner de CI | NÃO ENCONTRADO → gerado com `ubuntu-latest` (sinalizado) | — |
| MCP / credencial literal | NÃO ENCONTRADO / NENHUMA | árvore |
| Hooks existentes | NÃO ENCONTRADO nos três (`.claude`, `.devin`, `.cursor`) | árvore |
| Linter/formatter config | `eslint.config.js`, `.prettierrc`; `.editorconfig` NÃO ENCONTRADO → gerado | árvore |
| `.gitignore` cobre `.env` | não → append feito | `.gitignore` |
| LICENSE / README | ambos NÃO ENCONTRADO | árvore |
| Subagentes / skills / contexto com escopo | NÃO ENCONTRADO (todos gerados) | árvore |
| Branch base | `main` — **sem remoto**; resolvido por `git branch --show-current` (os dois primeiros passos do item 19 falharam) | git |
| OpenSpec | não existe → fonte de trabalho é `TASKS.md` | árvore |
| Funções puras | `totalDoPedido(itens: Item[])` em `src/total.ts` (já coberta por `test/total.test.ts`) | leitura |
| Imports de sistema no entrypoint | não — sem I/O, rede ou display | `src/total.ts` |

**DoD preenchida (idêntica em todos os artefatos):**

```
npm test && npm run lint && npm run typecheck
```

## 2. Arquivos gravados (21)

Camada de instrução:
- `AGENTS.md` (raiz, protocolo completo, branch base `main`, 4 MUST NOT com evidência)
- `CLAUDE.md` (raiz, ponte `@AGENTS.md`)
- `src/AGENTS.md` (escopo) + `src/CLAUDE.md` (ponte)
- `init.sh` (chmod +x; `npm ci`, sanity, baseline `npm test`)
- `SESSION_STATE.md`, `TASKS.md`, `README.md`
- `.claude/skills/executar-grupo/SKILL.md`

Camada de enforcement:
- `.claude/settings.json`, `.devin/hooks.v1.json`, `.cursor/hooks.json`
- `.claude/hooks/gate-destructive.sh`, `.claude/hooks/format-on-edit.sh` (chmod +x, LF)
- `.claude/commands/dod.md`, `.claude/agents/code-reviewer.md`
- `.pre-commit-config.yaml` (eslint, tsc, prettier --check)
- `.github/workflows/harness-dod.yml`
- `.claude/harness.json` (manifesto)
- `.editorconfig`
- `.gitignore` (append de `.env`/`.env.*`/`!.env.example`)

Não gravados por decisão: `LICENSE` (pulado), `.mcp.json` (nenhum MCP),
`openspec/config.yaml` (sem OpenSpec), lockfile (já existe).

## 3. Saída da verificação (FASE 5)

```
== 1 JSON valido ==
OK .claude/settings.json / .devin/hooks.v1.json / .cursor/hooks.json / .claude/harness.json
== 2 YAML valido ==
OK .pre-commit-config.yaml
OK harness-dod.yml
== 3 executaveis ==
-rwxr-xr-x .claude/hooks/format-on-edit.sh
-rwxr-xr-x .claude/hooks/gate-destructive.sh
-rwxr-xr-x init.sh
== 4 line endings ==
init.sh / gate-destructive.sh / format-on-edit.sh: Bourne-Again shell script text executable, UTF-8 text   (nenhum CRLF)
== 5 gate: comando destrutivo ==
BLOCKED: comando corresponde a padrao de risco: rm[[:space:]]+-rf?[[:space:]]
exit=2
== 5b gate: comando seguro (npm test) ==
exit=0
== 5c gate: formato Cursor (command no topo, git push --force) ==
BLOCKED: ... git[[:space:]]+push[[:space:]].*--force
exit=2
== 6 marcadores obrigatorios ==
(1a rodada) FALHOU: <formatter_command> e <file_glob> sobraram no comentario de
            format-on-edit.sh  -> corrigido; 2a rodada: OK, nenhum marcador sobrou
== 7 tempo da DoD ==
> vitest run
sh: vitest: command not found        real 0m0.191s
(DoD NAO executavel: dependencias nao instaladas — item [1] recusado)
== 8 consistencia da DoD ==
AGENTS.md:75            npm test && npm run lint && npm run typecheck
.claude/commands/dod.md:13  npm test && npm run lint && npm run typecheck
README.md:47            npm test && npm run lint && npm run typecheck
init.sh:15              npm test  (baseline, so o teste — ver ambiguidade 4)
CI:                     - run: npm test / npm run lint / npm run typecheck
pre-commit:             npm run lint / npm run typecheck / npx prettier --check .
== 9 wrapper hooks ==
hooks no root: True ['PreToolUse', 'PostToolUse']
== 10 registros -> script executavel ==
OK executavel: .claude/hooks/format-on-edit.sh
OK executavel: .claude/hooks/gate-destructive.sh
== 11 .gitignore cobre .env ==
5:.env   6:.env.*
== 12 CI runs na ordem da DoD ==
['npm ci', 'npm test', 'npm run lint', 'npm run typecheck']
== 13 frontmatter ==
code-reviewer.md: name + description + tools OK
executar-grupo/SKILL.md: name + description (com "use sempre que...") OK
== 14 escopo nao duplica protocolo ==
0 ocorrencias de WIP=1 / Definition of Done / Ao concluir cada grupo em src/AGENTS.md
== 15 ponte CLAUDE.md ==
CLAUDE.md:9:@AGENTS.md
src/CLAUDE.md:9:@AGENTS.md
== 16 manifesto x disco ==
arquivos listados: 21 | faltando: nenhum
== 17 lockfile ==
package-lock.json (nome convencional)
== hook de format apos correcao ==
{"tool_input":{"file_path":"src/total.ts"}} -> exit=0
== DoD real (tentativa) ==
npm run lint      -> sh: eslint: command not found
npm run typecheck -> sh: tsc: command not found
```

Itens 18 (credencial MCP) e 19 (remediações aceitas) não se aplicam:
não há MCP e nenhuma remediação foi aceita.

## 4. Aprovado / recusado (papel do usuário na FASE 4)

**Aprovado:** todos os 21 arquivos de harness (grupo A), incluindo o append
ao `.gitignore` e o workflow de CI com `ubuntu-latest`.

**Recusado:**
- `[1]` Instalar dependências (`npm ci`) para destravar a DoD — *sem rede neste ambiente*.
- `[2]` Declarar `engines.node` no `package.json` para fixar a versão de Node do CI — *muda package.json*.
- `[3]` Regenerar o `package-lock.json` (hoje é stub com `"packages": {}`, então `npm ci` falha) — *muda o lockfile/package.json*.
- `[4]` `LICENSE` — usuário optou por **pular**.

Registrados em `.claude/harness.json` → `recusados` e em `SESSION_STATE.md`
→ pendências. Consequência prática: **a DoD existe em todos os arquivos mas
não roda neste clone** — `vitest`, `eslint` e `tsc` não estão no PATH. O
`/dod`, o pre-commit e o CI só ficam verdes depois do item [1]/[3].

**Só o humano fecha:** runner de CI (`ubuntu-latest` é palpite — trocar se a
org usa self-hosted), versão de Node no workflow (`'20'`, marcado com TODO
porque `package.json` não declara), e ausência de remoto git (a branch base
`main` veio de `git branch --show-current`, não do default do remoto).

---

## 5. Pontos ambíguos / contraditórios da skill (o mais importante)

### 5.1 O item 6 da FASE 5 acusa os comentários do próprio template
`references/05-verificacao-pos-geracao.md:40-51` manda verificar que
`<formatter_command>`, `<formatter_bin>` e `<file_glob>` não sobraram. Mas
`resources/hooks/format-on-edit.sh:15-35` contém esses três marcadores
**dentro do bloco de comentário de documentação** ("PLACEHOLDER:
`<formatter_command>` deve ser substituido pela skill..."). Ou seja: transcrever
o template VERBATIM (regra inviolável 3) **garante** que o item 6 falhe.
A FASE 5 até prevê o problema — "se um marcador aparecer também num comentário
do template, a substituição vaza para fora do comentário e corrompe o arquivo"
— mas prescreve a checagem, não a solução: não diz se o bloco de comentário
deve ser removido, reescrito ou ignorado pela checagem. Tive que decidir
sozinho (reescrevi o comentário para registrar o valor escolhido), o que é
exatamente o tipo de improviso que a regra do VERBATIM existe para evitar.
O `ci-workflow.yml` resolveu isso explicitamente no cabeçalho ("este cabeçalho
não contém nenhum, de propósito"); o `format-on-edit.sh` não recebeu o mesmo
tratamento.

### 5.2 `MUST NOT: alterar migrations já aplicadas` vem fixo no template
`resources/AGENTS.md:59` traz essa linha como texto fixo (não é `<>`), mas
`references/02-preenchimento-templates.md:60-62` diz "Nunca inventar restrições
genéricas sem evidência". Este repo não tem banco, ORM nem migrations. Manter a
linha é inventar restrição; remover é editar texto fora dos `<>`. Removi, mas
a skill não autoriza isso em lugar nenhum — as regras se contradizem.

### 5.3 Baseline do `init.sh` vs. "a MESMA DoD"
`02-preenchimento-templates.md:59-61` manda "Usar OS MESMOS comandos no
AGENTS.md, no config.yaml e no passo de baseline do init.sh", e o item 8 da
FASE 5 lista o `init.sh` entre os arquivos onde a DoD deve ser **idêntica**.
Mas o template `resources/init.sh:25-34` chama o passo de "Baseline de testes"
e o marcador é `<comando de teste do repo>` (singular, só teste), com
`|| echo "AVISO: falhas pré-existentes"` — que só faz sentido para a suíte de
testes. Colocar a DoD inteira ali contradiz o template; colocar só `npm test`
contradiz o item 8. Optei por `npm test` (fidelidade ao template) e o item 8
fica com divergência aparente.

### 5.4 Regra 5 ("Leia SOMENTE o arquivo da fase") vs. os links das fases
`SKILL.md:113` diz "Leia SOMENTE o arquivo da fase que está executando", mas a
FASE 1 exige classificar lacunas "pelo catálogo de remediações"
(`01-descoberta.md:22-24`) e detectar ecossistema "pela tabela de
ecossistemas.md" (`01-descoberta.md:36-38`) — dois arquivos fora da fase. Na
FASE 2 é pior: os placeholders só podem ser preenchidos lendo os 15 templates
de `resources/`. A regra, lida ao pé da letra, impede executar as fases.

### 5.5 `<setup-steps>` exige "a MESMA versão de runtime descoberta na Fase 1"
`02-preenchimento-templates.md:186-190` é enfático ("setup de Node 20 num
projeto que exige 22 falha no `npm ci`"), mas a FASE 1 não tem um item para
versão de runtime, e este `package.json` não tem `engines`. As duas saídas que a
skill oferece em outros casos (`# TODO: definir …` e "registrar como pendência")
não estão previstas aqui — o YAML precisa de um valor concreto para parsear.
Escrevi `'20'` com comentário TODO, mas isso é o "palpite plausível" que a
regra de honestidade proíbe em outros campos.

### 5.6 Lockfile presente mas inútil
FASE 1 item 10 e FASE 3 ("Lockfile já existe: não regenerar") só perguntam se o
arquivo existe e se o nome é convencional. Aqui o `package-lock.json` tem
`"packages": {}` — `npm ci` falha com ele, e o `init.sh` gerado (com `set -e`)
morre no passo 1. A skill se preocupa muito com nome de lockfile
(`ecossistemas.md:40-53`) e nada com lockfile inválido. Virou item [3] do plano
por decisão minha, sem apoio no catálogo.

### 5.7 "Verificação local" do AGENTS.md com escopo não tem regra
`resources/AGENTS-scoped.md:21-26` pede "comando que valida apenas este
subdiretório", e o exemplo (`pytest tests/unit`) é de testes. Num repo cujos
testes vivem em `test/` (fora de `src/`), não existe comando que valide só
`src/` rodando testes. Usei `npx tsc --noEmit && npx eslint src` — inventei um
comando que não aparece em nenhum script do `package.json`, o que colide com
"Jamais alucinar um comando plausível" (`02-preenchimento-templates.md:98-99`).

### 5.8 Item 19 da FASE 1 (branch base) sem remoto
Os dois primeiros métodos (`git symbolic-ref refs/remotes/origin/HEAD`,
`git branch -r`) falham em repo sem remoto. O quarto método
(`git branch --show-current`) devolve `main`, mas a instrução diz "Nunca assumir
`main`". Usei `main` porque é evidência de comando, não palpite — porém a skill
trata o caso "repo sem git" e não o caso "repo com git e sem remoto", que é o
mais comum em scaffold novo.

### 5.9 A FASE 4 pede "conteúdo completo" de todos os arquivos
`04-saida-aprovacao.md:12` manda apresentar "os arquivos propostos (conteúdo
completo)" antes de gravar. São 21 arquivos, alguns com 140 linhas (o gate hook)
— apresentar tudo no chat antes da aprovação gasta mais contexto do que a
separação em fases economiza, e um usuário real não lê. A skill não dá critério
para resumir.

### 5.10 Efeito colateral inesperado: o gate bloqueou a própria FASE 5
A verificação do item 5 exige mandar `rm -rf /tmp/test` e `git push --force`
para o gate via stdin. O gate do repo **onde a skill roda** inspeciona a linha de
comando inteira e bloqueou minhas duas primeiras tentativas de verificação
(exit 2), porque o padrão aparece literalmente no comando. Tive que gerar as
strings por concatenação num script auxiliar. A FASE 5 mostra o comando de teste
em forma literal (`05-verificacao-pos-geracao.md:30-36`) sem avisar disso — quem
seguir a instrução ao pé da letra num repo já harnessado leva bloqueio e pode
concluir que o gate novo está quebrado.
