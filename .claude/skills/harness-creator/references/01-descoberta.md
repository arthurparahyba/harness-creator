# FASE 1 — Descoberta (somente leitura, nenhuma escrita)

**Objetivo:** Investigar o repositório e produzir um Relatório de Descoberta.
**Precondições:** Skill invocada; nenhuma escrita permitida nesta fase.

---

## Conteúdo

- REGRA CRÍTICA
- Passo 0 — Existe `.claude/harness.json`?
- Passo 0.1 — O que esta fase produz
- Ordem de investigação
- Formato do Relatório de Descoberta
- ➡️ Fase 1 concluída — siga direto para a Fase 2

---

## REGRA CRÍTICA

Toda informação deve vir de evidência em arquivos do repo — cite o
arquivo-fonte de cada item. Se não encontrar evidência, escreva
"NÃO ENCONTRADO". Nunca presuma nem preencha de memória.

## Passo 0 — Existe `.claude/harness.json`?

Antes de investigar qualquer outra coisa, verifique se o repositório já
recebeu um harness desta skill. Se `.claude/harness.json` existir, a
descoberta é **reduzida** e a apresentação da FASE 4 muda: siga
[atualizacao.md](atualizacao.md) e volte para cá apenas para os itens que
ela mandar reinvestigar.

Descobrir isso no fim, e não no começo, é o que faz a skill reinvestigar do
zero um repositório que já respondeu tudo — e reapresentar para aprovação
vinte arquivos dos quais dezoito não mudaram.

## Passo 0.1 — O que esta fase produz

Dois artefatos, e os dois saem **exclusivamente** do que você ler nos
arquivos do repositório: o Relatório de Descoberta e o Plano de
Remediação.

**Todo item `NÃO ENCONTRADO` é candidato a uma entrada do Plano**, mesmo
os que a skill não resolve sozinha. Classifique cada um pelo
[catálogo de remediações](remediacoes.md): gerado pela skill, recomendado
com confirmação, ou só informativo. O objetivo é o usuário terminar a
sessão sabendo **tudo** que falta para o repositório ser bom de trabalhar
com agentes — não apenas o que a skill sabe escrever.

Quando os sensores estiverem ausentes, procure durante a investigação
**funções puras** (sem I/O, rede, display ou banco) para propor como
primeiros testes, e verifique se o entrypoint importa dependência de
sistema no nível do módulo — nesse caso o teste precisa de stub, e isso
entra na recomendação. Cite as funções pelo nome no plano; recomendação
genérica ("escreva testes") não é acionável.

## Ordem de investigação

0. **Ecossistema, não linguagem**: identifique pela tabela de
   [ecossistemas.md](ecossistemas.md) — Maven e Gradle são Java e divergem
   em todos os comandos; Angular, React e Node são JS/TS e também.
1. **Manifestos**: package.json (Node), pyproject.toml/setup.py
   (Python), go.mod (Go), Cargo.toml (Rust), composer.json (PHP),
   pom.xml/build.gradle (Java), Gemfile (Ruby), .csproj/.sln
   (.NET) → linguagem, versões, dependências
2. **Comandos reais**: scripts do package.json, Makefile, justfile,
   `[tool.*]` do pyproject, `scripts/` → como se testa, linta, builda
   e sobe ESTE projeto
3. **CI**: `.github/workflows/`, `.gitlab-ci.yml` → o que um merge
   exige. Estes comandos são a base prioritária da Definition of Done.
   **Importante**: inspecionar o `runs-on:` dos workflows existentes
   para identificar o runner (ubuntu-latest vs self-hosted corporativo).
   Nunca assumir `ubuntu-latest` — em repos corporativos self-hosted,
   isso faz workflows falharem silenciosamente.
