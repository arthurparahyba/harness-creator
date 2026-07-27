"""Gradua um harness gerado por um MODELO executando a skill.

Diferente de `tests/`, que exercita `tests/gerar.py` — uma reimplementacao
deterministica da FASE 2 em Python. Aqui a entrada e o que sobrou no disco
depois de um agente ler o SKILL.md e decidir sozinho o que fazer, que e a
unica forma de pegar o modelo parafraseando um template, pulando a ponte
`CLAUDE.md` ou ignorando a FASE 5.

As assertions saem dos 19 itens da FASE 5: ela ja e uma rubrica objetiva.

Uso:
    python3 evals/gradua.py <caso> <caminho-do-repo> [caminho-do-relatorio]
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tests"))

from gerar import PREENCHIVEIS  # noqa: E402

Resultado = tuple[bool, str]

IGNORAR = {".git", "node_modules", "__pycache__", ".venv"}


def _arquivos(repo: Path) -> list[Path]:
    return [
        p for p in repo.rglob("*") if p.is_file() and not IGNORAR & set(p.relative_to(repo).parts)
    ]


def _texto(p: Path) -> str:
    try:
        return p.read_text(errors="replace")
    except OSError:
        return ""


def _gate(script: Path, comando: str) -> int:
    entrada = json.dumps({"tool_name": "Bash", "tool_input": {"command": comando}})
    return subprocess.run(
        ["bash", str(script)], input=entrada, capture_output=True, text=True, check=False
    ).returncode


def _u2_ponte(repo: Path) -> Resultado:
    """`@AGENTS.md` dentro de crase nao e parseado como import: vira texto."""
    claude = repo / "CLAUDE.md"
    if not claude.is_file():
        return False, "CLAUDE.md ausente na raiz"
    linhas = [ln.strip() for ln in _texto(claude).splitlines()]
    if "@AGENTS.md" in linhas:
        return True, "import na raiz encontrado"
    return False, f"sem linha '@AGENTS.md' solta; linhas: {linhas[:6]}"


def _u3_escopo(repo: Path) -> Resultado:
    escopados = [
        p for p in repo.rglob("AGENTS.md") if p.parent != repo and not IGNORAR & set(p.parts)
    ]
    if not escopados:
        return False, "nenhum AGENTS.md com escopo fora da raiz"
    sem_ponte = [
        str(p.parent.relative_to(repo)) for p in escopados if not (p.parent / "CLAUDE.md").is_file()
    ]
    if sem_ponte:
        return False, f"AGENTS.md com escopo sem CLAUDE.md irmao em: {sem_ponte}"
    return True, f"{len(escopados)} com escopo, todos com ponte"


def _u4_gate_arquivo(repo: Path) -> Resultado:
    g = repo / ".claude" / "hooks" / "gate-destructive.sh"
    if not g.is_file():
        return False, "gate-destructive.sh ausente"
    problemas = []
    if b"\r\n" in g.read_bytes():
        problemas.append("CRLF (gate falha ABERTO)")
    if not g.stat().st_mode & 0o111:
        problemas.append("sem bit de execucao")
    return (not problemas), "; ".join(problemas) or "existe, LF, executavel"


def _u9_manifesto(repo: Path) -> Resultado:
    m = repo / ".claude" / "harness.json"
    if not m.is_file():
        return False, ".claude/harness.json ausente"
    try:
        dados = json.loads(_texto(m))
    except json.JSONDecodeError as e:
        return False, f"manifesto nao parseia: {e}"
    listados = dados.get("harness", {}).get("arquivos", [])
    if not listados:
        return False, "manifesto sem lista de arquivos"
    fantasmas = [a for a in listados if not (repo / a).exists()]
    if fantasmas:
        return False, f"manifesto lista arquivo inexistente: {fantasmas[:4]}"
    return True, f"{len(listados)} arquivos, todos no disco"


def _corpo(texto: str) -> str:
    """Só as linhas funcionais: comentário de shell não executa nada.

    Um `*.{js,ts}` na linha que ALERTA contra brace expansion é documentação
    correta; o mesmo padrão no `case` é um hook que deixa de formatar em
    silêncio. Misturar os dois faz o graduador acusar o template por dizer a
    verdade.
    """
    return "\n".join(ln for ln in texto.splitlines() if not ln.lstrip().startswith("#"))


def _u10_marcadores(repo: Path) -> Resultado:
    """Implementa o item 6 da FASE 5 ao pé da letra, de propósito.

    A distinção entre comentário e corpo é reportada mas NÃO absolve: o item 6
    diz que estes marcadores não podem sobrar, sem ressalva. Se os templates
    os mantêm em cabeçalho didático que a regra do VERBATIM manda preservar,
    então a checagem é insatisfazível — e é isso que o resultado tem de
    mostrar, em vez de esconder atrás de uma exceção conveniente.
    """
    sobrou: list[str] = []
    for p in _arquivos(repo):
        txt = _texto(p)
        corpo = _corpo(txt)
        for marcador in PREENCHIVEIS:
            if marcador in txt:
                onde = "corpo" if marcador in corpo else "comentario"
                sobrou.append(f"{p.relative_to(repo)}:{marcador}({onde})")
    return (not sobrou), "; ".join(sobrou[:6]) or "nenhum marcador sobrou"


def _dod(repo: Path) -> str:
    agents = _texto(repo / "AGENTS.md")
    m = re.search(r"## Definition of Done(.*?)(?=\n## |\Z)", agents, re.S)
    return m.group(1) if m else ""


def universais(repo: Path, _relatorio: str) -> dict[str, Resultado]:
    gate = repo / ".claude" / "hooks" / "gate-destructive.sh"
    seguro = gate.is_file()
    return {
        "U1: AGENTS.md na raiz": (
            (repo / "AGENTS.md").is_file(),
            "presente" if (repo / "AGENTS.md").is_file() else "ausente",
        ),
        "U2: ponte CLAUDE.md na raiz": _u2_ponte(repo),
        "U3: AGENTS.md com escopo + ponte": _u3_escopo(repo),
        "U4: gate existe, LF, executavel": _u4_gate_arquivo(repo),
        "U5: gate bloqueia destrutivo (exit 2)": (
            seguro and _gate(gate, "rm -rf /tmp/x") == 2,
            f"exit {_gate(gate, 'rm -rf /tmp/x')}" if seguro else "sem gate",
        ),
        "U6: gate libera comando seguro (exit 0)": (
            seguro and _gate(gate, "git status") == 0,
            f"exit {_gate(gate, 'git status')}" if seguro else "sem gate",
        ),
        "U7: settings.json com wrapper hooks": _json_com_chave(
            repo / ".claude/settings.json", "hooks"
        ),
        "U8: hooks do Devin e do Cursor parseiam": _parseiam(
            repo, [".devin/hooks.v1.json", ".cursor/hooks.json"]
        ),
        "U9: manifesto confere com o disco": _u9_manifesto(repo),
        "U10: nenhum marcador preenchivel sobrou": _u10_marcadores(repo),
        "U11: comando /dod": _existe(repo, ".claude/commands/dod.md"),
        "U12: init.sh executavel": _executavel(repo, "init.sh"),
        "U13: SESSION_STATE.md": _existe(repo, "SESSION_STATE.md"),
    }


def _existe(repo: Path, rel: str) -> Resultado:
    ok = (repo / rel).exists()
    return ok, "presente" if ok else "ausente"


def _executavel(repo: Path, rel: str) -> Resultado:
    p = repo / rel
    if not p.is_file():
        return False, "ausente"
    ok = bool(p.stat().st_mode & 0o111)
    return ok, "executavel" if ok else "sem bit de execucao"


def _json_com_chave(p: Path, chave: str) -> Resultado:
    if not p.is_file():
        return False, "ausente"
    try:
        dados = json.loads(_texto(p))
    except json.JSONDecodeError as e:
        return False, f"nao parseia: {e}"
    ok = chave in dados
    return ok, f"chave '{chave}' {'presente' if ok else 'AUSENTE no nivel raiz'}"


def _parseiam(repo: Path, rels: list[str]) -> Resultado:
    falhas = []
    for rel in rels:
        p = repo / rel
        if not p.is_file():
            falhas.append(f"{rel} ausente")
            continue
        try:
            json.loads(_texto(p))
        except json.JSONDecodeError as e:
            falhas.append(f"{rel} nao parseia: {e}")
    return (not falhas), "; ".join(falhas) or "todos parseiam"


def caso_node(repo: Path, _relatorio: str) -> dict[str, Resultado]:
    dod = _dod(repo)
    fmt = _texto(repo / ".claude/hooks/format-on-edit.sh")
    return {
        "N1: DoD usa scripts reais do package.json": (
            "npm" in dod or "npx" in dod,
            f"DoD: {dod.strip()[:120]!r}",
        ),
        "N2: glob sem brace expansion": (
            not re.search(r"\*\.\{[a-z,]+\}", _corpo(fmt)),
            "glob com chaves no corpo (hook inerte)"
            if re.search(r"\*\.\{", _corpo(fmt))
            else "alternancia com | no corpo",
        ),
        "N3: pre-commit gerado (repo tem sensores)": _existe(repo, ".pre-commit-config.yaml"),
    }


def caso_dotnet(repo: Path, _relatorio: str) -> dict[str, Resultado]:
    dod = _dod(repo)
    pkg = repo / "package.json"
    return {
        "D1: NAO gerou package.json em repo .NET": (
            not pkg.exists(),
            "package.json inventado" if pkg.exists() else "ausente, como deve ser",
        ),
        "D2: o .sln real aparece nos comandos": (
            "Catalogo.sln" in dod,
            f"DoD: {dod.strip()[:120]!r}",
        ),
        "D3: a DoD usa comandos dotnet": ("dotnet" in dod, f"DoD: {dod.strip()[:120]!r}"),
    }


PURAS = ("margem_percentual", "normalizar_cnpj", "agrupar_por_vendedor", "faixa_de_comissao")


def caso_sem_sensores(repo: Path, relatorio: str) -> dict[str, Resultado]:
    dod = _dod(repo)
    inventou = [c for c in ("pytest", "ruff", "mypy") if c in dod and "TODO" not in dod]
    citadas = [f for f in PURAS if f in relatorio]
    stub = [t for t in ("conftest", "stub", "openpyxl", "requests") if t in relatorio]
    ci = (
        list((repo / ".github" / "workflows").glob("*.yml"))
        if (repo / ".github/workflows").is_dir()
        else []
    )
    return {
        "S1: NAO gerou pre-commit (DoD vazia)": (
            not (repo / ".pre-commit-config.yaml").exists(),
            "gerado com DoD vazia" if (repo / ".pre-commit-config.yaml").exists() else "ausente",
        ),
        "S2: NAO gerou workflow de CI": (
            not ci,
            f"gerou {[c.name for c in ci]}" if ci else "ausente",
        ),
        "S3: nao inventou comando de teste": (
            not inventou,
            f"inventou {inventou} sem sensor no repo"
            if inventou
            else f"DoD honesta: {dod.strip()[:80]!r}",
        ),
        "S4: remediacao cita funcao pura pelo nome": (
            bool(citadas),
            f"citou {citadas}" if citadas else "recomendacao generica, nao acionavel",
        ),
        "S5: remediacao trata dep de sistema do entrypoint": (
            bool(stub),
            f"mencionou {stub}" if stub else "sem stub: o primeiro teste morre com ImportError",
        ),
    }


CASOS = {"node": caso_node, "dotnet": caso_dotnet, "sem-sensores": caso_sem_sensores}


def graduar(caso: str, repo: Path, relatorio: str) -> dict[str, object]:
    checks = universais(repo, relatorio) | CASOS[caso](repo, relatorio)
    expectations = [
        {"text": nome, "passed": ok, "evidence": ev} for nome, (ok, ev) in checks.items()
    ]
    passaram = sum(1 for e in expectations if e["passed"])
    return {
        "caso": caso,
        "repo": str(repo),
        "passaram": passaram,
        "total": len(expectations),
        "expectations": expectations,
    }


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    caso, repo = sys.argv[1], Path(sys.argv[2])
    relatorio = _texto(Path(sys.argv[3])) if len(sys.argv) > 3 else ""
    resultado = graduar(caso, repo, relatorio)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    return 0 if resultado["passaram"] == resultado["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
