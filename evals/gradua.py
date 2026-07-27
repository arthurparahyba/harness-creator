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

Resultado = tuple[bool, str]

IGNORAR = {".git", "node_modules", "__pycache__", ".venv"}


def _texto(p: Path) -> str:
    try:
        return p.read_text(errors="replace")
    except OSError:
        return ""


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


def _corpo(texto: str) -> str:
    """Só as linhas funcionais: comentário de shell não executa nada.

    Um `*.{js,ts}` na linha que ALERTA contra brace expansion é documentação
    correta; o mesmo padrão no `case` é um hook que deixa de formatar em
    silêncio. Misturar os dois faz o graduador acusar o template por dizer a
    verdade.
    """
    return "\n".join(ln for ln in texto.splitlines() if not ln.lstrip().startswith("#"))


def _dod(repo: Path) -> str:
    agents = _texto(repo / "AGENTS.md")
    m = re.search(r"## Definition of Done(.*?)(?=\n## |\Z)", agents, re.S)
    return m.group(1) if m else ""


VERIFICADOR = RAIZ / ".claude" / "skills" / "harness-creator" / "resources" / "verificar-harness.sh"


def _do_verificador(repo: Path) -> dict[str, Resultado]:
    """Delega as checagens mecânicas ao script que a própria skill entrega.

    Reimplementar aqui o que o `verificar-harness.sh` já faz criava duas
    fontes: o eval podia aprovar um harness que o verificador reprovava, e
    ninguém saberia qual dos dois estava certo. Agora o eval mede o mesmo que
    o usuário vê ao rodar o script no repositório dele.
    """
    r = subprocess.run(
        ["sh", str(VERIFICADOR), "--raiz", str(repo), "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        dados = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"V0: verificador executa": (False, f"saida ilegivel: {r.stderr[:120]}")}
    return {f"V: {c['check']}": (bool(c["passed"]), str(c["evidence"])) for c in dados["checks"]}


def universais(repo: Path, _relatorio: str) -> dict[str, Resultado]:
    # O que o verificador não cobre porque não é mecânico ou é específico do
    # eval: presença dos artefatos que a FASE 4 prometeu entregar.
    proprias: dict[str, Resultado] = {
        "U1: AGENTS.md na raiz": (
            (repo / "AGENTS.md").is_file(),
            "presente" if (repo / "AGENTS.md").is_file() else "ausente",
        ),
        "U3: AGENTS.md com escopo + ponte": _u3_escopo(repo),
        "U8: hooks do Devin e do Cursor parseiam": _parseiam(
            repo, [".devin/hooks.v1.json", ".cursor/hooks.json"]
        ),
        "U11: comando /dod": _existe(repo, ".claude/commands/dod.md"),
        "U12: init.sh executavel": _executavel(repo, "init.sh"),
        "U13: SESSION_STATE.md": _existe(repo, "SESSION_STATE.md"),
    }
    return _do_verificador(repo) | proprias


def _existe(repo: Path, rel: str) -> Resultado:
    ok = (repo / rel).exists()
    return ok, "presente" if ok else "ausente"


def _executavel(repo: Path, rel: str) -> Resultado:
    p = repo / rel
    if not p.is_file():
        return False, "ausente"
    ok = bool(p.stat().st_mode & 0o111)
    return ok, "executavel" if ok else "sem bit de execucao"


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
