---
name: harness-creator
description: >
  Gera um harness completo para agentes de codigo (AGENTS.md com protocolo
  de sessao, config.yaml do OpenSpec, init.sh, SESSION_STATE.md, TASKS.md,
  hooks de agent loop, pre-commit, comando /dod, lockfile) adaptado ao
  repositorio atual, via descoberta de stack/comandos/convencoes + templates
  de protocolo fixo. Use esta skill sempre que o usuario pedir para
  configurar um harness, criar ou melhorar um AGENTS.md, preparar um
  repositorio para agentes de IA, configurar OpenSpec com regras de
  execucao, criar init.sh ou protocolo de sessao, ou mencionar harness
  engineering, checkpoints por grupos de tasks, WIP=1 ou continuidade
  entre sessoes - mesmo que nao use a palavra "harness".
license: MIT
metadata:
  author: squad-harness
  version: "2.3"
---

# Harness Creator

## TL;DR

Gera o harness de um repositorio combinando **descoberta** (o que varia
por repo: stack, comandos, convencoes) com **templates de protocolo fixo**
(o que deve ser identico sempre: grupos/checkpoints, WIP=1, DoD, handoff).
Resultado: duas camadas (instrucao + enforcement) gravadas no repo alvo,
validadas e prontas para uso por agentes de IA.

## Escopo: fluxo completo ou edicao pontual

O fluxo de 6 fases existe para **gerar ou atualizar o harness**. Nem todo
pedido que menciona `AGENTS.md` pede isso: "acrescente no AGENTS.md que
usamos pnpm" e "prepare este repo para agentes" sao pedidos de tamanhos
diferentes, e responder ao primeiro com seis fases e uma pausa de
aprovacao gasta a sessao do usuario num ritual que ele nao pediu.

O criterio e objetivo, para nao virar julgamento a cada invocacao: se o
pedido **nomeia a edicao** e o arquivo alvo ja existe, faca so a edicao e
diga em uma linha que o fluxo completo esta disponivel. Em qualquer outro
caso — inclusive pedido vago sobre o repo estar pronto para agentes — rode
o fluxo completo. O default e o fluxo: quem invoca esta skill sem apontar
uma linha especifica esta pedindo o harness.

## EXECUCAO IMEDIATA (ler primeiro)

Quando esta skill for invocada, comece
imediatamente a FASE 1 (Descoberta). A skill e auto-executavel: o
usuario ja disse o que quer (configurar harness) ao invoca-la.

Fluxo obrigatorio sem intervenção do usuario:
1. FASE 1 — Descoberta do repo + Plano de Remediacao
2. FASE 2 — Preencha os templates com os dados descobertos
3. FASE 3 — Resolva conflitos com arquivos existentes
4. FASE 4 — Apresente resultados e **AGUARDE aprovacao** (unica pausa)
5. FASE 5 — Apos aprovacao, grave e valide o que gravou
6. FASE 6 — Feche o gate de CI

A unica vez que voce deve parar e esperar o usuario e na FASE 4
(aprovacao antes de gravar). Antes e depois disso, execute tudo
autonomamente — nenhuma outra fase pede confirmacao para prosseguir.

## Principio central

**O que precisa ser consistente nao se deixa para o modelo redigir — se
transcreve do template.** Voce raciocina apenas na descoberta e no
preenchimento dos placeholders `<>`.

O harness tem duas camadas, ambas geradas por esta skill:
1. **Instrucao** — AGENTS.md na raiz (protocolo: DoD, grupos, WIP=1),
   AGENTS.md com escopo no diretorio de codigo (restricoes locais),
   CLAUDE.md ao lado de cada um deles importando o irmao (`@AGENTS.md`),
   skill `executar-grupo` (procedimento sob demanda), init.sh,
   SESSION_STATE.md, config.yaml, TASKS.md. O protocolo fica so na raiz;
   escopo e procedimento saem dela para nao pesar o contexto de todo
   request. A ponte CLAUDE.md nao e redundancia: sem ela o protocolo nao
   entra no contexto do Claude Code, que so carrega CLAUDE.md.
2. **Enforcement** — hooks de agent loop (gate destrutivo + auto-format),
   pre-commit portatil, comando /dod, workflow de CI, lockfile. Sem esta
   camada, a DoD e so um texto que o agente pode ignorar.

A geracao e **verificada**: a FASE 5 confere cada artefato gravado —
JSON e YAML que parseiam, scripts executaveis com LF, a DoD identica em
todos os arquivos, e o gate hook executado de verdade para provar que
devolve exit 2 num comando destrutivo e 0 num seguro. A skill cobra
evidencia de comando do agente que usa o harness; ela mesma nao declara
sucesso sem executar o que gerou.

E o que a skill nao gera, ela **recomenda**. Nem toda lacuna se resolve
com arquivo de harness: num repo sem test runner o agente nao tem como
verificar o proprio trabalho, por mais AGENTS.md que exista. Esses casos
viram um Plano de Remediacao, com comando exato e impacto declarado, apresentado na FASE 4 para o usuario aceitar
item a item — porque instalar pytest muda o contrato do projeto, e isso e
decisao dele. Diagnosticar sem receita devolve ao usuario o trabalho que
a skill existe para fazer. Ver
[references/remediacoes.md](references/remediacoes.md).

