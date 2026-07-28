"""Testes do harness GERADO, em repositórios de exemplo de cada ecossistema.

`test_skill.py` valida os templates; aqui o harness é de fato produzido
sobre uma fixture real e depois executado. A diferença importa: um glob
como `*.{js,ts}` passa em qualquer inspeção do template e só se revela
inerte quando o hook gerado roda contra um arquivo `.ts` de verdade.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml
from gerar import COM_SENSORES, PREENCHIVEIS, Stack, entrada_do_hook, gerar

MARCADORES = re.compile("|".join(re.escape(m) for m in PREENCHIVEIS))


# Só os ecossistemas com DoD real: `sem-sensores` não recebe enforcement por
# construção, então as asserções sobre CI e pre-commit não se aplicam a ele.
# O que ele deve NÃO ter é verificado em `test_honestidade`.
@pytest.fixture(params=sorted(COM_SENSORES), name="repo")
def _repo(request: pytest.FixtureRequest, tmp_path: Path) -> tuple[Path, Stack, str]:
    nome = str(request.param)
    destino = tmp_path / nome
    stack = gerar(nome, destino)
    return destino, stack, nome


def _roda_hook(
    script: Path, entrada: str, extra_path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if extra_path is not None:
        env["PATH"] = f"{extra_path}{os.pathsep}{env['PATH']}"
    return subprocess.run(
        ["bash", str(script)], input=entrada, capture_output=True, text=True, env=env, check=False
    )


def test_json_gerado_parseia(repo: tuple[Path, Stack, str]) -> None:
    destino, _, _ = repo
    for rel in (".claude/settings.json", ".devin/hooks.v1.json"):
        json.loads((destino / rel).read_text())


def test_yaml_gerado_parseia(repo: tuple[Path, Stack, str]) -> None:
    destino, _, _ = repo
    for rel in (".pre-commit-config.yaml", ".github/workflows/harness-dod.yml"):
        assert yaml.safe_load((destino / rel).read_text()) is not None


def test_nenhum_marcador_sobreviveu(repo: tuple[Path, Stack, str]) -> None:
    """Só as linhas ATIVAS importam. Os templates listam nos comentários os
    exemplos das outras stacks (`dotnet format <sln>` num repo Node), e isso
    é documentação, não marcador esquecido. Marcador em comentário que
    corrompe o arquivo ao ser substituído é pego pelos testes de parse."""
    destino, stack, _ = repo
    gerados = [
        destino / "AGENTS.md",
        destino / stack.dir_escopo / "AGENTS.md",
        destino / "init.sh",
        destino / ".claude/commands/dod.md",
        destino / ".claude/hooks/format-on-edit.sh",
        destino / ".pre-commit-config.yaml",
        destino / ".github/workflows/harness-dod.yml",
    ]
    sobreviventes = []
    for p in gerados:
        for n, linha in enumerate(p.read_text().splitlines(), 1):
            if not linha.lstrip().startswith("#") and MARCADORES.search(linha):
                sobreviventes.append(f"{p.name}:{n}: {linha.strip()[:60]}")
    assert sobreviventes == [], f"marcadores não preenchidos: {sobreviventes}"


def test_todo_registro_de_hook_aponta_para_script_executavel(
    repo: tuple[Path, Stack, str],
) -> None:
    """Um registro por agente-alvo, todos apontando para scripts que existem.

    Registro órfão é falha silenciosa: no Claude Code e no Devin o hook morre
    e o comando destrutivo passa; no Cursor, com `failClosed`, o agente perde
    o shell inteiro. Nenhum dos dois aparece como erro para o usuário.
    """
    destino, _, _ = repo
    configs = [".claude/settings.json", ".devin/hooks.v1.json", ".cursor/hooks.json"]
    encontrados: set[str] = set()
    for rel in configs:
        caminho = destino / rel
        assert caminho.is_file(), f"{rel} não foi gerado — agente sem enforcement"
        referencias = set(re.findall(r"[.\w/-]*\.claude/hooks/[a-z-]+\.sh", caminho.read_text()))
        assert referencias, f"{rel} não registra nenhum hook"
        for ref in referencias:
            # `lstrip("./")` comeria o ponto de `.claude`: é remoção de prefixo.
            script = destino / ref.removeprefix("./")
            assert script.is_file(), f"{rel} aponta para script inexistente: {ref}"
            assert os.access(script, os.X_OK), f"{rel} aponta para script não executável: {ref}"
            encontrados.add(script.name)
    assert encontrados == {"gate-destructive.sh", "format-on-edit.sh"}


@pytest.mark.parametrize("evento", ["tool_input", "cursor"])
def test_gate_gerado_bloqueia_nos_dois_formatos_de_entrada(
    repo: tuple[Path, Stack, str], evento: str
) -> None:
    """O Cursor manda `command` no topo; Claude Code e Devin, em `tool_input`.

    Ler só um formato deixa o gate inerte no outro agente — ele responde 0
    para tudo, inclusive para o comando destrutivo.
    """
    destino, _, _ = repo
    comando = "git push origin main --force"
    entrada = (
        json.dumps({"command": comando}) if evento == "cursor" else entrada_do_hook("Bash", comando)
    )
    assert _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada).returncode == 2


def test_manifesto_lista_arquivos_que_existem(repo: tuple[Path, Stack, str]) -> None:
    """O manifesto é o que torna o harness atualizável e removível.

    Listando arquivo que não foi gravado, ele mente sobre o estado do repo e
    a próxima geração trata como "da skill" algo que nunca existiu.
    """
    destino, stack, _ = repo
    manifesto = json.loads((destino / ".claude/harness.json").read_text())["harness"]
    assert manifesto["dod"] == stack.dod, "manifesto com DoD diferente da gerada"
    assert manifesto["versao"], "manifesto sem versão da skill"
    ausentes = [a for a in manifesto["arquivos"] if not (destino / a).is_file()]
    assert ausentes == [], f"manifesto lista arquivo inexistente: {ausentes}"
    for essencial in ("AGENTS.md", "CLAUDE.md", ".claude/hooks/gate-destructive.sh"):
        assert essencial in manifesto["arquivos"], f"manifesto não registra {essencial}"


def test_dod_identica_em_todo_lugar(repo: tuple[Path, Stack, str]) -> None:
    """DoD divergente entre AGENTS.md e /dod faz o agente verificar uma coisa
    e o CI cobrar outra."""
    destino, stack, _ = repo
    for rel in ("AGENTS.md", ".claude/commands/dod.md"):
        assert stack.dod in (destino / rel).read_text(), f"DoD ausente ou diferente em {rel}"


def test_ci_roda_todos_os_comandos_da_dod(repo: tuple[Path, Stack, str]) -> None:
    """Um CI que roda menos que a DoD é pior que nenhum: o agente acha que
    verificou tudo e o pipeline nunca cobra o que ficou de fora."""
    destino, stack, _ = repo
    workflow = yaml.safe_load((destino / ".github/workflows/harness-dod.yml").read_text())
    steps = [s.get("run", "") for s in workflow["jobs"]["dod"]["steps"]]
    ausentes = [c for c in stack.comandos if not any(c in s for s in steps)]
    assert ausentes == [], f"comandos da DoD que o CI não roda: {ausentes}"


def test_escopo_nao_duplica_o_protocolo(repo: tuple[Path, Stack, str]) -> None:
    destino, stack, _ = repo
    escopo = (destino / stack.dir_escopo / "AGENTS.md").read_text()
    corpo = re.sub(r"<!--.*?-->", "", escopo, flags=re.S)
    for termo in ("WIP=1", "Definition of Done", "SESSION_STATE"):
        assert termo not in corpo


def test_ponte_claude_md_importa_o_agents_md_irmao(repo: tuple[Path, Stack, str]) -> None:
    """O Claude Code carrega CLAUDE.md e não carrega AGENTS.md — nem na raiz,
    nem em subdiretório. Sem a ponte o protocolo é gravado e nunca entra no
    contexto: nada falha, o agente só ignora as regras. O import precisa
    começar a linha, fora de crase e de bloco de código, senão não é
    parseado e vira texto literal."""
    destino, stack, _ = repo
    for diretorio in (destino, destino / stack.dir_escopo):
        ponte = diretorio / "CLAUDE.md"
        assert ponte.exists(), f"sem ponte para o Claude Code em {diretorio}"
        linhas = ponte.read_text().splitlines()
        assert "@AGENTS.md" in linhas, f"{ponte} não importa o AGENTS.md irmão"
        assert (diretorio / "AGENTS.md").exists(), f"import de {ponte} não resolve"


def test_ponte_nao_duplica_o_protocolo(repo: tuple[Path, Stack, str]) -> None:
    """Ponte é import, não cópia: duas fontes divergem na primeira edição."""
    destino, stack, _ = repo
    for diretorio in (destino, destino / stack.dir_escopo):
        corpo = re.sub(r"<!--.*?-->", "", (diretorio / "CLAUDE.md").read_text(), flags=re.S)
        for termo in ("WIP=1", "Definition of Done", "SESSION_STATE"):
            assert termo not in corpo, f"{diretorio}/CLAUDE.md copiou o protocolo"


@pytest.mark.parametrize(
    "comando", ["rm -rf /tmp/x", "git push --force", "npm publish", "dotnet nuget push p.nupkg"]
)
def test_gate_gerado_bloqueia(repo: tuple[Path, Stack, str], comando: str) -> None:
    destino, _, _ = repo
    r = _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada_do_hook("Bash", comando))
    assert r.returncode == 2, "exit != 2 significa gate falhando ABERTO"


def test_gate_gerado_libera_a_dod_da_stack(repo: tuple[Path, Stack, str]) -> None:
    """O gate não pode bloquear o próprio comando que o harness manda rodar."""
    destino, stack, _ = repo
    primeiro = stack.dod.split("&&")[0].strip()
    r = _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada_do_hook("Bash", primeiro))
    assert r.returncode == 0, f"o gate bloqueou a própria DoD: {primeiro}"


def test_formatter_alcanca_o_codigo_da_stack(repo: tuple[Path, Stack, str], tmp_path: Path) -> None:
    destino, stack, nome = repo
    fake = tmp_path / f"bin-{nome}"
    fake.mkdir()
    (fake / stack.formatter_bin).write_text('#!/bin/bash\nprintf "FORMATADO" >> "$1"\n')
    (fake / stack.formatter_bin).chmod(0o755)

    alvo = destino / stack.formatavel
    original = alvo.read_text()
    _roda_hook(
        destino / ".claude/hooks/format-on-edit.sh",
        entrada_do_hook("Edit", str(alvo)),
        extra_path=fake,
    )
    assert "FORMATADO" in alvo.read_text(), (
        f"o hook não alcançou {stack.formatavel} com o glob {stack.file_glob!r}"
    )
    assert alvo.read_text() != original


def test_formatter_ignora_o_que_nao_e_codigo(repo: tuple[Path, Stack, str], tmp_path: Path) -> None:
    destino, stack, nome = repo
    fake = tmp_path / f"bin-neg-{nome}"
    fake.mkdir()
    (fake / stack.formatter_bin).write_text('#!/bin/bash\nprintf "FORMATADO" >> "$1"\n')
    (fake / stack.formatter_bin).chmod(0o755)

    alvo = destino / stack.nao_formatavel
    _roda_hook(
        destino / ".claude/hooks/format-on-edit.sh",
        entrada_do_hook("Edit", str(alvo)),
        extra_path=fake,
    )
    assert "FORMATADO" not in alvo.read_text(), (
        f"o hook formatou {stack.nao_formatavel}, que não é código da stack"
    )
