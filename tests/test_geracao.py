"""Testes do harness GERADO, em repositórios de exemplo de cada ecossistema.

`test_skill.py` valida os templates; aqui o harness é de fato produzido
sobre uma fixture real e depois executado. A diferença importa: um glob
como `*.{js,ts}` passa em qualquer inspeção do template e só se revela
inerte quando o hook gerado roda contra um arquivo `.ts` de verdade.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml
from gerar import COM_SENSORES, PREENCHIVEIS, Stack, entrada_do_hook, gerar

MARCADORES = re.compile("|".join(re.escape(m) for m in PREENCHIVEIS))


# Só os ecossistemas com DoD real: `sem-sensores` não recebe enforcement por
# construção, então as asserções sobre CI e pre-commit não se aplicam a ele.
# O que ele deve NÃO ter é verificado em `test_honestidade`.
@pytest.fixture(params=sorted(COM_SENSORES), name="repo")
def _repo(request: pytest.FixtureRequest, tmp_path: Path) -> tuple[Path, Stack, str]:
    nome = str(request.param)
    destino = tmp_path / nome
    stack = gerar(nome, destino)
    return destino, stack, nome


def _roda_hook(
    script: Path,
    entrada: str,
    extra_path: Path | None = None,
    cwd: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    if extra_path is not None:
        env["PATH"] = f"{extra_path}{os.pathsep}{env['PATH']}"
    if extra_env is not None:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(script)],
        input=entrada,
        capture_output=True,
        text=True,
        env=env,
        cwd=None if cwd is None else str(cwd),
        check=False,
    )


def test_json_gerado_parseia(repo: tuple[Path, Stack, str]) -> None:
    destino, _, _ = repo
    for rel in (".claude/settings.json", ".devin/hooks.v1.json"):
        json.loads((destino / rel).read_text())


def test_yaml_gerado_parseia(repo: tuple[Path, Stack, str]) -> None:
    destino, _, _ = repo
    for rel in (".pre-commit-config.yaml", ".github/workflows/harness-dod.yml"):
        assert yaml.safe_load((destino / rel).read_text()) is not None


def test_nenhum_marcador_sobreviveu(repo: tuple[Path, Stack, str]) -> None:
    """Só as linhas ATIVAS importam. Os templates listam nos comentários os
    exemplos das outras stacks (`dotnet format <sln>` num repo Node), e isso
    é documentação, não marcador esquecido. Marcador em comentário que
    corrompe o arquivo ao ser substituído é pego pelos testes de parse."""
    destino, stack, _ = repo
    gerados = [
        destino / "AGENTS.md",
        destino / stack.dir_escopo / "AGENTS.md",
        destino / "init.sh",
        destino / ".claude/commands/dod.md",
        destino / ".claude/hooks/format-on-edit.sh",
        destino / ".pre-commit-config.yaml",
        destino / ".github/workflows/harness-dod.yml",
    ]
    sobreviventes = []
    for p in gerados:
        for n, linha in enumerate(p.read_text().splitlines(), 1):
            if not linha.lstrip().startswith("#") and MARCADORES.search(linha):
                sobreviventes.append(f"{p.name}:{n}: {linha.strip()[:60]}")
    assert sobreviventes == [], f"marcadores não preenchidos: {sobreviventes}"


def test_todo_registro_de_hook_aponta_para_script_executavel(
    repo: tuple[Path, Stack, str],
) -> None:
    """Um registro por agente-alvo, todos apontando para scripts que existem.

    Registro órfão é falha silenciosa: no Claude Code e no Devin o hook morre
    e o comando destrutivo passa; no Cursor, com `failClosed`, o agente perde
    o shell inteiro. Nenhum dos dois aparece como erro para o usuário.
    """
    destino, _, _ = repo
    configs = [".claude/settings.json", ".devin/hooks.v1.json", ".cursor/hooks.json"]
    encontrados: set[str] = set()
    for rel in configs:
        caminho = destino / rel
        assert caminho.is_file(), f"{rel} não foi gerado — agente sem enforcement"
        referencias = set(re.findall(r"[.\w/-]*\.claude/hooks/[a-z-]+\.sh", caminho.read_text()))
        assert referencias, f"{rel} não registra nenhum hook"
        for ref in referencias:
            # `lstrip("./")` comeria o ponto de `.claude`: é remoção de prefixo.
            script = destino / ref.removeprefix("./")
            assert script.is_file(), f"{rel} aponta para script inexistente: {ref}"
            assert os.access(script, os.X_OK), f"{rel} aponta para script não executável: {ref}"
            encontrados.add(script.name)
    assert encontrados == {"gate-destructive.sh", "format-on-edit.sh"}


@pytest.mark.parametrize("evento", ["tool_input", "cursor"])
def test_gate_gerado_bloqueia_nos_dois_formatos_de_entrada(
    repo: tuple[Path, Stack, str], evento: str
) -> None:
    """O Cursor manda `command` no topo; Claude Code e Devin, em `tool_input`.

    Ler só um formato deixa o gate inerte no outro agente — ele responde 0
    para tudo, inclusive para o comando destrutivo.
    """
    destino, _, _ = repo
    comando = "git push origin main --force"
    entrada = (
        json.dumps({"command": comando}) if evento == "cursor" else entrada_do_hook("Bash", comando)
    )
    assert _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada).returncode == 2


def test_manifesto_lista_arquivos_que_existem(repo: tuple[Path, Stack, str]) -> None:
    """O manifesto é o que torna o harness atualizável e removível.

    Listando arquivo que não foi gravado, ele mente sobre o estado do repo e
    a próxima geração trata como "da skill" algo que nunca existiu.
    """
    destino, stack, _ = repo
    manifesto = json.loads((destino / ".claude/harness.json").read_text())["harness"]
    assert manifesto["dod"] == stack.dod_gerada, "manifesto com DoD diferente da gerada"
    assert manifesto["versao"], "manifesto sem versão da skill"
    ausentes = [a for a in manifesto["arquivos"] if not (destino / a).is_file()]
    assert ausentes == [], f"manifesto lista arquivo inexistente: {ausentes}"
    for essencial in ("AGENTS.md", "CLAUDE.md", ".claude/hooks/gate-destructive.sh"):
        assert essencial in manifesto["arquivos"], f"manifesto não registra {essencial}"


def test_dod_identica_em_todo_lugar(repo: tuple[Path, Stack, str]) -> None:
    """DoD divergente entre AGENTS.md e /dod faz o agente verificar uma coisa
    e o CI cobrar outra."""
    destino, stack, _ = repo
    for rel in ("AGENTS.md", ".claude/commands/dod.md"):
        assert stack.dod in (destino / rel).read_text(), f"DoD ausente ou diferente em {rel}"


def test_ci_roda_todos_os_comandos_da_dod(repo: tuple[Path, Stack, str]) -> None:
    """Um CI que roda menos que a DoD é pior que nenhum: o agente acha que
    verificou tudo e o pipeline nunca cobra o que ficou de fora."""
    destino, stack, _ = repo
    workflow = yaml.safe_load((destino / ".github/workflows/harness-dod.yml").read_text())
    steps = [s.get("run", "") for s in workflow["jobs"]["dod"]["steps"]]
    ausentes = [c for c in stack.comandos if not any(c in s for s in steps)]
    assert ausentes == [], f"comandos da DoD que o CI não roda: {ausentes}"


def test_escopo_nao_duplica_o_protocolo(repo: tuple[Path, Stack, str]) -> None:
    destino, stack, _ = repo
    escopo = (destino / stack.dir_escopo / "AGENTS.md").read_text()
    corpo = re.sub(r"<!--.*?-->", "", escopo, flags=re.S)
    for termo in ("WIP=1", "Definition of Done", "SESSION_STATE"):
        assert termo not in corpo


def test_ponte_claude_md_importa_o_agents_md_irmao(repo: tuple[Path, Stack, str]) -> None:
    """O Claude Code carrega CLAUDE.md e não carrega AGENTS.md — nem na raiz,
    nem em subdiretório. Sem a ponte o protocolo é gravado e nunca entra no
    contexto: nada falha, o agente só ignora as regras. O import precisa
    começar a linha, fora de crase e de bloco de código, senão não é
    parseado e vira texto literal."""
    destino, stack, _ = repo
    for diretorio in (destino, destino / stack.dir_escopo):
        ponte = diretorio / "CLAUDE.md"
        assert ponte.exists(), f"sem ponte para o Claude Code em {diretorio}"
        linhas = ponte.read_text().splitlines()
        assert "@AGENTS.md" in linhas, f"{ponte} não importa o AGENTS.md irmão"
        assert (diretorio / "AGENTS.md").exists(), f"import de {ponte} não resolve"


def test_ponte_nao_duplica_o_protocolo(repo: tuple[Path, Stack, str]) -> None:
    """Ponte é import, não cópia: duas fontes divergem na primeira edição."""
    destino, stack, _ = repo
    for diretorio in (destino, destino / stack.dir_escopo):
        corpo = re.sub(r"<!--.*?-->", "", (diretorio / "CLAUDE.md").read_text(), flags=re.S)
        for termo in ("WIP=1", "Definition of Done", "SESSION_STATE"):
            assert termo not in corpo, f"{diretorio}/CLAUDE.md copiou o protocolo"


@pytest.mark.parametrize(
    "comando", ["rm -rf /tmp/x", "git push --force", "npm publish", "dotnet nuget push p.nupkg"]
)
def test_gate_gerado_bloqueia(repo: tuple[Path, Stack, str], comando: str) -> None:
    destino, _, _ = repo
    r = _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada_do_hook("Bash", comando))
    assert r.returncode == 2, "exit != 2 significa gate falhando ABERTO"


def test_gate_gerado_libera_a_dod_da_stack(repo: tuple[Path, Stack, str]) -> None:
    """O gate não pode bloquear o próprio comando que o harness manda rodar."""
    destino, stack, _ = repo
    primeiro = stack.dod.split("&&")[0].strip()
    r = _roda_hook(destino / ".claude/hooks/gate-destructive.sh", entrada_do_hook("Bash", primeiro))
    assert r.returncode == 0, f"o gate bloqueou a própria DoD: {primeiro}"


# Stub que VALIDA o argv em vez de aceitar qualquer coisa.
#
# O stub anterior fazia `printf FORMATADO >> "$1"` — escrevia no primeiro
# argumento, fosse ele qual fosse. Com o gerador preenchendo
# `<formatter_command>` só com o binário, o hook gerado era `mvn "$ARQUIVO"`,
# o stub recebia o caminho em `$1` e o teste passava. O hook real, que é
# `mvn spotless:apply <arquivo>`, aborta com "Unknown lifecycle phase" — e
# nenhum teste via isso, porque o stub aceitava tudo.
#
# Agora o stub procura o caminho ENTRE os argumentos, nas formas que as
# ferramentas de verdade usam (posicional, `-DspotlessFiles=`,
# `-PspotlessIdeHook=`, `--include`). Se o comando gerado não passar o
# arquivo de um jeito que a ferramenta entenderia, nada é formatado e o
# teste reprova — que é o comportamento que faltava.
_STUB_VALIDADOR = r"""#!/bin/bash
# Grava o argv recebido, um por linha, com o prefixo de flag removido
# (`-DspotlessFiles=/x` vira `/x`). O teste confere se o caminho ALVO está
# nessa lista — não basta a ferramenta ter sido chamada com algum arquivo:
# `dotnet format Catalogo.sln --include <alvo>` passa dois caminhos, e a
# versão anterior deste stub aceitava o primeiro que existisse no disco.
for arg in "$@"; do
  printf '%s\n' "${arg#*=}" >> "$STUB_LOG"
