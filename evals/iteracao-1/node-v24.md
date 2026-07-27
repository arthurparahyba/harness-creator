# Execução da skill `harness-creator` v2.4 — repo `pedidos-api` (Node/TS)

Prompt simulado: "acabei de entrar nesse projeto e vamos usar o Claude Code
nele pra valer. dá uma olhada e deixa o repo preparado pra isso" → pedido
vago sobre o repo estar pronto para agentes ⇒ fluxo completo (6 fases),
conforme a seção "Escopo" do SKILL.md.

---

## 1. Ecossistema detectado e DoD

Relatório de Descoberta (fonte citada por item):

```
- Ecossistema:                  Node / TS (package.json sem angular.json nem framework de UI)
- Monorepo/workspace:           não (sem `workspaces`, sem pnpm-workspace/nx/turbo)
- Tipo de aplicação:            módulo/lib de domínio (src/total.ts exporta função pura; sem servidor/CLI)
- Stack com versões:            TypeScript ^5.5 (strict, noEmit, ES2022 — tsconfig.json),
                                vitest ^2.0, eslint ^9 (flat config), prettier ^3.3 (package.json);
                                ESM (`"type": "module"`). Node local v26.3.0 (não declarado no repo)
- Diretório de código principal: src/
- Comando de teste:             `npm test` → `vitest run` (package.json scripts)
- Comando de lint/format:       `npm run lint` → `eslint .`; `npm run format` → `prettier --write .`
- Comando de types/build:       `npm run typecheck` → `tsc --noEmit`
- Comandos exigidos pelo CI:    NÃO ENCONTRADO (sem .github/workflows, sem .gitlab-ci.yml)
- Runner de CI:                 NÃO ENCONTRADO
- Formatter da linguagem:       prettier (.prettierrc + devDependency)
- Lockfile:                     package-lock.json (presente, porém `"packages": {}` — vazio)
- MCP servers:                  NÃO ENCONTRADO
- Credencial literal em MCP:    NENHUMA
- Hooks existentes:             NÃO ENCONTRADO (sem .claude/, .devin/, .cursor/)
- Linter/formatter config:      eslint.config.js + .prettierrc; .editorconfig NÃO ENCONTRADO
- .gitignore cobre .env:        não (só node_modules/ e dist/)
- LICENSE presente:             não
- README.md presente:           não
- Subagentes existentes:        NÃO ENCONTRADO
- Skills existentes:            NÃO ENCONTRADO
- Contexto com escopo:          NÃO ENCONTRADO
- Branch base do fluxo:         main (sem remoto; `git symbolic-ref refs/remotes/origin/HEAD` falha,
                                `git branch -r` vazio → `git branch --show-current` = main)
- CI presente:                  NÃO ENCONTRADO
- Ferramenta de migration:      NÃO ENCONTRADO (sem ORM/migrations na árvore)
- Convenções já documentadas:   NÃO ENCONTRADO (sem README/CONTRIBUTING/.cursorrules)
- OpenSpec presente:            não → fonte de trabalho = TASKS.md
- Funções puras candidatas:     n/a (sensores existem; `totalDoPedido` já tem teste)
- Imports de sistema no entrypoint: não
```

**DoD preenchida:** `npm test && npm run lint && npm run typecheck`

(usei os scripts reais do package.json em vez do exemplo do template
`npx tsc --noEmit`, porque o repo já expõe `typecheck`; ecossistemas.md
manda confirmar com os scripts reais.)

---

## 2. Arquivos gravados (21)

Camada de instrução:
- `AGENTS.md` (raiz, protocolo completo, DoD, 4 MUST NOT derivados de evidência)
- `CLAUDE.md` (raiz, ponte `@AGENTS.md` — verbatim)
- `src/AGENTS.md` (escopo: ESM, strict, eslint-disable, onde ficam os testes)
- `src/CLAUDE.md` (ponte — verbatim)
- `init.sh` (chmod +x, `npm ci` / `node --version` + lint / `npm test`)
- `SESSION_STATE.md` (preenchido com estado real e pendências)
- `TASKS.md` (esqueleto do template, verbatim)
- `README.md` (novo — não existia)
- `.claude/skills/executar-grupo/SKILL.md` (verbatim)

