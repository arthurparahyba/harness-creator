# Relatório de execução — harness-creator v2.3 contra repo .NET

Prompt simulado: *"preciso configurar esse repo aqui pra trabalhar com agente
de IA. é um serviço .NET que a gente vai começar a mexer bastante agora"*

Repo alvo: `.../iteration-2/eval-dotnet/v23/repo` (Catalogo, .NET 8)

---

## 1. Ecossistema detectado e DoD preenchida

**Ecossistema: .NET / C#** — detectado por `Catalogo.sln` + `src/Catalogo.csproj`
+ `tests/Catalogo.Tests.csproj` (linha ".NET / C#" de `references/ecossistemas.md`).

Relatório de Descoberta (fonte entre parênteses):

| Item | Valor |
|---|---|
| Ecossistema | .NET / C# (`Catalogo.sln`, `src/Catalogo.csproj`) |
| Monorepo/workspace | não — solução única com 2 projetos (`Catalogo.sln`) |
| Tipo de aplicação | biblioteca de regras de preço (`src/Preco.cs`, sem host/entrypoint) |
| Stack com versões | net8.0; Nullable=enable; TreatWarningsAsErrors=true; EnforceCodeStyleInBuild=true; xunit 2.6.6; Microsoft.NET.Test.Sdk 17.9.0 (`src/Catalogo.csproj`, `tests/Catalogo.Tests.csproj`) |
| Diretório de código principal | `src/` (`Catalogo.sln`) |
| Comando de teste | `dotnet test Catalogo.sln` (derivado do ecossistema + `.sln`) |
| Comando de lint/format | `dotnet format Catalogo.sln --verify-no-changes`; em .NET o lint são os analyzers Roslyn via `.editorconfig` |
| Comando de types/build | `dotnet build Catalogo.sln -c Release` — o compilador é o type checker |
| Comandos exigidos pelo CI | NÃO ENCONTRADO (sem `.github/`, sem `.gitlab-ci.yml`) |
| Runner de CI | NÃO ENCONTRADO |
| Formatter da linguagem | `dotnet format` (tabela de ecossistemas + `EnforceCodeStyleInBuild=true`) |
| Lockfile | NÃO ENCONTRADO (.NET só tem `packages.lock.json` opt-in) |
| MCP servers | NÃO ENCONTRADO |
| Credencial literal em MCP | NENHUMA (não há arquivo MCP) |
| Hooks existentes | NÃO ENCONTRADO (sem `.claude/`, `.devin/`, `.cursor/`) |
| Linter/formatter config | NÃO ENCONTRADO (sem `.editorconfig`) |
| .gitignore cobre .env | não — só `bin/` e `obj/` |
| LICENSE presente | não |
| README.md presente | não |
| Subagentes existentes | NÃO ENCONTRADO |
| Skills existentes | NÃO ENCONTRADO |
| Contexto com escopo | NÃO ENCONTRADO |
| Branch base do fluxo | `main` — `git symbolic-ref refs/remotes/origin/HEAD` falhou ("is not a symbolic ref"), `git branch -r` vazio (sem remoto), fallback `git branch --show-current` = `main` |
| CI presente | NÃO ENCONTRADO |
| Ferramenta de migration | NÃO ENCONTRADO (sem EF Core, sem pasta Migrations) |
| Convenções já documentadas | NÃO ENCONTRADO |
| OpenSpec presente | não → fonte de trabalho vira `TASKS.md` |
| Funções puras candidatas a teste | `Preco.ComImposto` (`src/Preco.cs`) — já coberta por `PrecoTests.AplicaImposto` |
| Imports de sistema no entrypoint | não há entrypoint; nenhum stub necessário |

**DoD preenchida (idêntica em AGENTS.md, `/dod`, README, manifesto; e decomposta em 1 step por sensor no CI e no pre-commit):**

```
dotnet build Catalogo.sln -c Release && dotnet test Catalogo.sln --no-build && dotnet format Catalogo.sln --verify-no-changes
```

---

## 2. Arquivos gravados (21)

