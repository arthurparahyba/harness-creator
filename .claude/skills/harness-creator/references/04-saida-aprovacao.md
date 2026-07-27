# FASE 4 — Saída e aprovação

**Objetivo:** Apresentar os arquivos propostos e o Plano de Remediação, e
aguardar aprovação explícita antes de gravar.
**Precondições:** Fases 1–3 concluídas.

---

## Ordem de apresentação

1. O Relatório de Descoberta (com fontes)
2. Os arquivos propostos (conteúdo completo), agrupados por camada:
   - Camada de instrução (AGENTS.md raiz, AGENTS.md com escopo, skill
     `executar-grupo`, init.sh, SESSION_STATE.md, README.md, etc.)
   - Camada de enforcement (hooks, pre-commit, /dod, workflow de CI,
     lockfile, .mcp.json, .editorconfig, .gitignore append, subagente)
3. **Plano de Remediação** — tudo que ainda separa o repositório do
   próximo nível, no formato do [catálogo](remediacoes.md): um item por
   ação (não por check), com os pontos, o nível que destrava, o que a
   aceitação modifica no repositório e o comando exato. Ordenar por
   nível destravado primeiro, pontos depois.

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
