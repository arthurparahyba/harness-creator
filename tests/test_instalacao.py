"""Sensores da instrução de instalação.

Quem chega ao repositório precisa descobrir duas coisas antes de qualquer
outra: onde a skill está e como colocá-la no projeto dele. Isso já esteve
escrito e envelheceu em silêncio — a instrução era `cp -r` a partir da raiz,
que só funciona para quem já clonou, e o README da própria skill (o arquivo
que VIAJA junto quando alguém copia o diretório) não tinha instalação nenhuma.

Documentado e não sensoreado é o padrão que este repositório já pagou caro
nos Grupos 33, 35, 44 e 45. Estes testes existem para que renomear a skill,
mover o diretório ou apagar a seção reprove o build, em vez de deixar uma
instrução que aponta para lugar nenhum.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SKILL = RAIZ / ".claude" / "skills" / "harness-creator"
DESTINO = ".claude/skills/harness-creator"

READMES = [RAIZ / "README.md", SKILL / "README.md"]


def _secao(texto: str, titulo: str) -> str:
    inicio = texto.index(titulo)
    resto = texto[inicio + len(titulo) :]
    fim = re.search(r"^## ", resto, re.MULTILINE)
    return resto[: fim.start()] if fim else resto


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.parent.name)
def test_readme_tem_secao_de_instalacao(readme: Path) -> None:
    """Os DOIS: o da raiz é o que o GitHub mostra, o da skill é o que segue
    junto no diretório copiado. Quem recebe o segundo não tem acesso ao
    primeiro."""
    assert "## Instalação" in readme.read_text(), (
        f"{readme.relative_to(RAIZ)} não tem seção de instalação — "
        "quem chega não descobre como usar a skill no projeto dele"
    )


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.parent.name)
def test_instalacao_cita_o_caminho_que_existe(readme: Path) -> None:
    """O caminho da skill é o dado que a instrução inteira depende. Movê-lo
    sem atualizar o texto entrega um `cp` que falha na primeira linha."""
    secao = _secao(readme.read_text(), "## Instalação")
    assert DESTINO in secao, f"a seção não diz o caminho da skill ({DESTINO})"
    assert SKILL.is_dir(), f"{DESTINO} não existe: a instrução aponta para o vazio"
    assert (SKILL / "SKILL.md").is_file(), (
        "o caminho existe mas não tem SKILL.md — copiá-lo não instala skill nenhuma"
    )


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.parent.name)
def test_instalacao_manda_invocar_pelo_nome(readme: Path) -> None:
    """Instalar não é usar. O nível E mediu pedidos indiretos acionando a
    skill em quase 0 de 10 casos — instrução que termina em "peça o harness"
    entrega um usuário que instalou certo e não consegue disparar."""
    secao = _secao(readme.read_text(), "## Instalação")
    assert "use a skill harness-creator" in secao, (
        "a seção não mostra o pedido literal que invoca a skill pelo nome"
    )


def test_readme_da_raiz_situa_a_skill_antes_da_primeira_secao() -> None:
    """O pedido que originou este grupo: "quem chega não identifica de cara
    onde está a skill". O teste do Grupo 37 mantém a evidência como primeira
    seção — então a localização precisa caber acima dela, em uma linha."""
    texto = (RAIZ / "README.md").read_text()
    abertura = texto[: texto.index("## ")]
    assert DESTINO in abertura, (
        "a abertura do README não diz onde a skill vive; quem chega tem de caçar o diretório"
    )


def test_instalacao_cobre_projeto_e_maquina() -> None:
    """São decisões diferentes: no projeto o time recebe pelo git, na máquina
    vale para todos os seus repos. Documentar só uma esconde a outra."""
    for readme in READMES:
        secao = _secao(readme.read_text(), "## Instalação")
        assert "~/.claude/skills" in secao, (
            f"{readme.relative_to(RAIZ)}: falta a instalação pessoal"
        )
        assert "<seu-repo>" in secao, (
            f"{readme.relative_to(RAIZ)}: falta a instalação no projeto alvo"
        )


def test_instalacao_declara_que_a_skill_e_do_claude_code() -> None:
    """A skill gera harness para três agentes, e daí sai a leitura errada de
    que ela se instala nos três. Copiar o diretório para o Cursor ou o Devin
    não faz nada: quem lê SKILL.md é o Claude Code."""
    for readme in READMES:
        secao = _secao(readme.read_text(), "## Instalação")
        assert "SKILL.md" in secao and "Claude Code" in secao, (
            f"{readme.relative_to(RAIZ)}: a seção não diz qual agente lê a skill"
        )

    frontmatter = (SKILL / "SKILL.md").read_text().split("---")[1]
    assert "Esta skill roda no Claude Code" in frontmatter, (
        "o `compatibility` lista três agentes sem dizer onde a SKILL roda — "
        "é a mesma leitura errada, no campo que o cliente exibe"
    )