## Arquivos gerados

A lista completa de templates (`resources/`) e destinos no repo esta em
[references/arquivos-gerados.md](references/arquivos-gerados.md).

Para explicar ao usuario **o que a skill muda no repositorio dele** — o
que cria, o que modifica, o que propoe e o que nunca faz — aponte para
[MUDANCAS-NO-REPOSITORIO.md](MUDANCAS-NO-REPOSITORIO.md), que e o
documento didatico voltado a quem vai aprovar as mudancas.

## Regras invioláveis

Valem em todas as fases. Cada uma existe porque o modo de falhar
correspondente ja aconteceu:

1. Nao pergunte o que fazer ao ser invocada — comece pela FASE 1.
2. A unica pausa e a FASE 4, antes de gravar qualquer arquivo.
3. Templates em `resources/` sao transcritos VERBATIM: so os trechos `<>`
   mudam. Parafrasear protocolo faz cada repo receber uma regra diferente.
4. Toda informacao da descoberta cita o arquivo-fonte. Nunca presuma.
5. Leia SOMENTE o arquivo da fase que esta executando, mais os catalogos
   que essa fase citar por link (`ecossistemas.md`, `remediacoes.md`,
   `atualizacao.md`). Carregar as seis fases de uma vez gasta o contexto
   que a separacao existe para poupar; recusar o catalogo que a fase pede
   deixa voce sem a tabela de que ela depende.
6. Nunca copie credencial literal de config MCP — converta para `${VAR}`.
7. Nao gere enforcement vazio: proponha os sensores que faltam e espere o sim.
8. Toda lacuna da descoberta vira item do Plano de Remediacao, inclusive a
   que a skill nao sabe gerar.
9. Detecte ECOSSISTEMA, nao linguagem: Maven != Gradle, Angular != React.
10. Nunca gere artefato estranho a stack (ex.: `package.json` em repo .NET).
11. Gere `CLAUDE.md` com `@AGENTS.md` ao lado de CADA `AGENTS.md` — o Claude
    Code carrega `CLAUDE.md` e nao carrega `AGENTS.md`.
12. O harness gerado vale para os tres agentes-alvo — Claude Code, Devin CLI
    e Cursor. Registrar hooks so de um deles deixa os outros sem enforcement.

## Roteiro das fases

Cada fase esta num arquivo de `references/`. **Leia o da fase que esta
executando, um por vez** — carregar os seis de uma vez gasta o contexto que
a separacao existe para poupar.

1. [FASE 1 — Descoberta (somente leitura)](references/01-descoberta.md)
2. [FASE 2 — Preenchimento VERBATIM dos templates](references/02-preenchimento-templates.md)
3. [FASE 3 — Resolucao de conflitos com o repo existente](references/03-resolucao-conflitos.md)
4. [FASE 4 — Saida e aprovacao (unica pausa)](references/04-saida-aprovacao.md)
5. [FASE 5 — Verificacao pos-geracao](references/05-verificacao-pos-geracao.md)
6. [FASE 6 — Fechamento do gate de CI](references/06-lembrete-ci.md)

## 📚 Referencias

- [Ecossistemas (comandos, lockfiles e globs por stack)](references/ecossistemas.md)
- [Catalogo de remediacoes (o que recomendar e a quem cabe decidir)](references/remediacoes.md)
- [Arquivos gerados (templates e destinos)](references/arquivos-gerados.md)
- [Conceitos do protocolo (glossario)](references/conceitos-protocolo.md)

## Diagnostico de harness ja instalado

Problemas **da geracao** sao respondidos pelo arquivo da fase que os
produz, com o motivo por extenso — nao ha atalho util para eles aqui. A
tabela abaixo cobre o caso que nenhuma fase alcanca: alguem chega com um
harness ja gravado que nao esta funcionando. Todos falham em silencio,
que e o que os torna dificeis de achar sem uma lista.

| Sintoma | Causa provavel |
|---|---|
| O agente ignora o protocolo, e o AGENTS.md esta la | Falta a ponte: o Claude Code carrega `CLAUDE.md` e nao `AGENTS.md`. Precisa de um `CLAUDE.md` com `@AGENTS.md` ao lado de CADA `AGENTS.md` |
| O gate bloqueia ate `npm test` | Hook de versao antiga, que exigia Python para ler o JSON, em repo sem Python. Os scripts atuais caem no fallback em awk |
| No Cursor o gate nao bloqueia nada | O Cursor manda `command` no topo do JSON; hook que le so `tool_input` recebe string vazia. Precisa de `.cursor/hooks.json` com `failClosed` |
| O agente nunca usa `/dod` nem `executar-grupo` | `<ferramentas-do-harness>` ficou vazio: o AGENTS.md e o unico arquivo lido sempre, e sem o ponteiro nada mais e alcancavel |
| Nenhum scanner enxerga os hooks | `.claude/settings.json` sem o wrapper `"hooks"` no nivel raiz |
