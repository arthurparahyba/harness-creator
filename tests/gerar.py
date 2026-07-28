"""Geração do harness a partir dos templates, para uso nos testes.

Reproduz o que a FASE 2 da skill faz: lê cada template de `resources/`,
substitui os marcadores com os valores do ecossistema e grava. Existe para
que os testes exercitem o **artefato gerado**, e não só o template — foi a
ausência disso que deixou passar o glob `*.{js,ts}`, que é sintaticamente
válido no template e inerte depois de gerado.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RESOURCES = RAIZ / ".claude" / "skills" / "harness-creator" / "resources"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# Marcadores que a skill PREENCHE: não podem sobreviver à geração e têm de
# estar documentados na FASE 2. Distintos dos ilustrativos (<hash>, <task>, …),
# que são parte do texto do protocolo e permanecem no arquivo gerado.
# Fonte única: `test_skill.py` valida a lista contra templates e references,
# `test_geracao.py` a usa para varrer o que foi gerado. Duas listas divergiam
# — `<setup-steps>` já esteve só numa delas.
PREENCHIVEIS = [
    "<branch-base>",
    "<caminho>",
    "<checks-do-repo>",
    "<como-propor-mudanca-de-plano>",
    "<data-iso>",
    "<dod-command>",
    "<ecossistema>",
    "<ferramentas-do-harness>",
    "<dod-steps>",
    "<file_glob>",
    "<formatter_bin>",
    "<formatter_command>",
    "<pre-commit-hooks>",
    "<runner>",
    "<setup-steps>",
    "<sln>",
    "<versao-da-skill>",
]


@dataclass(frozen=True)
class Stack:
    """Uma linha de `references/ecossistemas.md`, em forma executável."""

    dod: str
    file_glob: str
    formatter_bin: str
    dir_escopo: str
    setup_steps: str
    pre_commit: str
    formatavel: str
    """Arquivo real da fixture que o hook de formatação DEVE alcançar."""
    nao_formatavel: str
    """Arquivo real da fixture que o hook DEVE ignorar."""

    @property
    def comandos(self) -> list[str]:
        return [c.strip() for c in self.dod.split("&&")]

    @property
    def dod_steps(self) -> str:
        """Um `- run:` por comando da DoD, derivado da própria DoD.

        Escrever os steps à mão fazia o CI rodar menos que a DoD — o agente
        verificava três comandos e o pipeline cobrava um. A regra da FASE 5
        é que a DoD seja idêntica em todo lugar; derivar em vez de repetir
        é o que torna isso verdade por construção.
        """
        return "\n".join(f"      - run: {c}" for c in self.comandos)


STACKS: dict[str, Stack] = {
    "node": Stack(
        dod="npm test && npm run lint && npx tsc --noEmit",
        file_glob="*.js|*.ts|*.mjs|*.cjs",
        formatter_bin="npx",
        dir_escopo="src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint",
        formatavel="src/total.ts",
        nao_formatavel="package.json",
    ),
    "react": Stack(
        dod="npm test && npm run lint && npx tsc --noEmit",
        file_glob="*.js|*.jsx|*.ts|*.tsx",
        formatter_bin="npx",
        dir_escopo="src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint",
        formatavel="src/Contador.tsx",
        nao_formatavel="package.json",
    ),
    "angular": Stack(
        dod="npm test && npm run lint && npx tsc --noEmit",
        file_glob="*.ts|*.html|*.scss",
        formatter_bin="npx",
        dir_escopo="src/app",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint",
        formatavel="src/app/app.component.html",
        nao_formatavel="angular.json",
    ),
    "java-maven": Stack(
        dod="mvn test && mvn checkstyle:check && mvn spotless:check",
        file_glob="*.java",
        formatter_bin="mvn",
        dir_escopo="src/main/java",
        setup_steps="      - uses: actions/setup-java@v4",
        pre_commit="mvn checkstyle:check",
        formatavel="src/main/java/com/exemplo/Estoque.java",
        nao_formatavel="pom.xml",
    ),
    "java-gradle": Stack(
        dod="./gradlew test && ./gradlew checkstyleMain && ./gradlew spotlessCheck",
        file_glob="*.java|*.kt",
        formatter_bin="gradle",
        dir_escopo="src/main/java",
        setup_steps="      - uses: actions/setup-java@v4",
        pre_commit="./gradlew checkstyleMain",
        formatavel="src/main/java/com/exemplo/Fatura.java",
        nao_formatavel="build.gradle",
    ),
    "dotnet": Stack(
        dod=(
            "dotnet build Catalogo.sln -c Release && "
            "dotnet test Catalogo.sln --no-build && "
            "dotnet format Catalogo.sln --verify-no-changes"
        ),
        file_glob="*.cs",
        formatter_bin="dotnet",
        dir_escopo="src",
        setup_steps="      - uses: actions/setup-dotnet@v4",
        pre_commit="dotnet format Catalogo.sln --verify-no-changes",
        formatavel="src/Preco.cs",
        nao_formatavel="Catalogo.sln",
    ),
    "go": Stack(
        dod="go test ./... && golangci-lint run && gofmt -l .",
        file_glob="*.go",
        formatter_bin="gofmt",
        dir_escopo="internal",
        setup_steps="      - uses: actions/setup-go@v5",
        pre_commit="go vet ./...",
        formatavel="internal/frete/frete.go",
        nao_formatavel="go.mod",
    ),
    "monorepo": Stack(
        dod="npm test --workspaces && npm run lint --workspaces",
        file_glob="*.js|*.jsx|*.ts|*.tsx",
        formatter_bin="npx",
        dir_escopo="apps/web/src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint --workspaces",
        formatavel="apps/web/src/formata.ts",
        nao_formatavel="package.json",
    ),
    # Os quatro abaixo estavam só documentados em `ecossistemas.md`. Sem
    # fixture, a linha da tabela era uma promessa que nada exercitava.
    "python": Stack(
        dod="pytest && ruff check . && mypy",
        file_glob="*.py",
        formatter_bin="ruff",
        dir_escopo="cobranca",
        setup_steps=('      - uses: actions/setup-python@v5\n      - run: pip install -e ".[dev]"'),
        pre_commit="ruff check .",
        formatavel="cobranca/juros.py",
        nao_formatavel="pyproject.toml",
    ),
    "rust": Stack(
        dod="cargo test && cargo clippy -- -D warnings && cargo fmt --check",
        file_glob="*.rs",
        formatter_bin="rustfmt",
        dir_escopo="src",
        setup_steps="      - run: rustup toolchain install stable --profile minimal",
        pre_commit="cargo clippy -- -D warnings",
        formatavel="src/lib.rs",
        nao_formatavel="Cargo.toml",
    ),
    "ruby": Stack(
        dod="rspec && rubocop",
        file_glob="*.rb",
        formatter_bin="rubocop",
        dir_escopo="lib",
        setup_steps=("      - uses: ruby/setup-ruby@v1\n      - run: bundle install"),
        pre_commit="rubocop",
        formatavel="lib/comissao.rb",
        nao_formatavel="Gemfile",
    ),
    "php": Stack(
        dod="phpunit && phpcs src && phpstan analyse src",
        file_glob="*.php",
        formatter_bin="php-cs-fixer",
        dir_escopo="src",
        setup_steps=("      - uses: shivammathur/setup-php@v2\n      - run: composer install"),
        pre_commit="phpcs src",
        formatavel="src/Imposto.php",
        nao_formatavel="composer.json",
    ),
    # Repo Python sem test runner nem linter. A DoD vazia é o ponto: é ela que
    # desliga o enforcement. Não entra nas parametrizações que exigem DoD.
    "sem-sensores": Stack(
        dod="",
        file_glob="*.py",
        formatter_bin="formatter-nao-definido",
        dir_escopo="relatorios",
        setup_steps="      - uses: actions/setup-python@v5",
        pre_commit="",
        formatavel="relatorios/calculos.py",
        nao_formatavel="pyproject.toml",
    ),
}

COM_SENSORES = [n for n, s in STACKS.items() if s.dod]
"""Ecossistemas cujo harness inclui enforcement — os que têm DoD real."""

PRE_COMMIT_HOOK = """      - id: lint
        name: lint
        entry: bash -c '{cmd}'
        language: system
        pass_filenames: false
        stages: [pre-commit]"""


def _grava(destino: Path, rel: str, conteudo: str) -> None:
    alvo = destino / rel
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(conteudo, newline="\n")


def _preenche(
    template: str, subs: dict[str, str], remove_exemplos: bool = False, sln: str | None = None
) -> str:
    texto = (RESOURCES / template).read_text()
    if sln is not None:
        texto = texto.replace("<sln>", sln)
    for marcador, valor in subs.items():
        texto = texto.replace(marcador, valor)
    if remove_exemplos:
        texto = "\n".join(ln for ln in texto.split("\n") if not ln.startswith("<ex "))
    return texto


def gerar(nome: str, destino: Path) -> Stack:
    """Copia a fixture `nome` para `destino` e grava o harness sobre ela."""
    stack = STACKS[nome]
    shutil.copytree(FIXTURES / nome, destino, dirs_exist_ok=True)

    _grava(
        destino,
        "AGENTS.md",
        _preenche(
            "AGENTS.md",
            {
                "<2-3 linhas: o que é a aplicação, stack com versões exatas>": f"Fixture {nome}.",
                "<Preencher via descoberta — nunca de memória. Fontes: manifestos, CI>": "",
                "<comandos reais do repo, encadeados com &&, "
                "priorizando o que o CI exige>": stack.dod,
                "<branch-base>": "main",
                # Fixture sem `openspec/`: a variante correta é a do TASKS.md.
                "<como-propor-mudanca-de-plano>": (
                    "Para criar ou modificar o plano, acrescente o grupo ao `TASKS.md` no\n"
                    "formato descrito abaixo e confirme com o usuário antes de executá-lo."
                ),
                "<restrição 1 — derivada de convenção real do repo>": "editar artefato de build",
                "<restrição 2>": "alterar o lockfile à mão",
                "<ferramentas-do-harness>": (
                    "- Para fechar um grupo do plano: skill `executar-grupo` (passo a passo).\n"
                    "- Para verificar a Definition of Done: comando `/dod`.\n"
                    "- Antes de commitar um grupo: delegue a revisão ao subagente "
                    "`code-reviewer`.\n"
                    "- Hooks de agent loop ativos: gate de comandos destrutivos e formatação\n"
                    "  automática a cada edição."
                ),
            },
            remove_exemplos=True,
        ),
    )
    _grava(
        destino,
        f"{stack.dir_escopo}/AGENTS.md",
        _preenche(
            "AGENTS-scoped.md",
            {
                "<caminho>": stack.dir_escopo,
                '<restrição 1 — a mesma de "Regras de trabalho" do AGENTS.md raiz>': (
                    "editar artefato de build"
                ),
                "<restrição 2>": "alterar o lockfile à mão",
                "<restrição 3>": "importar de teste dentro de produção",
                "<padrão de acesso a dados, camadas ou nomenclatura descoberto na FASE 1>": (
                    "Camadas separadas por diretório."
                ),
                "<onde vivem os testes deste código>": "Testes ao lado do código.",
                "<comando que valida apenas este subdiretório, ex: pytest tests/unit>": (
                    stack.dod.split("&&")[0].strip()
                ),
            },
        ),
    )
    _grava(
        destino,
        ".claude/hooks/format-on-edit.sh",
        _preenche(
            "hooks/format-on-edit.sh",
            {
                "<file_glob>": stack.file_glob,
                "<formatter_bin>": stack.formatter_bin,
                "<formatter_command>": stack.formatter_bin,
            },
        ),
    )
    _grava(
        destino,
        ".claude/commands/dod.md",
        _preenche("dod-command.md", {"<dod-command>": stack.dod}),
    )
    _grava(
        destino,
        ".claude/agents/code-reviewer.md",
        _preenche(
            "agents/code-reviewer.md",
            {
                "<checks-do-repo>": (
                    f"5. **Camadas**: domain logic stays out of `{stack.dir_escopo}/infra`.\n"
                    "6. **Testes**: novos testes ficam ao lado do código que exercitam."
                )
            },
        ),
    )
    # Regra de honestidade da FASE 2: sem sensores, a DoD fica vazia e o
    # enforcement NÃO é gerado. Pre-commit sem hook e CI que passa sem rodar
    # nada dão ao agente um verde que ele não mereceu — pior que não ter
    # enforcement, porque parece ter.
    if stack.dod:
        _grava(
            destino,
            ".pre-commit-config.yaml",
            _preenche(
                "pre-commit-config.yaml",
                {"<pre-commit-hooks>": PRE_COMMIT_HOOK.format(cmd=stack.pre_commit)},
            ),
        )
        _grava(
            destino,
            ".github/workflows/harness-dod.yml",
            _preenche(
                "ci-workflow.yml",
                {
                    "<runner>": "ubuntu-latest",
                    "<setup-steps>": stack.setup_steps,
                    "<dod-steps>": stack.dod_steps,
                },
            ),
        )
    _grava(
        destino,
        "init.sh",
        _preenche(
            "init.sh",
            {
                "<comando de instalação do repo>": "echo deps",
                "<comandos de sanity do repo>": "echo sanity",
                "<comando de teste do repo>": stack.dod.split("&&")[0].strip(),
            },
        ),
    )
    for origem, alvo in [
        ("SESSION_STATE.md", "SESSION_STATE.md"),
        ("TASKS.md", "TASKS.md"),
        ("editorconfig-base", ".editorconfig"),
        ("claude-settings.json", ".claude/settings.json"),
        ("devin-hooks.json", ".devin/hooks.v1.json"),
        ("cursor-hooks.json", ".cursor/hooks.json"),
        ("hooks/gate-destructive.sh", ".claude/hooks/gate-destructive.sh"),
        ("verificar-harness.sh", ".claude/verificar-harness.sh"),
        ("skills/executar-grupo/SKILL.md", ".claude/skills/executar-grupo/SKILL.md"),
        ("CLAUDE.md", "CLAUDE.md"),
        ("CLAUDE.md", f"{stack.dir_escopo}/CLAUDE.md"),
    ]:
        _grava(destino, alvo, (RESOURCES / origem).read_text())

    scripts = (
        "init.sh",
        ".claude/hooks/gate-destructive.sh",
        ".claude/hooks/format-on-edit.sh",
        ".claude/verificar-harness.sh",
    )
    for script in scripts:
        (destino / script).chmod(0o755)

    readme = destino / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {nome}\n\nRepositorio de exemplo.\n\n## Testes\n\n```\n{stack.dod}\n```\n",
            newline="\n",
        )

    gitignore = destino / ".gitignore"
    gitignore.write_text(
        gitignore.read_text() + "\n# Environment files (never commit credentials)\n.env\n.env.*\n",
        newline="\n",
    )

    _grava_manifesto(destino, nome, stack)
    return stack


def _versao_da_skill() -> str:
    """A versão declarada no frontmatter do SKILL.md — fonte única."""
    texto = (RESOURCES.parent / "SKILL.md").read_text()
    achado = re.search(r'^\s+version:\s*"?([\d.]+)"?', texto, re.M)
    assert achado, "SKILL.md sem metadata.version"
    return achado.group(1)


def _grava_manifesto(destino: Path, nome: str, stack: Stack) -> None:
    """Registra o que ESTA execução gravou.

    É o que permite a uma geração futura atualizar o harness sem pisar em
    arquivo do usuário: o que está na lista é da skill, o resto não é.
    Por isso a lista é varrida do disco no fim, e não escrita à mão.
    """
    gerados = sorted(
        str(p.relative_to(destino))
        for p in destino.rglob("*")
        if p.is_file() and ".git" not in p.parts
    )
    _grava(
        destino,
        ".claude/harness.json",
        _preenche(
            "harness-manifest.json",
            {
                "<versao-da-skill>": _versao_da_skill(),
                "<data-iso>": "2026-07-27",
                "<ecossistema>": nome,
                "<dod-command>": stack.dod,
                '"<lista de caminhos gerados, um por linha, relativos à raiz>"': ",\n      ".join(
                    json.dumps(g) for g in gerados
                ),
                '"<itens do Plano de Remediação recusados ou adiados, para não repropor>"': "",
            },
        ),
    )


def entrada_do_hook(evento: str, valor: str) -> str:
    chave = "command" if evento == "Bash" else "file_path"
    return json.dumps({"tool_name": evento, "tool_input": {chave: valor}})
