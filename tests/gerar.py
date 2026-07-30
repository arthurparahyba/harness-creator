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
    "<como-propor-mudanca-de-plano>",
    "<data-iso>",
    "<dod-command>",
    "<ecossistema>",
    "<ferramentas-do-harness>",
    "<dod-steps>",
    "<file_glob>",
    "<formatter_bin>",
    "<formatter_command>",
    "<politica-de-entrega>",
    "<pre-commit-hooks>",
    "<prefixo-de-branch>",
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
    formatter_command: str
    """Comando REAL de `ecossistemas.md`, com `"$FILE_PATH"` na posição que a
    ferramenta exige. Antes isto era preenchido com `formatter_bin`, e o
    gerador de teste divergia da skill: nenhum teste exercitava o comando de
    verdade, que é como o hook ficou inerte em Java sem ninguém notar."""
    dir_escopo: str
    setup_steps: str
    pre_commit: str
    formatavel: str
    """Arquivo real da fixture que o hook de formatação DEVE alcançar."""
    nao_formatavel: str
    """Arquivo real da fixture que o hook DEVE ignorar."""
    escopa_por_arquivo: bool = True
    """Se o formatter aceita caminho de arquivo.

    `spring-javaformat` e `ktlint` sem `--file` formatam o modulo inteiro:
    pendurar isso no hook de edicao faria cada tecla disparar uma JVM e um
    build completo. Hook que atrapalha e hook que o time desliga — e quando
    desliga, leva o resto do enforcement junto. Nesses casos a formatacao vai
    para o pre-commit e o CI, e a ausencia vira item do Plano de Remediacao.
    """

    @property
    def comandos(self) -> list[str]:
        return [c.strip() for c in self.dod_gerada.split("&&")] if self.dod else []

    @property
    def dod_gerada(self) -> str:
        """A DoD que vai para os arquivos: comandos da stack + check-arch.

        Regra arquitetural so vale se algo a executar sem ninguem pedir — na
        cadeia da DoD ela vira parte de "concluido", que e o unico ponto que
        o agente sempre consulta. Repo sem sensores continua com DoD vazia
        (regra de honestidade da FASE 2): inventar uma DoD que so roda o
        check-arch daria um verde que o repositorio nao merece.
        """
        if not self.dod:
            return ""
        return f"{self.dod} && bash .claude/check-arch.sh"

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
        formatter_command='npx prettier --write "$FILE_PATH"',
        dir_escopo="src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint",
        formatavel="src/total.ts",
        nao_formatavel="package.json",
    ),
    # Mesma stack do `node`; o que muda e a arvore: esta fixture tem
    # `openspec/`, e e a unica que exercita o ramo com OpenSpec.
    "node-openspec": Stack(
        dod="npm test && npm run lint && npx tsc --noEmit",
        file_glob="*.js|*.ts|*.mjs|*.cjs",
        formatter_bin="npx",
        formatter_command='npx prettier --write "$FILE_PATH"',
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
        formatter_command='npx prettier --write "$FILE_PATH"',
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
        formatter_command='npx prettier --write "$FILE_PATH"',
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
        formatter_command='mvn -q spotless:apply -DspotlessFiles="$FILE_PATH"',
        dir_escopo="src/main/java",
        setup_steps="      - uses: actions/setup-java@v4",
        pre_commit="mvn checkstyle:check",
        formatavel="src/main/java/com/exemplo/Estoque.java",
        nao_formatavel="pom.xml",
    ),
    "java-gradle": Stack(
        dod="./gradlew test && ./gradlew checkstyleMain && ./gradlew spotlessCheck",
        file_glob="*.java|*.kt",
        formatter_bin="./gradlew",
        formatter_command='./gradlew -q spotlessApply -PspotlessIdeHook="$FILE_PATH"',
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
        formatter_command='dotnet format Catalogo.sln --include "$FILE_PATH"',
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
        formatter_command='gofmt -w "$FILE_PATH"',
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
        formatter_command='npx prettier --write "$FILE_PATH"',
        dir_escopo="apps/web/src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint --workspaces",
        formatavel="apps/web/src/formata.ts",
        nao_formatavel="package.json",
    ),
    # Mesma árvore do `monorepo`, com o ponto de entrada único já aplicado na
    # raiz. É a recomendação do grupo B em forma de fixture: com ela, a DoD
    # usa os scripts REAIS do repositório (`npm test`) em vez da forma
    # delegante que a skill precisa inventar quando a raiz é vazia.
    "monorepo-com-raiz": Stack(
        dod="npm test && npm run lint && npm run typecheck",
        file_glob="*.js|*.jsx|*.ts|*.tsx",
        formatter_bin="npx",
        formatter_command='npx prettier --write "$FILE_PATH"',
        dir_escopo="apps/web/src",
        setup_steps="      - uses: actions/setup-node@v4\n      - run: npm ci",
        pre_commit="npm run lint",
        formatavel="apps/web/src/formata.ts",
        nao_formatavel="package.json",
    ),
    # Perfil Spring: formatter que NAO escopa por arquivo. Sem esta fixture, a
    # regra "nao gere hook que formata o modulo inteiro" era so prosa.
    "java-spring": Stack(
        dod="mvn test && mvn checkstyle:check",
        file_glob="*.java",
        formatter_bin="mvn",
        formatter_command="",
        escopa_por_arquivo=False,
        dir_escopo="src/main/java",
        setup_steps="      - uses: actions/setup-java@v4",
        pre_commit="mvn spring-javaformat:validate",
        formatavel="src/main/java/com/exemplo/Pedido.java",
        nao_formatavel="pom.xml",
    ),
    # Os quatro abaixo estavam só documentados em `ecossistemas.md`. Sem
    # fixture, a linha da tabela era uma promessa que nada exercitava.
    "python": Stack(
        dod="pytest && ruff check . && mypy",
        file_glob="*.py",
        formatter_bin="ruff",
        formatter_command='ruff format "$FILE_PATH"',
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
        formatter_command='rustfmt "$FILE_PATH"',
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
        formatter_command='rubocop -A "$FILE_PATH"',
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
        formatter_command='php-cs-fixer fix "$FILE_PATH"',
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
        formatter_command='formatter-nao-definido "$FILE_PATH"',
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


def _sem_format_hook(no: object) -> object:
    """Poda do config de hook toda entrada que cite o `format-on-edit.sh`."""
    if isinstance(no, list):
        return [_sem_format_hook(x) for x in no if "format-on-edit" not in json.dumps(x)]
    if isinstance(no, dict):
        return {k: _sem_format_hook(v) for k, v in no.items()}
    return no


def gerar(nome: str, destino: Path) -> Stack:
    """Copia a fixture `nome` para `destino` e grava o harness sobre ela."""
    stack = STACKS[nome]
    shutil.copytree(FIXTURES / nome, destino, dirs_exist_ok=True)

    # Condicao do catalogo (`arquivos-gerados.md`): `openspec/config.yaml`
    # somente se `openspec/` existir; `TASKS.md` somente se NAO existir. Sao
    # exclusivos — duas fontes de trabalho no mesmo repo e o agente escolhendo
    # a errada em metade das sessoes.
    usa_openspec = (destino / "openspec").is_dir()

    _grava(
        destino,
        "AGENTS.md",
        _preenche(
            "AGENTS.md",
            {
                "<2-3 linhas: o que é a aplicação, stack com versões exatas>": f"Fixture {nome}.",
                "<Preencher via descoberta — nunca de memória. Fontes: manifestos, CI>": "",
                "<comandos reais do repo, encadeados com &&, "
                "priorizando o que o CI exige>": stack.dod_gerada,
                "<branch-base>": "main",
                # A variante depende do repo: mandar usar `/opsx:propose` num
                # repo sem OpenSpec instrui o agente a chamar um comando que
                # nao existe, e a sessao morre no primeiro pedido novo.
                "<como-propor-mudanca-de-plano>": (
                    "Para criar ou modificar planos (proposals, specs, tasks), use os\n"
                    "comandos OpenSpec (`/opsx:propose`, `/opsx:apply`) — nunca edite\n"
                    "artefatos de `openspec/` manualmente."
                    if usa_openspec
                    else "Para criar ou modificar o plano, acrescente o grupo ao `TASKS.md` no\n"
                    "formato descrito abaixo e confirme com o usuário antes de executá-lo."
                ),
                # Fixtures não têm histórico git: o prefixo cai no default
                # declarado e a política pede a decisão ao usuário, que é o
                # comportamento correto na ausência de evidência.
                "<prefixo-de-branch>": "feature/",
                "<politica-de-entrega>": (
                    "- Política de entrega após o commit do grupo: NÃO ENCONTRADA no\n"
                    "  repositório. Confirme com o time se é push + PR ou merge direto\n"
                    "  antes de publicar a primeira feature branch."
                ),
                "<restrição 1 — derivada de convenção real do repo>": "editar artefato de build",
                "<restrição 2>": "alterar o lockfile à mão",
                "<ferramentas-do-harness>": (
                    "- Para fechar um grupo do plano: skill `executar-grupo` (passo a passo).\n"
                    "- Para verificar a Definition of Done: comando `/dod`.\n"
                    "- Hooks de agent loop ativos: gate de comandos destrutivos e formatação\n"
                    "  automática a cada edição.\n"
                    "- Para conferir se o protocolo vem sendo seguido:\n"
                    "  `sh .claude/medir-aderencia.sh` (diagnóstico, não gate)."
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
    # Formatter que nao escopa por arquivo NAO vira hook de edicao: rodaria o
    # modulo inteiro a cada tecla. A formatacao fica no pre-commit e no CI, e
    # a ausencia e um item do Plano de Remediacao — hook faltando sem
    # explicacao parece esquecimento da skill.
    if stack.escopa_por_arquivo:
        _grava(
            destino,
            ".claude/hooks/format-on-edit.sh",
            _preenche(
                "hooks/format-on-edit.sh",
                {
                    "<file_glob>": stack.file_glob,
                    "<formatter_bin>": stack.formatter_bin,
                    "<formatter_command>": stack.formatter_command,
                },
            ),
        )
    _grava(
        destino,
        ".claude/commands/dod.md",
        _preenche("dod-command.md", {"<dod-command>": stack.dod_gerada}),
    )
    # Registro de regras arquiteturais + runner. Vão SEMPRE, inclusive em repo
    # sem sensores: as regras da semente checam invariantes do próprio harness
    # (hooks que parseiam, manifesto válido, marcador sobrevivente), que não
    # dependem de test runner nenhum. O que não vai, sem sensores, é a DoD que
    # os executa — ver `dod_gerada`.
    _grava(destino, ".harness/arch-rules.json", (RESOURCES / "arch-rules.json").read_text())
    # Registro de risco do gate. Vai junto do arch-rules e pelo mesmo motivo:
    # o que precisa ser ajustado por repositório não pode morar dentro de um
    # script. A defesa contra edição maliciosa é a regra G01, que executa o
    # gate na cadeia da DoD.
    _grava(destino, ".harness/gate-rules.json", (RESOURCES / "gate-rules.json").read_text())
    _grava(destino, ".claude/check-arch.sh", (RESOURCES / "check-arch.sh").read_text())
    (destino / ".claude/check-arch.sh").chmod(0o755)
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
        *(() if usa_openspec else (("TASKS.md", "TASKS.md"),)),
        ("editorconfig-base", ".editorconfig"),
        ("hooks/gate-destructive.sh", ".claude/hooks/gate-destructive.sh"),
        # Vai SEMPRE, inclusive onde o `format-on-edit.sh` não vai: observar
        # não depende de o formatter escopar por arquivo, e é justamente no
        # repo com menos enforcement que saber o que a sessão fez vale mais.
        ("hooks/registrar-sessao.sh", ".claude/hooks/registrar-sessao.sh"),
        ("verificar-harness.sh", ".claude/verificar-harness.sh"),
        ("medir-aderencia.sh", ".claude/medir-aderencia.sh"),
        ("skills/executar-grupo/SKILL.md", ".claude/skills/executar-grupo/SKILL.md"),
        ("CLAUDE.md", "CLAUDE.md"),
        ("CLAUDE.md", f"{stack.dir_escopo}/CLAUDE.md"),
    ]:
        _grava(destino, alvo, (RESOURCES / origem).read_text())

    # Config de hook apontando para script inexistente e falha silenciosa: no
    # Claude Code e no Devin o hook morre, e no Cursor com `failClosed` o
    # agente perde o shell inteiro. Sem hook de formatacao, o registro dele
    # sai dos tres.
    for origem, alvo in [
        ("claude-settings.json", ".claude/settings.json"),
        ("devin-hooks.json", ".devin/hooks.v1.json"),
        ("cursor-hooks.json", ".cursor/hooks.json"),
    ]:
        cfg = json.loads((RESOURCES / origem).read_text())
        if not stack.escopa_por_arquivo:
            cfg = _sem_format_hook(cfg)
        _grava(destino, alvo, json.dumps(cfg, indent=2, ensure_ascii=False) + "\n")

    if usa_openspec:
        # Os valores vão entre parênteses porque os marcadores em prosa são
        # longos: sem eles o `ruff format` colapsa cada par numa linha só e o
        # `ruff check` reprova por E501 — as duas metades da mesma ferramenta
        # discordando, com o hook de formatação aplicando a que quebra a DoD.
        subs_openspec = {
            "<stack e ferramentas de teste/lint/types descobertas — 2-3 linhas>": (
                f"Fixture {nome}. Verificação: {stack.dod_gerada}."
            ),
            "<comandos reais do repo encadeados com && — idênticos ao AGENTS.md>": (
                stack.dod_gerada
            ),
            "<3-6 restrições — idênticas às do AGENTS.md, derivadas do repo real>": (
                "- Não editar artefato de build\n  - Não alterar o lockfile à mão"
            ),
        }
        _grava(
            destino,
            "openspec/config.yaml",
            _preenche("openspec-config.yaml", subs_openspec),
        )

    # O agente cita a branch base no comando de diff, então não é cópia crua:
    # marcador não preenchido aqui é marcador sobrevivente, e a FASE 5 o acusa.
    _grava(
        destino,
        ".claude/agents/propor-regra-arch.md",
        _preenche("agents/propor-regra-arch.md", {"<branch-base>": "main"}),
    )

    scripts = (
        "init.sh",
        ".claude/hooks/gate-destructive.sh",
        ".claude/hooks/registrar-sessao.sh",
        *((".claude/hooks/format-on-edit.sh",) if stack.escopa_por_arquivo else ()),
        ".claude/verificar-harness.sh",
        ".claude/medir-aderencia.sh",
    )
    for script in scripts:
        (destino / script).chmod(0o755)

    readme = destino / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {nome}\n\nRepositorio de exemplo.\n\n## Testes\n\n```\n{stack.dod}\n```\n",
            newline="\n",
        )

    # O ignore é do SUBDIRETÓRIO `trace/`, nunca de `.harness/`: as regras
    # arquiteturais moram em `.harness/arch-rules.json` e são versionadas de
    # propósito — é o registro que faz cada classe de erro ser cometida uma
    # vez só. Ignorar `.harness/` inteiro mataria isso junto com o trace.
    gitignore = destino / ".gitignore"
    gitignore.write_text(
        gitignore.read_text()
        + "\n# Environment files (never commit credentials)\n.env\n.env.*\n"
        + "\n# Agent session trace (local, never commit)\n.harness/trace/\n",
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
                "<dod-command>": stack.dod_gerada,
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
