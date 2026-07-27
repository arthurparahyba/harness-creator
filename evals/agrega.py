"""Consolida os gradings de uma iteração num quadro comparativo por versão.

Roda `gradua.py` para cada caso e cada versão presente no workspace e imprime
uma tabela. O que interessa não é só o total: é QUAL assertion separa as duas
versões. Assertion que passa nas duas não discrimina nada e só infla o
número — vale a pena saber disso antes de comemorar um placar.

Uso:
    python3 evals/agrega.py <workspace>/iteration-N
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gradua import CASOS, graduar  # noqa: E402


def _relatorio(d: Path) -> str:
    p = d / "relatorio.md"
    return p.read_text(errors="replace") if p.is_file() else ""


def coletar(iteracao: Path) -> dict[str, dict[str, Any]]:
    """Grada cada `eval-<caso>/<versao>/repo` que existir no workspace."""
    resultados: dict[str, dict[str, Any]] = {}
    for caso in CASOS:
        base = iteracao / f"eval-{caso}"
        if not base.is_dir():
            continue
        for versao_dir in sorted(base.iterdir()):
            repo = versao_dir / "repo"
            if not repo.is_dir():
                continue
            chave = f"{caso}/{versao_dir.name}"
            resultados[chave] = graduar(caso, repo, _relatorio(versao_dir))
            resultados[chave]["tem_relatorio"] = (versao_dir / "relatorio.md").is_file()
    return resultados


def _discriminantes(resultados: dict[str, dict[str, Any]]) -> list[str]:
    """Assertions cujo resultado difere entre as versões do MESMO caso.

    São as únicas que dizem alguma coisa sobre a mudança de versão; o resto
    mede o patamar absoluto da skill, que também importa mas é outra
    pergunta.
    """
    linhas = []
    casos = {c.split("/")[0] for c in resultados}
    for caso in sorted(casos):
        versoes = {k.split("/")[1]: v for k, v in resultados.items() if k.startswith(f"{caso}/")}
        if len(versoes) < 2:
            continue
        por_nome: dict[str, dict[str, bool]] = {}
        for versao, dados in versoes.items():
            for exp in dados["expectations"]:
                por_nome.setdefault(exp["text"], {})[versao] = bool(exp["passed"])
        for nome, res in por_nome.items():
            if len(set(res.values())) > 1:
                estado = ", ".join(
                    f"{v}={'PASS' if ok else 'FAIL'}" for v, ok in sorted(res.items())
                )
                linhas.append(f"  {caso} · {nome} → {estado}")
    return linhas


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    iteracao = Path(sys.argv[1])
    resultados = coletar(iteracao)
    if not resultados:
        print(f"nenhum repo graduável em {iteracao}")
        return 2

    print(f"{'CASO/VERSAO':<26} {'PASSOU':>8} {'RELATORIO':>10}")
    print("-" * 46)
    for chave, dados in sorted(resultados.items()):
        placar = f"{dados['passaram']}/{dados['total']}"
        print(f"{chave:<26} {placar:>8} {'sim' if dados['tem_relatorio'] else 'NAO':>10}")

    print("\nFALHAS por caso/versao:")
    for chave, dados in sorted(resultados.items()):
        falhas = [e["text"] for e in dados["expectations"] if not e["passed"]]
        print(f"  {chave}: {', '.join(falhas) if falhas else 'nenhuma'}")

    disc = _discriminantes(resultados)
    print("\nASSERTIONS QUE DISCRIMINAM AS VERSOES:")
    print(
        "\n".join(disc) if disc else "  nenhuma — as duas versoes se comportam igual nesta rubrica"
    )

    saida = iteracao / "grading.json"
    saida.write_text(json.dumps(resultados, indent=2, ensure_ascii=False))
    print(f"\ngrading completo em {saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
