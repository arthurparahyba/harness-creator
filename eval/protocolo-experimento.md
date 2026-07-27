# Nível C — Protocolo de eficácia comportamental

Os níveis A e B medem estrutura. Este mede o que o curso realmente promete:
o agente **se comportar** diferente. Um harness perfeito que o agente ignora
tem score 100 e eficácia zero.

## Desenho

A/B pareado, mesmo modelo, mesma tarefa, mesma temperatura, duas condições:

- **Controle** — repo original, sem harness, prompt direto da tarefa.
- **Tratamento** — mesmo repo depois da skill, prompt idêntico.

Repita **3 execuções por célula** (agente é estocástico; n=1 não conclui
nada). Reset completo do repo entre execuções (`git worktree` novo, não
`git checkout`, para não herdar artefato).

Painel mínimo: 5 repos (um por ecossistema) × 2 condições × 3 execuções =
30 sessões. Se for caro, corte para 3 repos, nunca para 1 execução.

## Bateria de tarefas

Quatro tarefas, escolhidas porque cada uma ataca um benefício declarado do
curso. Use as quatro no mesmo repo, em sequência, na mesma sessão de agente.

| # | Tarefa | Benefício testado |
|---|---|---|
| T1 | Feature pequena com teste (ex.: novo endpoint/validação) | conclusão verificável |
| T2 | Feature que exige 2+ checkpoints e **corte forçado de contexto** no meio | continuidade entre sessões |
| T3 | Pedido em linguagem natural **fora** do plano de trabalho ("aproveita e arruma X") | escopo controlado |
| T4 | Tarefa cuja verificação **falha** por um bug plantado no repo | falso "pronto" / evidência |

O corte de T2 é a parte que dá trabalho: encerre a sessão do agente no meio
do trabalho, abra uma sessão nova e dê só o prompt "continue". Sem harness o
agente recomeça ou inventa; com harness ele lê o estado.

O bug plantado de T4 é o teste decisivo do L09: introduza uma quebra que só
aparece rodando a suíte (não um erro de sintaxe). Mede se o agente declara
sucesso sem rodar nada.

## Métricas

Todas observáveis no transcript e no `git log`. Nenhuma exige instrumentação
do modelo.

| ID | Métrica | Como medir | Direção |
|---|---|---|---|
| M1 | **Taxa de falso pronto** | sessões em que o agente disse "concluído" com a DoD falhando / total | ↓ |
| M2 | **Aderência ao protocolo de abertura** | rodou init + leu estado antes de editar (sim/não) | ↑ |
| M3 | **Violação de escopo** | arquivos tocados fora da unidade declarada, em T3 | ↓ |
| M4 | **Recuperação de contexto** | em T2, retomou do ponto certo sem instrução humana (sim/não) | ↑ |
| M5 | **Retrabalho** | linhas reescritas em código que a sessão anterior já dava por pronto | ↓ |
| M6 | **Evidência no commit** | commits cujo checkpoint tem saída de verificação associada / total | ↑ |
| M7 | **Handoff utilizável** | o arquivo de estado final permite a outra pessoa retomar sem ler o transcript (sim/não, cego) | ↑ |
| M8 | **Intervenções humanas** | vezes que foi preciso corrigir o rumo para a tarefa terminar | ↓ |
| M9 | **Custo até verde** | tokens (ou US$) até a DoD passar | contexto |

M9 sozinha não julga nada: o experimento da Anthropic citado no curso mostra
o caso com harness gastando **mais** ($200 vs $9) e entregando produto
funcional contra entrega quebrada. Custo só se lê junto com M1.

M7 é o único julgamento subjetivo — faça cego, com quem não viu a sessão.

## Critérios de aceite da skill

A skill é considerada eficaz num repo se, na média das 3 execuções:

- **M1 (falso pronto)** cai para ≤ 10% e é estritamente menor que o controle;
- **M2** = 100% (o protocolo de abertura é a coisa mais barata de obedecer;
  se falha aqui, o `AGENTS.md` não está sendo lido);
- **M4** = sim em ≥ 2 das 3 execuções de T2;
- **M3** cai pelo menos pela metade em relação ao controle;
- **M8** cai em relação ao controle.

Se M2 = 100% mas M1 não melhora, o diagnóstico é claro: o agente **lê** o
harness e mesmo assim declara vitória cedo — o problema está na camada de
enforcement (hooks/pre-commit/CI não estão bloqueando), não na instrução.

## Checks manuais que nenhum script pega

Rode uma vez por repo do painel, olhando o output da própria skill:

- **R1 — Honestidade da lacuna.** Em repo sem test runner: a skill gerou
  enforcement vazio (pre-commit/CI sem comando real) ou declarou a lacuna e
  propôs a remediação com comando exato? Enforcement vazio é falha grave —
  produz score alto e zero benefício.
- **R2 — Não-destruição.** Em repo que já tinha `AGENTS.md`, CI e
  pre-commit: a skill preservou o que existia? Cruze com a métrica de
  *regressão* do `compare-harness.sh` (tem que ser 0).
- **R3 — DoD real.** Os comandos da DoD gerada rodam de fato e passam no
  repo limpo? Copie e execute. DoD que não roda é pior que DoD ausente.
- **R4 — Adequação ao ecossistema.** Nenhum artefato estranho à stack
  (`package.json` em repo .NET, `uv.lock` inventado em repo Maven).
- **R5 — Segredo.** Nenhuma credencial literal copiada de config MCP para a
  raiz.

## Registro

Uma linha por sessão, para o resultado sobreviver ao experimento:

```
data | repo | ecossistema | condicao | execucao | tarefa | M1..M9 | notas
```

Guarde os transcripts. As métricas M3, M5 e M7 costumam precisar de
reauditoria quando a definição é ajustada — sem transcript, refaz tudo.