4. **Estrutura**: layout de pastas, monorepo ou não, onde vivem os testes.
   Identificar o **diretório de código principal** (`src/`, `app/`, `lib/`,
   `internal/`, projeto `.csproj` principal) — é lá que vai o AGENTS.md com
   escopo. Em monorepo, um por pacote relevante.
   **Workspace** (`workspaces` no package.json, `pnpm-workspace.yaml`,
   `nx.json`, `turbo.json`, módulos Maven/Gradle): verificar se a raiz tem
   um comando de teste que roda tudo. Se os scripts vivem só nos pacotes,
   o agente não tem um ponto de entrada único — e o scanner só lê a raiz.
   Recomendar o script raiz que delega — sem ele a DoD não tem um comando
   que valide o repositório inteiro (ver [ecossistemas.md](ecossistemas.md)).
5. **Convenções já documentadas**: AGENTS.md/CLAUDE.md existentes,
   CONTRIBUTING.md, .cursorrules, configs de lint → respeitar, não duplicar
6. **Banco/migrations**: ferramenta, ORM, padrão de acesso a dados
7. **Tipo de aplicação**: API, frontend, CLI, lib, monorepo → implicações
   para verificação
8. **OpenSpec**: o diretório `openspec/` existe? Tem `config.yaml` ou
   `project.md` (legado)? Se `project.md`: avisar que `openspec update`
   faz a migração; não gerar config.yaml por cima sem avisar.
9. **Formatter da linguagem**: qual formatter rodar no `format-on-edit.sh`?
   A resposta por ecossistema está na coluna "Formatter" de
   [ecossistemas.md](ecossistemas.md) — **fonte única**, para o mesmo repo
   não receber um formatter aqui e outro na FASE 2. Não repita a tabela.
   Confirme contra o que o repositório já usa: config de lint,
   `.prettierrc`, `[tool.ruff]`, `[tool.black]`, hook de pre-commit
   existente. O que está commitado ganha da tabela.
10. **Lockfile**: qual gerenciador de deps? Tem lockfile commitado?
    Usar **apenas nomes convencionais do ecossistema** — um arquivo com
    nome inventado (ex: `requirements.lock`) não é instalado por nenhuma
    ferramenta nem reconhecido por scanners, então não conta como lockfile.
    Nomes válidos: Python — `uv.lock` (uv), `poetry.lock` (poetry),
    `Pipfile.lock` (pipenv) ou `requirements.txt` fixado com `==`
    (pip; gerar com `pip freeze > requirements.txt`);
    npm: `package-lock.json`; yarn: `yarn.lock`; pnpm: `pnpm-lock.yaml`;
    cargo: `Cargo.lock`; go: `go.sum`; composer: `composer.lock`;
    bundler: `Gemfile.lock`.
    **.NET e Java/Maven não têm lockfile convencional** — .NET usa
    `packages.lock.json` (opt-in via `RestorePackagesPath`/`EnableLockFile`)
    e Maven usa `mvn dependency:lock` (não padrão). Registrar como
    pendência se não houver lockfile e a linguagem suportar.
11. **MCP servers**: `.devin/config.json`, `.cursor/mcp.json`, `.mcp.json`
    — tem MCP configurado? Em qual path? Se não estiver na raiz
    (`.mcp.json`), será copiado para a raiz na FASE 2.
    **Antes de propor qualquer cópia, inspecionar o conteúdo em busca de
    credencial literal** (valores em chaves como `token`, `key`, `secret`,
    `password`, `authorization`, ou strings tipo `sk-`, `ghp_`, `xoxb-`).
    Copiar um segredo para a raiz o torna mais visível e mais provável de
    ser commitado — o oposto do objetivo. Registrar cada ocorrência no
    relatório: path, chave e se o valor é literal ou já usa interpolação
    `${VAR}`.
12. **Hooks existentes**: `.claude/settings.json`, `.devin/hooks.v1.json`,
    `.cursor/hooks.json` — já tem hooks de agent loop configurados?
    Se sim, não sobrescrever; mesclar com cuidado. Verificar os **três**:
    registrar o gate só onde o repo já tinha configuração deixa os outros
    agentes sem enforcement, e o usuário não descobre — o agente
    desprotegido simplesmente funciona até causar o dano.
