# Ecossistemas

"Linguagem" não basta para decidir os comandos. Maven e Gradle são Java e
divergem em tudo que a skill preenche; Angular, React e Node são JS/TS e
também. Esta tabela é por **ecossistema**, que é a unidade real de decisão.

Detecte na FASE 1 pelo manifesto e **confirme com os scripts reais do
repositório** — a tabela orienta onde procurar, não substitui a evidência.
Se o `package.json` define `"test": "jest --runInBand"`, a DoD usa isso, e
não o que está escrito aqui.

---

## Conteúdo

- Tabela de preenchimento
- Lockfiles
- Monorepos e workspaces

---

## Tabela de preenchimento

| Ecossistema | Detectar por | Teste | Lint | Types | Formatter | `<file_glob>` |
|---|---|---|---|---|---|---|
| **Node / TS** | `package.json` sem `angular.json` nem framework de UI | `npm test` | `eslint .` | `tsc --noEmit` | `npx prettier --write "$FILE_PATH"` | `*.js\|*.ts\|*.mjs\|*.cjs` |
| **React** | `react` em `dependencies` | `vitest run` / `jest` | `eslint .` | `tsc --noEmit` | `npx prettier --write "$FILE_PATH"` | `*.js\|*.jsx\|*.ts\|*.tsx` |
| **Angular** | `angular.json` | `ng test --watch=false` | `ng lint` | `tsc --noEmit` (ver `strictTemplates`) | `npx prettier --write "$FILE_PATH"` | `*.ts\|*.html\|*.scss` |
| **Java / Maven + spotless** | `pom.xml` com `spotless-maven-plugin` | `mvn test` | `mvn checkstyle:check` | compilador | `mvn -q spotless:apply -DspotlessFiles="$FILE_PATH"` | `*.java` |
| **Java / Maven + spring-javaformat** | `pom.xml` com `spring-javaformat-maven-plugin` | `mvn test` | `mvn checkstyle:check` | compilador | **não escopa por arquivo — sem hook** | `*.java` |
| **Java / Gradle** | `build.gradle(.kts)` | `./gradlew test` | `./gradlew checkstyleMain` | compilador | `./gradlew -q spotlessApply -PspotlessIdeHook="$FILE_PATH"` | `*.java\|*.kt` |
| **.NET / C#** | `.sln` ou `.csproj` | `dotnet test <sln>` | analyzers via `.editorconfig` | compilador | `dotnet format <sln> --include "$FILE_PATH"` | `*.cs` |
| **Go** | `go.mod` | `go test ./...` | `golangci-lint run` | compilador | `gofmt -w "$FILE_PATH"` | `*.go` |
| **Python** | `pyproject.toml`, `setup.py` | `pytest` | `ruff check .` | `mypy` | `ruff format "$FILE_PATH"` | `*.py` |
| **Rust** | `Cargo.toml` | `cargo test` | `cargo clippy` | compilador | `rustfmt "$FILE_PATH"` | `*.rs` |
| **Ruby** | `Gemfile` | `rspec` | `rubocop` | — | `rubocop -A "$FILE_PATH"` | `*.rb` |
| **PHP** | `composer.json` | `phpunit` | `phpcs` | `phpstan` | `php-cs-fixer fix "$FILE_PATH"` | `*.php` |

### Formatter que não escopa por arquivo

Duas linhas da tabela dizem **"não escopa por arquivo — sem hook"** em vez de
um comando. Não é lacuna: é a resposta certa.

`spring-javaformat` (toda a família Spring, incluindo o Spring PetClinic) e
`ktlint` sem `--file` formatam o **módulo inteiro**. Pendurar isso no
`format-on-edit.sh` faria cada tecla disparar uma JVM e um build completo —
alguns segundos por edição. Um hook que atrapalha é um hook que o time
desliga, e quando ele é desligado some junto com o resto do enforcement.

Nesses casos:
- **não gere** `format-on-edit.sh` nem o registro dele nos configs de hook
  dos três agentes;
- a formatação vai para o **pre-commit** e para o **CI**, onde rodar o módulo
  inteiro é aceitável porque acontece uma vez, não a cada edição;
- registre um item no Plano de Remediação explicando a ausência — hook que
  falta sem explicação parece esquecimento da skill.

A regra geral continua valendo e vem antes da tabela: **o que está commitado
ganha**. Inspecione qual plugin o manifesto declara, não só se existe algum.

A coluna **Formatter** é o valor de `<formatter_command>` e já inclui
`"$FILE_PATH"` na posição que a ferramenta exige — o template do hook **não**
o anexa no fim. Formatter que roda como plugin de build (`spotless`) não
aceita caminho posicional: `mvn spotless:apply <arquivo>` faz o Maven ler o
caminho como fase de ciclo de vida e abortar com `Unknown lifecycle phase`,
e o `2>/dev/null || true` do hook engole o erro. O hook fica inerte e nada
acusa. Por isso Maven usa `-DspotlessFiles=` e Gradle usa
`-PspotlessIdeHook=`, que são as formas documentadas de escopar por arquivo.

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
