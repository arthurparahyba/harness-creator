"""Consolida uma rodada do nível C numa tabela comparativa.

Lê o que as sessões deixaram no disco — os JSONs do `claude -p`, o exit code
da DoD gravado pelo `roda.sh`, e o `git log`/estado da árvore de cada célula —
e monta o quadro control × harness.

O que ele NÃO faz é julgar o transcript. "Declarou pronto com a DoD
falhando" exige ler o que a sessão escreveu, e um regex sobre texto livre
daria um número com cara de objetivo e nenhuma base. O que este arquivo mede
é o substituto mecânico e mais duro: **em que estado a sessão deixou o
repositório**. Uma sessão que termina com a DoD vermelha é um superconjunto
das que declararam pronto indevidamente — inclui também as que só pararam no
meio. O relatório escrito à mão separa os dois casos; a tabela não finge
separar.

Uso:
    python3 eval/nivel-c/mede.py <workdir> [--json]
    python3 eval/nivel-c/mede.py --autoteste
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CONDICOES = ("control", "harness")


@dataclass
class Celula:
    """Uma tarefa numa condição."""

    tarefa: str
    condicao: str
    turns: int | None = None
    duracao_s: int | None = None
    custo: float = 0.0
    dod: str = "n/d"

    @property
    def rodou(self) -> bool:
        return self.turns is not None


@dataclass
class Condicao:
    nome: str
    celulas: list[Celula] = field(default_factory=list)
    commits: int = 0
    sujos: int = 0
    dod_final: str = "n/d"

    @property
    def custo(self) -> float:
        return sum(c.custo for c in self.celulas)

    @property
    def turns(self) -> int:
        return sum(c.turns or 0 for c in self.celulas)

    @property
    def medidas(self) -> int:
        return sum(1 for c in self.celulas if c.dod != "n/d")

    @property
    def vermelhas(self) -> int:
        return sum(1 for c in self.celulas if c.dod == "vermelha")

    @property
    def placar_dod(self) -> str:
        """`0 de 4` quando nada foi medido é o pior resultado possível: lê-se
        como quatro sessões verdes. Só há número quando há medição."""
        if self.medidas == 0:
            return "n/d (nenhuma sessão mediu a DoD)"
        sufixo = f" (de {self.medidas} medidas)" if self.medidas != len(self.celulas) else ""
        return f"{self.vermelhas} de {self.medidas}{sufixo}"


def _le_json(p: Path) -> dict[str, Any]:
    try:
        dados: dict[str, Any] = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return dados


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    return r.stdout.strip()


def _ordem_das_tarefas(catalogo: Path) -> list[str]:
    dados = _le_json(catalogo)
    tarefas = dados.get("tarefas", [])
    return [str(t["id"]) for t in tarefas] or ["T1", "T3", "T2", "T4"]


def coletar(workdir: Path, catalogo: Path) -> dict[str, Condicao]:
    runs = workdir / "runs"
    base = (
        (runs / "commit-base.txt").read_text().strip()
        if (runs / "commit-base.txt").is_file()
        else ""
    )
    resultado: dict[str, Condicao] = {}

    for cond in CONDICOES:
        c = Condicao(nome=cond)
        for tarefa in _ordem_das_tarefas(catalogo):
            cel = Celula(tarefa=tarefa, condicao=cond)
            dados = _le_json(runs / f"{tarefa}-{cond}.json")
            if dados:
                cel.turns = dados.get("num_turns")
                cel.duracao_s = round(dados.get("duration_ms", 0) / 1000)
                cel.custo = float(dados.get("total_cost_usd", 0.0))
            dod = runs / f"{tarefa}-{cond}.dod"
            if dod.is_file():
                cel.dod = "verde" if dod.read_text().strip() == "0" else "vermelha"
            c.celulas.append(cel)

        repo = workdir / cond
        if (repo / ".git").is_dir():
            # O ponto de partida de cada célula é o HEAD que o `roda.sh`
            # registrou antes da primeira sessão — na célula `harness` isso é
            # DEPOIS do commit de instalação do harness, que não é trabalho da
            # rodada e inflaria a contagem em exatamente um commit a favor
            # dela. Sem esse arquivo cai-se no commit base do `preparar.sh`.
            inicio = runs / f"inicio-{cond}.txt"
            partida = inicio.read_text().strip() if inicio.is_file() else base
            intervalo = f"{partida}..HEAD" if partida else "HEAD"
            log = _git(repo, "log", "--oneline", intervalo)
            c.commits = len([ln for ln in log.splitlines() if ln.strip()])
            c.sujos = len([ln for ln in _git(repo, "status", "--short").splitlines() if ln.strip()])
            ultima = [cel for cel in c.celulas if cel.dod != "n/d"]
            c.dod_final = ultima[-1].dod if ultima else "n/d"
        resultado[cond] = c
    return resultado


def tabela(resultado: dict[str, Condicao]) -> str:
    ctrl, harn = resultado["control"], resultado["harness"]
    linhas = ["## Placar", "", "| Métrica | Controle | Com harness |", "|---|---|---|"]
    linhas += [
        f"| Sessões terminadas com a DoD vermelha | {ctrl.placar_dod} | {harn.placar_dod} |",
        f"| Commits na rodada | {ctrl.commits} | {harn.commits} |",
        f"| Arquivos soltos no fim | {ctrl.sujos} | {harn.sujos} |",
        f"| DoD no estado final | {ctrl.dod_final} | {harn.dod_final} |",
        f"| Custo | US$ {ctrl.custo:.2f} | US$ {harn.custo:.2f} |",
        f"| Turns | {ctrl.turns} | {harn.turns} |",
        "",
        "## Por tarefa",
        "",
        "| Tarefa | Célula | Turns | Duração | Custo | DoD depois |",
        "|---|---|---|---|---|---|",
    ]
    for tarefa in [c.tarefa for c in ctrl.celulas]:
        for cond in CONDICOES:
            cel = next(c for c in resultado[cond].celulas if c.tarefa == tarefa)
            if not cel.rodou:
                linhas.append(f"| {tarefa} | {cond} | — | — | — | não executada |")
                continue
            linhas.append(
                f"| {tarefa} | {cond} | {cel.turns} | {cel.duracao_s}s "
                f"| US$ {cel.custo:.3f} | {cel.dod} |"
            )
    linhas += [
        "",
        "As linhas acima são mecânicas. Escopo (M3), recuperação de contexto",
        "(M4) e handoff (M7) saem do transcript e vão no relatório da rodada.",
    ]
    return "\n".join(linhas)


def _autoteste() -> int:
    """Monta uma rodada sintética e confere que a tabela sai coerente.

    Existe porque a alternativa é só descobrir que o medidor quebrou depois de
    gastar a bateria inteira — que é o momento em que refazer custa mais caro.
    """
    catalogo = Path(__file__).resolve().parent / "tarefas.json"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "rodada"
        (work / "runs").mkdir(parents=True)
        (work / "runs" / "commit-base.txt").write_text("abc1234\n")
        for tarefa in _ordem_das_tarefas(catalogo):
            for cond in CONDICOES:
                (work / "runs" / f"{tarefa}-{cond}.json").write_text(
                    json.dumps({"num_turns": 5, "duration_ms": 1000, "total_cost_usd": 0.5})
                )
                (work / "runs" / f"{tarefa}-{cond}.dod").write_text(
                    "1\n" if cond == "control" else "0\n"
                )
        resultado = coletar(work, catalogo)
        saida = tabela(resultado)

    esperado = len(_ordem_das_tarefas(catalogo))
    assert resultado["control"].vermelhas == esperado, "DoD vermelha não contabilizada"
    assert resultado["harness"].vermelhas == 0, "DoD verde contada como vermelha"
    assert f"US$ {esperado * 0.5:.2f}" in saida, "custo agregado não bate"
    assert saida.count("| T") >= esperado * 2, "faltou linha por tarefa/condição"
    print(saida)
    print("\nautoteste OK")
    return 0


def main(argv: list[str]) -> int:
    if "--autoteste" in argv:
        return _autoteste()
    if not argv:
        print(__doc__)
        return 2
    workdir = Path(argv[0]).resolve()
    if not (workdir / "runs").is_dir():
        print(f"sem runs/ em {workdir}: rode o preparar.sh e o roda.sh antes", file=sys.stderr)
        return 2
    catalogo = Path(__file__).resolve().parent / "tarefas.json"
    resultado = coletar(workdir, catalogo)
    if "--json" in argv:
        print(
            json.dumps(
                {
                    cond: {
                        "commits": c.commits,
                        "sujos": c.sujos,
                        "dod_final": c.dod_final,
                        "custo": round(c.custo, 3),
                        "turns": c.turns,
                        "vermelhas": c.vermelhas,
                        "celulas": [vars(cel) for cel in c.celulas],
                    }
                    for cond, c in resultado.items()
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print(tabela(resultado))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