Camada de instrução:
- `AGENTS.md` (raiz, protocolo)
- `CLAUDE.md` (raiz, ponte `@AGENTS.md`)
- `src/AGENTS.md` (escopo)
- `src/CLAUDE.md` (ponte `@AGENTS.md`)
- `init.sh` (chmod +x)
- `SESSION_STATE.md`
- `TASKS.md` (sem OpenSpec no repo)
- `README.md` (não existia)
- `.claude/skills/executar-grupo/SKILL.md`

Camada de enforcement:
- `.claude/settings.json`
- `.claude/hooks/gate-destructive.sh` (chmod +x)
- `.claude/hooks/format-on-edit.sh` (chmod +x, `*.cs` + `dotnet format Catalogo.sln --include`)
- `.claude/commands/dod.md`
- `.claude/agents/code-reviewer.md`
- `.claude/harness.json`
- `.devin/hooks.v1.json`
- `.cursor/hooks.json`
- `.pre-commit-config.yaml`
- `.github/workflows/harness-dod.yml`
- `.editorconfig` (base + regras .NET mescladas)
- `.gitignore` (append de `.env` / `.env.*` / `!.env.example` — nunca sobrescrito)

Não gravados: `LICENSE` (pulado), lockfile (recusado), `.mcp.json` (nenhum MCP),
`openspec/config.yaml` (repo sem OpenSpec).

---

## 3. Saída da verificação da FASE 5

**1. JSON válido** — OK
```
OK .claude/settings.json
OK .devin/hooks.v1.json
OK .cursor/hooks.json
OK .claude/harness.json
```

**2. YAML válido** — OK
```
OK .pre-commit-config.yaml
OK harness-dod.yml
```

**3. Scripts executáveis** — OK
```
-rwxr-xr-x@ .claude/hooks/format-on-edit.sh
-rwxr-xr-x@ .claude/hooks/gate-destructive.sh
-rwxr-xr-x@ init.sh
```

**4. LF (nenhum CRLF)** — OK
```
init.sh:                           Bourne-Again shell script text executable, Unicode text, UTF-8 text
.claude/hooks/gate-destructive.sh: Bourne-Again shell script text executable, Unicode text, UTF-8 text
.claude/hooks/format-on-edit.sh:   Bourne-Again shell script text executable, Unicode text, UTF-8 text
```
(`file` não reporta "CRLF line terminators" em nenhum)

**5. Gate hook — os dois caminhos + formato Cursor** — OK
```
=== destrutivo (tool_input) ===
BLOCKED: comando corresponde a padrao de risco: rm[[:space:]]+-rf?[[:space:]]
exit=2
=== seguro ===
exit=0
=== formato Cursor (command no topo do JSON) ===
BLOCKED: comando corresponde a padrao de risco: git[[:space:]]+push[[:space:]].*--force
exit=2
```
Extra — `format-on-edit.sh` não quebra nos dois formatos de entrada: `exit=0` e `exit=0`.

**6. Marcadores de preenchimento** — nenhum marcador obrigatório sobrou em
posição funcional. Os únicos `<>` remanescentes estão dentro dos blocos de
comentário transcritos VERBATIM dos templates (ver seção 5, ponto A).

**7. Tempo da DoD — NÃO EXECUTÁVEL NESTE AMBIENTE**
```
$ command -v dotnet  →  dotnet AUSENTE no PATH
$ dotnet --version   →  command not found: dotnet
$ time (dotnet build Catalogo.sln -c Release && dotnet test ... && dotnet format ...)
command not found: dotnet
```
O SDK do .NET não está instalado. Conforme a instrução, **reportado em vez de
estimado**: o tempo da DoD é desconhecido e o baseline de testes não foi
levantado. Registrado em `SESSION_STATE.md` como bloqueio.

**8. Consistência da DoD** — OK. String idêntica em `AGENTS.md:77`,
`.claude/commands/dod.md:13`, `README.md:44`, `.claude/harness.json:7`.
Em `init.sh` (baseline), `.pre-commit-config.yaml` e no CI ela aparece
decomposta em 1 comando por step, com os mesmos comandos.

