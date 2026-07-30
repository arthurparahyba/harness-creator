"""Testes do gate graduado — `gate-rules.json` + `gate-destructive.sh`.

O gate era binário e errava dos dois lados. Cada teste aqui defende um dos
dois lados, e o par importa mais que qualquer teste isolado:

- **Falso bloqueio** é o erro mais caro, porque ensina a driblar. Um gate que
  barra `rm -rf node_modules` treina a pessoa a contornar, e o contorno
  aprendido num caso obviamente errado depois passa por cima dos bloqueios
  certos. Testado por `test_excecao_declarada_passa`.
- **Falso verde**: tudo fora da lista passava em silêncio, inclusive
  `git commit --no-verify`. Testado pela classificação de risco.

E o teste que sustenta os outros: `test_excecao_nao_vira_buraco`. Uma exceção
mal ancorada é pior que nenhuma exceção, porque parece proteção.

Os comandos de risco são montados em partes (`R + F`), nunca escritos por
extenso: o gate DESTE repositório inspeciona o comando de shell que o pytest
dispara, e um `rm -rf` literal aqui bloquearia a própria suíte.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RESOURCES = RAIZ / ".claude" / "skills" / "harness-creator" / "resources"
GATE = RESOURCES / "hooks" / "gate-destructive.sh"
REGISTRO = RESOURCES / "gate-rules.json"

R = "rm"
F = "-rf"


def _gate(comando: str, regras: Path | None = None) -> int:
    env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}
    if regras is not None:
        env["HARNESS_GATE_RULES"] = str(regras)
    return subprocess.run(
        ["bash", str(GATE)],
        input=json.dumps({"tool_input": {"command": comando}}),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    ).returncode


@pytest.fixture(name="regras")
def _regras(tmp_path: Path) -> Path:
    destino = tmp_path / "gate-rules.json"
    shutil.copy(REGISTRO, destino)
    return destino


# ------------------------------------------------------------ falso bloqueio


@pytest.mark.parametrize(
    "alvo",
    ["node_modules", "dist", "build", "target", "__pycache__", ".venv", "/tmp/scratch-abc"],
)
def test_excecao_declarada_passa(alvo: str, regras: Path) -> None:
    """O erro que motivou o registro: nesta mesma sessão o gate barrou a
    limpeza de um scratchpad, e a saída foi contornar o comando."""
    assert _gate(f"{R} {F} {alvo}", regras) == 0, f"falso bloqueio em `{R} {F} {alvo}`"


@pytest.mark.parametrize("alvo", ["/", "~", "~/Documents", "src", "$HOME", ".."])
def test_alvo_perigoso_continua_bloqueado(alvo: str, regras: Path) -> None:
    """As exceções não podem alcançar nada disto. `src` é o caso sutil: não é
    catastrófico como `/`, mas é código-fonte não commitado indo embora."""
    assert _gate(f"{R} {F} {alvo}", regras) == 2, f"passou: `{R} {F} {alvo}`"


# ------------------------------------------- o teste que sustenta os outros


@pytest.mark.parametrize(
    "sufixo",
    [
        f"&& {R} {F} /",
        f"; {R} {F} /",
        f"| xargs {R} {F}",
        "$(echo /)",
        "`echo /`",
    ],
)
def test_excecao_nao_vira_buraco(sufixo: str, regras: Path) -> None:
    """Exceção mal ancorada é pior que exceção nenhuma: parece proteção.

    Sem `^...$` e sem proibir `; | & $` e crase no caminho,
    `rm -rf node_modules && rm -rf /` casaria a exceção pelo começo e o gate
    liberaria a segunda metade junto.
    """
    assert _gate(f"{R} {F} node_modules {sufixo}", regras) == 2, (
        f"a exceção abriu buraco para: node_modules {sufixo}"
    )


# ----------------------------------------------------- registro indisponível


def test_sem_registro_cai_no_fallback(tmp_path: Path) -> None:
    """Gate sem registro não pode virar gate sem proteção — seria transformar
    "alguém apagou um arquivo" em "o harness parou de proteger", sem nada
    acusando."""
    assert _gate(f"{R} {F} /", tmp_path / "nao-existe.json") == 2


def test_registro_corrompido_cai_no_fallback(tmp_path: Path) -> None:
    quebrado = tmp_path / "gate-rules.json"
    quebrado.write_text("{ isto nao e json valido", newline="\n")
    assert _gate(f"{R} {F} /", quebrado) == 2


def test_registro_sem_regra_de_bloqueio_cai_no_fallback(tmp_path: Path) -> None:
    """O drible mais curto: trocar todo `bloquear` por `permitir`. O fallback
    o anula, e é por isso que ele existe."""
    r = json.loads(REGISTRO.read_text())
    for regra in r:
        if regra["nivel"] == "bloquear":
            regra["nivel"] = "permitir"
    alvo = tmp_path / "gate-rules.json"
    alvo.write_text(json.dumps(r, indent=2), newline="\n")
    assert _gate(f"{R} {F} /", alvo) == 2


def test_comando_seguro_passa_em_qualquer_configuracao(regras: Path, tmp_path: Path) -> None:
    """O par que impede "gate que bloqueia tudo" de passar por gate bom."""
    for cfg in (regras, tmp_path / "nao-existe.json"):
        for cmd in ("git status", "npm test", "ls -la", "pytest -q"):
            assert _gate(cmd, cfg) == 0, f"bloqueou comando seguro `{cmd}`"


# --------------------------------------------------------------- integridade


def test_registro_e_json_valido_e_completo() -> None:
    r = json.loads(REGISTRO.read_text())
    niveis = {x["nivel"] for x in r}
    assert niveis == {"permitir", "bloquear", "avisar"}, f"níveis inesperados: {niveis}"
    ids = [x["id"] for x in r]
    assert len(ids) == len(set(ids)), "id duplicado no registro"
    for regra in r:
        assert regra["why"].strip(), (
            f"{regra['id']} sem `why`. Exceção sem motivo escrito vira lista de "
            "desculpas que só cresce, e ninguém depois sabe se ainda vale"
        )


def test_toda_regra_de_bloqueio_tem_fix(regras: Path) -> None:
    """Agente que vê comando bloqueado sem saída sugerida improvisa uma —
    e a improvisação mais curta costuma ser desligar o que bloqueou."""
    for regra in json.loads(REGISTRO.read_text()):
        if regra["nivel"] == "bloquear":
            assert regra["fix"].strip(), f"{regra['id']} bloqueia sem dizer o caminho certo"


def _check_arch(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", ".claude/check-arch.sh"], cwd=repo, capture_output=True, text=True, check=False
    )


def test_g01_aprova_harness_recem_gerado(tmp_path: Path) -> None:
    """Se a regra reprova o que a skill acabou de gerar, o primeiro contato do
    usuário com ela é um vermelho que ele não causou — e a reação natural a
    isso é apagar a regra, matando a catraca antes de ela girar uma vez."""
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    r = _check_arch(repo)
    assert r.returncode == 0, f"check-arch reprovou geração limpa:\n{r.stdout}"
    assert "G01" in r.stdout and "G02" in r.stdout, "as regras do gate não foram executadas"


def test_g01_detecta_excecao_ampla_acrescentada(tmp_path: Path) -> None:
    """O drible que de fato funciona: manter os bloqueios e abrir uma exceção
    larga por cima. É a razão de a regra existir.

    Impedir a edição antes que ela ocorra não era opção — o Cursor não tem
    evento de pré-edição de arquivo, e enforcement que só vale num dos três
    agentes-alvo viola a regra 10 da skill. Onde a prevenção não é portátil,
    detecta-se; e detectar na cadeia da DoD significa a cada grupo.
    """
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    registro = repo / ".harness" / "gate-rules.json"
    regras = json.loads(registro.read_text())
    regras.insert(
        0,
        {
            "id": "X99",
            "nivel": "permitir",
            "padrao": "^rm.*$",
            "what": "",
            "why": "precisava passar",
            "fix": "",
        },
    )
    registro.write_text(json.dumps(regras, indent=2), newline="\n")
    r = _check_arch(repo)
    assert r.returncode == 1, f"gate enfraquecido passou na DoD:\n{r.stdout}"
    assert "G01" in r.stdout


def test_g01_detecta_gate_removido(tmp_path: Path) -> None:
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    (repo / ".claude" / "hooks" / "gate-destructive.sh").unlink()
    r = _check_arch(repo)
    assert r.returncode == 1, f"gate ausente passou na DoD:\n{r.stdout}"


def test_g02_detecta_gate_que_bloqueia_tudo(tmp_path: Path) -> None:
    """A G01 sozinha é satisfeita por um gate que bloqueia TUDO — que passa na
    checagem e torna o agente inútil. É o par que impede isso."""
    import gerar

    repo = tmp_path / "node"
    gerar.gerar("node", repo)
    (repo / ".claude" / "hooks" / "gate-destructive.sh").write_text(
        "#!/bin/bash\nexit 2\n", newline="\n"
    )
    r = _check_arch(repo)
    assert r.returncode == 1, f"gate que bloqueia tudo passou na DoD:\n{r.stdout}"
    assert "G02" in r.stdout


def test_gate_nao_escreve_em_disco() -> None:
    """A propriedade que mantém o gate vivo quando o disco enche.

    Escrita pode falhar; falha mata o script; script morto devolve exit 1, que
    em `PreToolUse` significa "erro não-bloqueante" — e o comando destrutivo
    executa. O gate falha ABERTO. Quem registra é o `registrar-sessao.sh`, que
    roda ao lado e pode morrer sem consequência.
    """
    texto = GATE.read_text()
    for escrita in (">>", "tee ", "mktemp"):
        assert escrita not in texto, f"o gate escreve em disco (`{escrita}`)"
