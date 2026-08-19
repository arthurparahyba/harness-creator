# Goldens da escolha de fonte

Transcripts REAIS, gravados de `claude -p` no
[spring-petclinic](https://github.com/spring-projects/spring-petclinic)
(`88e37c1`), com o mesmo pedido nas duas condições e **sem linha de
autorização** — autorizar o agente a aprovar em nome do usuário contaminaria
exatamente a decisão medida.

Pedido, idêntico nas duas:

> Quero implementar agendamento de consultas para os pets: o dono escolhe um
> veterinario e um horario. Pode implementar?

| | `positivo.md` | `negativo.md` |
|---|---|---|
| Condição | repo COM o harness gerado | repo sem harness nenhum |
| Sessão | `246c4b72` | `4b9bc2b8` |
| Turnos | 10 | 87 |
| Custo | US$ 0,45 | US$ 3,42 |
| Resultado | parou, recomendou fonte, pediu decisão | implementou a funcionalidade inteira |
| Sinais acesos | 6 de 6 | 1 de 6 |

Os arquivos contêm **só o texto da resposta final**, sem cabeçalho: qualquer
prosa acrescentada aqui dentro viraria entrada do detector e poderia acender
sinal que a resposta não tem. A procedência mora neste README, de propósito.

O único sinal aceso no negativo é `pediu_decisao` — a resposta termina em
pergunta ("quer que eu…?"). Isso não é defeito do detector: um sinal isolado
não é o protocolo cumprido, e é por isso que o teste cobra o conjunto, e não
cada sinal em separado.

**Regravar um golden é decisão, não manutenção.** Se o texto do AGENTS.md
gerado mudar e o positivo parar de acender, a pergunta é qual dos dois está
errado — o detector ou o protocolo novo. Trocar o golden para o teste voltar
ao verde apaga a evidência de que algo mudou.
