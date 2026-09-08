"""O memlog é a memória de trabalho da sessão: append-only, atômica, cega.

Estes sensores exercitam o script DE VERDADE (não grep de palavra), porque o
que importa é o COMPORTAMENTO — que ele só acrescenta, nunca reescreve o
passado, recusa qualquer verbo fora de init/append, e que a geração o instala
executável e nomeado no protocolo.
"""

from __future__ import annotations

import stat
import subprocess
from pathlib import Path

from gerar import gerar

RAIZ = Path(__file__).resolve().parent.parent
MEMLOG = RAIZ / ".claude" / "skills" / "harness-creator" / "resources" / "memlog.sh"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["sh", str(MEMLOG), *args], capture_output=True, text=True, check=False)


def test_append_auto_inicia_e_conta(tmp_path: Path) -> None:
    alvo = tmp_path / "feat" / "memlog.md"
    r1 = _run("append", str(alvo), "decisao", "arquivar em vez de fatiar")
    assert r1.returncode == 0, r1.stderr
    assert '"entries":1' in r1.stdout
    assert alvo.exists()
    r2 = _run("append", str(alvo), "descoberta", "git merge nao le -F -")
    assert '"entries":2' in r2.stdout


def test_append_preserva_o_passado(tmp_path: Path) -> None:
    """Append-only de verdade: o que já estava fica byte a byte no começo."""
    alvo = tmp_path / "memlog.md"
    _run("append", str(alvo), "nota", "primeira")
    uma = alvo.read_text()
    _run("append", str(alvo), "nota", "segunda")
    duas = alvo.read_text()
    assert duas.startswith(uma)
    assert "primeira" in duas and "segunda" in duas


def test_init_grava_frontmatter(tmp_path: Path) -> None:
    alvo = tmp_path / "memlog.md"
    r = _run("init", str(alvo), "topic=memoria", "goal=append")
    assert r.returncode == 0
    txt = alvo.read_text()
    assert txt.startswith("---\n")
    assert "topic: memoria" in txt
    assert "goal: append" in txt


def test_recusa_verbo_fora_de_init_append(tmp_path: Path) -> None:
    """A invariante append-only, por comportamento: qualquer verbo que não
    seja init/append é recusado com exit 2 — não há editar nem apagar."""
    alvo = tmp_path / "memlog.md"
    _run("append", str(alvo), "nota", "existente")
    for verbo in ("edit", "delete", "remove", "set", "rewrite"):
        r = _run(verbo, str(alvo), "nota", "x")
        assert r.returncode == 2, f"{verbo} devia ser recusado com exit 2"


def test_geracao_instala_o_memlog_executavel_e_lf(tmp_path: Path) -> None:
    gerar("python", tmp_path)
    script = tmp_path / ".claude" / "memlog.sh"
    assert script.exists(), "geração não emitiu .claude/memlog.sh"
    assert script.stat().st_mode & stat.S_IXUSR, "memlog.sh não é executável"
    assert b"\r\n" not in script.read_bytes(), "memlog.sh tem CRLF"


def test_protocolo_gerado_nomeia_o_memlog(tmp_path: Path) -> None:
    """AGENTS.md e executar-grupo do harness gerado apontam o memlog — senão
    o agente nunca o usa (o AGENTS é o único arquivo lido sempre)."""
    gerar("python", tmp_path)
    agents = (tmp_path / "AGENTS.md").read_text()
    skill = tmp_path / ".claude" / "skills" / "executar-grupo" / "SKILL.md"
    assert "memlog.sh" in agents
    assert "memlog" in skill.read_text()