Camada de enforcement:
- `.claude/settings.json`, `.devin/hooks.v1.json`, `.cursor/hooks.json` (verbatim)
- `.claude/hooks/gate-destructive.sh` (verbatim, +x)
- `.claude/hooks/format-on-edit.sh` (+x; `*.js|*.ts|*.jsx|*.tsx|*.mjs|*.cjs`, `prettier`, `prettier --write`)
- `.claude/commands/dod.md`
- `.claude/agents/code-reviewer.md` (4 checks derivados do repo)
- `.claude/harness.json` (manifesto, com `recusados` preenchido)
- `.pre-commit-config.yaml` (eslint, tsc, prettier --check)
- `.github/workflows/harness-dod.yml` (não havia CI)
- `.editorconfig` (base)
- `.gitignore` (append de `.env`, `.env.*`, `!.env.example` — nunca sobrescrito)

Não gravados: `LICENSE` (usuário pulou), lockfile (já existe), `.mcp.json`
(sem MCP), `openspec/config.yaml` (sem OpenSpec).

---

## 3. Verificação da FASE 5 (saída real)

| # | Check | Resultado |
|---|---|---|
| 1 | JSON válido | OK: `.claude/settings.json`, `.devin/hooks.v1.json`, `.cursor/hooks.json`, `.claude/harness.json` |
| 2 | YAML válido | OK: `.pre-commit-config.yaml`, `.github/workflows/harness-dod.yml` |
| 3 | chmod +x | `-rwxr-xr-x` em `init.sh`, `gate-destructive.sh`, `format-on-edit.sh` |
| 4 | LF | `file` → "Bourne-Again shell script text executable, UTF-8 text" nos 3 (nenhum CRLF) |
| 5 | Gate hook | destrutivo → **exit 2** com `BLOCKED: ... rm[[:space:]]+-rf?[[:space:]]`; `npm test` → **exit 0** |
| 6 | Marcadores | 2 restantes, ambos **dentro do bloco de comentário do próprio template** de `format-on-edit.sh` (linhas 15 e 25) — ver ambiguidade A |
| 7 | Tempo da DoD | **NÃO EXECUTÁVEL**: `npm test` → `sh: vitest: command not found` (sem `node_modules`, sem rede). Reportado, não estimado |
| 8 | Consistência da DoD | idêntica em `AGENTS.md:71`, `.claude/commands/dod.md:13`, `README.md:32`; CI com 1 step por sensor na mesma ordem; `init.sh` usa os mesmos comandos separados (baseline); pre-commit idem — ver ambiguidade C |
| 9 | wrapper `hooks` | `hooks no raiz: True ['hooks']` |
| 10 | registros → script | `OK exec .claude/hooks/format-on-edit.sh`, `OK exec .claude/hooks/gate-destructive.sh` |
| 11 | `.gitignore` cobre `.env` | linhas 5-7 |
| 12 | CI = DoD | `['npm ci', 'npm test', 'npm run lint', 'npm run typecheck']` |
| 13 | frontmatter | `code-reviewer.md` e `executar-grupo/SKILL.md` com `name:`+`description:` |
| 14 | escopo sem protocolo | `src/AGENTS.md` não contém WIP=1/DoD/handoff/grupos |
| 15 | ponte CLAUDE.md | `CLAUDE.md:9:@AGENTS.md` e `src/CLAUDE.md:9:@AGENTS.md` (fora de crase) |
| 16 | manifesto x disco | `faltando: nenhum | total 21` |
| 17 | lockfile | `package-lock.json` (nome convencional) — porém vazio, ver recusa [2] |
| 18 | credencial MCP | n/a |
| 19 | remediações aceitas | nenhuma aceita ⇒ nada a executar |

FASE 6: repo não tinha CI ⇒ workflow gerado com `runs-on: ubuntu-latest`,
sinalizado para troca caso a organização use self-hosted. O passo "Hooks
intactos" (roda o gate e exige exit 2) já cobre a recomendação de impedir
que o harness seja desfeito em silêncio.

---

## 4. Aprovado / recusado (papel de usuário na FASE 4)

**Aprovado:** todos os 21 arquivos de harness (grupo A).

**Recusado (registrado em `.claude/harness.json:recusados` e em `SESSION_STATE.md`):**

