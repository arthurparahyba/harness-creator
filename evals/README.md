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

## Estado

A infraestrutura está pronta e o graduador validado. **A primeira rodada
completa ainda não existe**: os seis runs da iteração 1 foram interrompidos
por limite de sessão da API antes de qualquer um terminar de gravar. O que
sobrou no disco não é resultado — é run pela metade, e graduá-lo produziria
um número que não mede a skill.
