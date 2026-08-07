# harness-creator

Prepara um repositório para trabalho com agentes de IA de código — contexto,
protocolo de sessão, guardrails de runtime e sensores, adaptados à stack que
o repositório de fato usa.

O produto é uma skill, e ela vive em
[.claude/skills/harness-creator/](.claude/skills/harness-creator/). Para usá-la
no seu projeto, veja **[Instalação](#instalação)**.

## Isso funciona?

Você pede uma correção. O agente reescreve o javadoc **descrevendo o bug como
comportamento correto**, em 4 turns, sem executar nada — e informa que
terminou.

Isso não é hipótese: aconteceu numa medição. Em 2026-07-28 a pergunta foi
testada com um A/B pareado sobre o
[spring-petclinic](https://github.com/spring-projects/spring-petclinic)
(Java 17, Maven) — duas cópias do mesmo commit, uma com o harness gerado pela
skill e outra sem, quatro tarefas idênticas em cada uma.

| | Sem harness | Com harness |
|---|---|---|
| Declarou pronto com a suíte falhando | 3 de 4 sessões | 0 de 4 |
| Arquivos tocados fora do pedido | 2 | 0 |
| Estado final | 0 commits, build vermelho | 4 commits, build verde |
| Custo em API | US$ 1,94 | US$ 3,20 |

Na tarefa do javadoc, a cópia com harness recusou-se a commitar por cima de
uma mudança que não estava no plano de trabalho.

**O harness custa 65% mais caro.** Ele troca trabalho solto e quebrado por
trabalho commitado e verificado — é o mesmo desenho de custo que o
experimento citado no curso de harness engineering encontrou. Se o seu
gargalo é o preço da API e não a confiabilidade do resultado, essa troca não
compensa.

**n=1 por célula, num ecossistema só**: os números são direcionais, não
conclusivos. O relatório com as citações, as métricas que exigem leitura do
transcript e o que a rodada **não** prova está em
[eval/nivel-c/petclinic-2026-07-28.md](eval/nivel-c/petclinic-2026-07-28.md).
A bateria é reexecutável em qualquer repositório pelo comando `/exp-nivel-c`
(ver [eval/nivel-c/](eval/nivel-c/README.md)).

## Instalação

A skill é o diretório
[.claude/skills/harness-creator/](.claude/skills/harness-creator/). Instalar é
copiar esse diretório para onde o Claude Code procura skills — não há build,
dependência nem passo de registro.

**No projeto**, para o time inteiro receber pelo git:

```bash
git clone --depth 1 https://github.com/arthurparahyba/harness-creator.git /tmp/harness-creator
mkdir -p <seu-repo>/.claude/skills
cp -r /tmp/harness-creator/.claude/skills/harness-creator <seu-repo>/.claude/skills/
```

**Só na sua máquina**, valendo em todos os seus projetos:

```bash
mkdir -p ~/.claude/skills
cp -r /tmp/harness-creator/.claude/skills/harness-creator ~/.claude/skills/
```

Se você já está dentro de um clone deste repositório, pule o `git clone` e
copie daqui mesmo:
`cp -r .claude/skills/harness-creator <seu-repo>/.claude/skills/`

### Como pedir o harness

Abra o Claude Code no repositório alvo e **peça pelo nome da skill**:

> use a skill harness-creator para preparar este repositório para agentes de IA

Nomear a skill não é preciosismo. A bateria de disparo deste repositório
mediu pedidos indiretos — "prepare este repo para IA" — acionando a skill em
quase 0 de 10 casos: o agente tende a achar que resolve sozinho e escreve um
`AGENTS.md` de improviso. O instrumento dessa medição está sob suspeita e a
investigação continua aberta (ver [evals/README.md](evals/README.md)), mas o
caminho que não depende disso custa três palavras.

A skill investiga a stack, mostra o que vai gravar e **para uma vez** para
você aprovar. Depois grava, executa o que gerou e cola a saída.

Ela não presume: cada informação do harness cita o arquivo do seu repositório
de onde veio. Onde não há evidência, ela escreve que não encontrou em vez de
inventar — um `AGENTS.md` com o comando de teste errado bloqueia todo commit
do time.

### A skill roda no Claude Code; o harness vale nos três

Quem lê `SKILL.md` é o Claude Code — instalar este diretório no Cursor ou no
Devin não faz nada. O que vale nos três agentes é o **harness gerado**: o
mesmo protocolo e os mesmos hooks são gravados para Claude Code, Devin CLI e
Cursor. Rode a skill uma vez, commite o resultado, e quem usa Cursor ou Devin
no time recebe o harness pelo git sem nunca instalar skill nenhuma.

## O que muda no seu projeto

Não é uma lista de arquivos — é o que deixa de dar errado:

| Antes | Depois |
|---|---|
| "Pronto" é o julgamento do agente | "Pronto" significa que **estes comandos passaram**, e a saída é colada como evidência |
| O agente inventa tarefas fora do pedido | Só executa o que está no plano de trabalho; o resto vira pendência registrada |
| `git push --force` e `rm -rf` executam | **Não executam.** Não é aviso: o comando é bloqueado antes de rodar |
| Voltar depois de três dias recomeça do zero | O estado da última sessão está escrito: commit, testes, bloqueios, próximo passo |
| O erro achado numa revisão se repete meses depois | Vira regra executável no registro arquitetural, e o build reprova se ele voltar |
| Cada agente (Claude Code, Devin, Cursor) tem regras diferentes | Os três leem o mesmo protocolo e disparam os mesmos hooks |
| O harness "parece" instalado | A skill executa o que gerou e cola a saída — não declara sucesso sem verificar |

O detalhamento de **cada alteração que ela cria, modifica ou propõe** está em
[MUDANCAS-NO-REPOSITORIO.md](.claude/skills/harness-creator/MUDANCAS-NO-REPOSITORIO.md).

## Maturidade

O repositório alvo é medido com
[harness-score](https://paladini.io/harness-score/):

```bash
npx -y harness-score
```

Nos 14 ecossistemas de teste, a geração leva o alvo de **L0 para L4**, com
ganho de **+67 pontos** (ver [tests/fixtures/](tests/fixtures/README.md)).
Numa execução real sobre o spring-petclinic, o repositório saiu de
`L0 · 39/108` para `L4 · 89/108`.

## Trabalhar neste repositório

A skill tem seu próprio
[README](.claude/skills/harness-creator/README.md), com as 6 fases por dentro.

```bash
./init.sh                # instala deps, roda o baseline, mostra o estado
pytest -q                # sensores da skill
ruff check . && mypy     # lint e tipos
```

[tests/test_skill.py](tests/test_skill.py) valida o que só quebraria na
máquina de quem usa a skill: templates JSON e YAML que corrompem ao
substituir marcador, arquivos gravados com CRLF (que fazem o gate hook falhar
**aberto**), links mortos entre as fases, e marcadores citados numa fase mas
ausentes dos templates. O gate hook é executado de verdade e precisa devolver
exit 2 para comando destrutivo e exit 0 para comando seguro.

O protocolo de trabalho (grupos, WIP=1, Definition of Done) está no
[AGENTS.md](AGENTS.md), e as regras dos templates em
[.claude/skills/harness-creator/AGENTS.md](.claude/skills/harness-creator/AGENTS.md).
O CI trava o nível deste repositório em L4 — remover um hook ou um sensor
deixa o build vermelho.
