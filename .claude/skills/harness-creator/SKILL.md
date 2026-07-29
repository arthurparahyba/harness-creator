---
name: harness-creator
description: >
  Gera ou atualiza o harness de um repositorio para agentes de codigo.
  Use esta skill sempre que o usuario pedir para configurar um harness,
  criar ou melhorar um AGENTS.md, preparar um repositorio para agentes de
  IA, criar init.sh ou protocolo de sessao, configurar OpenSpec com regras
  de execucao, ou mencionar harness engineering, checkpoints por grupos de
  tasks, WIP=1 ou continuidade entre sessoes - mesmo que nao use a palavra
  "harness". Gera AGENTS.md com protocolo de sessao, SESSION_STATE.md,
  TASKS.md, init.sh, hooks de agent loop, pre-commit, comando /dod, regras
  arquiteturais executaveis e verificador do harness, adaptados a stack
  descoberta no repositorio.
license: MIT
metadata:
  author: squad-harness
  version: "2.5"
---

# Harness Creator

## O fluxo — e o passo 0, que decide se ele se aplica

**Passo 0: dimensione o pedido antes de executar.** O fluxo de 6 fases
existe para gerar ou atualizar o harness inteiro. Nem todo pedido que
menciona `AGENTS.md` pede isso, e responder a um pedido de uma linha com
seis fases e uma pausa de aprovacao gasta a sessao do usuario num ritual
que ele nao pediu.

O criterio e objetivo, para nao virar julgamento a cada invocacao: **se o
pedido nomeia a edicao e o arquivo alvo ja existe**, faca so a edicao
pontual e diga em uma linha que o fluxo completo esta disponivel. Em
qualquer outro caso, rode o fluxo — inclusive quando o pedido for vago
sobre o repo estar pronto para agentes. O default e o fluxo: quem invoca
esta skill sem apontar uma linha especifica esta pedindo o harness.

```
Pedido: "acrescente no AGENTS.md que usamos pnpm"
Acao:   edita a linha; uma frase dizendo que o fluxo completo existe

Pedido: "prepare este repo para agentes" / "configura o harness aqui"
Acao:   fluxo completo, a partir da FASE 1

Pedido: "no Cursor o gate nao bloqueia nada"
Acao:   tabela de diagnostico no fim deste arquivo; edicao pontual
```

Escolhido o fluxo, ele roda **inteiro e sem perguntar nada**, com uma
parada so:

1. [FASE 1 — Descoberta (somente leitura)](references/01-descoberta.md)
2. [FASE 2 — Preenchimento VERBATIM dos templates](references/02-preenchimento-templates.md)
3. [FASE 3 — Resolucao de conflitos com o repo existente](references/03-resolucao-conflitos.md)
4. [FASE 4 — Saida e aprovacao](references/04-saida-aprovacao.md) ← **unica pausa**
5. [FASE 5 — Verificacao pos-geracao](references/05-verificacao-pos-geracao.md)
6. [FASE 6 — Fechamento do gate de CI](references/06-lembrete-ci.md)

A pausa e na FASE 4 porque e o momento anterior a gravar: depois de gravar
ela ja nao protege nada, e uma confirmacao por fase transformaria um fluxo
autonomo em seis interrupcoes. Antes e depois dela, execute tudo sozinho.

**Leia SOMENTE o arquivo da fase que esta executando**, um por vez, mais os
catalogos que essa fase citar por link (`ecossistemas.md`,
`remediacoes.md`, `atualizacao.md`). Carregar as seis de uma vez gasta o
contexto que a separacao existe para poupar; recusar o catalogo que a fase
pede deixa voce sem a tabela de que ela depende.

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
   request.
2. **Enforcement** — hooks de agent loop (gate destrutivo + auto-format),
   pre-commit portatil, comando /dod, workflow de CI, e o registro de regras
   arquiteturais (`.harness/arch-rules.json` + `.claude/check-arch.sh`) na
   cadeia da DoD. Sem esta camada, a DoD e so um texto que o agente pode
   ignorar. O registro de regras e o degrau que falta a uma revisao: revisor
   julga caso a caso e esquece; regra fica, e cada classe de erro e cometida
   uma vez so.

