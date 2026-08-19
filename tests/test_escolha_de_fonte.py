"""Sensor determinístico do detector de escolha de fonte (`eval/escolha-de-fonte/`).

Nenhum modelo é chamado aqui: os transcripts são fixture em disco. O que se
verifica é o INSTRUMENTO — que ele acende no golden positivo e fica apagado no
negativo. Sem o par, um detector que reconhecesse qualquer texto passaria
verde, que foi o que aconteceu com o detector do nível E (Grupo 25.5).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

RAIZ = Path(__file__).resolve().parent.parent
EVAL = RAIZ / "eval" / "escolha-de-fonte"
GOLDENS = RAIZ / "tests" / "fixtures" / "escolha-de-fonte"


def _detecta_mod() -> ModuleType:
    """Carrega por caminho: `eval/` não é pacote e não vai virar um só para o
    teste. O `roda.sh` chama o mesmo arquivo por caminho — exercitar a mesma
    porta de entrada é parte do que este teste cobre."""
    spec = importlib.util.spec_from_file_location("detecta", EVAL / "detecta.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["detecta"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module", name="detecta")
def _detecta() -> ModuleType:
    return _detecta_mod()


def test_golden_positivo_acende_os_seis_sinais(detecta: ModuleType) -> None:
    """A resposta real de uma sessão limpa com o harness instalado cumpre o
    protocolo inteiro. Se este teste cair, ou o detector regrediu ou o texto do
    AGENTS.md gerado mudou sem o detector acompanhar."""
    texto = detecta.texto_da_resposta(GOLDENS / "positivo.md")
    r = detecta.detecta(texto)
    assert r.completo, f"golden positivo não acendeu tudo — faltou: {r.faltando}"


def test_golden_negativo_nao_acende(detecta: ModuleType) -> None:
    """O caso que dá valor ao teste anterior.

    Um detector que acende em qualquer texto mede zero e parece saudável. O
    negativo é a resposta de um repositório SEM harness ao mesmo pedido: ela
    pode até conversar sobre o plano, mas não faz os movimentos que o protocolo
    prescreve.
    """
    texto = detecta.texto_da_resposta(GOLDENS / "negativo.md")
    r = detecta.detecta(texto)
    assert not r.completo, (
        "golden negativo acendeu os seis sinais — o detector não distingue nada"
    )
    assert "citou_as_duas_fontes" not in r.acesos, (
        "resposta sem harness citando as duas fontes: o sinal está frouxo demais"
    )


def test_todo_sinal_tem_razao_declarada(detecta: ModuleType) -> None:
    """Sinal sem o porquê vira número que ninguém sabe interpretar quando cai."""
    for nome, (razao, padroes) in detecta.SINAIS.items():
        assert razao.strip(), f"sinal {nome} sem razão declarada"
        assert padroes, f"sinal {nome} sem padrão"


def test_cli_do_detector_devolve_exit_util() -> None:
    """A bateria (`roda.sh`) conta rodada acesa pelo exit code — 0 é protocolo
    cumprido, 1 é incompleto. Se isso inverter, a taxa inverte junto."""
    for golden, esperado in (("positivo.md", 0), ("negativo.md", 1)):
        r = subprocess.run(
            [sys.executable, str(EVAL / "detecta.py"), str(GOLDENS / golden)],
            capture_output=True,
            text=True,
        )
        assert r.returncode == esperado, f"{golden}: exit {r.returncode}, esperado {esperado}"


def test_detector_le_o_json_do_claude_p(detecta: ModuleType, tmp_path: Path) -> None:
    """O `roda.sh` grava JSON do `claude -p`; o golden é `.md`. As duas portas
    de entrada existem, e a que a bateria usa é a que ninguém testa à mão."""
    alvo = tmp_path / "rodada.json"
    alvo.write_text(json.dumps({"result": "texto qualquer"}), encoding="utf-8")
    assert detecta.texto_da_resposta(alvo) == "texto qualquer"

    ruim = tmp_path / "sem-result.json"
    ruim.write_text(json.dumps({"outro": 1}), encoding="utf-8")
    with pytest.raises(ValueError):
        detecta.texto_da_resposta(ruim)


def test_bateria_fica_fora_da_dod() -> None:
    """`roda.sh` chama modelo e custa dinheiro: dentro da DoD, ela seria pulada
    na prática e levaria o resto junto."""
    dod = (RAIZ / "AGENTS.md").read_text()
    assert "escolha-de-fonte/roda.sh" not in dod, "a bateria entrou na Definition of Done"
    corpo = (EVAL / "roda.sh").read_text()
    assert "fora da Definition of Done" in corpo, "o script não declara que está fora da DoD"
    assert "\r" not in corpo, "roda.sh com CRLF"
