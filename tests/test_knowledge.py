"""A base knowledge/ é o conhecimento de componente do repositório: revisável,
com proveniência e Prova. O AGENTS.md aponta para ela, nunca a inclui inline
(progressive disclosure — o AGENTS é lido a cada turno)."""

from __future__ import annotations

from pathlib import Path

from gerar import gerar


def test_geracao_instala_knowledge_readme(tmp_path: Path) -> None:
    gerar("python", tmp_path)
    assert (tmp_path / "knowledge" / "README.md").exists()


def test_readme_documenta_formato_e_prova(tmp_path: Path) -> None:
    gerar("python", tmp_path)
    readme = (tmp_path / "knowledge" / "README.md").read_text()
    for marca in ("derivado_de", "baseline_commit", "Prova"):
        assert marca in readme, f"README não documenta {marca}"


def test_agents_aponta_sem_inline(tmp_path: Path) -> None:
    """Progressive disclosure: o AGENTS aponta o README; o DETALHE (o formato,
    ex. `derivado_de`) mora no README, não no AGENTS lido a cada turno."""
    gerar("python", tmp_path)
    agents = (tmp_path / "AGENTS.md").read_text()
    assert "knowledge/README.md" in agents
    assert "derivado_de" not in agents


def test_agents_wira_o_loop_de_conhecimento(tmp_path: Path) -> None:
    """O passo 3 manda checar knowledge/ antes de investigar e registrar o
    durável — senão a base nunca se popula nem se consulta."""
    gerar("python", tmp_path)
    agents = (tmp_path / "AGENTS.md").read_text()
    assert "knowledge/" in agents
    assert "registre" in agents.lower()
