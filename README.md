# harness-creator

Repositório da skill **harness-creator**, que gera o harness completo de um
repositório para agentes de IA de código: contexto, protocolo de sessão,
guardrails de runtime e sensores — adaptados à stack detectada.

A skill em si vive em
[.claude/skills/harness-creator/](.claude/skills/harness-creator/) e tem seu
próprio [README](.claude/skills/harness-creator/README.md) explicando o que ela
faz e por quê.

Para uma explicação objetiva de **quais alterações ela faz e propõe num
repositório**, veja
[MUDANCAS-NO-REPOSITORIO.md](.claude/skills/harness-creator/MUDANCAS-NO-REPOSITORIO.md).

## Trabalhar neste repositório

```bash
./init.sh                # instala deps, roda o baseline, mostra o estado
pytest -q                # sensores da skill
ruff check . && mypy     # lint e tipos
```

O protocolo de trabalho (grupos, WIP=1, Definition of Done) está no
[AGENTS.md](AGENTS.md). As regras específicas dos templates estão em
[.claude/skills/harness-creator/AGENTS.md](.claude/skills/harness-creator/AGENTS.md).

## Os sensores

[tests/test_skill.py](tests/test_skill.py) valida o que só quebraria na máquina
de quem usa a skill: templates JSON e YAML que corrompem ao substituir
marcador, arquivos gravados com CRLF (que fazem o gate hook falhar **aberto**),
links mortos entre as fases, e marcadores citados numa fase mas ausentes dos
templates. O gate hook é executado de verdade e precisa devolver exit 2 para
comando destrutivo e exit 0 para comando seguro.

## Maturidade

Este repositório é medido com [harness-score](https://paladini.io/harness-score/):

```bash
npx -y harness-score
```

O CI trava o nível em L4 — remover um hook ou um sensor deixa o build vermelho.