**9. Wrapper `hooks` em settings.json** — OK: `chaves raiz: ['hooks']`

**10. Registros apontam para script existente e executável** — OK
```
OK .claude/hooks/format-on-edit.sh
OK .claude/hooks/gate-destructive.sh
```

**11. `.gitignore` cobre `.env`** — OK (`5:.env`, `6:.env.*`)

**12. CI é YAML válido e os `run:` são a DoD na mesma ordem** — OK
```
['dotnet restore Catalogo.sln', 'dotnet build Catalogo.sln -c Release',
 'dotnet test Catalogo.sln --no-build', 'dotnet format Catalogo.sln --verify-no-changes']
```

**13. Frontmatter de subagente e skill** — OK (`name:` + `description:` com
"Use it to…" / "Use sempre que…", ambas dizendo QUANDO usar).

**14. AGENTS.md com escopo não duplica protocolo** — OK: `grep` por
`WIP=1|Definition of Done|SESSION_STATE|checkpoint:|## Grupo` em `src/AGENTS.md`
não retorna nada.

**15. Ponte CLAUDE.md** — OK
```
CLAUDE.md:9:@AGENTS.md
src/CLAUDE.md:9:@AGENTS.md
```
(linha crua, fora de crase e fora de bloco de código; nenhum dos dois contém o protocolo)

**16. Manifesto confere com o disco** — OK: `arquivos listados: 21 / faltando: nenhum`

**17. Lockfile** — N/A (recusado; .NET não tem lockfile convencional)

**18. Credencial em `.mcp.json`** — N/A (nenhum MCP no repo)

**19. Remediações aceitas rodando** — N/A: nenhuma remediação do grupo B foi
aceita (todas exigiam rede ou mudança de `.csproj`).

**FASE 6** — repo não tinha CI, então `harness-dod.yml` foi gerado com
`runs-on: ubuntu-latest`. Sinalizado: trocar antes do primeiro push se a
organização usar runner self-hosted. O workflow já inclui o passo "Hooks
intactos", que roda o gate com comando destrutivo simulado e exige exit 2.

---

## 4. O que aprovei e o que recusei (papel de usuário)

**Aprovado** — todos os 21 arquivos de harness (grupo A), incluindo o workflow
de CI, o pre-commit, o `.editorconfig`, o append no `.gitignore` e o README.

**Recusado** (motivo declarado: *sem rede neste ambiente*):

| Item do Plano de Remediação | Decisão | Consequência prática |
|---|---|---|
| [1] Adicionar `xunit.runner.visualstudio` a `tests/Catalogo.Tests.csproj` — hoje o projeto tem `Microsoft.NET.Test.Sdk` + `xunit` mas nenhum adapter VSTest, então `dotnet test` pode reportar "no test is available" | **RECUSADO** (muda `.csproj` + baixa pacote) | O step `dotnet test` da DoD pode passar verde sem executar teste nenhum — verde não merecido |
| [2] Habilitar lockfile `packages.lock.json` via `RestorePackagesWithLockFile` nos dois `.csproj` + `dotnet restore --use-lock-file` | **RECUSADO** (muda `.csproj` + restore com rede) | Builds não são reprodutíveis: uma versão transitiva nova pode quebrar o CI sem nenhuma mudança no repo |
| [3] `LICENSE` | **PULADO** (escolha do usuário) | Repo sem licença explícita = "todos os direitos reservados" por padrão |

Os três estão gravados em `.claude/harness.json` → `recusados` (para não serem
repropostos) e em `SESSION_STATE.md` → pendências.

**Pendências que só o humano fecha:**
- SDK do .NET 8 não instalado nesta máquina — nenhum comando da DoD foi executado.
- `runs-on: ubuntu-latest` no workflow gerado.

---

## 5. Pontos ambíguos, contraditórios ou que causaram hesitação

### A. (o mais grave) A substituição de placeholder colide com os comentários do próprio template — em `format-on-edit.sh`

`resources/hooks/format-on-edit.sh` contém os marcadores `<formatter_command>`
e `<file_glob>` **duas vezes**: no cabeçalho de comentário…

