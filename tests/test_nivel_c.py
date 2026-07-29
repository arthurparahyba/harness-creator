"""Testes da bateria do nível C (`eval/nivel-c/`).

Não executam a bateria — ela custa dólares e depende de rede, de um JDK e do
`claude` CLI. O que se verifica aqui é o que quebra silenciosamente entre uma
rodada e outra: catálogo de tarefas mal formado, script com CRLF, prompt que
sumiu, bug plantado apontando para um trecho que o alvo não tem mais.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

RAIZ = Path(__file__).resolve().parent.parent
NIVEL_C = RAIZ / "eval" / "nivel-c"
SCRIPTS = ["preparar.sh", "roda.sh"]


def _mede() -> ModuleType:
    """`eval/nivel-c/` não é pacote nem está no pythonpath do pytest, e não
    vai virar um só para o teste: o `mede.py` é chamado por caminho, do
    comando e da linha `Verificação:` do grupo. Carregar por caminho aqui é
    exercitar a mesma porta de entrada que o uso real."""
    spec = importlib.util.spec_from_file_location("mede", NIVEL_C / "mede.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Registrar ANTES de executar: o módulo usa `from __future__ import
    # annotations`, e `@dataclass` resolve as anotações em texto procurando a
    # classe em `sys.modules`. Sem esta linha o import morre no primeiro
    # dataclass, com um erro que não fala nada sobre a causa.
    sys.modules["mede"] = mod
    spec.loader.exec_module(mod)
    return mod


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


def _rodada_sintetica(raiz: Path, dod_por_condicao: dict[str, str]) -> Path:
    """Uma rodada de mentira, com os arquivos que o `roda.sh` deixaria."""
    work = raiz / "rodada"
    (work / "runs").mkdir(parents=True)
    (work / "runs" / "commit-base.txt").write_text("abc1234\n")
    for tarefa in ("T1", "T3", "T2", "T4"):
        for cond, cod in dod_por_condicao.items():
            (work / "runs" / f"{tarefa}-{cond}.json").write_text(
                json.dumps({"num_turns": 3, "duration_ms": 2000, "total_cost_usd": 0.25})
            )
            if cod:
                (work / "runs" / f"{tarefa}-{cond}.dod").write_text(cod)
    return work


def test_mede_separa_as_duas_condicoes(tmp_path: Path) -> None:
    mede = _mede()
    work = _rodada_sintetica(tmp_path, {"control": "1\n", "harness": "0\n"})
    resultado = mede.coletar(work, NIVEL_C / "tarefas.json")
    assert resultado["control"].vermelhas == 4
    assert resultado["harness"].vermelhas == 0
    assert resultado["control"].custo == pytest.approx(1.0)


def test_mede_nao_conta_dod_nao_medida_como_verde(tmp_path: Path) -> None:
    """O modo de falhar que este teste existe para impedir: sem nenhum arquivo
    `.dod`, a contagem de vermelhas é zero — e `0 de 4` lê-se como quatro
    sessões verdes, que é o oposto do que se sabe."""
    mede = _mede()
    work = _rodada_sintetica(tmp_path, {"control": "", "harness": ""})
    resultado = mede.coletar(work, NIVEL_C / "tarefas.json")
    assert "n/d" in resultado["control"].placar_dod
    assert "0 de 4" not in resultado["control"].placar_dod


def test_mede_recusa_workdir_sem_runs(tmp_path: Path) -> None:
    mede = _mede()
    assert mede.main([str(tmp_path)]) == 2


def test_autoteste_do_medidor_passa() -> None:
    """O `--autoteste` é a verificação do Grupo 23 no TASKS.md: se ele deixar
    de valer, a linha `Verificação:` daquele grupo vira decoração."""
    r = subprocess.run(
        [sys.executable, str(NIVEL_C / "mede.py"), "--autoteste"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    assert "autoteste OK" in r.stdout


def test_comando_aponta_para_os_scripts_reais() -> None:
    texto = (RAIZ / ".claude" / "commands" / "exp-nivel-c.md").read_text()
    for script in ("preparar.sh", "roda.sh", "mede.py"):
        assert script in texto, f"o comando não menciona {script}"
    assert "verificar-harness.sh" in texto, (
        "o comando deixou de exigir a verificação do harness antes de medir comportamento"
    )


def _secao_do_readme() -> str:
    texto = (RAIZ / "README.md").read_text()
    inicio = texto.index("## Isso funciona?")
    fim = texto.index("## ", inicio + 3)
    return texto[inicio:fim]


def test_readme_aponta_para_o_relatorio_e_para_a_bateria() -> None:
    secao = _secao_do_readme()
    alvo = "eval/nivel-c/petclinic-2026-07-28.md"
    assert alvo in secao, "a seção do README não leva ao relatório que a sustenta"
    assert (RAIZ / alvo).is_file(), f"{alvo} não existe: link quebrado na vitrine"
    assert "exp-nivel-c" in secao, "o README mostra o resultado sem dizer como reproduzir"


def test_todo_numero_do_readme_existe_no_relatorio() -> None:
    """A vitrine não pode andar sozinha. Número que aparece no README e não no
    relatório é ou erro de digitação ou dado que envelheceu — e nos dois casos
    quem lê o README não tem como saber. Vale a pena o teste ser chato aqui:
    a alternativa é o repositório que prega evidência de comando publicar um
    número sem lastro."""
    relatorio = (RAIZ / "eval" / "nivel-c" / "petclinic-2026-07-28.md").read_text()
    secao = _secao_do_readme()
    padroes = [
        r"US\$ \d+,\d+",  # custo por célula
        r"\d+ de \d+",  # placar de sessões
        r"\d+%",  # variação de custo
    ]
    afirmacoes = [m for p in padroes for m in re.findall(p, secao)]
    assert afirmacoes, "a seção perdeu os números: virou texto de marketing"
    orfas = [a for a in afirmacoes if a not in relatorio]
    assert orfas == [], f"número no README sem lastro no relatório: {orfas}"


def test_evidencia_e_a_primeira_secao_do_readme() -> None:
    """Quem abre o README está decidindo "isso resolve um problema meu?".

    A versão anterior gastava 36 das suas 76 linhas antes da prova: dizia o
    que o repositório é, onde a skill vive, e como rodar os testes DESTE
    projeto — respondendo "como contribuo?" para quem perguntava "adoto?".

    É a mesma inversão que o Grupo 25 corrigiu na `description` da skill, e
    pelo mesmo motivo: o que faz alguém agir não pode ficar abaixo do que a
    coisa é.
    """
    texto = (RAIZ / "README.md").read_text()
    secoes = [ln for ln in texto.splitlines() if ln.startswith("## ")]
    assert secoes, "README sem seções"
    assert secoes[0] == "## Isso funciona?", (
        f"a primeira seção do README é {secoes[0]!r}, não a evidência. "
        "Prova antes de feature, feature antes de contribuição."
    )
    assert secoes[-1] == "## Trabalhar neste repositório", (
        "a seção de contribuidor não está no fim — é outra audiência"
    )
