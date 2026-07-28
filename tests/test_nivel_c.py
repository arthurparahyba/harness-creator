"""Testes da bateria do nível C (`eval/nivel-c/`).

Não executam a bateria — ela custa dólares e depende de rede, de um JDK e do
`claude` CLI. O que se verifica aqui é o que quebra silenciosamente entre uma
rodada e outra: catálogo de tarefas mal formado, script com CRLF, prompt que
sumiu, bug plantado apontando para um trecho que o alvo não tem mais.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

RAIZ = Path(__file__).resolve().parent.parent
NIVEL_C = RAIZ / "eval" / "nivel-c"
SCRIPTS = ["preparar.sh", "roda.sh"]


@pytest.fixture(scope="module", name="catalogo")
def _catalogo() -> dict[str, Any]:
    dados: dict[str, Any] = json.loads((NIVEL_C / "tarefas.json").read_text())
    return dados


def test_catalogo_tem_as_quatro_tarefas(catalogo: dict[str, Any]) -> None:
    ids = [t["id"] for t in catalogo["tarefas"]]
    assert ids == ["T1", "T3", "T2", "T4"], (
        f"ordem do catálogo mudou: {ids}. T3 e T2 dependem do estado que T1 deixa"
    )


def test_toda_tarefa_tem_prompt_e_beneficio(catalogo: dict[str, Any]) -> None:
    for t in catalogo["tarefas"]:
        assert t["prompt"].strip(), f"{t['id']} sem prompt"
        assert t["beneficio"].strip(), f"{t['id']} sem benefício declarado"
        assert t["sessao"] in {"nova", "resume"}, f"{t['id']}: sessão {t['sessao']!r}"


def test_ordem_declarada_bate_com_a_ordem_do_arquivo(catalogo: dict[str, Any]) -> None:
    """`roda.sh` é chamado tarefa a tarefa por quem executa; se a ordem do
    arquivo divergir do campo `ordem`, as duas leituras discordam e a rodada
    sai numa sequência que ninguém escolheu."""
    ordens = [t["ordem"] for t in catalogo["tarefas"]]
    assert ordens == sorted(ordens) == [1, 2, 3, 4]


def test_a_autorizacao_e_uma_so(catalogo: dict[str, Any]) -> None:
    """A frase de autorização vale para as duas condições. Uma frase por
    tarefa (ou por condição) tornaria as células não comparáveis, que é o
    único jeito de o experimento mentir sem ninguém notar."""
    assert catalogo["autorizacao"].strip()
    for t in catalogo["tarefas"]:
        assert "autoriza" not in t["prompt"].lower(), (
            f"{t['id']}: autorização embutida no prompt em vez de vir do campo único"
        )


def test_tarefa_com_resume_nao_e_a_primeira(catalogo: dict[str, Any]) -> None:
    primeira = catalogo["tarefas"][0]
    assert primeira["sessao"] == "nova", "a primeira tarefa não tem sessão anterior para retomar"


def test_bug_plantado_e_substituicao_real(catalogo: dict[str, Any]) -> None:
    preparos = [t["preparo"] for t in catalogo["tarefas"] if "preparo" in t]
    assert preparos, "nenhuma tarefa planta bug: T4 não mede falso pronto sem isso"
    for p in preparos:
        assert p["de"] != p["para"]
        assert p["arquivo"].endswith((".java", ".py", ".ts", ".go", ".cs", ".rb", ".php"))
        assert p["teste_que_quebra"], "bug plantado sem o teste que o denuncia não é verificável"


@pytest.mark.parametrize("nome", SCRIPTS)
def test_script_existe_executavel_e_sem_crlf(nome: str) -> None:
    p = NIVEL_C / nome
    assert p.is_file(), f"{nome} ausente"
    assert p.stat().st_mode & 0o111, f"{nome} sem bit de execução"
    assert b"\r\n" not in p.read_bytes(), f"{nome} com CRLF: o shebang morre"


@pytest.mark.parametrize("nome", SCRIPTS)
def test_script_tem_sintaxe_valida(nome: str) -> None:
    r = subprocess.run(["sh", "-n", str(NIVEL_C / nome)], capture_output=True, text=True)
    assert r.returncode == 0, f"{nome}: {r.stderr}"


@pytest.mark.parametrize("nome", SCRIPTS)
def test_script_sem_argumento_mostra_uso_e_falha(nome: str) -> None:
    """Rodar sem argumento tem de explicar e sair != 0. Um script que segue
    com variável vazia apaga o diretório errado ou mede a célula errada."""
    r = subprocess.run(["sh", str(NIVEL_C / nome)], capture_output=True, text=True)
    assert r.returncode != 0
    assert "Uso:" in r.stdout or "Uso:" in r.stderr


def test_roda_sh_entra_no_repo_alvo() -> None:
    """A decisão de método mais fácil de perder numa refatoração: sem o `cd`
    para o repo alvo, o `claude -p` carrega o AGENTS.md DESTE repositório e a
    célula de controle passa a ter protocolo."""
    texto = (NIVEL_C / "roda.sh").read_text()
    assert 'cd "$ALVO"' in texto, "roda.sh deixou de entrar no repo alvo antes de chamar o claude"


def test_roda_sh_mede_a_dod_depois_da_sessao() -> None:
    texto = (NIVEL_C / "roda.sh").read_text()
    assert "dod.txt" in texto and ".dod" in texto, (
        "roda.sh não registra o estado da DoD: sobra acreditar no que a sessão disse"
    )


def test_relatorio_da_rodada_esta_linkado_no_readme() -> None:
    readme = (NIVEL_C / "README.md").read_text()
    for rodada in NIVEL_C.glob("*-20*.md"):
        assert rodada.name in readme, f"{rodada.name} não aparece na tabela de rodadas"