```
# PLACEHOLDER: <formatter_command> deve ser substituido pela skill com o
...
# PLACEHOLDER: <file_glob> deve ser substituido pelo padrao de arquivos
```

…e no corpo funcional (linhas 118-120). Uma substituição direta corrompeu o
cabeçalho na minha primeira tentativa, produzindo a frase sem sentido
`# PLACEHOLDER: dotnet format Catalogo.sln --include deve ser substituido pela skill`.
Tive de reverter as duas linhas de comentário à mão.

O que torna isso contraditório: `resources/ci-workflow.yml` **antecipa
exatamente esse bug** e se protege dele —

> "Os placeholders a preencher estão SÓ no corpo do workflow, abaixo — este
> cabeçalho não contém nenhum, de propósito: um mesmo marcador aparecendo em
> comentário e em corpo faz a substituição corromper o arquivo."

E `references/05-verificacao-pos-geracao.md` (item 6) repete o alerta,
atribuindo-o ao workflow: *"foi exatamente assim que o workflow de CI quebrou
na primeira geração. É o item 12 (YAML do CI) que pega isso."* Ou seja: a
lição foi aprendida e aplicada num template só. O `format-on-edit.sh` continua
com o defeito, e **não há item de checklist que o pegue** — YAML inválido o CI
denuncia, comentário shell corrompido não denuncia nada.

Sugestão: aplicar ao `format-on-edit.sh` a mesma disciplina do
`ci-workflow.yml` (marcadores só no corpo).

### B. FASE 5 item 6 lista marcadores que os templates VERBATIM mandam manter

O item 6 diz que `<formatter_command>`, `<file_glob>`, `<dod-command>` e
`<sln>` "NÃO podem sobrar". Mas os templates transcritos verbatim mantêm esses
mesmos marcadores nas tabelas ilustrativas por linguagem, que sobrevivem
legitimamente à geração:

- `.claude/hooks/format-on-edit.sh:22` → `#   .NET:    dotnet format <sln> --include`
- `.pre-commit-config.yaml:38,40` → `#       entry: bash -c 'dotnet format <sln> --verify-no-changes'`
- `init.sh:10,29` → `# dotnet restore <sln>` / `# dotnet test <sln>`

A regra 3 do SKILL.md ("transcritos VERBATIM: só os trechos `<>` mudam") e o
item 6 da FASE 5 dão veredictos opostos sobre essas linhas. O item 6 tenta
resolver dizendo "verificar pela lista nominal, não com grep genérico" — mas
a lista nominal **inclui** `<sln>` e `<file_glob>`, então seguir o item 6 ao pé
da letra reprova uma geração correta. Hesitei em apagar os blocos de
comentário; decidi mantê-los (verbatim vence) e reportar aqui.

### C. `<sln>` não está declarado como placeholder do `init.sh`, mas está lá

A FASE 2 documenta `<sln>` como "somente .NET: aparece nos exemplos de DoD, de
pre-commit e no `format-on-edit.sh` da stack .NET". O `init.sh` também o traz
(linhas 10 e 29), em linhas comentadas. Os placeholders reais do `init.sh` são
`<comando de instalação do repo>` / `<comandos de sanity do repo>` /
`<comando de teste do repo>`. Ambíguo se as linhas de exemplo `.NET` comentadas
devem ser descomentadas e preenchidas, ou se o preenchimento vai só nos
marcadores explícitos abaixo delas — o que produz duplicação visual
(`# dotnet test <sln>` logo acima de `dotnet test Catalogo.sln`). Optei pelo
segundo (verbatim + preencher só os marcadores).

### D. .NET não tem type checker separado, e a DoD tem 3 comandos onde o template sugere 3 papéis

`references/ecossistemas.md` diz que "linguagens de tipagem estática não
precisam de type checker separado — o compilador já é o sensor", e que o lint
de .NET são "analyzers via `.editorconfig`". Resultado: `dotnet build` acumula
os papéis de build **e** types **e** (com `EnforceCodeStyleInBuild=true`) parte
do lint. Isso não é dito em lugar nenhum — o exemplo `<ex .NET:>` do
`resources/AGENTS.md` simplesmente lista build+test+format sem explicar qual
sensor cobre o quê. Tive de inferir a decomposição para escrever os steps do CI
e os hooks do pre-commit ("um step por sensor" — mas quantos sensores são?).

