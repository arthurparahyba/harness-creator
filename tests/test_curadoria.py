"""A catraca do Grupo 53 virou curadoria: no fim do grupo o agente relê o
memlog e o diff e PROMOVE o durável — regra verificável para arch-rules,
conhecimento de componente para knowledge/. O que não dura fica só no memlog.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RESOURCES = RAIZ / ".claude" / "skills" / "harness-creator" / "resources"
EXECUTAR = RESOURCES / "skills" / "executar-grupo" / "SKILL.md"


def test_curadoria_le_o_memlog_e_o_diff() -> None:
    texto = EXECUTAR.read_text()
    assert "memlog" in texto, "a curadoria não relê o memlog da funcionalidade"
    assert "diff" in texto


def test_curadoria_promove_para_os_dois_destinos() -> None:
    """Regra verificável -> arch-rules; conhecimento de componente -> knowledge/.
    Sem os dois destinos, a curadoria vira só a catraca antiga."""
    texto = EXECUTAR.read_text()
    assert "arch-rules.json" in texto
    assert "knowledge/" in texto
    assert "propor-regra-arch" in texto  # a afordância da regra segue lá


def test_curadoria_nomeia_a_regua_de_durabilidade() -> None:
    """O espectro memlog -> knowledge/ -> arch-rule é o que diz ATÉ ONDE
    promover cada achado."""
    texto = EXECUTAR.read_text()
    assert "arch-rule" in texto
    assert "durabilidade" in texto or "efêmero" in texto
