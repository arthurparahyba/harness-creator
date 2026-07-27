"""Sensores da skill harness-creator.

A skill gera arquivos que só falham na máquina de quem os usa: um `\\r` num
hook, um YAML que corrompe ao substituir placeholder, um link morto entre
fases. Estes testes rodam essas verificações antes de virarem problema de
outra pessoa.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

# A lista de marcadores vive em `gerar.py`: os dois arquivos de teste precisam
# dela e duas cópias divergiam em silêncio.
from gerar import PREENCHIVEIS

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / ".claude" / "skills" / "harness-creator"
RESOURCES = SKILL / "resources"
REFERENCES = SKILL / "references"

IGNORADOS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
}


def arquivos_do_repo() -> list[Path]:
    return [
        p for p in RAIZ.rglob("*") if p.is_file() and not IGNORADOS & set(p.relative_to(RAIZ).parts)
    ]


def test_nenhum_arquivo_com_crlf() -> None:
    """CRLF num .sh vira shebang `/bin/bash^M` e o hook morre com exit 1.

    Em PreToolUse, exit 1 é erro não-bloqueante: o comando destrutivo executa.
    O gate falha ABERTO, silenciosamente.
    """
    culpados = []
    for p in arquivos_do_repo():
        dados = p.read_bytes()
        if b"\0" in dados[:8192]:
            continue  # binário: \r\n ali é coincidência de bytes, não quebra de linha
        if b"\r\n" in dados:
            culpados.append(str(p.relative_to(RAIZ)))
    assert culpados == [], f"arquivos com CRLF: {culpados}"


@pytest.mark.parametrize("nome", ["claude-settings.json", "devin-hooks.json"])
def test_templates_json_parseiam(nome: str) -> None:
    json.loads((RESOURCES / nome).read_text())


def test_settings_tem_wrapper_hooks() -> None:
    """Sem a chave `hooks` na raiz, nenhum scanner detecta os hooks."""
    assert "hooks" in json.loads((RESOURCES / "claude-settings.json").read_text())


@pytest.mark.parametrize(
    "nome", ["ci-workflow.yml", "pre-commit-config.yaml", "openspec-config.yaml"]
)
def test_templates_yaml_parseiam_apos_preenchimento(nome: str) -> None:
    """Regressão: um marcador repetido no comentário de cabeçalho fazia a
    substituição vazar para fora do comentário e corromper o YAML."""
    texto = (RESOURCES / nome).read_text()
    for marcador in PREENCHIVEIS:
        texto = texto.replace(marcador, _dummy(marcador))
    yaml.safe_load(texto)


def _dummy(marcador: str) -> str:
    if marcador in ("<setup-steps>", "<dod-steps>"):
        return "      - run: echo ok"
    if marcador == "<pre-commit-hooks>":
        return "      - id: x\n        entry: echo ok\n        language: system"
    return "x"


@pytest.mark.parametrize("nome", ["gate-destructive.sh", "format-on-edit.sh"])
def test_hooks_tem_shebang_na_primeira_linha(nome: str) -> None:
    assert (RESOURCES / "hooks" / nome).read_bytes().startswith(b"#!/bin/bash\n")


@pytest.fixture(scope="session")
def path_sem_python(tmp_path_factory: pytest.TempPathFactory) -> str:
    """PATH com o essencial de shell e NENHUM Python.

    É o ambiente real de um container Go, .NET ou Java. O gate exigia Python
    para ler o JSON e saía com exit 2 quando não o encontrava — ou seja,
    bloqueava TODO comando do agente, do `npm test` ao `go build`. O harness
    deixava de proteger e passava a impedir o trabalho.
    """
    destino = tmp_path_factory.mktemp("path-sem-python")
    for binario in ("bash", "cat", "grep", "sed", "awk", "env", "printf"):
        origem = shutil.which(binario)
        if origem:
            (destino / binario).symlink_to(origem)
    return str(destino)


def _rodar_gate(comando: str, *, cursor: bool = False, path: str | None = None) -> int:
    """Executa o gate com o JSON no formato de cada agente.

    `cursor=True` usa `{"command": ...}` no topo, que é o que o
    `beforeShellExecution` do Cursor envia; os demais aninham em `tool_input`.
    """
    payload = (
        {"command": comando}
        if cursor
        else {"tool_name": "Bash", "tool_input": {"command": comando}}
    )
    return _rodar_gate_bruto(json.dumps(payload), path=path)


def _rodar_gate_bruto(entrada: str, *, path: str | None = None) -> int:
    return subprocess.run(
        ["bash", str(RESOURCES / "hooks" / "gate-destructive.sh")],
        input=entrada,
        capture_output=True,
        text=True,
        env={"PATH": path} if path else None,
        check=False,
    ).returncode


@pytest.mark.parametrize(
    "comando",
    [
        "rm -rf /tmp/x",
        "git push origin main --force",
        "git reset --hard HEAD~3",
        "DROP TABLE users",
        # Publicação de artefato: irreversível em registry público.
        "npm publish",
        "pnpm publish --access public",
        "mvn deploy -DskipTests",
        "mvn release:perform",
        "./gradlew publish",
        "dotnet nuget push pkg.nupkg -k $KEY",
        "cargo publish",
        "twine upload dist/*",
        "terraform destroy -auto-approve",
        "go clean -modcache",
    ],
)
def test_gate_bloqueia_destrutivo(comando: str) -> None:
    assert _rodar_gate(comando) == 2, "exit != 2 significa gate falhando ABERTO"


@pytest.mark.parametrize(
    "comando",
    [
        "pytest",
        "ruff check .",
        "git status",
        # Um gate que bloqueia o dia a dia é desligado pelo time na primeira
        # semana — o falso positivo custa tanto quanto o falso negativo.
        "npm test",
        "npm ci",
        "npm run build",
        "mvn test",
        "./gradlew test",
        "dotnet test App.sln",
        "go test ./...",
        "ng test --watch=false",
        "terraform plan",
        "go clean -testcache",
    ],
)
def test_gate_libera_comando_seguro(comando: str) -> None:
    assert _rodar_gate(comando) == 0


@pytest.mark.parametrize(
    ("comando", "esperado"),
    [
        ("rm -rf /tmp/x", 2),
        ("git push origin main --force", 2),
        ("npm test", 0),
        ("go build ./...", 0),
    ],
)
def test_gate_funciona_sem_python_instalado(
    comando: str, esperado: int, path_sem_python: str
) -> None:
    """O fallback em awk é o que mantém o gate útil fora de repo Python.

    Sem ele o hook saía 2 para qualquer entrada: o agente não conseguia rodar
    nem o `npm test` da própria DoD.
    """
    assert _rodar_gate(comando, path=path_sem_python) == esperado


@pytest.mark.parametrize(
    ("comando", "esperado"), [("terraform destroy -auto-approve", 2), ("npm ci", 0)]
)
def test_gate_entende_o_formato_do_cursor(comando: str, esperado: int) -> None:
    """`beforeShellExecution` manda `command` no topo, não em `tool_input`.

    Lendo só `tool_input`, o gate via string vazia e liberava tudo no Cursor.
    """
    assert _rodar_gate(comando, cursor=True) == esperado


def test_gate_libera_evento_sem_comando() -> None:
    """Sem chave `command` não há o que inspecionar — bloquear aqui trava
    leitura de arquivo e qualquer outro tool."""
    entrada = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "/a.txt"}})
    assert _rodar_gate_bruto(entrada) == 0


def test_gate_bloqueia_comando_ilegivel() -> None:
    """Fail-closed apenas quando existe comando e ele não pôde ser lido."""
    assert _rodar_gate_bruto('{"tool_input":{"command":') == 2


def test_extracao_de_json_identica_nos_dois_hooks() -> None:
    """Os hooks duplicam o bloco de extração de propósito: `source` de lib
    irmã morre com exit 1 se o arquivo sumir, e exit 1 em PreToolUse é falha
    ABERTA. O preço da duplicação é este teste — sem ele as cópias divergem."""
    inicio, fim = "# ---8<--- ", "# ---8<--- fim da extracao de JSON ---8<---"
    blocos = []
    for nome in ("gate-destructive.sh", "format-on-edit.sh"):
        texto = (RESOURCES / "hooks" / nome).read_text()
        corpo = texto[texto.index(inicio) : texto.index(fim)]
        # A primeira linha nomeia o arquivo irmão; o resto tem de ser igual.
        blocos.append("\n".join(corpo.splitlines()[1:]))
    assert blocos[0] == blocos[1], "extração de JSON divergiu entre os hooks"


def _preparar_format_hook(tmp: Path, glob: str) -> tuple[Path, dict[str, str]]:
    """Gera o format-on-edit.sh preenchido com um formatter de mentira que
    marca o arquivo, para verificar se o hook de fato o alcança."""
    formatter = tmp / "formatador-falso"
    formatter.write_text('#!/bin/bash\nprintf "FORMATADO" >> "$1"\n')
    formatter.chmod(0o755)
    script = tmp / "format-on-edit.sh"
    script.write_text(
        (RESOURCES / "hooks" / "format-on-edit.sh")
        .read_text()
        .replace("<file_glob>", glob)
        .replace("<formatter_bin>", formatter.name)
        .replace("<formatter_command>", str(formatter))
    )
    script.chmod(0o755)
    env = {"PATH": f"{tmp}:/usr/bin:/bin", "HOME": str(tmp)}
    return script, env


@pytest.mark.parametrize(
    ("arquivo", "deve_formatar"),
    [("app.ts", True), ("app.jsx", True), ("Componente.tsx", True), ("main.py", False)],
)
def test_format_on_edit_alcanca_os_arquivos_da_stack(
    tmp_path: Path, arquivo: str, deve_formatar: bool
) -> None:
    """Regressão: `case` NÃO faz brace expansion, então o glob `*.{js,ts}`
    que a skill documentava nunca casava — em todo repo JS/TS o hook de
    formatação simplesmente não rodava, sem erro nenhum."""
    script, env = _preparar_format_hook(tmp_path, "*.js|*.ts|*.jsx|*.tsx")
    alvo = tmp_path / arquivo
    alvo.write_text("conteudo\n")
    subprocess.run(
        ["bash", str(script)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(alvo)}}),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert ("FORMATADO" in alvo.read_text()) is deve_formatar


def test_format_on_edit_entende_o_formato_do_cursor(tmp_path: Path) -> None:
    """`afterFileEdit` manda `file_path` no topo do JSON. Lendo só
    `tool_input`, o hook saía em silêncio e nada era formatado no Cursor."""
    script, env = _preparar_format_hook(tmp_path, "*.ts")
    alvo = tmp_path / "app.ts"
    alvo.write_text("conteudo\n")
    subprocess.run(
        ["bash", str(script)],
        input=json.dumps({"file_path": str(alvo), "edits": []}),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert "FORMATADO" in alvo.read_text()


def test_glob_com_brace_expansion_nao_funciona_em_case(tmp_path: Path) -> None:
    """Prova de que a sintaxe antiga é inerte — é por isso que a doc proíbe."""
    script, env = _preparar_format_hook(tmp_path, "*.{js,ts,jsx,tsx}")
    alvo = tmp_path / "app.ts"
    alvo.write_text("conteudo\n")
    subprocess.run(
        ["bash", str(script)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(alvo)}}),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert "FORMATADO" not in alvo.read_text()


def test_documentacao_nunca_sugere_glob_com_chaves() -> None:
    """Um exemplo com `{}` na doc reintroduz o bug na próxima geração."""
    # Linha que ALERTA contra o padrão necessariamente o cita; a que o
    # SUGERE, não. Distinguir pelo vocabulário do alerta.
    alerta = ("brace", "casa com nada", "nunca casa", "não casa")
    culpados = []
    for p in [*REFERENCES.glob("*.md"), RESOURCES / "hooks" / "format-on-edit.sh"]:
        for linha in p.read_text().splitlines():
            if re.search(r"\*\.\{[a-z,]+\}", linha) and not any(a in linha for a in alerta):
                culpados.append(f"{p.name}: {linha.strip()[:70]}")
    assert culpados == [], f"glob com brace expansion sugerido em: {culpados}"


def test_skill_md_tem_frontmatter_valido() -> None:
    m = re.match(r"^---\n(.*?)\n---", SKILL.joinpath("SKILL.md").read_text(), re.S)
    assert m, "SKILL.md sem frontmatter"
    fm = yaml.safe_load(m.group(1))
    assert fm["name"] == "harness-creator"
    assert len(fm["description"]) >= 40


def test_frontmatter_nao_tem_campo_inerte() -> None:
    """O loader de skill lê `name` e `description`; o resto do frontmatter é
    texto que ninguém aplica.

    `required-reading` mandava carregar as nove references e a constraint ao
    lado mandava ler só a da fase atual — duas instruções opostas no mesmo
    bloco. Quando a regra vale, ela vive no corpo, que é o que o agente lê.
    """
    m = re.match(r"^---\n(.*?)\n---", SKILL.joinpath("SKILL.md").read_text(), re.S)
    assert m is not None
    inertes = {"execution-mode", "phase-count", "required-reading", "critical-constraints"}
    presentes = inertes & set(yaml.safe_load(m.group(1)))
    assert not presentes, f"campo inerte de volta no frontmatter: {sorted(presentes)}"


def test_corpo_nao_repete_a_lista_de_gatilhos_da_description() -> None:
    """Triggering se decide pela `description`; o corpo so carrega DEPOIS.

    A secao "Quando ativar esta skill" repetia a description quase palavra
    por palavra — nove linhas que nao influenciam disparo nenhum e que
    disputam contexto com o roteiro das fases, que e o que o agente
    realmente precisa ter em maos depois que a skill ja disparou.
    """
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    assert "## Quando ativar" not in corpo, (
        "lista de gatilhos de volta no corpo: ela pertence a `description`"
    )


def test_skill_distingue_fluxo_completo_de_edicao_pontual() -> None:
    """Sem essa fronteira, "acrescente uma linha no AGENTS.md" recebe seis
    fases e uma pausa de aprovacao — um ritual que o usuario nao pediu e que
    gasta a sessao dele."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    assert "edicao pontual" in corpo, "fronteira de escopo perdida na SKILL.md"


