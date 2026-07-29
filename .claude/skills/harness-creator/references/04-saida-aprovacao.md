# FASE 4 — Saída e aprovação

**Objetivo:** Apresentar os arquivos propostos e o Plano de Remediação, e
aguardar aprovação explícita antes de gravar.
**Precondições:** Fases 1–3 concluídas.

---


## Fluxo de branches inferido — confirme antes de gravar

Apresente, em três linhas, o que a FASE 1 concluiu sobre o fluxo, **com a
evidência de cada uma**:

```
Branch base:  main          (fonte: git symbolic-ref refs/remotes/origin/HEAD)
Prefixo:      feat/         (fonte: 12 de 15 branches do histórico usam feat/)
Entrega:      push + PR     (fonte: .github/PULL_REQUEST_TEMPLATE.md + CODEOWNERS)
```

Vai aqui, e não numa pergunta própria, porque o fluxo já tem **uma** pausa: a
Regra 1 proíbe perguntar qual caminho seguir, e uma confirmação por assunto
transformaria um fluxo autônomo em várias interrupções. Este é o momento
anterior a gravar — é onde o usuário corrige de graça.

Quando algum dos três for default por falta de evidência, diga isso com todas
as letras (`sem evidência no repo — usando o default`). Default apresentado
como descoberta é pior que pergunta: o usuário aprova achando que a skill viu
algo que ela não viu.

## Ordem de apresentação

1. O Relatório de Descoberta (com fontes)
2. Os arquivos propostos, agrupados por camada:
   - Camada de instrução (AGENTS.md raiz, AGENTS.md com escopo, skill
     `executar-grupo`, init.sh, SESSION_STATE.md, README.md, etc.)
   - Camada de enforcement (hooks, pre-commit, /dod, workflow de CI,
     lockfile, .mcp.json, .editorconfig, .gitignore append, subagente)

   **Quanto mostrar de cada um depende do risco de aprovar sem ler.** São
   perto de vinte artefatos: despejar o conteúdo integral dos vinte produz
   uma parede de texto que ninguém revisa, e aprovação que ninguém leu não
   é aprovação — é a pausa virando formalidade. Pior, gasta o contexto
   justamente antes da fase que grava.

   - **Arquivo novo, que só existe por causa do harness** (hooks, `/dod`,
     `SESSION_STATE.md`, manifesto, subagente, skill): uma linha com o
     destino e os valores preenchidos. Nada é destruído se estiver errado,
     e a FASE 5 verifica cada um.
   - **Arquivo que sobrescreve, dá append ou altera conteúdo do usuário**
     (`AGENTS.md`/`CLAUDE.md` preexistente, `.gitignore`, `.mcp.json` com
     credencial, `.editorconfig`): **diff completo, sempre**. É o que o
     usuário precisa auditar, porque é o único caso em que aprovar errado
     custa trabalho dele.
   - **AGENTS.md da raiz, quando é novo**: conteúdo integral mesmo assim.
     É o arquivo que passa a governar todas as sessões de agente no
     repositório, e os `MUST NOT` dele saíram da descoberta — se algum foi
     inferido errado, este é o momento de o usuário ver.

   Ofereça o conteúdo integral de qualquer outro sob demanda, numa linha.
   Quem quiser ler tudo continua podendo; quem não quiser não paga por isso.
3. **Plano de Remediação** — tudo que ainda separa o repositório de um
   harness completo, no formato do [catálogo](remediacoes.md): um item por
   ação (não por check), dizendo o que a aceitação modifica no
   repositório, o comando exato e o que o agente passa a poder fazer.
   Ordenar pelo que **destrava outra coisa** primeiro — sensores antes de
   tudo, porque habilitam a DoD, o pre-commit e o CI.

   Não usar vocabulário de pontuação ("+6 pontos", "nível 4"): é o placar
   de uma ferramenta externa que o usuário não roda e que não existe em
   lugar nenhum do harness entregue. O catálogo já proíbe isso; a FASE 4 é
   onde o plano é redigido, então é aqui que a proibição precisa valer.

   Colher a decisão **item a item** — aceitar, recusar ou adiar. Isto é
   parte da mesma pausa da FASE 4, não uma segunda rodada de perguntas:
   apresente o plano junto com os arquivos e peça uma resposta só.

   Se um item aceito criar sensores, refaça o preenchimento da DoD com
   os comandos novos e gere o enforcement que passou a ter o que
   verificar (`.pre-commit-config.yaml`, workflow de CI) antes de gravar.
   Itens recusados ou adiados: não aplicar, não repropor na sessão, e
   registrar os adiados em `SESSION_STATE.md`.

4. Lista de pendências que ninguém além do humano resolve (migração
   project.md, runner corporativo, segredo a rotacionar)
   Sinalizar explicitamente, quando aplicável:
   - **Runner de CI**: o workflow gerado usa `ubuntu-latest`; se a
     organização usa self-hosted, trocar antes do primeiro push.
   - **Credenciais em MCP**: cada valor literal substituído por
     `${VAR}`, com a lista de variáveis a exportar e o aviso de que o
     segredo original precisa ser rotacionado se já foi commitado.
   - **Step de DoD no CI existente**: quando o repo já tem pipeline, o
     step proposto é sugestão — a skill não edita o pipeline.
   - **DoD lenta demais para o ritmo do grupo**: se a cronometragem da
     FASE 5 (item 7) passar de ~3 minutos, propor a divisão em verificação
     rápida por grupo e DoD completa antes do push, dizendo quais sensores
     ficariam em cada uma. Quem decide é o usuário: tirar um sensor da
     verificação por grupo é abrir mão de detecção precoce, e o custo dessa
     troca depende do projeto. Sem a divisão, a DoD longa é pulada na
     prática e o WIP=1 perde o gate que o sustenta.
5. **Oferta de LICENSE**: se não existir, perguntar ao usuário qual
   licença adicionar (proprietária "All rights reserved", MIT, Apache-2.0,
   ou pular). Se o usuário escolher, gerar o arquivo `LICENSE` apropriado.

## Ação após aprovação

**AGUARDAR APROVAÇÃO EXPLÍCITA do usuário antes de gravar qualquer
arquivo.** Após aprovação: gravar, `chmod +x init.sh` e nos scripts
`.claude/hooks/*.sh`, e sugerir o commit "checkpoint: harness inicial"
como checkpoint zero do repo.

Esta é a **única** pausa. Depois de gravar, siga direto para a FASE 5 e
a FASE 6 sem pedir confirmação — elas só verificam e relatam.

> Esta é a **única pausa** obrigatória do fluxo. Antes desta fase,
> execute tudo autonomamente.

---

## ⏸️ ÚNICA PAUSA DO FLUXO — aguarde aqui

A pausa é **antes** de gravar, não depois: apresente arquivos e Plano de
Remediação, e espere a resposta do usuário. Recebida a aprovação, grave
o que foi aceito e siga direto para a
[Fase 5](05-verificacao-pos-geracao.md), sem nova confirmação.
