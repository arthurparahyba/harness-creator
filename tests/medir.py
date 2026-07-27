"""Mede a maturidade das fixtures antes e depois do harness.

Uso: `python tests/medir.py`

NÃO é um teste, e não roda no `pytest`: depende de rede (`npx`) e de uma
ferramenta externa. Existe só para este repositório acompanhar se a
geração continua eficaz em cada ecossistema — a skill entregue não usa
`harness-score` para nada.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gerar import FIXTURES, STACKS, gerar  # noqa: E402

PADRAO = re.compile(r"Maturity: (L\d).*?Score: (\d+)/108")


def medir(caminho: Path) -> tuple[str, int]:
    saida = subprocess.run(
        ["npx", "-y", "harness-score", str(caminho)],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    achado = PADRAO.search(saida)
    if achado is None:
        raise RuntimeError(f"não consegui medir {caminho}:\n{saida}")
    return achado.group(1), int(achado.group(2))


def main() -> int:
    resultados: dict[str, dict[str, object]] = {}
    print(f"{'ECOSSISTEMA':<14}{'ANTES':<12}{'DEPOIS':<12}DELTA")
    print("-" * 46)
    with tempfile.TemporaryDirectory() as tmp:
        for nome in sorted(STACKS):
            nivel_antes, antes = medir(FIXTURES / nome)
            destino = Path(tmp) / nome
            gerar(nome, destino)
            nivel_depois, depois = medir(destino)
            resultados[nome] = {
                "antes": f"{nivel_antes} {antes}/108",
                "depois": f"{nivel_depois} {depois}/108",
                "delta": depois - antes,
            }
            print(
                f"{nome:<14}{nivel_antes + ' ' + str(antes):<12}"
                f"{nivel_depois + ' ' + str(depois):<12}+{depois - antes}"
            )
    destino_json = Path(__file__).resolve().parent / "medicao.json"
    relatorio = json.dumps(resultados, indent=2, ensure_ascii=False) + "\n"
    destino_json.write_text(relatorio, newline="\n")
    print(f"\nrelatório em {destino_json.relative_to(Path.cwd())}")
    return 0


if __name__ == "__main__":
    if shutil.which("npx") is None:
        print("npx não encontrado — medição requer Node instalado.", file=sys.stderr)
        raise SystemExit(1)
    raise SystemExit(main())
