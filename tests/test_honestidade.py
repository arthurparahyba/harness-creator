"""A regra de honestidade: o que a skill NÃO pode gerar.

O comportamento mais delicado da skill é o que ela deixa de fazer. Um harness
que gera enforcement sem sensor por trás — pre-commit sem hook, CI que passa
sem rodar nada — dá ao agente um verde que ele não mereceu, e isso é pior que
não ter enforcement, porque parece ter.

Até aqui esse comportamento não tinha sensor nenhum: os testes de geração
exercitavam só os ecossistemas com DoD real, então uma regressão que passasse
a gerar enforcement vazio sairia sem ninguém perceber.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from gerar import STACKS, gerar


@pytest.fixture(name="sem_sensores")
def _sem_sensores(tmp_path: Path) -> Path:
    destino = tmp_path / "sem-sensores"
    gerar("sem-sensores", destino)
    return destino


def test_dod_vazia_nao_gera_pre_commit(sem_sensores: Path) -> None:
    """Pre-commit com lista de hooks vazia é um gate que aprova tudo."""
    assert not (sem_sensores / ".pre-commit-config.yaml").exists()


def test_dod_vazia_nao_gera_workflow_de_ci(sem_sensores: Path) -> None:
    """CI verde sem rodar sensor nenhum é o pior sinal possível: o time passa
    a confiar num check que não checa."""
    workflows = sem_sensores / ".github" / "workflows"
    gerados = list(workflows.glob("*.yml")) if workflows.is_dir() else []
    assert gerados == [], f"CI gerado sem sensores: {[p.name for p in gerados]}"


def test_dod_vazia_ainda_gera_a_camada_de_instrucao(sem_sensores: Path) -> None:
    """A honestidade não é desistir do harness: sem sensores o repositório
    continua ganhando protocolo, ponte e gate. O que não vem é o enforcement
    que precisaria de um sensor para significar alguma coisa."""
    for obrigatorio in (
        "AGENTS.md",
        "CLAUDE.md",
        "init.sh",
        "SESSION_STATE.md",
        ".claude/hooks/gate-destructive.sh",
    ):
        assert (sem_sensores / obrigatorio).exists(), f"{obrigatorio} faltando"


def test_dod_vazia_nao_inventa_comando_de_teste(sem_sensores: Path) -> None:
    """Inventar `pytest` num repo que não o tem é pior que DoD vazia: o agente
    roda, recebe `command not found` e conclui que o repositório está
    quebrado."""
    agents = (sem_sensores / "AGENTS.md").read_text()
    dod = agents.split("## Definition of Done")[1].split("## ")[0]
    for inventado in ("pytest", "ruff", "mypy"):
        assert inventado not in dod, f"DoD inventou `{inventado}` sem sensor no repo"


@pytest.mark.parametrize(
    ("ecossistema", "estranho"),
    [
        ("dotnet", "package.json"),
        ("dotnet", "requirements.txt"),
        ("go", "package.json"),
        ("java-maven", "package.json"),
        ("python", "package.json"),
        ("rust", "package.json"),
        ("php", "Gemfile"),
        ("ruby", "composer.json"),
    ],
)
def test_nao_gera_artefato_estranho_a_stack(
    ecossistema: str, estranho: str, tmp_path: Path
) -> None:
    """Regra inviolável 8. Além de inútil, o artefato estranho é o sinal
    visível de que a descoberta errou — e o usuário perde a confiança no resto
    do harness, com razão."""
    destino = tmp_path / ecossistema
    gerar(ecossistema, destino)
    assert not (destino / estranho).exists(), (
        f"{ecossistema} recebeu `{estranho}`, que não é da stack dele"
    )


def test_todo_ecossistema_da_tabela_tem_fixture() -> None:
    """`ecossistemas.md` promete uma linha por stack suportada. Linha sem
    fixture é promessa que nada exercita — foi o caso de Python, Rust, Ruby e
    PHP, documentados desde o começo e nunca gerados uma vez."""
    documentados = {
        "node",
        "react",
        "angular",
        "java-maven",
        "java-gradle",
        "dotnet",
        "go",
        "python",
        "rust",
        "ruby",
        "php",
    }
    faltando = documentados - set(STACKS)
    assert faltando == set(), f"ecossistema documentado e sem fixture: {sorted(faltando)}"