| # | Item | Motivo | Consequência prática |
|---|---|---|---|
| 1 | `npm ci` para instalar deps | sem rede neste ambiente | a DoD nunca foi comprovada neste clone; `/dod` e pre-commit falham por `command not found` até haver `node_modules` |
| 2 | `npm install --package-lock-only` para regenerar o lock | sem rede | `package-lock.json` tem `"packages": {}` e não bate com as devDependencies ⇒ `npm ci` (init.sh e CI) vai falhar |
| 3 | `engines.node` no `package.json` | não alterar package.json | a versão do Node no workflow (`'20'`) é escolha, não evidência |
| 4 | `npx prettier --check .` na DoD | mudaria o contrato do projeto | formatação continua não verificada pela DoD (só pelo pre-commit, que é opcional) |

**Pendência só do humano:** `LICENSE` — escolhido **pular**.

---

## 5. Pontos ambíguos / contraditórios da skill (o mais importante)

### A. `resources/hooks/format-on-edit.sh` — o cabeçalho do template contradiz a FASE 5

`resources/hooks/format-on-edit.sh:15` e `:25` são comentários que dizem
"PLACEHOLDER: `<formatter_command>` deve ser substituido pela skill…" e
"PLACEHOLDER: `<file_glob>` …". Duas regras colidem:

- `SKILL.md:115` (regra inviolável 3): "Templates em `resources/` são
  transcritos VERBATIM: só os trechos `<>` mudam."
- `05-verificacao-pos-geracao.md:46-51`: `<formatter_command>`,
  `<formatter_bin>` e `<file_glob>` estão na lista dos marcadores que
  **não podem sobrar** no arquivo gerado.

