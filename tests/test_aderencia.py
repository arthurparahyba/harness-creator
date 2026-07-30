"""Testes do `medir-aderencia.sh` — o medidor de protocolo do harness gerado.

O teste central deste arquivo não é "o script roda". É **o script separa um
histórico obediente de um desobediente**. Um medidor que aprova os dois não
mede nada, e é assim que quase todo eval mal escrito falha: ele produz um
número, o número parece plausível, e ninguém verifica que ele reagiria a um
mundo diferente.

Por isso cada asserção aqui vem em par: o caso que deve alertar e o que não
deve. As histórias git são construídas em memória, commit a commit, em vez
de virarem fixture em disco — repositório git dentro de `tests/fixtures/`
seria um `.git` aninhado no `.git` deste repo, que o próprio git trata como
caso especial.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
MEDIDOR = RAIZ / ".claude" / "skills" / "harness-creator" / "resources" / "medir-aderencia.sh"

GRUPO_CONCLUIDO = """## Grupo {n} - objetivo {n}
- [x] {n}.1 primeira task
- [x] {n}.2 segunda task
Verificação: `echo ok`
"""

GRUPO_ABERTO = """## Grupo {n} - objetivo {n}
- [ ] {n}.1 primeira task
- [ ] {n}.2 segunda task
Verificação: `echo ok`
"""


def _git(repo: Path, *args: str, data: str | None = None) -> None:
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin",
        "HOME": str(repo),
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    if data is not None:
        # As DUAS datas. `git log --since` filtra por data de COMMITTER, e
        # `--date`/`GIT_AUTHOR_DATE` sozinhos mexem só na de autor — foi assim
        # que a primeira versão destes testes acusou o leitor de um defeito
        # que era do setup.
        env["GIT_AUTHOR_DATE"] = data
        env["GIT_COMMITTER_DATE"] = data
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True, env=env)


def _init(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q", "-b", "main")


def _commit(repo: Path, assunto: str, arquivos: dict[str, str]) -> None:
    for rel, conteudo in arquivos.items():
        alvo = repo / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(conteudo, newline="\n")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", assunto)


def _tasks(*grupos: str) -> str:
    return "# TASKS.md\n\n" + "\n".join(grupos)


def _medir(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(MEDIDOR), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _json(repo: Path, *args: str) -> dict[str, object]:
    r = _medir(repo, "--json", *args)
    assert r.returncode == 0, f"medidor falhou:\n{r.stdout}\n{r.stderr}"
    return dict(json.loads(r.stdout))


def _medidas(saida: dict[str, object]) -> list[dict[str, object]]:
    bruto = saida["resultado"]
    assert isinstance(bruto, list)
    return [m for m in bruto if isinstance(m, dict)]


def _alerta(saida: dict[str, object], nome: str) -> bool:
    for m in _medidas(saida):
        if str(m["medida"]).startswith(nome):
            return bool(m["alerta"])
    raise AssertionError(f"medida ausente: {nome}")


@pytest.fixture(name="obediente")
def _obediente(tmp_path: Path) -> Path:
    """Três grupos concluídos, três checkpoints, handoff em cada um."""
    repo = tmp_path / "obediente"
    _init(repo)
    grupos = []
    for n in (1, 2, 3):
        grupos.append(GRUPO_CONCLUIDO.format(n=n))
        _commit(
            repo,
            f"checkpoint: objetivo {n}",
            {
                "TASKS.md": _tasks(*grupos),
                f"src/modulo{n}.txt": f"conteudo {n}",
                "SESSION_STATE.md": f"- Commit verificado: grupo {n}\n",
            },
        )
    return repo


@pytest.fixture(name="desobediente")
def _desobediente(tmp_path: Path) -> Path:
    """Mesmos três grupos marcados, um checkpoint só, e sem handoff nenhum."""
    repo = tmp_path / "desobediente"
    _init(repo)
    _commit(repo, "inicial", {"SESSION_STATE.md": "- Commit verificado: nenhum\n"})
    grupos = [GRUPO_CONCLUIDO.format(n=n) for n in (1, 2, 3)]
    for i, assunto in enumerate(["wip", "fix", "ajustes", "mais coisas"]):
        _commit(repo, assunto, {f"src/solto{i}.txt": "x"})
    _commit(repo, "checkpoint: objetivo 3", {"TASKS.md": _tasks(*grupos)})
    return repo


# --------------------------------------------------------------- o par central


def test_separa_obediente_de_desobediente(obediente: Path, desobediente: Path) -> None:
    """O teste que dá sentido a todos os outros.

    Medidor que aprova os dois históricos não mede nada — e o modo de falha é
    silencioso, porque ele continua imprimindo números plausíveis.
    """
    bom = _json(obediente)
    ruim = _json(desobediente)
    assert bom["alertas"] == 0, f"histórico obediente alertou: {bom}"
    assert isinstance(ruim["alertas"], int) and ruim["alertas"] >= 3, (
        f"histórico desobediente passou quase limpo: {ruim}"
    )


def test_proporcao_de_checkpoints(obediente: Path, desobediente: Path) -> None:
    assert not _alerta(_json(obediente), "Commits de checkpoint")
    assert _alerta(_json(desobediente), "Commits de checkpoint")


def test_grupo_marcado_sem_checkpoint(obediente: Path, desobediente: Path) -> None:
    """Três grupos marcados concluídos contra um único commit de checkpoint."""
    assert not _alerta(_json(obediente), "Grupos concluidos")
    assert _alerta(_json(desobediente), "Grupos concluidos")


def test_grupo_com_task_aberta_nao_conta_como_concluido(tmp_path: Path) -> None:
    """A definição de "concluído" sai do template (`- [ ]` / `- [x]`), não do
    símbolo de status no título, que é convenção de cada repositório."""
    repo = tmp_path / "aberto"
    _init(repo)
    _commit(
        repo,
        "checkpoint: objetivo 1",
        {
            "TASKS.md": _tasks(GRUPO_CONCLUIDO.format(n=1), GRUPO_ABERTO.format(n=2)),
            "SESSION_STATE.md": "- Commit verificado: grupo 1\n",
        },
    )
    # 1 concluído, 1 aberto, 1 checkpoint: o grupo aberto não pode ser cobrado.
    assert not _alerta(_json(repo), "Grupos concluidos")


# ------------------------------------------------------------------- handoff


def test_handoff_no_commit_seguinte_conta(tmp_path: Path) -> None:
    """Medido contra o próprio repositório da skill, exigir o SESSION_STATE no
    MESMO commit dava 4 de 17; aceitando o commit seguinte, 17 de 17. O
    protocolo manda registrar o hash do checkpoint no arquivo, o que obriga o
    commit dele a existir antes. Uma medida com falso positivo desse tamanho é
    desligada na primeira semana e leva o resto do relatório junto."""
    repo = tmp_path / "handoff-depois"
    _init(repo)
    _commit(repo, "checkpoint: objetivo 1", {"src/a.txt": "a"})
    _commit(repo, "handoff", {"SESSION_STATE.md": "- Commit verificado: abc123\n"})
    assert not _alerta(_json(repo), "SESSION_STATE")


def test_checkpoint_sem_handoff_nenhum_alerta(tmp_path: Path) -> None:
    repo = tmp_path / "sem-handoff"
    _init(repo)
    _commit(repo, "inicial", {"README.md": "x"})
    _commit(repo, "checkpoint: objetivo 1", {"src/a.txt": "a"})
    _commit(repo, "checkpoint: objetivo 2", {"src/b.txt": "b"})
    assert _alerta(_json(repo), "SESSION_STATE")


# --------------------------------------------------------------------- escopo


def test_escopo_estourado_alerta(tmp_path: Path) -> None:
    """Sinal, não prova: por isso o limiar é alto (40 arquivos)."""
    repo = tmp_path / "escopo"
    _init(repo)
    _commit(
        repo,
        "checkpoint: objetivo 1",
        {
            **{f"src/arq{i}.txt": "x" for i in range(60)},
            "SESSION_STATE.md": "- Commit verificado: grupo 1\n",
            "TASKS.md": _tasks(GRUPO_CONCLUIDO.format(n=1)),
        },
    )
    assert _alerta(_json(repo), "Escopo")


def test_escopo_normal_nao_alerta(obediente: Path) -> None:
    assert not _alerta(_json(obediente), "Escopo")


# ------------------------------------------------- não consegui medir (exit 2)


def test_sem_git_sai_2(tmp_path: Path) -> None:
    """Exit 2 é "não consegui medir", categoria distinta de "aderência baixa".

    Confundir as duas faria um scaffold sem git parecer um time indisciplinado.
    """
    repo = tmp_path / "sem-git"
    repo.mkdir()
    r = _medir(repo)
    assert r.returncode == 2, r.stdout


def test_repo_sem_commit_sai_2(tmp_path: Path) -> None:
    repo = tmp_path / "vazio"
    _init(repo)
    r = _medir(repo)
    assert r.returncode == 2, r.stdout
    assert "sem commits" in r.stderr


def test_sem_fonte_de_trabalho_alerta_mas_nao_derruba(tmp_path: Path) -> None:
    """Sem TASKS.md nem OpenSpec o agente inventa tarefas — é alerta. Mas o
    script continua medindo o resto: exit 0, e as outras três medidas saem."""
    repo = tmp_path / "sem-fonte"
    _init(repo)
    _commit(repo, "checkpoint: objetivo 1", {"SESSION_STATE.md": "- x\n"})
    saida = _json(repo)
    assert _alerta(saida, "Grupos concluidos")
    assert saida["medidas"] == 5


# --------------------------------------------- medida 5: sessões sem commit


HOOK_TRACE = (
    RAIZ / ".claude" / "skills" / "harness-creator" / "resources" / "hooks" / "registrar-sessao.sh"
)


def _trace(repo: Path, linhas: list[tuple[str, str, str]]) -> None:
    """Grava trace à mão, com `json.dumps` — que põe espaço depois dos
    dois-pontos, ao contrário do `printf` compacto do hook.

    A divergência é de propósito: o leitor precisa tolerar as duas formas. A
    primeira versão dele não tolerava, e o modo de falha era o pior possível
    — reportava "trace vazio" em vez de erro, e quem lesse concluiria que não
    houve sessão nenhuma. O formato exato do hook é coberto pelo teste de
    integração no fim desta seção.
    """
    destino = repo / ".harness" / "trace"
    destino.mkdir(parents=True, exist_ok=True)
    conteudo = "".join(
        json.dumps({"ts": ts, "evento": ev, "alvo": "x", "sessao": sid}) + "\n"
        for ts, ev, sid in linhas
    )
    (destino / "2026-07-30.jsonl").write_text(conteudo, newline="\n")


def test_sem_trace_a_medida_se_declara_cega(obediente: Path) -> None:
    """Harness recém-instalado não tem trace. Calar seria pior que declarar:
    quem lê o relatório precisa saber que a medida não olhou nada."""
    saida = _json(obediente)
    assert not _alerta(saida, "Sessoes sem commit")
    cego = next(m["cego_para"] for m in _medidas(saida) if str(m["medida"]).startswith("Sessoes"))
    assert "nao gravou nada" in str(cego)


def test_sessao_com_edicao_e_sem_commit_hoje_alerta(tmp_path: Path) -> None:
    """O buraco que as medidas 1-4 declaravam não ver: houve trabalho, e ele
    não passou por fronteira nenhuma."""
    repo = tmp_path / "trabalho-perdido"
    _init(repo)
    # Commit antigo, para o repo ter HEAD; a medida olha commits de HOJE.
    _commit(repo, "checkpoint: objetivo 1", {"SESSION_STATE.md": "- x\n"})
    _git(repo, "commit", "-q", "--amend", "--no-edit", data="2020-01-01T10:00:00")
    _trace(repo, [("2026-07-30T10:00:00Z", "edit", "s1"), ("2026-07-30T10:05:00Z", "shell", "s1")])
    assert _alerta(_json(repo), "Sessoes sem commit")


def test_sessao_so_de_leitura_nao_alerta(tmp_path: Path) -> None:
    """Sessão que só rodou comandos e não editou nada é investigação
    legítima. Cobrar commit dela transformaria o medidor em ruído — e medida
    que grita sem motivo é a primeira a ser ignorada."""
    repo = tmp_path / "so-leitura"
    _init(repo)
    _commit(repo, "checkpoint: objetivo 1", {"SESSION_STATE.md": "- x\n"})
    _git(repo, "commit", "-q", "--amend", "--no-edit", data="2020-01-01T10:00:00")
    _trace(repo, [("2026-07-30T10:00:00Z", "shell", "s1"), ("2026-07-30T10:01:00Z", "shell", "s1")])
    assert not _alerta(_json(repo), "Sessoes sem commit")


def test_le_o_trace_que_o_hook_realmente_escreve(tmp_path: Path) -> None:
    """Integração hook → leitor, sem formato escrito à mão no meio.

    Os dois foram feitos juntos e é fácil eles concordarem por engano num
    formato que nenhum dos dois produz de verdade. Aqui o arquivo vem do hook.
    """
    repo = tmp_path / "integrado"
    _init(repo)
    _commit(repo, "checkpoint: objetivo 1", {"SESSION_STATE.md": "- x\n"})
    _git(repo, "commit", "-q", "--amend", "--no-edit", data="2020-01-01T10:00:00")
    env = dict(os.environ)
    env["HARNESS_TRACE_DIR"] = str(repo / ".harness" / "trace")
    for payload in (
        '{"session_id":"s1","tool_input":{"command":"npm test"}}',
        '{"session_id":"s1","tool_input":{"file_path":"src/a.ts"}}',
    ):
        subprocess.run(
            ["sh", str(HOOK_TRACE)],
            input=payload,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
    assert (repo / ".harness" / "trace").exists(), "o hook não gravou nada"
    assert _alerta(_json(repo), "Sessoes sem commit"), (
        "o leitor não entendeu o arquivo que o próprio hook escreveu"
    )


# ------------------------------------------------------------------ contratos


def test_nunca_e_gate(desobediente: Path) -> None:
    """A garantia mais importante do contrato: alerta não vira exit != 0.

    "Aderência caiu de 80% para 60%" não tem conserto no harness, tem conversa
    com o time. Atrás de um exit 1 isso viraria "alguém quebrou alguma coisa",
    e a reação previsível a um vermelho que ninguém causou é desligar o sensor.
    """
    r = _medir(desobediente)
    assert r.returncode == 0, f"medidor virou gate:\n{r.stdout}"


def test_toda_medida_declara_o_que_nao_ve(obediente: Path) -> None:
    """Instrumento que não declara seu limite é lido como se não tivesse
    nenhum — e este mede histórico commitado, não sessões."""
    for m in _medidas(_json(obediente)):
        assert str(m["cego_para"]).strip(), f"medida sem limite declarado: {m['medida']}"


def test_alerta_traz_what_why_fix(desobediente: Path) -> None:
    """Número solto não diz a ninguém o que fazer na segunda-feira, e agente
    que vê número ruim sem receita tende a atacar o medidor."""
    saida = _medir(desobediente).stdout
    for campo in ("WHAT:", "WHY:", "FIX:"):
        assert campo in saida, f"alerta sem {campo}"


def test_janela_de_commits_e_configuravel(obediente: Path) -> None:
    assert _json(obediente, "--commits", "2")["commits_analisados"] == 2


def test_janela_invalida_sai_2(obediente: Path) -> None:
    assert _medir(obediente, "--commits", "abc").returncode == 2


def test_sem_python_e_sem_jq(obediente: Path, tmp_path: Path) -> None:
    """Precisa rodar em repo Go, .NET ou Java, onde exigir Python ou jq
    transformaria o diagnóstico em erro de setup. Mesma restrição do gate e do
    check-arch — e ela já foi violada uma vez, na versão do hook que lia o JSON
    com Python."""
    magro = tmp_path / "bin-magro"
    magro.mkdir()
    for ferramenta in ("git", "sh", "awk", "sed", "sort", "grep", "cut", "mktemp", "rm"):
        caminho = shutil.which(ferramenta)
        if caminho:
            (magro / ferramenta).symlink_to(caminho)
    r = subprocess.run(
        ["sh", str(MEDIDOR)],
        cwd=obediente,
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": str(magro), "HOME": str(obediente)},
    )
    assert r.returncode == 0, f"medidor exige ferramenta ausente:\n{r.stdout}\n{r.stderr}"
    assert "ADERENCIA" in r.stdout
