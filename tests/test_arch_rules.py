"""O `check` do `arch-rules.json` precisa chegar ao shell como foi escrito.

O modo de falha que originou este arquivo é o pior que uma regra pode ter:
ela **passa sempre**. Uma regra com `mkfs\\.` chegava ao shell como
`mkfs\\\\.` — regex que casa barra invertida seguida de qualquer coisa, ou
seja, nada. O `check-arch` imprimia `[ok]` em toda execução sem nunca ter
verificado coisa alguma. Regra que sempre passa é pior que regra ausente:
ocupa a linha do relatório e compra confiança.

Havia DOIS caminhos e os dois perdiam a barra, de formas diferentes — jq
por `@tsv`, awk por não desfazer `\\\\`. Por isso todo teste aqui roda contra
os dois: consertar um só e declarar vitória é o defeito que este repositório
já cometeu no Grupo 35 e pagou no Grupo 44.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RESOURCES = RAIZ / ".claude" / "skills" / "harness-creator" / "resources"
RUNNER = RESOURCES / "check-arch.sh"
SEMENTE = RESOURCES / "arch-rules.json"


def _roda(repo: Path, *, com_jq: bool) -> subprocess.CompletedProcess[str]:
    """Executa o runner forçando um dos dois caminhos do parser.

    `com_jq=False` monta um PATH sem jq — é assim que o fallback em awk é
    exercitado de verdade, em vez de ficar como código que ninguém roda.
    """
    if com_jq:
        env = {"PATH": os.environ["PATH"]}
    else:
        # O PATH tira `jq` e SÓ ele. Tirar mais transformaria o teste numa
        # medição do PATH: a regra A03 da semente usa `python3` como um dos
        # fallbacks e falharia por ausência de ferramenta, não por defeito
        # do parser — e o vermelho apontaria para o lugar errado.
        magro = repo / "bin-sem-jq"
        magro.mkdir(exist_ok=True)
        for f in ("bash", "sh", "awk", "grep", "sed", "test", "printf", "cat", "ls", "python3"):
            alvo = shutil.which(f)
            if alvo and not (magro / f).exists():
                (magro / f).symlink_to(alvo)
        env = {"PATH": str(magro)}
        assert shutil.which("jq", path=str(magro)) is None, "o PATH magro ainda tem jq"
    return subprocess.run(
        ["bash", str(RUNNER)], cwd=repo, capture_output=True, text=True, env=env, check=False
    )


def _com_regras(repo: Path, regras: list[dict[str, str]]) -> Path:
    (repo / ".harness").mkdir(parents=True, exist_ok=True)
    (repo / ".harness" / "arch-rules.json").write_text(json.dumps(regras, indent=2), newline="\n")
    return repo


@pytest.mark.parametrize("com_jq", [True, False], ids=["jq", "awk"])
def test_barra_invertida_chega_intacta(tmp_path: Path, com_jq: bool) -> None:
    """O par que define o teste: o `check` casa o ponto LITERAL e só ele.

    Sem o `.` literal, `alvoXtxt` também casaria — e uma regra que casa
    demais falha na direção oposta, acusando o que está certo.
    """
    repo = _com_regras(
        tmp_path,
        [
            {
                "id": "T01",
                "description": "ponto literal casa",
                "check": "ls | grep -q 'alvo\\.txt'",
                "expect": "exit-0",
                "what": "",
                "why": "",
                "fix": "",
            }
        ],
    )
    (repo / "alvo.txt").write_text("x", newline="\n")
    assert _roda(repo, com_jq=com_jq).returncode == 0, "regra correta reprovou"

    (repo / "alvo.txt").unlink()
    (repo / "alvoXtxt").write_text("x", newline="\n")
    r = _roda(repo, com_jq=com_jq)
    assert r.returncode == 1, (
        "a barra invertida foi perdida: o `.` virou coringa e casou 'alvoXtxt'\n" + r.stdout
    )


@pytest.mark.parametrize("com_jq", [True, False], ids=["jq", "awk"])
def test_regra_que_nao_casa_nada_reprova(tmp_path: Path, com_jq: bool) -> None:
    """A guarda contra o modo de falha original.

    Se a barra fosse re-escapada, o padrão não casaria NADA — e uma regra
    `exit-nonzero` que nunca casa passa sempre. Este teste é o inverso do
    de cima: aqui o `[ok]` só é legítimo se o padrão realmente não achou.
    """
    repo = _com_regras(
        tmp_path,
        [
            {
                "id": "T02",
                "description": "ausencia verificada",
                "check": "ls | grep -q 'proibido\\.txt'",
                "expect": "exit-nonzero",
                "what": "",
                "why": "",
                "fix": "",
            }
        ],
    )
    (repo / "ok.txt").write_text("x", newline="\n")
    assert _roda(repo, com_jq=com_jq).returncode == 0

    (repo / "proibido.txt").write_text("x", newline="\n")
    r = _roda(repo, com_jq=com_jq)
    assert r.returncode == 1, "regra de ausência não pegou o arquivo proibido\n" + r.stdout


@pytest.mark.parametrize("com_jq", [True, False], ids=["jq", "awk"])
def test_os_dois_parsers_concordam_na_semente(tmp_path: Path, com_jq: bool) -> None:
    """Divergência entre os dois caminhos é o defeito de origem, e ela é
    silenciosa: quem tem jq nunca vê o que quem não tem recebe."""
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    r = _roda(repo, com_jq=com_jq)
    assert r.returncode == 0, f"semente reprovou (jq={com_jq}):\n{r.stdout}"
    assert "7 regra(s), nenhuma violada" in r.stdout, r.stdout


def test_a04_da_semente_usa_ponto_literal() -> None:
    """A regra que motivou tudo. Ela exclui `.claude/skills/`, e com o `.`
    como coringa passaria a excluir também `Xclaude/skills/` — improvável,
    mas o ponto é que a regra deve dizer o que quer dizer."""
    a04 = next(r for r in json.loads(SEMENTE.read_text()) if r["id"] == "A04")
    assert "\\." in a04["check"], "A04 voltou a usar coringa no lugar do ponto literal"


def _a05() -> dict[str, str]:
    regra: dict[str, str] = next(r for r in json.loads(SEMENTE.read_text()) if r["id"] == "A05")
    return regra


@pytest.mark.parametrize("com_jq", [True, False], ids=["jq", "awk"])
@pytest.mark.parametrize(
    ("layout", "aceita"),
    [
        ("tasks", True),
        ("tasks-so-readme", True),
        ("legado", True),
        ("openspec", True),
        ("vazio", False),
    ],
)
def test_a05_aceita_as_formas_de_plano_e_so_elas(
    tmp_path: Path, com_jq: bool, layout: str, aceita: bool
) -> None:
    """A fonte mudou de forma; repositório com harness antigo não pode virar
    vermelho por isso.

    O plano passou a ser `tasks/<funcionalidade>/tasks.md`, mas o `TASKS.md`
    único na raiz continua sendo o plano REAL de quem gerou o harness antes —
    com o histórico de grupos que os commits de checkpoint referenciam.
    Reprovar essa forma transformaria a mudança de layout em quebra para todo
    repositório já em uso, e a reação natural a um vermelho que o usuário não
    causou é apagar o arquivo de regras.

    O par que dá sentido ao teste é o `vazio`: sem nenhuma das formas a regra
    tem de reprovar, senão ela aceita tudo e não verifica nada.
    """
    repo = _com_regras(tmp_path / layout, [_a05()])
    if layout == "tasks":
        (repo / "tasks" / "login").mkdir(parents=True)
        (repo / "tasks" / "login" / "tasks.md").write_text("## Grupo 1 - x\n", newline="\n")
    elif layout == "tasks-so-readme":
        (repo / "tasks").mkdir(parents=True)
        (repo / "tasks" / "README.md").write_text("# Planos\n", newline="\n")
    elif layout == "legado":
        (repo / "TASKS.md").write_text("## Grupo 1 - x\n", newline="\n")
    elif layout == "openspec":
        (repo / "openspec" / "changes").mkdir(parents=True)

    r = _roda(repo, com_jq=com_jq)
    if aceita:
        assert r.returncode == 0, f"A05 reprovou o layout `{layout}`:\n{r.stdout}"
    else:
        assert r.returncode != 0, f"A05 aprovou repositório sem fonte nenhuma:\n{r.stdout}"