A geracao e **verificada**: a FASE 5 confere cada artefato gravado —
JSON e YAML que parseiam, scripts executaveis com LF, a DoD equivalente
entre os arquivos que a declaram, e o gate hook executado de verdade para
provar que devolve exit 2 num comando destrutivo e 0 num seguro. A skill
cobra evidencia de comando do agente que usa o harness; ela mesma nao
declara sucesso sem executar o que gerou.

## Regras invioláveis

Valem em todas as fases. Cada uma vem com o modo de falhar que a originou —
sem ele voce nao tem como julgar os casos que a regra nao previu:

1. **Nao pergunte qual caminho seguir.** Decida pelo passo 0 e execute.
   Perguntar devolve ao usuario a triagem que a skill existe para fazer.
2. **Templates em `resources/` sao transcritos VERBATIM**: so os trechos
   `<>` mudam. Parafrasear protocolo faz cada repo receber uma regra
   diferente, e a inconsistencia so aparece meses depois, quando duas
   equipes comparam os proprios AGENTS.md.
3. **Toda informacao da descoberta cita o arquivo-fonte.** Presumir produz
   um harness que descreve um repositorio que nao existe: DoD com o comando
   errado passa a bloquear todo commit do time.
4. **Nunca copie credencial literal de config MCP** — converta para
   `${VAR}`. Copiar o segredo para a raiz o torna mais visivel e mais
   provavel de ser commitado, que e o oposto do objetivo (detalhe na
   [FASE 1](references/01-descoberta.md)).
5. **Nao gere enforcement vazio**: proponha os sensores que faltam e espere
   o sim. Pre-commit sem hook e CI que passa sem rodar nada dao ao agente um
   verde que ele nao mereceu — pior que nao ter enforcement, porque parece
   ter.
6. **Toda lacuna da descoberta vira item do Plano de Remediacao**, inclusive
   a que a skill nao sabe gerar. Diagnosticar sem receita devolve ao usuario
   o trabalho que a skill existe para fazer (catalogo em
   [remediacoes.md](references/remediacoes.md)).
7. **Detecte ECOSSISTEMA, nao linguagem**: Maven != Gradle, Angular !=
   React. Eles divergem em tudo que a skill preenche, e acertar a linguagem
   e errar o ecossistema gera uma DoD que nao roda.
8. **Nunca gere artefato estranho a stack** (ex.: `package.json` em repo
   .NET). Alem de inutil, e o sinal visivel de que a descoberta errou — o
   usuario perde a confianca no resto do harness, com razao.
9. **Gere `CLAUDE.md` com `@AGENTS.md` ao lado de CADA `AGENTS.md`.** O
   Claude Code carrega `CLAUDE.md` e nao carrega `AGENTS.md`: sem a ponte o
   protocolo nunca entra em contexto e nada falha — o agente apenas o ignora.
10. **O harness vale para os tres agentes-alvo** — Claude Code, Devin CLI e
    Cursor. Registrar hooks so de um deixa os outros dois sem enforcement
    nenhum, e ninguem percebe ate alguem rodar um comando destrutivo no
    agente errado.

## Referencias

Catalogos, lidos sob demanda quando uma fase os citar:

- [Arquivos gerados (templates de `resources/` e seus destinos)](references/arquivos-gerados.md)
- [Ecossistemas (comandos, lockfiles e globs por stack)](references/ecossistemas.md)
- [Catalogo de remediacoes (o que recomendar e a quem cabe decidir)](references/remediacoes.md)
- [Atualizacao de harness existente (quando ha `.claude/harness.json`)](references/atualizacao.md)
- [Conceitos do protocolo (glossario)](references/conceitos-protocolo.md)

Para explicar ao usuario **o que a skill muda no repositorio dele** — o que
cria, o que modifica, o que propoe e o que nunca faz — aponte para
[MUDANCAS-NO-REPOSITORIO.md](MUDANCAS-NO-REPOSITORIO.md), o documento
didatico voltado a quem vai aprovar as mudancas.

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
