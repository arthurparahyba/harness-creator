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

## Isso funciona?

Harness é instrução: o agente pode ignorar. Em 2026-07-28 a pergunta foi
medida com um A/B pareado sobre o
[spring-petclinic](https://github.com/spring-projects/spring-petclinic)
(Java 17, Maven) — duas cópias do mesmo commit, uma com o harness gerado pela
skill e outra sem, quatro tarefas idênticas em cada uma.

| | Sem harness | Com harness |
|---|---|---|
| Declarou pronto com a suíte falhando | 3 de 4 sessões | 0 de 4 |
| Arquivos tocados fora do pedido | 2 | 0 |
| Estado final | 0 commits, build vermelho | 4 commits, build verde |
| Custo em API | US$ 1,94 | US$ 3,20 |

O caso mais claro foi a tarefa com um bug plantado: sem harness, o agente
reescreveu o javadoc **descrevendo o bug como comportamento correto**, em 4
turns e sem executar nada. Com harness, recusou-se a commitar por cima de uma
mudança que não estava no plano de trabalho.

O harness custa 65% mais caro e entrega trabalho commitado e verificado
contra trabalho solto e quebrado — é o mesmo desenho de custo que o
experimento citado no curso de harness engineering encontrou.

**n=1 por célula**, num ecossistema só: os números são direcionais, não
conclusivos. O relatório com as citações, as métricas que exigem leitura do
transcript e o que a rodada não prova está em
[eval/nivel-c/petclinic-2026-07-28.md](eval/nivel-c/petclinic-2026-07-28.md).
A bateria é reexecutável em qualquer repositório pelo comando `/exp-nivel-c`
(ver [eval/nivel-c/](eval/nivel-c/README.md)).

## Maturidade

Este repositório é medido com [harness-score](https://paladini.io/harness-score/):

```bash
npx -y harness-score
```

O CI trava o nível em L4 — remover um hook ou um sensor deixa o build vermelho.
