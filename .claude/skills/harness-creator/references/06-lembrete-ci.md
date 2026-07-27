# FASE 6 — Fechamento do gate de CI

**Objetivo:** Garantir que a Definition of Done também roda no CI, que é
o único enforcement que ninguém consegue pular.
**Precondições:** Fase 5 concluída.

---

## Por que o CI importa

Pre-commit e hooks de agent loop são enforcement **local**: valem na
máquina de quem instalou, e `git commit --no-verify` os contorna. O CI é
o enforcement **remoto** — roda em toda push, para todo mundo, sem
depender de setup local. Sem ele, a DoD é opcional na prática.

## O que fazer, conforme o caso

**Repo não tinha CI** (workflow gerado na Fase 2): confirmar com o
usuário que `runs-on: ubuntu-latest` serve. Em organização com runner
self-hosted, `ubuntu-latest` faz o workflow falhar de forma silenciosa ou
nunca ser agendado — trocar antes do primeiro push.

**Repo já tinha CI** (nada foi gerado): verificar se os comandos da DoD
já rodam no pipeline. Se rodam, o gate está fechado, nada a fazer. Se não
rodam, apresentar o step proposto e o arquivo onde entraria, e deixar o
usuário aplicar. A skill não edita pipeline existente porque:

- Runners variam (ubuntu-latest vs self-hosted corporativo)
- Pipelines reusáveis (ex: iupipes) podem já cobrir lint/test
- Schemas variam (GitHub Actions, GitLab CI, Jenkins, etc.)

## O harness pode ser desfeito sem ninguém notar

Um hook apagado, um sensor removido do manifesto, um `AGENTS.md` com
escopo que sumiu num merge: nada disso quebra o build, então ninguém
descobre até um agente causar o dano que o harness existia para evitar.

Avisar o usuário desse risco e sugerir a proteção que couber no
pipeline dele. As duas mais baratas:

- Fazer o CI falhar se os scripts referenciados em `.claude/settings.json`
  não existirem no repositório — hook apontando para arquivo ausente falha
  aberto e passa despercebido.
- Rodar o próprio gate hook com um comando destrutivo simulado e exigir
  exit 2, do mesmo jeito que a FASE 5 faz. É o teste que prova que a
  proteção continua ligada.

A skill não escolhe ferramenta de auditoria para o usuário: descreve o que
precisa ser protegido e deixa a implementação com quem conhece o pipeline.

---

## ✅ SUCESSO — Harness Gerado!

| Componente | Status |
|------------|--------|
| Camada de instrução (AGENTS.md raiz + escopo, skill, init.sh) | ✅ |
| Camada de enforcement (hooks, pre-commit, /dod, CI) | ✅ |
| Verificação pós-geração (gate testado, DoD consistente) | ✅ |
| Plano de Remediação respondido | ✅ |
| Gate de CI | ✅ |
