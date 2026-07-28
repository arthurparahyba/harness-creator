# Nível C — a bateria comportamental

O [protocolo](../protocolo-experimento.md) descreve o desenho; este diretório
é a execução dele. A diferença entre os dois é a mesma que separa `tests/` de
`evals/` neste repositório: um descreve o que deveria acontecer, o outro
registra o que aconteceu, com a saída de comando junto.

| Nível | Mede | Onde |
|---|---|---|
| A / B | O repositório alvo tem as capacidades? | [`../`](../) |
| D | O modelo executando a skill gera o harness certo? | [`../../evals/`](../../evals/) |
| **C** | O agente **se comporta** diferente com o harness? | aqui |

Os níveis A, B e D podem ir bem todos ao mesmo tempo e a skill ainda assim
não servir para nada: um harness perfeito que o agente ignora tem score
cheio e eficácia zero. É esse buraco que esta bateria fecha.

## O desenho

A/B pareado sobre o mesmo repositório alvo, duas cópias limpas:

```
alvo/
  control/   clone sem harness
  harness/   clone com a skill aplicada e commitada
```

Quatro tarefas por célula, cada uma atacando um benefício declarado do curso
de harness engineering. **A ordem importa**: T3 e T2 dependem do estado que
T1 deixa.

| # | Tarefa | Benefício testado |
|---|---|---|
| T1 | Feature pequena com teste | conclusão verificável |
| T3 | Pedido em linguagem natural fora do plano | escopo controlado |
| T2 | Sessão nova, prompt só "continue" | continuidade entre sessões |
| T4 | Bug plantado que só a suíte revela | falso "pronto" / evidência |

## Três decisões de método que a validade depende

1. **Cada sessão roda `cd` para dentro do repo alvo.** É a mesma lição que
   invalidou duas execuções do nível E: rodando da raiz deste repositório, o
   `claude -p` carrega o `CLAUDE.md` → `AGENTS.md` **daqui** e obedece o
   protocolo local — inclusive na célula de controle, que existe justamente
   para não ter protocolo nenhum. O resultado pareceria "o harness não fez
   diferença" quando o que houve foi as duas células receberem o mesmo
   harness.
2. **As sessões são headless (`claude -p --output-format json`).** O JSON
   traz `num_turns`, `duration_ms`, `total_cost_usd` e `session_id` — M9 sai
   de graça, e o `session_id` permite continuar a mesma célula em T3 sem
   reabrir contexto.
3. **O agente é autorizado a aprovar em nome do usuário**, com a frase
   idêntica nas duas células. Sem isso a célula com harness trava na primeira
   confirmação que o protocolo pede e a comparação morre ali. O custo é que
   esta bateria **não mede** a qualidade da negociação com o humano — só o
   que vem antes e depois dela.

## O que esta bateria NÃO mede

- **Variância.** O protocolo pede 3 execuções por célula; a rodada de
  2026-07-28 fez 1. Com n=1, um resultado só vira evidência quando o
  mecanismo é visível no transcript — por isso o relatório cita as frases,
  não só os números.
- **Generalização entre ecossistemas.** Um repositório Java/Maven não diz
  nada sobre um monorepo TypeScript.
- **A qualidade do harness gerado.** Isso é o nível D. Uma célula com
  harness pode se comportar melhor porque o protocolo é bom, não porque a
  skill o gerou bem.

## Rodadas registradas

| Data | Alvo | Ecossistema | Relatório |
|---|---|---|---|
| 2026-07-28 | spring-projects/spring-petclinic | Java / Maven | [petclinic-2026-07-28.md](petclinic-2026-07-28.md) |

Os JSONs brutos de cada sessão ficam em [`runs/`](runs/). Eles são o que
permite reauditar M3, M5 e M7 quando a definição da métrica muda — sem eles,
mudar a definição significa pagar a bateria inteira de novo.
