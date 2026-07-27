# Ecossistemas

"Linguagem" não basta para decidir os comandos. Maven e Gradle são Java e
divergem em tudo que a skill preenche; Angular, React e Node são JS/TS e
também. Esta tabela é por **ecossistema**, que é a unidade real de decisão.

Detecte na FASE 1 pelo manifesto e **confirme com os scripts reais do
repositório** — a tabela orienta onde procurar, não substitui a evidência.
Se o `package.json` define `"test": "jest --runInBand"`, a DoD usa isso, e
não o que está escrito aqui.

---

## Tabela de preenchimento

| Ecossistema | Detectar por | Teste | Lint | Types | Formatter | `<file_glob>` |
|---|---|---|---|---|---|---|
| **Node / TS** | `package.json` sem `angular.json` nem framework de UI | `npm test` | `eslint .` | `tsc --noEmit` | `prettier --write` | `*.js\|*.ts\|*.mjs\|*.cjs` |
| **React** | `react` em `dependencies` | `vitest run` / `jest` | `eslint .` | `tsc --noEmit` | `prettier --write` | `*.js\|*.jsx\|*.ts\|*.tsx` |
| **Angular** | `angular.json` | `ng test --watch=false` | `ng lint` | `tsc --noEmit` (ver `strictTemplates`) | `prettier --write` | `*.ts\|*.html\|*.scss` |
| **Java / Maven** | `pom.xml` | `mvn test` | `mvn checkstyle:check` | compilador | `mvn spotless:apply` | `*.java` |
| **Java / Gradle** | `build.gradle(.kts)` | `./gradlew test` | `./gradlew checkstyleMain` | compilador | `./gradlew spotlessApply` | `*.java\|*.kt` |
| **.NET / C#** | `.sln` ou `.csproj` | `dotnet test <sln>` | analyzers via `.editorconfig` | compilador | `dotnet format <sln>` | `*.cs` |
| **Go** | `go.mod` | `go test ./...` | `golangci-lint run` | compilador | `gofmt -w` | `*.go` |
| **Python** | `pyproject.toml`, `setup.py` | `pytest` | `ruff check .` | `mypy` | `ruff format` | `*.py` |
| **Rust** | `Cargo.toml` | `cargo test` | `cargo clippy` | compilador | `rustfmt` | `*.rs` |
| **Ruby** | `Gemfile` | `rspec` | `rubocop` | — | `rubocop -A` | `*.rb` |
| **PHP** | `composer.json` | `phpunit` | `phpcs` | `phpstan` | `php-cs-fixer fix` | `*.php` |

`<file_glob>` vira padrão de `case`, que **não faz brace expansion**:
`*.{js,ts}` não casa com nada e o hook para de formatar em silêncio.
Sempre alternância com `|`.

Linguagens de tipagem estática (Go, Rust, Java, C#) não precisam de type
checker separado — o compilador já é o sensor. Nesses casos a etapa de
tipos da DoD é o próprio build.

---

## Lockfiles

Usar sempre o nome convencional do ecossistema. Nome inventado não é
instalado por nenhuma ferramenta e não serve de lockfile.

| Ecossistema | Lockfile |
|---|---|
| Node / React / Angular | `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` |
| Python | `uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.txt` fixado com `==` |
| Go | `go.sum` |
| Rust | `Cargo.lock` |
| Ruby | `Gemfile.lock` |
| PHP | `composer.lock` |
| Java / .NET | sem convenção estabelecida — registrar como pendência |

---

## Monorepos e workspaces

Detectar por `workspaces` no `package.json`, `pnpm-workspace.yaml`,
`nx.json`, `turbo.json`, ou módulos Maven/Gradle.

O problema recorrente é que os comandos de teste e lint vivem nos pacotes
e não há nada na raiz que valide o repositório inteiro. Sem isso a DoD não
tem como existir: ela precisa de um comando único que o agente rode e que
cubra tudo que ele pode ter quebrado. Recomendar o script raiz que delega
— `npm test --workspaces`, `turbo test`, `nx run-many -t test`,
`pnpm -r test` — como item do grupo B do [catálogo](remediacoes.md).

Em monorepo, gerar **um `AGENTS.md` com escopo por pacote relevante**, não
um só na raiz: as restrições de `apps/web` não são as de `apps/api`.