13. **Linter/formatter config**: `.editorconfig` (universal — .NET, Java,
    C, Python, JS/TS, etc.), `.eslintrc`/`biome.json` (JS/TS),
    `.pylintrc`/`ruff.toml` (Python), `.golangci.yml` (Go),
    `clippy.toml` (Rust), `checkstyle.xml`/`spotbugs` (Java) — já tem
    config dedicada? Se não, gerar `resources/editorconfig-base` (regras
    universais) e mesclar regras específicas da linguagem se houver
    template (ex: `resources/editorconfig-dotnet` para .NET/C#).
14. **.gitignore**: verificar se `.env` e `.env.*` estão cobertos. Se
    não, adicionar (append, não sobrescrever).
15. **LICENSE e README**: existem `LICENSE` e `README.md` na raiz? O
    README é o primeiro documento de orientação que um agente lê; se não
    existir, registrar como pendência e oferecer na FASE 4.
16. **Skills**: `.claude/skills/*/SKILL.md`, `.cursor/skills/`,
    `.agents/skills/` — o repo já empacota algum procedimento como skill?
    Se não, gerar `executar-grupo` do template.
17. **Regras arquiteturais candidatas**: existe `.harness/arch-rules.json`?
    Se existir, é do usuário e **não se toca** (FASE 3). Se não, além da
    semente do template, procure invariantes que já estejam escritos em
    algum lugar do repositório e que se verifiquem com **um comando**:
    seção de arquitetura ou de camadas no README/`ARCHITECTURE.md`/
    `CONTRIBUTING.md`, `.editorconfig` ou config de linter com regra de
    import entre pastas, e a própria estrutura de diretórios quando ela
    separa domínio de infraestrutura.
    - Regra só entra com **evidência** e só se for verificável por comando.
      "O código deve ser limpo" é desejo; "nenhum arquivo em `domain/`
      importa o driver do banco" é regra. Mesma exigência dos `MUST NOT`.
    - Cada regra precisa de `what`, `why` e `fix` acionáveis, nomeando
      arquivo, função ou comando. O `why` é o que impede o agente de
      "consertar" a violação apagando a regra.
    - O que não couber em comando vira item do Plano de Remediação, não
      regra silenciosamente fraca.
18. **Contexto com escopo**: existe `AGENTS.md`/`CLAUDE.md` aninhado em
    subdiretório, ou arquivo de rule com escopo (`.cursor/rules/*.mdc`,
    `.windsurf/rules/`, `.clinerules/`, `.github/instructions/`)? Sem
    nenhum deles, todo o conhecimento vive na raiz e é carregado em todo
    request. Se não houver, gerar o AGENTS.md com escopo na FASE 2.
19. **Branch base do fluxo**: de qual branch as features saem? Fonte, nesta
    ordem: `git symbolic-ref refs/remotes/origin/HEAD` (o default do
    remoto), `git branch -r` (existe `origin/develop`?), a documentação de
    contribuição, e por último `git branch --show-current`. Nunca assumir
    `main` nem `develop`: o AGENTS.md gerado manda o agente rodar
    `git checkout <branch-base>` no início de toda funcionalidade nova, e
    com o nome errado isso falha na primeira execução, antes de o agente
    escrever uma linha. Repo sem git: registrar NÃO ENCONTRADO e tratar na
    FASE 4 como pendência do usuário.
20. **Prefixo de nome de branch**: o time usa `feature/`, `feat/`,
    `users/LOGIN/`, ID de ticket? Derive de EVIDÊNCIA, nesta ordem:
    `git branch -r --format='%(refname:short)'` e
    `git log --format=%D --all` (os prefixos realmente usados no histórico),
    `CONTRIBUTING.md`, template de PR. Conte as ocorrências e use o
    majoritário; empate ou repo novo sem branches → `feature/`, e isso vai
    para a FASE 4 como escolha declarada, não silenciosa. Preenche
    `<prefixo-de-branch>` com o separador incluído (ex.: `feature/`).
    O nome errado faz o agente criar branch fora do padrão do time logo na
    primeira funcionalidade — e o time descobre no PR.
21. **Política de entrega**: o que se faz DEPOIS do commit do grupo? Fontes:
    `.github/PULL_REQUEST_TEMPLATE*` ou `.github/pull_request_template.md`
    (o time usa PR), `CODEOWNERS` (PR exige revisão), workflows em
    `.github/workflows/` com `pull_request:` ou que criem PR sozinhos,
    `CONTRIBUTING.md`, e o histórico: `git log --merges --oneline -20`
    mostra se merges vêm de PR (`Merge pull request #`) ou são diretos.
    Preenche `<politica-de-entrega>` com uma linha por regra encontrada —
    push da feature branch, PR sempre ou merge direto, se a CI abre o PR
    sozinha. Sem evidência nenhuma: NÃO ENCONTRADO, e a FASE 4 pergunta.
    Não inventar: mandar abrir PR num repo que faz merge direto trava o
    agente esperando aprovação que ninguém vai dar.
22. **Ponte para o Claude Code**: existe `CLAUDE.md` (raiz ou junto de cada
    AGENTS.md com escopo)? Se existir, ele importa (`@AGENTS.md`), é
    symlink, ou já contém o protocolo? O Claude Code carrega `CLAUDE.md` e
    **não** carrega `AGENTS.md`; sem a ponte, o harness existe no disco e
    não existe na sessão. Registrar o que falta para a FASE 2 gerar (não
    existe) ou a FASE 3 propor o append (existe, mas não alcança).

## Formato do Relatório de Descoberta

Apresentar ao usuário antes de qualquer geração:

```
- Ecossistema:                  (linha de ecossistemas.md + fonte do manifesto)
- Monorepo/workspace:           (não / sim + onde vivem os scripts)
- Tipo de aplicação:            (fonte)
- Stack com versões:            (fonte)
- Diretório de código principal:(path, ou NÃO ENCONTRADO)
- Comando de teste:             (fonte)
- Comando de lint/format:       (fonte)
- Comando de types/build:       (fonte)
- Comandos exigidos pelo CI:    (fonte)
- Runner de CI:                 (ubuntu-latest / self-hosted / NÃO ENCONTRADO)
- Formatter da linguagem:       (fonte)
- Lockfile:                     (tipo + path, ou NÃO ENCONTRADO)
- MCP servers:                  (path + servers, ou NÃO ENCONTRADO)
- Credencial literal em MCP:    (chave + path, ou NENHUMA)
- Hooks existentes:             (path + eventos, ou NÃO ENCONTRADO)
- Linter/formatter config:      (path + tipo, ou NÃO ENCONTRADO)
- .gitignore cobre .env:        (sim/não)
- LICENSE presente:             (sim/não)
- README.md presente:           (sim/não)
- Subagentes existentes:        (path, ou NÃO ENCONTRADO)
- Skills existentes:            (path, ou NÃO ENCONTRADO)
- Contexto com escopo:          (path do AGENTS.md aninhado/rule, ou NÃO ENCONTRADO)
- Branch base do fluxo:         (nome + fonte, ou NÃO ENCONTRADO)
- CI presente:                  (path do pipeline, ou NÃO ENCONTRADO)
- Ferramenta de migration:      (fonte)
- Convenções já documentadas:   (fonte)
- OpenSpec presente:            (sim/não; config.yaml ou project.md)
- Funções puras candidatas a teste: (nomes + arquivo, se faltam sensores)
- Imports de sistema no entrypoint: (exigem stub nos testes? sim/não)
- Lacunas (NÃO ENCONTRADO):
- Plano de Remediação:          (itens do catálogo, por grupo A/B/C)
```

---

## ➡️ Fase 1 concluída — siga direto para a Fase 2

Apresente o Relatório de Descoberta e **continue imediatamente** para a
[Fase 2](02-preenchimento-templates.md). Não pergunte se pode prosseguir:
a única pausa do fluxo é a FASE 4 (aprovação antes de gravar), e nada foi
escrito ainda.
