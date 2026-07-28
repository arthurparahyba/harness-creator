---
name: "Nível C: bateria comportamental"
description: Roda o experimento A/B que mede se o harness muda o comportamento do agente, e consolida a tabela comparativa
category: Evaluation
tags: [eval, harness, experimento, nivel-c]
---

Executa uma rodada do nível C: o mesmo repositório alvo com e sem harness,
quatro tarefas por célula, e a tabela comparativa no fim.

Argumento opcional: o repositório alvo (URL). Sem argumento, usa o
`alvo_padrao` de `eval/nivel-c/tarefas.json`.

## Antes de começar

Leia `eval/nivel-c/README.md`. As três decisões de método descritas lá são o
que separa uma medição de um número bonito — em especial a de que **cada
sessão roda de dentro do repo alvo**. Rodar da raiz deste repositório faz a
célula de controle carregar o `AGENTS.md` daqui e receber um protocolo que
ela existe para não ter.

Confirme que o ambiente tem: `claude` no PATH, `git`, e a toolchain do alvo
(para o `alvo_padrao`, um JDK e `JAVA_HOME` exportado).

## Passos

1. **Preparar o painel**, num diretório de trabalho novo:

   ```
   sh eval/nivel-c/preparar.sh <workdir>
   ```

   Ele clona o alvo, cria `control/` e `harness/` do mesmo commit e roda o
   baseline. **Baseline vermelho aborta a rodada** — com a suíte já quebrada,
   T4 não distingue o bug plantado do que já estava lá.

2. **Aplicar a skill** em `<workdir>/harness/` e commitar o resultado ali.
   Este passo é manual porque é um modelo lendo o `SKILL.md` que o executa —
   é o que o nível D mede. Confira com:

   ```
   sh <workdir>/harness/.claude/verificar-harness.sh --raiz <workdir>/harness
   ```

   Reprovação aqui é defeito da geração: conserte antes de medir
   comportamento, senão a rodada mede um harness quebrado.

3. **Rodar as tarefas**, na ordem do catálogo e nas duas condições. T3 e T2
   dependem do estado que T1 deixa; inverter a ordem mede outra coisa:

   ```
   sh eval/nivel-c/roda.sh <workdir> control T1
   sh eval/nivel-c/roda.sh <workdir> harness T1
   sh eval/nivel-c/roda.sh <workdir> control T3
   ... e assim por diante, para T3, T2 e T4
   ```

   O `roda.sh` aplica o bug plantado de T4, roda a sessão e, depois dela,
   executa a DoD do alvo — o estado do repositório é medido, não perguntado.

4. **Consolidar**:

   ```
   python3 eval/nivel-c/mede.py <workdir>
   ```

5. **Escrever o relatório** em `eval/nivel-c/<alvo>-<data>.md`, colando a
   tabela do passo 4 e acrescentando o que só sai do transcript: violação de
   escopo em T3, recuperação de contexto em T2, e se alguma sessão declarou
   pronto com a DoD vermelha. Use
   `eval/nivel-c/petclinic-2026-07-28.md` como formato. Acrescente a rodada à
   tabela de `eval/nivel-c/README.md` e copie os JSONs para
   `eval/nivel-c/runs/`.

## Regras

- A saída de comando É a evidência. Nenhuma linha da tabela vem de impressão
  sobre o que a sessão escreveu.
- A tabela do `mede.py` é mecânica de propósito: ela mede **em que estado a
  sessão deixou o repositório**, não se o agente "declarou pronto". A segunda
  leitura é do relatório, e tem de vir com a citação junto.
- Reporte o n. Uma execução por célula é o piso; o protocolo pede três, e
  abaixo disso o número é direcional, não conclusivo.
- Rodada abortada no meio também vira relatório: qual célula parou, em que
  tarefa e por quê. Rodada sem registro é dinheiro gasto sem evidência.
