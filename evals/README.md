# Nível D — a skill executada por um modelo

Os níveis A, B e C, em [`eval/`](../eval/README.md), medem o **repositório
alvo**: quanto do harness existe depois que a skill passou. Este nível mede
outra coisa — se um modelo lendo o `SKILL.md` consegue produzir aquele
harness.

A distinção não é acadêmica. Os 254 testes de [`tests/`](../tests/) exercitam
`tests/gerar.py`, que é uma **reimplementação determinística da FASE 2 em
Python**. Ela substitui marcadores exatamente como deveria, sempre. Se o
modelo parafrasear um template, esquecer a ponte `CLAUDE.md`, pular a FASE 5
ou inventar um comando de teste num repo sem sensores, nenhum daqueles
testes reprova — eles estão validando a cópia, não o original.

| Nível | Mede | Instrumento |
|---|---|---|
| A / B / C | O repositório alvo | [`eval/`](../eval/) |
| **D** | O modelo executando a skill | este diretório |

## Como roda

Um subagente por caso e por versão da skill, cada um com uma cópia limpa de
uma fixture como repositório alvo. O subagente lê o `SKILL.md` e decide
sozinho o que fazer — é justamente essa liberdade que se está medindo.

```
python3 evals/gradua.py <caso> <repo-gerado> [relatorio.md]
```

O graduador é programático de propósito: as assertions saem dos 19 itens da
FASE 5, que já são uma rubrica objetiva (JSON parseia, gate devolve exit 2,
manifesto confere com o disco). Julgar isso a olho seria trocar evidência de
comando por opinião — exatamente o que a skill proíbe ao agente que a usa.

## Os três casos

| Caso | Fixture | O que só ele pega |
|---|---|---|
| `node` | `tests/fixtures/node` | Preenchimento com sensores reais; glob do hook de formatação |
| `dotnet` | `tests/fixtures/dotnet` | Regra inviolável 10 — não gerar artefato estranho à stack |
| `sem-sensores` | `tests/fixtures/sem-sensores` | **Regra de honestidade**: DoD vazia, nada de pre-commit nem CI, remediação citando as funções puras pelo nome |

`sem-sensores` é o mais informativo. É onde a skill não pode gerar uma DoD
real, e o comportamento correto — lacuna declarada e receita com comando
exato — é o oposto do que um gerador ingênuo faz. Nenhum teste em `tests/`
cobre isso hoje.

## Duas decisões de harness que mudam o que está sendo medido

Vale declarar, porque quem ler os números depois precisa saber:

1. **O subagente aprova em nome do usuário.** A FASE 4 é uma pausa que
   espera um humano; sem alguém para responder, o run morre ali e nada é
   gravado. Então o subagente recebe instrução de aprovar os arquivos de
   harness e **recusar** os itens de remediação que instalem dependências.
   Consequência: este nível não mede a qualidade da apresentação da FASE 4,
   só o que vem antes e depois dela.
2. **A recusa das remediações é fixa.** Isso mantém os runs comparáveis
   entre versões, mas significa que o caminho "usuário aceita sensores, a
   DoD deixa de ser vazia e o enforcement é gerado nesta mesma execução"
   (FASE 2, regra de honestidade) **não é exercitado**. É a maior lacuna
   conhecida deste nível.

## Iteração 1 — resultado

Seis runs completos (3 casos × v2.3/v2.4), em [`iteracao-1/`](iteracao-1/).

| Caso / versão | Placar | Falhou |
|---|---|---|
| node / v2.3 | 16/16 | — |
| node / v2.4 | 15/16 | U10 |
| dotnet / v2.3 | 15/16 | U10 |
| dotnet / v2.4 | 16/16 | — |
| sem-sensores / v2.3 | 17/18 | U10 |
| sem-sensores / v2.4 | 18/18 | — |

**97 de 100 assertions.** O patamar absoluto é alto: um modelo lendo o
`SKILL.md` produz um harness que passa na própria FASE 5, inclusive nos
casos difíceis — em `dotnet` nenhum agente inventou `package.json`, e em
`sem-sensores` os dois deixaram a DoD vazia e **não** geraram pre-commit
nem CI, que é a regra de honestidade funcionando.

### O delta entre versões é zero, e isso era o esperado

A única assertion que falha em qualquer lugar é a U10 (marcador
preenchível sobrando), e ela **inverte de lado**: falha na v2.3 em dois
casos e na v2.4 no terceiro. Não é diferença de versão — é variância entre
agentes diante de uma instrução ambígua (ver defeito 1 abaixo). Metade
apagou o cabeçalho do template, metade o preservou.

Dizer que a v2.4 "melhorou" seria ler ruído como sinal. Os Grupos 11–13
mexeram na fronteira de escopo, no modo de atualização e na apresentação da
FASE 4 — nada disso muda o artefato gerado, que é o que esta rubrica mede.

### O que a rodada realmente entregou

Os relatórios, não o placar. Seis agentes independentes encontraram os
mesmos defeitos na instrução — nenhum deles detectável pelos 254 testes de
`tests/`, porque só aparecem quando alguém tenta *obedecer* a skill:

1. **`format-on-edit.sh` traz `<formatter_command>`, `<file_glob>` e `<sln>`
   no cabeçalho de comentário e no corpo.** A regra 3 manda transcrever
   VERBATIM; o item 6 da FASE 5 proíbe esses marcadores de sobrar. As duas
   não podem valer ao mesmo tempo, e a skill não diz qual cede. É a causa
   direta da oscilação da U10. O `ci-workflow.yml` já se defende disso no
   próprio cabeçalho — a correção foi aplicada a um template só.
2. **`resources/AGENTS.md:59` fixa `MUST NOT: alterar migrations já
   aplicadas` fora de placeholder.** Todos os seis agentes bateram nisso;
   todos removeram, sem respaldo textual. Regra 3 contra regra 4.
3. **`# TODO: definir formatter` quebra o script.** Ele é substituído dentro
   de `if command -v <formatter_bin> ...; then`, e o `#` comenta o `then`:
   erro de sintaxe, hook morto a cada edição. Nenhum item da FASE 5 pega.
4. **O item 8 da FASE 5 é insatisfazível.** Exige DoD idêntica em seis
   arquivos, mas o `init.sh` roda só o teste, o pre-commit é lista de hooks
   e o CI é um step por sensor. Três dos seis divergem por construção.
5. **O item 5 da FASE 5 se auto-bloqueia.** O comando de teste contém
   `rm -rf` literal e é barrado pelo gate do repo onde a skill roda.
   Reproduzível 100%; aconteceu também fora dos runs, ao montar este eval.
6. **Formatter de Python tem três respostas** na skill: `black --quiet`
   (`01-descoberta.md`, `02-preenchimento`), `ruff format`
   (`ecossistemas.md`) e `# TODO`. Nada diz qual vence.
7. **Lockfile está no grupo A** (gerado sem perguntar) mas exige rede.
8. **`git checkout <base> && git pull` falha em repo com git e sem remoto** —
   a FASE 1 item 19 só previu "repo sem git".
9. **A FASE 4 fala em "pontos" e "nível que destrava"**, vocabulário de um
   sistema de pontuação que não existe em nenhum arquivo da skill.

Viraram o Grupo 15 no `TASKS.md`.
