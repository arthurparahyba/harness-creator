# FASE 3 — Resolução de conflitos com o repositório existente

**Objetivo:** Preservar conteúdo útil do repo e aplicar o protocolo do
template onde houver sobreposição.
**Precondições:** Fase 2 concluída, templates preenchidos.

---

## Regras de conflito

- **AGENTS.md/CLAUDE.md já existe**: preservar o conteúdo descritivo
  útil (comandos, estrutura, convenções), mas o protocolo do template
  PREVALECE sobre seções sobrepostas (workflow, testing, commits).
  Mostrar o diff proposto ao usuário.
- **`CLAUDE.md` já existe** (raiz ou subdiretório): NUNCA sobrescrever.
  Verificar se ele alcança o `AGENTS.md` — por `@AGENTS.md`, por symlink,
  ou porque o próprio protocolo já está nele. Se não alcançar, propor na
  FASE 4 o append de uma única linha `@AGENTS.md` no topo, mostrando o
  diff. Sobrescrever aqui apaga instrução que o usuário escreveu; não
  fazer nada deixa o protocolo fora do contexto do Claude Code.
- **Bloco gerenciado** `<!-- OPENSPEC:START/END -->` presente (versões
  antigas do OpenSpec): preservar intacto; inserir o protocolo após ele.
- **Conteúdo descritivo extenso** (estrutura detalhada, convenções por
  módulo): mover para arquivos AGENTS.md com escopo em subdiretórios
  (conhecimento perto do código). O protocolo nunca sai da raiz.
- **AGENTS.md com escopo já existe** no subdiretório (ou há rule com
  escopo em `.cursor/rules/`, `.clinerules/`, `.github/instructions/`):
  não sobrescrever e não gerar um segundo. Se faltarem as restrições
  descobertas na Fase 1, propor um append ao arquivo existente.
- **Skills já existem** (`.claude/skills/*/SKILL.md` ou equivalente): não
  gerar `executar-grupo`. Se nenhuma delas cobre o procedimento de fechar
  grupo, oferecer como adição na FASE 4.
- **CI já existe** (`.github/workflows/`, `.gitlab-ci.yml`, etc.): NUNCA
  gerar `harness-dod.yml` por cima nem editar o pipeline. Verificar se os
  comandos da DoD já rodam lá; se não rodarem, mostrar na FASE 4 o step
  proposto e o arquivo onde ele entraria, e deixar o usuário aplicar.
  Respeitar o `runs-on:` existente — nunca trocar para `ubuntu-latest`.
- **`README.md` já existe**: não sobrescrever, mesmo que esteja pobre.
- **TASKS.md flat já existente** (sem grupos): não reescrever por conta
  própria — propor o agrupamento ao usuário.
- **Hooks já existentes** (`.claude/settings.json` com chave `hooks`,
  `.devin/hooks.v1.json`, `.cursor/hooks.json`): não sobrescrever. Mesclar
  os hooks do template com os existentes, preservando hooks custom do
  usuário. Mostrar o diff. Cada um dos três é avaliado separadamente: o
  repo pode ter config de um agente e nenhuma dos outros, e nesse caso os
  que faltam são gerados normalmente.
- **`.pre-commit-config.yaml` já existe**: não sobrescrever. Mostrar o
  template como sugestão e deixar o usuário decidir.
- **Lockfile já existe**: não regenerar. Só registrar se está
  desatualizado (opcional).
- **`.editorconfig` já existe**: não sobrescrever. Mostrar o template
  como sugestão de regras adicionais e deixar o usuário decidir.
- **`.gitignore` já existe**: nunca sobrescrever. Só fazer append das
  linhas `.env` se faltarem.
- **`.claude/agents/` já existe**: não sobrescrever subagentes existentes.
  Adicionar `code-reviewer.md` apenas se não houver nenhum subagente.
- **`LICENSE` já existe**: não sobrescrever.
- **`.claude/harness.json` já existe**: o repositório já recebeu um harness
  desta skill. Ler o manifesto ANTES de resolver os demais conflitos: os
  arquivos listados em `arquivos` foram gerados pela skill e podem ser
  atualizados; os que não estão na lista são do usuário e seguem a regra
  normal de não sobrescrever. Comparar `versao` com a atual e apresentar na
  FASE 4 o que mudou entre as duas. Os itens de `recusados` **não voltam a
  ser propostos** — o usuário já decidiu.

---

## ➡️ Fase 3 concluída — siga direto para a Fase 4

Continue imediatamente para a [Fase 4](04-saida-aprovacao.md), onde tudo
é apresentado de uma vez para aprovação. Nada foi escrito ainda.