done
exit 0
"""


def _stub(diretorio: Path, binario: str, repo_root: Path) -> Path:
    """Instala o stub onde o hook realmente vai procurá-lo.

    Wrapper de build (`./gradlew`) não é resolvido pelo PATH: mora na raiz do
    repositório. Escrever o stub no PATH e esperar que `command -v ./gradlew`
    o encontrasse era o que mascarava o caso Gradle.
    """
    diretorio.mkdir(parents=True, exist_ok=True)
    alvo = (repo_root / binario[2:]) if binario.startswith("./") else (diretorio / binario)
    alvo.parent.mkdir(parents=True, exist_ok=True)
    alvo.write_text(_STUB_VALIDADOR)
    alvo.chmod(0o755)
    return diretorio


def _argv_recebido(destino: Path, stack: Stack, alvo: Path, fake: Path, log: Path) -> list[str]:
    env_log = {"STUB_LOG": str(log)}
    _roda_hook(
        destino / ".claude/hooks/format-on-edit.sh",
        entrada_do_hook("Edit", str(alvo)),
        extra_path=fake,
        cwd=destino,
        extra_env=env_log,
    )
    return log.read_text().splitlines() if log.exists() else []


def test_formatter_alcanca_o_codigo_da_stack(repo: tuple[Path, Stack, str], tmp_path: Path) -> None:
    destino, stack, nome = repo
    fake = _stub(tmp_path / f"bin-{nome}", stack.formatter_bin, destino)
    alvo = destino / stack.formatavel

    argv = _argv_recebido(destino, stack, alvo, fake, tmp_path / f"log-{nome}")

    assert str(alvo) in argv, (
        f"o caminho de {stack.formatavel} não chegou ao formatter. "
        f"glob {stack.file_glob!r}, comando {stack.formatter_command!r}, "
        f"argv recebido: {argv}"
    )


def test_formatter_ignora_o_que_nao_e_codigo(repo: tuple[Path, Stack, str], tmp_path: Path) -> None:
    destino, stack, nome = repo
    fake = _stub(tmp_path / f"bin-neg-{nome}", stack.formatter_bin, destino)
    alvo = destino / stack.nao_formatavel

    argv = _argv_recebido(destino, stack, alvo, fake, tmp_path / f"log-neg-{nome}")

    assert str(alvo) not in argv, (
        f"o hook mandou {stack.nao_formatavel} para o formatter, e ele não é "
        f"código da stack. argv: {argv}"
    )


def test_formatter_command_nao_e_so_o_binario(repo: tuple[Path, Stack, str]) -> None:
    """O comando tem de ser o de `ecossistemas.md`, não o binário sozinho.

    Este é o sensor da cegueira que deixou o defeito de Java passar: enquanto
    `gerar.py` preenchia `<formatter_command>` com `formatter_bin`, o hook
    gerado nos testes era `mvn <arquivo>` — que nem existe como comando — e
    o hook real, `mvn spotless:apply <arquivo>`, nunca era exercitado.
    """
    _, stack, nome = repo
    assert stack.formatter_command.strip() != stack.formatter_bin, (
        f"{nome}: <formatter_command> reduzido ao binário {stack.formatter_bin!r}. "
        "O gerador tem de reproduzir o comando real da tabela de ecossistemas."
    )


def test_formatter_command_passa_o_arquivo(repo: tuple[Path, Stack, str]) -> None:
    """Todo comando de formatação precisa referenciar o arquivo editado.

    Sem isso o hook formata o projeto inteiro a cada edit, ou nada — foi o
    caso do Maven, que lia o caminho posicional como fase de ciclo de vida e
    abortava, com o erro engolido pelo `2>/dev/null || true`.
    """
    _, stack, nome = repo
    assert '"$FILE_PATH"' in stack.formatter_command, (
        f"{nome}: {stack.formatter_command!r} não passa o arquivo editado."
    )


def test_hook_gerado_nao_anexa_o_caminho_no_fim(repo: tuple[Path, Stack, str]) -> None:
    """O template não pode voltar a anexar `"$FILE_PATH"` depois do comando.

    Anexar quebra todo formatter que precisa do caminho numa flag
    (`-DspotlessFiles=`, `-PspotlessIdeHook=`), que é justamente o caso dos
    dois ecossistemas Java.
    """
    destino, stack, nome = repo
    corpo = (destino / ".claude/hooks/format-on-edit.sh").read_text()
    assert f'{stack.formatter_command} "$FILE_PATH"' not in corpo, (
        f"{nome}: o hook anexa o caminho depois do comando, que já o contém."
    )


def test_check_arch_gerado_roda_e_aprova_o_harness_recem_gerado(
    repo: tuple[Path, Stack, str],
) -> None:
    """O harness que a skill acabou de gerar tem de passar nas próprias regras.

    Se a semente reprovasse numa geração limpa, o primeiro contato do usuário
    com o registro de regras seria um vermelho que ele não causou — e a
    reação natural a isso é apagar o arquivo.
    """
    destino, _, nome = repo
    r = subprocess.run(
        ["bash", str(destino / ".claude/check-arch.sh"), str(destino)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, f"{nome}: check-arch reprovou o harness recém-gerado:\n{r.stdout}"
    assert "nenhuma violada" in r.stdout


def test_check_arch_gerado_detecta_violacao(repo: tuple[Path, Stack, str]) -> None:
    """E precisa reprovar de verdade quando a regra é violada.

    Sensor que só sabe dizer "ok" é pior que sensor nenhum: dá um verde que
    ninguém conferiu. Aqui o gate é corrompido de propósito.
    """
    destino, _, nome = repo
    (destino / ".claude/hooks/gate-destructive.sh").write_text("if [ 1\n")
    r = subprocess.run(
        ["bash", str(destino / ".claude/check-arch.sh"), str(destino)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 1, f"{nome}: check-arch não reprovou um gate quebrado"
    assert "WHAT:" in r.stdout and "WHY:" in r.stdout and "FIX:" in r.stdout, (
        "a mensagem precisa dos três campos: sem WHY o agente 'conserta' "
        f"apagando a regra. Saída:\n{r.stdout}"
    )


def test_dod_gerada_executa_o_check_arch(repo: tuple[Path, Stack, str]) -> None:
    """A regra só vale se algo a executar sem ninguém pedir.

    Registro fora da cadeia de verificação é documento com sintaxe de JSON —
    o degrau 3, não o 4.
    """
    destino, _, nome = repo
    for rel in ("AGENTS.md", ".claude/commands/dod.md"):
        assert "check-arch.sh" in (destino / rel).read_text(), (
            f"{nome}: {rel} não roda o check-arch — as regras não têm cabo"
        )


def test_arch_rules_tem_os_tres_campos_acionaveis(repo: tuple[Path, Stack, str]) -> None:
    """`what`, `why` e `fix` em toda regra, e o `fix` precisa ser específico."""
    destino, _, nome = repo
    regras = json.loads((destino / ".harness/arch-rules.json").read_text())
    assert regras, f"{nome}: registro de regras vazio"
    for regra in regras:
        for campo in ("id", "description", "check", "what", "why", "fix"):
            assert regra.get(campo), f"{nome}: regra {regra.get('id')} sem `{campo}`"
        assert len(regra["fix"]) > 30, (
            f"{nome}: fix de {regra['id']} curto demais para ser acionável: {regra['fix']!r}"
        )


def test_agents_md_nao_fixa_o_prefixo_feature(repo: tuple[Path, Stack, str]) -> None:
    """O prefixo tem de vir do marcador, não estar cravado no template.

    Num repo que usa `feat/` ou `users/LOGIN/`, um `feature/` fixo faz o
    agente criar a branch fora do padrão do time logo na primeira
    funcionalidade — e o time só descobre no PR.
    """
    destino, _, nome = repo
    agents = (destino / "AGENTS.md").read_text()
    linha = [x for x in agents.splitlines() if "git checkout -b" in x]
    assert linha, f"{nome}: AGENTS.md não manda criar a feature branch"
    assert "<prefixo-de-branch>" not in linha[0], f"{nome}: marcador sobreviveu"


def test_politica_de_entrega_presente_e_honesta(repo: tuple[Path, Stack, str]) -> None:
    """Sem evidência no repo, a política declara que não foi encontrada.

    Inventar "abra PR" num repo que faz merge direto trava o agente esperando
    uma aprovação que ninguém vai dar; inventar "merge direto" num repo que
    exige PR fura o processo do time. As fixtures não têm histórico git, então
    o esperado aqui é justamente a declaração de ausência.
    """
    destino, _, nome = repo
    commits = (destino / "AGENTS.md").read_text().split("## Commits")[1].split("## ")[0]
    assert "<politica-de-entrega>" not in commits, f"{nome}: marcador sobreviveu"
    assert "NÃO ENCONTRADA" in commits, (
        f"{nome}: sem evidência de fluxo, a política tem de dizer que não foi "
        f"encontrada em vez de inventar uma. Seção Commits:\n{commits}"
    )


def test_agente_propositor_nao_pode_escrever(repo: tuple[Path, Stack, str]) -> None:
    """O agente propõe regra; não edita o registro.

    Um agente com permissão de escrita em `arch-rules.json` tem, em toda
    violação, o caminho curto de reescrever a regra em vez de corrigir o
    código — e a catraca passa a girar para os dois lados.
    """
    destino, _, nome = repo
    corpo = (destino / ".claude/agents/propor-regra-arch.md").read_text()
    m = re.search(r"^tools:\s*(.+)$", corpo, re.M)
    assert m, f"{nome}: agente sem campo `tools` — herda o conjunto completo"
    ferramentas = {x.strip() for x in m.group(1).split(",")}
    proibidas = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
    assert not (ferramentas & proibidas), (
        f"{nome}: agente propositor com ferramenta de escrita: "
        f"{sorted(ferramentas & proibidas)}"
    )


def test_agente_propositor_devolve_regra_e_nao_veredito(
    repo: tuple[Path, Stack, str],
) -> None:
    """Veredito evapora no commit; regra fica.

    Foi essa a diferença que justificou reintroduzir um subagente depois de o
    Grupo 28 remover o revisor: a saída é durável, não descartável.
    """
    destino, _, nome = repo
    corpo = (destino / ".claude/agents/propor-regra-arch.md").read_text()
    assert "APPROVED" not in corpo.split("## O que você NÃO faz")[1].split("##")[1], (
        f"{nome}: o agente voltou a emitir veredito"
    )
    for campo in ('"check"', '"what"', '"why"', '"fix"'):
        assert campo in corpo, f"{nome}: rascunho sem o campo {campo}"
    assert "<branch-base>" not in corpo, f"{nome}: marcador sobreviveu no agente"


def test_check_arch_aprova_harness_sem_hook_de_formatacao(
    repo: tuple[Path, Stack, str], tmp_path: Path
) -> None:
    """Harness parcial não pode reprovar nas próprias regras.

    Nem todo repositório recebe os dois hooks: um formatter que não escopa por
    arquivo (`spring-javaformat` no Spring PetClinic) formataria o módulo
    inteiro a cada edit, e a skill manda não gerar enforcement que atrapalha.
    Sem o hook, a regra A02 reprovava — e o primeiro contato do usuário com o
    registro de regras virava um vermelho que ele não causou. A reação natural
    a isso é apagar o arquivo, o que mata a catraca antes de ela girar.
    """
    destino, _, nome = repo
    (destino / ".claude/hooks/format-on-edit.sh").unlink()
    r = subprocess.run(
        ["bash", str(destino / ".claude/check-arch.sh"), str(destino)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, (
        f"{nome}: check-arch reprovou um harness sem o hook de formatação, "
        f"que é uma geração legítima:\n{r.stdout}"
    )