Se eu transcrevo verbatim, o check 6 falha (e a FASE 5 diz que check
falhando "é defeito da geração, corrija antes de seguir"). Se eu apago o
comentário, violo a regra 3. Ironia: a própria FASE 5 avisa do risco
inverso ("se um marcador aparecer também num comentário do template, a
substituição vaza para fora do comentário e corrompe o arquivo"), ou seja,
o autor sabe que há marcador em comentário — mas não diz o que fazer com
ele. **Optei por transcrever verbatim e reportar.** O mesmo problema, não
detectado pelo grep nominal, existe em `resources/pre-commit-config.yaml`
(comentário com `dotnet format <sln>`) e no cabeçalho de
`resources/ci-workflow.yml`.

### B. `<formatter_bin>` num ecossistema Node é enforcement que nunca dispara

`02-preenchimento-templates.md:154-156`: "`<formatter_bin>`: nome do
binário do formatter (ex: `black`, `prettier`, `gofmt`, `rustfmt`). É
testado com `command -v`, então precisa ser o executável, não a linha
inteira." Em Node o prettier é dependência **local** — `command -v prettier`
falha em qualquer máquina que não o tenha global, e o hook sai 0 sem
formatar nada, exatamente o "para de formatar em silêncio" que a skill
diz querer evitar.

Pior: isso contradiz o parágrafo de `02-preenchimento-templates.md:92-97`
("Comandos do init.sh invocam a ferramenta pelo interpretador, não pelo
executável solto: `python3 -m pip`, `npx tsc`... senão a sessão morre").
A mesma preocupação vale para o hook, mas ali a instrução manda o
contrário. Hesitei bastante entre `prettier` e `npx prettier`; segui a
instrução literal porque o exemplo cita `prettier` nominalmente.
**Sugestão:** para JS/TS, `<formatter_bin>` = `npx` e
`<formatter_command>` = `npx prettier --write`.

### C. A "identidade" da DoD no `init.sh` e no pre-commit é impossível como escrita

`02-preenchimento-templates.md:60-63`: "Usar OS MESMOS comandos no
AGENTS.md, no config.yaml e no passo de baseline do init.sh (redundância
deliberada; nunca versões divergentes)". Mas o template do `init.sh`
(`resources/init.sh:34`) exige `<comando de teste do repo> || echo "AVISO..."`
— só o teste, e sem lint/typecheck, porque o baseline não pode parar no
primeiro erro. E `05-verificacao-pos-geracao.md:70-77` cobra a DoD
"IDÊNTICA" em 6 arquivos, incluindo `init.sh` e `.pre-commit-config.yaml`,
onde ela **estruturalmente não pode ser a mesma string** (um é `||`
tolerante, o outro é uma lista de hooks id/entry). Não dá para satisfazer
"idêntico" literalmente; interpretei como "mesmos comandos, não mesma
linha", mas a checagem não define isso.

### D. `resources/AGENTS.md:59` embute um MUST NOT sem evidência

A linha `- MUST NOT: alterar migrations já aplicadas — criar nova` está
na parte **fixa** do template (não é `<restrição N>`), enquanto
`02-preenchimento-templates.md:57-59` diz "Nunca inventar restrições
genéricas sem evidência" e `01-descoberta.md` manda registrar
"Ferramenta de migration: NÃO ENCONTRADO". Este repo não tem banco nem
migrations. Transcrever verbatim = gravar uma regra inventada; remover =
editar fora dos `<>`. **Removi a linha** e substituí por restrições com
evidência — mas a skill deveria marcar essa linha como condicional.

### E. Versão de runtime obrigatória, sem instrução para o caso NÃO ENCONTRADO

`02-preenchimento-templates.md:188-190`: "Usar a MESMA versão de runtime
descoberta na Fase 1: setup de Node 20 num projeto que exige 22 falha no
`npm ci`". O repo não declara versão (sem `engines`, sem `.nvmrc`, sem
CI). A skill tem regra explícita para comando NÃO ENCONTRADO
(`# TODO: definir comando de teste`) e para branch base
(`# TODO: definir branch base`), mas **nenhuma** para versão de runtime —
e um `node-version: '# TODO'` quebraria o YAML. Escolhi `'20'` e levei à
aprovação; a skill deveria mandar perguntar isso na FASE 4.

### F. `TASKS.md` é gravado como esqueleto de placeholders

`arquivos-gerados.md:20` manda gerar `TASKS.md` sempre que não houver
OpenSpec, e o template é só `## Grupo 1 - <objetivo coeso...>`. A FASE 5
lista `<objetivo>` e `<task>` como placeholders **ilustrativos que devem
permanecer** — ok — mas o resultado é que a "fonte de trabalho ativa" do
repo nasce sem nenhuma tarefa real, enquanto o AGENTS.md diz "Nunca invente
tarefas fora da fonte de trabalho ativa" e "Identifique o próximo grupo
desmarcado". Na prática o primeiro agente que rodar `./init.sh` encontra um
grupo de placeholders para executar. Não é erro de instrução, mas é um
estado inicial confuso que nenhuma fase comenta.

### G. Quem preenche o `SESSION_STATE.md` inicial não está dito

O template vem com `<hash>`, `<X/Y passando>` etc. Nenhuma fase diz se a
skill deve preenchê-lo com o estado atual ou gravá-lo em branco. A FASE 4
manda "registrar os adiados em `SESSION_STATE.md`", o que implica preencher,
mas o item 6 da FASE 5 não lista `<hash>`/`<X/Y passando>` entre os
proibidos **nem** entre os ilustrativos. Preenchi com o estado real.

### H. Ordem de leitura vs. regra 5 ("leia somente o arquivo da fase")

`SKILL.md:119-122` proíbe carregar as seis fases de uma vez, mas a FASE 2
só é executável depois de ler ~20 templates de `resources/` — que não são
"catálogos citados por link" e cujo custo de contexto é maior que o das
fases. A regra otimiza o que é barato e não menciona o que é caro.

### I. Sem instrução sobre `chmod +x` nos hooks fora do momento da gravação

`04-saida-aprovacao.md:80-81` menciona `chmod +x` só de passagem, na frase
sobre o commit. Um `cp` preserva o bit de execução do template, mas quem
gerar os arquivos escrevendo conteúdo (o caminho normal para um LLM)
produz `.sh` sem `+x`, e a FASE 5 item 3 só descobre depois. Vale um passo
explícito na FASE 2/4.

### J. Detalhe operacional

O gate hook do **repositório da skill** bloqueou a minha própria execução
do teste da FASE 5, porque o comando de verificação contém literalmente
`rm -rf /tmp/test` (`05-verificacao-pos-geracao.md:30`). Tive de montar o
JSON de teste via arquivo. A FASE 5 poderia sugerir o payload por
heredoc/arquivo, como o `ci-workflow.yml` já faz com `printf`.
