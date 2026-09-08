# knowledge/ — conhecimento do repositório

Conhecimento caro de descobrir, que não deve ser re-investigado a cada sessão:
como um componente não-óbvio funciona, como uma solução da empresa se configura
e se evolui, como resolver os problemas dela. O agente lê daqui antes de
investigar, e escreve aqui o que descobriu. Trocar uma investigação multi-turno
(cara em tempo e tokens) por uma leitura é o ponto.

Isto é documentação para o agente e para o time; nenhuma ferramenta lê como
plano.

## Quando usar (o gatilho)

Antes de investigar um componente, um erro ou uma funcionalidade que você não
conhece: **cheque primeiro se já há um arquivo aqui.** Se houver e a **Prova**
ainda passar, use e siga. Se faltar, ou se a Prova falhar (o código mudou),
investigue e **registre/atualize** o arquivo.

## Como investigar

1. Cheque `knowledge/` e as **Fontes** abaixo antes de ler código às cegas.
2. Escope a pergunta a UMA coisa (um componente, um erro), não o repo inteiro.
3. Leia só a fatia relevante; rode algo que **prove** o comportamento.
4. Escreva o que entendeu no formato abaixo, com a Prova.

## Formato de um arquivo de conhecimento (`knowledge/<componente>.md`)

```
---
componente: <nome, ex: TaaC (testes)>
derivado_de: [<globs dos arquivos que sustentam isto, ex: config/taac/**>]
baseline_commit: <hash do commit em que foi verificado>
atualizado: <YYYY-MM-DD>
---

## O que é / como funciona
...

## Como evoluir
...

## Como resolver problemas
...

## Prova
<comando re-rodável que demonstra o comportamento, com a saída esperada; OU,
 melhor, o ponteiro para o teste que já cobre isto — "é testado" vale mais que
 "foi testado", porque o CI mantém a prova de graça.>
```

**Obsolescência.** O `derivado_de` + `baseline_commit` dizem de onde o
conhecimento saiu. Se algum arquivo de `derivado_de` mudou desde o
`baseline_commit`, trate como possivelmente velho: re-rode a Prova. Se passa,
ainda vale; se falha, atualize. Hierarquia de frescor: **Prova re-rodável >
proveniência > suspeita**.

## Fontes de investigação (canais deste repo)

Canais que tornam a investigação mais objetiva — comandos, MCPs, páginas de
doc. Acrescente aqui quando descobrir um: toda investigação futura passa a
consultá-los primeiro. Começa vazio; é preenchido pelo time/agente ao longo do
tempo.

<!-- exemplos (troque pelos reais e apague este comentário):
- Docs internas: MCP `<nome>` (query pela página do produto)
- Grafo de dependências: `<comando>`
-->