def test_regras_inviolaveis_estao_no_corpo() -> None:
    """As regras saíram do frontmatter para o corpo — não podem ter sumido."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    for regra in ("VERBATIM", "unica pausa", "SOMENTE o arquivo da fase", "${VAR}"):
        assert regra in corpo, f"regra perdida na migração do frontmatter: {regra}"


def _destinos_canonicos() -> set[str]:
    """Caminhos de destino declarados em `references/arquivos-gerados.md`."""
    texto = (REFERENCES / "arquivos-gerados.md").read_text()
    # A tabela escreve o destino com barra inicial (`/init.sh`) e a prosa sem.
    return {c.removeprefix("./").strip("/") for c in re.findall(r"`([^`\s]+)`", texto)}


def test_todo_template_tem_destino_documentado() -> None:
    """Template em `resources/` fora da tabela é arquivo que a skill copia
    sem ninguém saber para onde — e que some do plano de aprovação da FASE 4."""
    texto = (REFERENCES / "arquivos-gerados.md").read_text()
    faltando = [
        str(p.relative_to(RESOURCES))
        for p in RESOURCES.rglob("*")
        if p.is_file() and p.name not in texto and str(p.relative_to(RESOURCES)) not in texto
    ]
    assert faltando == [], f"template sem destino em arquivos-gerados.md: {faltando}"


@pytest.mark.parametrize("doc", ["README.md", "MUDANCAS-NO-REPOSITORIO.md"])
def test_docs_nao_citam_caminho_fora_da_tabela_canonica(doc: str) -> None:
    """`arquivos-gerados.md` é a fonte única dos destinos.

    README e MUDANCAS descrevem os mesmos artefatos em prosa; quando um
    destino muda, é ali que a versão antiga sobrevive. Citar caminho é
    permitido — inventar ou manter um que a tabela não conhece, não.
    """
    canonicos = _destinos_canonicos()
    # `<dir-principal>` na tabela é o diretório de código descoberto: a prosa
    # o instancia (`src/AGENTS.md`) e isso não é divergência.
    com_escopo = {c.split("/")[-1] for c in canonicos if c.startswith("<dir-principal>/")}
    citados = set(re.findall(r"`([.\w-]+/[\w./-]+)`", (SKILL / doc).read_text()))
    invencoes = sorted(
        c
        for c in citados
        if c.removeprefix("./").strip("/") not in canonicos and c.split("/")[-1] not in com_escopo
    )
    assert invencoes == [], f"{doc} cita caminho ausente da tabela canônica: {invencoes}"


def test_links_markdown_internos_resolvem() -> None:
    mortos: list[str] = []
    for md in SKILL.rglob("*.md"):
        for alvo in re.findall(r"\]\(([^)#:]+\.md)\)", md.read_text()):
            if not (md.parent / alvo).is_file():
                mortos.append(f"{md.relative_to(SKILL)} -> {alvo}")
    assert mortos == [], f"links quebrados: {mortos}"


@pytest.mark.parametrize("marcador", PREENCHIVEIS)
def test_marcador_preenchivel_esta_documentado(marcador: str) -> None:
    """A instrução tem de estar na FASE 2, que é onde o marcador é preenchido.

    Aceitar a menção em qualquer reference dava falsa segurança: `<setup-steps>`
    aparecia só na lista de proibidos da FASE 5 — o teste passava e o agente
    chegava na hora de preencher sem nenhuma instrução de como fazê-lo.
    """
    fase2 = (REFERENCES / "02-preenchimento-templates.md").read_text()
    assert marcador in fase2, f"{marcador} não é explicado na FASE 2 (é lá que se preenche)"


@pytest.mark.parametrize("marcador", PREENCHIVEIS)
def test_marcador_preenchivel_existe_em_algum_template(marcador: str) -> None:
    """O inverso: instrução para preencher marcador que não existe mais."""
    corpo = "".join(p.read_text() for p in RESOURCES.rglob("*") if p.is_file())
    assert marcador in corpo, f"{marcador} documentado mas ausente dos templates"


def test_nenhum_marcador_orfao_nas_references() -> None:
    """Marcador citado numa fase mas inexistente nos templates é instrução
    para preencher algo que não existe — renomeie um template e a fase fica
    apontando para o nome antigo, em silêncio.

    A allowlist é explícita de propósito: notação de prosa nova exige uma
    edição deliberada aqui, e é isso que impede a lista de virar um filtro
    frouxo que deixa a drift real passar.
    """
    prosa = {
        "<dir-principal>",  # arquivos-gerados.md, coluna de destino
        "<n>",
        "<score>",  # formato do Plano de Remediação
        "<nivel-medido>",
        "<nivel-medido-na-fase-5>",  # instruções de substituição
        "<nome>",  # padrão de hook do pre-commit
    }
    padrao = re.compile(r"<[a-z][a-z0-9_-]*>")
    nos_templates = {
        m for p in RESOURCES.rglob("*") if p.is_file() for m in padrao.findall(p.read_text())
    }
    orfaos = sorted(
        {
            m
            for p in REFERENCES.glob("*.md")
            for m in padrao.findall(p.read_text())
            if m not in nos_templates and m not in prosa
        }
    )
    assert orfaos == [], f"marcadores citados em references/ mas ausentes dos templates: {orfaos}"


def test_skill_nao_depende_de_ferramenta_externa_de_medicao() -> None:
    """A skill precisa funcionar em qualquer repositório, sem rede e sem
    instalar nada. Depender de um scanner externo para fazer o trabalho a
    torna refém da disponibilidade e do vocabulário dele.

    ESTE repositório pode usar o scanner à vontade para evoluir a skill —
    o que não pode é a skill entregue depender dele.
    """
    proibido = re.compile(r"harness-score|\bL[0-4]\b|/108\b")
    culpados = []
    for p in SKILL.rglob("*"):
        if not p.is_file() or b"\0" in p.read_bytes()[:8192]:
            continue
        for n, linha in enumerate(p.read_text().splitlines(), 1):
            # A linha que PROÍBE o vocabulário precisa poder citá-lo.
            if proibido.search(linha) and "ferramenta externa" not in linha:
                culpados.append(f"{p.relative_to(SKILL)}:{n}")
    assert culpados == [], f"acoplamento a ferramenta de medição em: {culpados}"


def test_existe_exatamente_uma_pausa_no_fluxo() -> None:
    """A skill promete autonomia até a FASE 4. Bloco de pausa em outra fase
    faz o agente parar quatro vezes a mais do que o projeto pretende."""
    com_pausa = sorted(p.name for p in REFERENCES.glob("*.md") if "PAUSA" in p.read_text())
    assert com_pausa == ["04-saida-aprovacao.md"], f"pausas em: {com_pausa}"


def test_marcador_preenchivel_nunca_aparece_em_comentario_de_template() -> None:
    """Marcador em comentário E em corpo é uma contradição sem saída.

    A regra 3 manda transcrever VERBATIM, e o item 6 da FASE 5 proíbe o
    marcador de sobrar. Com o marcador dentro do cabeçalho didático, cumprir
    uma quebra a outra — e a substituição ainda grava a instrução falsa
    "PLACEHOLDER: prettier --write deve ser substituido pela skill" no repo
    do usuário. Na iteração 1 do nível D, seis agentes bateram nisso e
    metade apagou o cabeçalho, metade o preservou: a geração passou a
    depender de qual saída o modelo escolheu.

    O `ci-workflow.yml` já se defendia disso; a defesa não tinha sido
    aplicada aos demais templates.
    """
    culpados = []
    for p in RESOURCES.rglob("*"):
        if not p.is_file() or b"\0" in p.read_bytes()[:8192]:
            continue
        # Em Markdown `#` é título, não comentário: o marcador ali é conteúdo
        # a substituir, não documentação. Só `<!-- -->` comenta em .md.
        prefixos = ("<!--",) if p.suffix == ".md" else ("#", "<!--")
        for n, linha in enumerate(p.read_text().splitlines(), 1):
            if not linha.lstrip().startswith(prefixos):
                continue
            for marcador in PREENCHIVEIS:
                if marcador in linha:
                    culpados.append(f"{p.relative_to(RESOURCES)}:{n} {marcador}")
    assert culpados == [], f"marcador preenchivel em comentario: {culpados}"


def test_format_hook_sobrevive_a_ausencia_de_formatter(tmp_path: Path) -> None:
    """Sem formatter, o hook tem de virar no-op — não morrer.

    `# TODO: definir formatter` era a instrução da FASE 2, e o marcador do
    binário fica dentro de `if command -v ... ; then`: o `#` comenta o resto
    da linha, inclusive o `then`. O script passa a falhar com erro de
    sintaxe a cada edição de arquivo, e nenhum item da FASE 5 acusa.
    """
    script, env = _preparar_format_hook(tmp_path, "*.py")
    texto = script.read_text().replace(str(tmp_path / "formatador-falso"), "formatter-nao-definido")
    script.write_text(texto.replace("formatador-falso", "formatter-nao-definido"))
    alvo = tmp_path / "modulo.py"
    alvo.write_text("x = 1\n")
    r = subprocess.run(
        ["bash", str(script)],
        input=json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(alvo)}}),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert r.returncode == 0, f"hook sem formatter quebrou: {r.stderr.strip()[:200]}"
    assert "syntax error" not in r.stderr, r.stderr
    assert alvo.read_text() == "x = 1\n", "no-op deveria deixar o arquivo intacto"


def test_fase2_proibe_todo_dentro_do_hook_de_formatacao() -> None:
    """A instrução que causava o bug não pode voltar por descuido."""
    fase2 = (REFERENCES / "02-preenchimento-templates.md").read_text()
    assert "formatter-nao-definido" in fase2, "FASE 2 sem o preenchimento seguro"


def test_template_agents_nao_traz_restricao_sem_evidencia() -> None:
    """`MUST NOT` fora de `<restrição N>` é regra inventada em todo repo.

    A de migrations vinha fixa e chegava em repositório sem banco nenhum.
    Regra sem evidência ensina o leitor a ignorar a lista inteira.
    """
    # As fixas permitidas são as do PROTOCOLO, que valem em qualquer
    # repositório porque falam do próprio jeito de trabalhar — não do domínio.
    # A allowlist é explícita de propósito: acrescentar uma exige justificar
    # por que ela vale para todo repo do mundo, que é a pergunta certa.
    do_protocolo = ("fonte de trabalho ativa", "escopo do grupo atual")
    # Bullets quebram em várias linhas, e a continuação costuma carregar
    # justamente o trecho que identifica a regra: avaliar linha a linha
    # acusaria a primeira metade de uma regra legítima.
    bullets: list[str] = []
    for ln in (RESOURCES / "AGENTS.md").read_text().splitlines():
        if ln.strip().startswith("- "):
            bullets.append(ln.strip())
        elif bullets and ln.startswith("  ") and ln.strip():
            bullets[-1] += " " + ln.strip()
    inventadas = [
        b
        for b in bullets
        if b.startswith("- MUST NOT:") and "<" not in b and not any(p in b for p in do_protocolo)
    ]
    assert inventadas == [], f"restrição sem evidência fixa no template: {inventadas}"


def test_fase4_exige_conteudo_integral_no_que_destroi_trabalho_do_usuario() -> None:
    """A FASE 4 mostra resumo do que é novo e diff do que altera arquivo do
    usuário — a regra não pode degenerar em "resuma tudo".

    Aprovar sem ler é o risco dos dois lados: o despejo de vinte arquivos
    faz o usuário aprovar no atacado, e o resumo de um `.gitignore` sendo
    reescrito esconde o único caso em que o erro custa trabalho dele.
    """
    texto = (REFERENCES / "04-saida-aprovacao.md").read_text()
    assert "diff completo, sempre" in texto, "FASE 4 sem garantia de diff no destrutivo"
    for destrutivo in (".gitignore", ".mcp.json", "AGENTS.md"):
        assert destrutivo in texto, f"{destrutivo} fora da regra de apresentação"


def test_modo_de_atualizacao_e_alcancavel_das_fases_que_o_usam() -> None:
    """O manifesto existe desde a v2.3 e nenhuma fase o usava para atualizar.

    O caminho só vale se a FASE 1 souber encurtar a descoberta e a FASE 3
    souber que a regra de não sobrescrever não se aplica ao que a própria
    skill gerou. Citado só na SKILL.md, o catálogo nunca é aberto na hora
    em que decide alguma coisa.
    """
    for fase in ("01-descoberta.md", "03-resolucao-conflitos.md"):
        assert "atualizacao.md" in (REFERENCES / fase).read_text(), (
            f"{fase} não alcança o modo de atualização"
        )


def test_atualizacao_preserva_as_recusas_anteriores() -> None:
    """Repropor um item recusado é a skill ignorando decisão já tomada — e
    uma recusa não expira porque a skill mudou de versão."""
    texto = (REFERENCES / "atualizacao.md").read_text()
    assert "recusados" in texto and "repropor" in texto


def test_agents_scoped_nao_carrega_o_protocolo() -> None:
    """O AGENTS.md com escopo é escopo, não protocolo: duplicado, ele diverge
    do da raiz na primeira edição."""
    corpo = re.sub(r"<!--.*?-->", "", (RESOURCES / "AGENTS-scoped.md").read_text(), flags=re.S)
    for termo in ("WIP=1", "Definition of Done", "SESSION_STATE", "## Commits"):
        assert termo not in corpo, f"protocolo duplicado no template com escopo: {termo}"


def test_nenhuma_instrucao_da_skill_e_bloqueada_pelo_proprio_gate() -> None:
    """A skill roda dentro de repositórios protegidos pelo gate que ela mesma
    gera. Uma instrução que contenha a sequência destrutiva literal é
    bloqueada na hora de ser executada — e o item que ela manda verificar
    simplesmente não é verificado.

    O caso real: a FASE 5 mandava testar o gate com `rm -rf` escrito por
    extenso, então a checagem mais importante do enforcement nunca rodava.
    """
    gate = RESOURCES / "hooks" / "gate-destructive.sh"
    bloqueadas = []
    for doc in sorted(REFERENCES.glob("*.md")) + [SKILL / "SKILL.md"]:
        # Só o que está em bloco de código: é o que alguém copia e executa.
        # Prosa que menciona um comando destrutivo não roda, e proibi-la
        # impediria a skill de explicar o que o gate bloqueia.
        dentro = False
        for n, linha in enumerate(doc.read_text().splitlines(), 1):
            if linha.lstrip().startswith("```"):
                dentro = not dentro
                continue
            if not dentro or not linha.strip():
                continue
            payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": linha}})
            r = subprocess.run(["bash", str(gate)], input=payload, capture_output=True, text=True)
            if r.returncode == 2:
                bloqueadas.append(f"{doc.name}:{n}: {linha.strip()[:60]}")
    assert bloqueadas == [], f"instrução que o próprio gate bloqueia: {bloqueadas}"


def test_fase5_cobra_equivalencia_da_dod_e_nao_igualdade_literal() -> None:
    """Exigir a DoD IDÊNTICA em seis arquivos é insatisfazível por construção:
    o init.sh roda só o baseline, o pre-commit é lista de hooks e o CI é um
    step por sensor. Checagem impossível não é rigor — o agente marca como ok
    sem ter verificado, que é pior do que não ter o item."""
    texto = (REFERENCES / "05-verificacao-pos-geracao.md").read_text()
    assert "IDÊNTICO em" not in texto, "voltou a exigir igualdade literal da DoD"
    assert "Equivalência da DoD" in texto
    assert "conjunto de sensores" in texto


def test_formatter_de_python_tem_uma_resposta_so() -> None:
    """Formatter com respostas divergentes faz a geração oscilar entre
    execuções: o mesmo repo recebe `black` numa e `ruff format` noutra.
    `ecossistemas.md` é a fonte única — o resto aponta para ela."""
    fonte = REFERENCES / "ecossistemas.md"
    culpados = []
    for p in SKILL.rglob("*"):
        if not p.is_file() or p == fonte or b"\0" in p.read_bytes()[:8192]:
            continue
        for n, linha in enumerate(p.read_text().splitlines(), 1):
            if re.search(r"\bblack\b", linha) and "ecossistemas.md" not in linha:
                # Citar `[tool.black]` como pista de descoberta é legítimo:
                # é onde procurar o que o repo já usa, não uma prescrição.
                if "[tool.black]" in linha:
                    continue
                culpados.append(f"{p.relative_to(SKILL)}:{n}")
    assert culpados == [], f"segunda resposta para formatter de Python em: {culpados}"


def test_lockfile_e_recomendado_e_nao_gerado() -> None:
    """Gerar lockfile exige resolver dependências pela rede, e a resolução fixa
    versões para o time inteiro. Isso muda o contrato do projeto, então é
    grupo B (recomendado, item a item) e não grupo A (gerado)."""
    gerados = (REFERENCES / "arquivos-gerados.md").read_text()
    linhas_de_tabela = [ln for ln in gerados.splitlines() if ln.startswith("|")]
    assert not any("Lockfile" in ln for ln in linhas_de_tabela), (
        "lockfile voltou para a tabela de arquivos gerados"
    )
    catalogo = (REFERENCES / "remediacoes.md").read_text()
    assert "### Lockfile ausente" in catalogo, "lockfile não virou item do grupo B"


def test_criacao_de_branch_funciona_em_repo_sem_remoto() -> None:
    """`git pull` num repo sem remoto falha, e o passo 4 do protocolo é a
    primeira coisa que o agente executa numa funcionalidade nova: ele quebra
    antes de qualquer trabalho."""
    texto = (RESOURCES / "AGENTS.md").read_text()
    assert "git remote" in texto, "git pull sem guarda para repo sem remoto"


VERIFICADOR = RESOURCES / "verificar-harness.sh"


def test_verificador_aprova_harness_recem_gerado(tmp_path: Path) -> None:
    """O verificador é a FASE 5 executável. Se ele reprova o que a própria
    skill acabou de gerar, ou ele está errado ou a geração está — e nos dois
    casos o usuário recebe um harness que se declara quebrado."""
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    r = subprocess.run(
        ["sh", str(VERIFICADOR), "--raiz", str(repo)], capture_output=True, text=True
    )
    assert r.returncode == 0, f"verificador reprovou geração limpa:\n{r.stdout}"


def test_verificador_reprova_repo_sem_harness(tmp_path: Path) -> None:
    """Checagem que passa em diretório vazio não mede nada. As de ponte e de
    hooks registrados passavam por vacuidade: sem nenhum AGENTS.md, "todo
    AGENTS.md tem irmão" é verdade e não significa coisa alguma."""
    r = subprocess.run(
        ["sh", str(VERIFICADOR), "--raiz", str(tmp_path)], capture_output=True, text=True
    )
    assert r.returncode == 1, "verificador aprovou diretório sem harness nenhum"
    for check in ("Ponte CLAUDE.md", "Hooks registrados"):
        linha = next(ln for ln in r.stdout.splitlines() if check in ln)
        assert linha.startswith("FALHA"), f"passou por vacuidade: {linha}"