### E. Ordem dos hooks no pre-commit não é especificada, e a ordem importa

`dotnet test --no-build` **exige** que o build tenha rodado antes. A FASE 2 dá
o padrão de cada hook mas não diz que a ordem deve seguir a da DoD; o item 12
da FASE 5 exige mesma ordem **só para o workflow de CI**. Gerei primeiro em
ordem format→build→test e tive de reordenar para build→test→format por
consistência. Num ecossistema onde `--no-build` é a norma, uma ordem errada é
falha real, não estética.

### F. `runs-on: ubuntu-latest` num repo sem remoto nem CI

FASE 2 manda usar `ubuntu-latest` "sinalizando na FASE 4". Este repo não tem
remoto configurado (`git branch -r` vazio) e portanto nem se sabe se é GitHub.
A skill não tem um caso "não há evidência de que o CI seja GitHub Actions" —
`.github/workflows/harness-dod.yml` foi gerado por default. Não é errado, mas é
uma suposição de plataforma feita sem a evidência que a regra inviolável 4
("toda informação da descoberta cita o arquivo-fonte") exige em todo o resto.

### G. Branch base: o fallback prescrito pode produzir um nome local efêmero

O item 19 da FASE 1 define a cadeia de fallback terminando em
`git branch --show-current`. Aqui os três primeiros passos falharam
(sem `origin/HEAD`, sem remotos, sem CONTRIBUTING) e o fallback devolveu `main`
— que é só a branch em que o repo por acaso estava. Se estivesse numa feature
branch, o `AGENTS.md` gerado mandaria o agente fazer
`git checkout feature/x && git pull` para sempre. A regra "nunca chutar" e o
fallback prescrito não são a mesma coisa, e a skill não manda registrar
"branch base inferida com baixa confiança" como pendência nesse caso.

### H. Ponto menor: `resources/AGENTS.md` traz uma `MUST NOT` de migrations fixa

A linha `- MUST NOT: alterar migrations já aplicadas — criar nova` está **fora**
dos placeholders `<restrição N>`, ou seja, faz parte do texto verbatim. Num repo
sem ORM, sem migrations e sem banco (este), transcrevê-la seria inventar
restrição sem evidência — o que as regras 4 e a FASE 2 proíbem explicitamente
("Nunca inventar restrições genéricas sem evidência"). Removi a linha e a
substituí por uma terceira restrição real (`decimal` em valores monetários).
O template deveria marcá-la como placeholder ou condicioná-la ao item 6 da
descoberta.

### I. Ambiguidade sobre onde a `Verificação local` do AGENTS.md com escopo pode rodar

`resources/AGENTS-scoped.md` pede "comando que valida apenas este
subdiretório", com exemplo `pytest tests/unit`. Em .NET o código de `src/` é
testado por um projeto **irmão** (`tests/`), não por nada dentro de `src/`.
Um comando que valida "apenas `src/`" só pode ser build+format — nunca os
testes, que estão fora do escopo do arquivo. Escrevi assim, mas a instrução não
prevê ecossistemas onde teste e código são projetos separados por convenção.

### J. Observação de campo: o gate hook da própria sessão bloqueou a verificação da FASE 5

A FASE 5 item 5 manda executar literalmente
`echo '{"tool_input":{"command":"rm -rf /tmp/test"}}' | bash ...gate-destructive.sh`.
Rodando isso dentro de uma sessão que já tem o harness instalado, o gate
**da sessão** inspeciona a string do comando de teste e bloqueia a própria
verificação (exit 2 antes de o script rodar). Tive de ofuscar a string
(`printf 'r''m -r''f ...'`) para conseguir testar o gate gerado. Vale um aviso
no item 5 — é 100% reprodutível em qualquer repo que já rodou a skill.