def test_verificador_nao_depende_de_python(tmp_path: Path) -> None:
    """Ele roda no repositório do usuário, que pode ser Go, .NET ou Java. Foi
    o mesmo motivo que fez o Grupo 6 tirar o Python do gate: exigi-lo
    transformava o enforcement em erro de setup."""
    import gerar

    repo = tmp_path / "go"
    gerar.gerar("go", repo)
    # Stub que se anuncia como Python e não roda: é o caso real (binário
    # presente mas quebrado, como o stub da MS Store) e isola a variável sem
    # amputar o resto do PATH, que o script legitimamente usa.
    falso = tmp_path / "bin-sem-python"
    falso.mkdir()
    for nome in ("python3", "python"):
        stub = falso / nome
        stub.write_text("#!/bin/sh\nexit 1\n")
        stub.chmod(0o755)
    env = {**os.environ, "PATH": f"{falso}:{os.environ['PATH']}"}
    r = subprocess.run(
        ["sh", str(VERIFICADOR), "--raiz", str(repo)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, f"verificador falhou sem Python no PATH:\n{r.stdout}\n{r.stderr}"
    assert "sem Python" in r.stdout, "não anunciou que caiu na checagem mais fraca"


def test_verificador_nao_carrega_marcador_preenchivel() -> None:
    """Ele é template como os outros: um marcador escrito por extenso seria
    substituído pela FASE 2 dentro do próprio script, corrompendo a lista que
    ele usa para detectar marcadores que sobraram."""
    texto = VERIFICADOR.read_text()
    presentes = [m for m in PREENCHIVEIS if m in texto]
    assert presentes == [], f"marcador literal no verificador: {presentes}"


def test_fase5_delega_as_checagens_mecanicas_ao_verificador() -> None:
    """Dezenove itens em prosa dependem de o modelo ter paciência com os
    dezenove. O que é mecânico vira script; o que sobra na fase é o que exige
    julgamento — e aí a prosa está justificada."""
    texto = (REFERENCES / "05-verificacao-pos-geracao.md").read_text()
    assert "verificar-harness.sh" in texto, "FASE 5 não chama o verificador"
    for julgamento in ("Tempo da DoD", "Equivalência da DoD", "Remediações aceitas"):
        assert julgamento in texto, f"item de julgamento perdido da FASE 5: {julgamento}"


def test_eval_e_skill_verificam_pela_mesma_fonte() -> None:
    """Duas implementações da mesma checagem divergem, e aí o eval aprova o
    que o verificador reprova sem ninguém saber qual está certo."""
    texto = (RAIZ / "evals" / "gradua.py").read_text()
    assert "verificar-harness.sh" in texto, "gradua.py voltou a reimplementar as checagens"


def test_triagem_de_escopo_nao_e_contradita_pelo_resto_do_corpo() -> None:
    """O passo 0 decide entre fluxo completo e edição pontual. Uma segunda
    instrução mandando começar pela FASE 1 sem condição sobrescreve essa
    decisão para quem lê de cima para baixo — e o pedido de uma linha volta a
    receber seis fases."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    incondicionais = [
        ln
        for ln in corpo.splitlines()
        if re.search(r"comece (imediatamente|pela FASE 1)", ln, re.I)
    ]
    assert incondicionais == [], f"ordem incondicional de iniciar a FASE 1: {incondicionais}"
    assert "passo 0" in corpo.lower(), "triagem de escopo deixou de ser passo do fluxo"


def test_roteiro_das_fases_aparece_uma_vez_so() -> None:
    """O roteiro estava em três lugares (EXECUÇÃO IMEDIATA, regras e Roteiro),
    e "leia só a fase atual" em dois. Cada cópia é uma que pode divergir, e
    todas disputam o contexto da mesma invocação."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    # Entrada de roteiro é uma linha numerada que abre com o link da fase. Uma
    # regra que aponta para a fase no meio da frase é ponteiro, não roteiro.
    entradas = re.findall(r"^\d+\. \[FASE (\d)", corpo, re.M)
    assert entradas == list("123456"), f"roteiro das fases duplicado ou incompleto: {entradas}"


def test_toda_regra_inviolavel_traz_o_modo_de_falhar() -> None:
    """Uma regra sem o porquê não é aplicável fora do caso que a gerou: o
    modelo não tem como julgar a situação que ela não previu, e o resultado é
    obediência literal onde era preciso critério."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    bloco = corpo.split("## Regras invioláveis")[1].split("\n## ")[0]
    regras = re.split(r"\n(?=\d+\. )", bloco.strip())[1:]
    curtas = [r.split("\n")[0][:50] for r in regras if len(r.split()) < 20]
    assert curtas == [], f"regra sem modo de falhar declarado: {curtas}"


def test_skill_md_nao_contradiz_o_que_as_fases_dizem() -> None:
    """A SKILL.md resume o que as fases detalham, e resumo desatualizado é uma
    segunda fonte: o modelo lê o corpo em toda invocação e a fase só na hora.
    Estes dois divergiram assim que o Grupo 16 corrigiu a FASE 5."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    assert "DoD identica" not in corpo, (
        "SKILL.md ainda promete DoD idêntica; a FASE 5 cobra equivalência"
    )
    camada = corpo.split("**Enforcement**")[1].split("\n\n")[0]
    assert "lockfile" not in camada.lower(), (
        "lockfile de volta na camada de enforcement; ele é remediação do grupo B"
    )


def test_fronteira_de_escopo_tem_exemplos() -> None:
    """Critério em prosa é onde a skill mais erra de tamanho. Exemplos de
    pedido→ação resolvem o caso ambíguo que a regra não alcança."""
    corpo = SKILL.joinpath("SKILL.md").read_text().split("---", 2)[-1]
    assert corpo.count("Pedido:") >= 2, "exemplos da fronteira de escopo sumiram"
    assert "Acao:" in corpo


def test_plano_de_remediacao_nao_fala_em_pontuacao() -> None:
    """O placar é de uma ferramenta externa que o usuário não roda. A FASE 4 é
    onde o plano é redigido, então é lá que a proibição do catálogo precisa
    valer — senão ela fica só no catálogo e o plano sai com pontos."""
    texto = (REFERENCES / "04-saida-aprovacao.md").read_text()
    assert "vocabulário de pontuação" in texto
    assert "pontos depois" not in texto, "ordenação por pontuação voltou à FASE 4"
