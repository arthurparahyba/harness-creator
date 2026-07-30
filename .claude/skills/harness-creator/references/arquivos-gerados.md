# Arquivos gerados pela skill

Referência completa dos templates em `resources/` e seus destinos no
repositório alvo.

---

## Conteúdo

- Camada de instrução (sempre)
- Camada de enforcement (sempre, a menos que já exista)
- Camada de enforcement (condicional)

---

## Camada de instrução (sempre)

| Template (em `resources/`) | Destino no repo | Condição |
|---|---|---|
| AGENTS.md | `/AGENTS.md` (raiz) | sempre |
| CLAUDE.md | `/CLAUDE.md` (raiz) | sempre (se não existir) |
| AGENTS-scoped.md | `<dir-principal>/AGENTS.md` | se não houver contexto com escopo |
| CLAUDE.md | `<dir-principal>/CLAUDE.md` | junto do AGENTS.md com escopo |
| skills/executar-grupo/SKILL.md | `.claude/skills/executar-grupo/SKILL.md` | se não houver skills |
| init.sh | `/init.sh` (chmod +x) | sempre |
| SESSION_STATE.md | `/SESSION_STATE.md` | sempre |
| openspec-config.yaml | `/openspec/config.yaml` | somente se `openspec/` existir |
| TASKS.md | `/TASKS.md` | somente se `openspec/` NÃO existir |

O `CLAUDE.md` é o mesmo template nos dois destinos e não tem placeholder:
só a linha `@AGENTS.md`. Existe porque o Claude Code carrega `CLAUDE.md` e
**não** carrega `AGENTS.md` — nem na raiz, nem em subdiretório. Sem a ponte,
o protocolo é gravado mas nunca entra no contexto, e o harness só funciona
nos agentes que leem `AGENTS.md` (Devin, Codex). Como o `@` é import e não
cópia, o conteúdo continua vivendo num lugar só.

## Camada de enforcement (sempre, a menos que já exista)

| Template (em `resources/`) | Destino no repo | Condição |
|---|---|---|
| claude-settings.json | `.claude/settings.json` | sempre (se não existir) |
| devin-hooks.json | `.devin/hooks.v1.json` | sempre (se não existir) |
| cursor-hooks.json | `.cursor/hooks.json` | sempre (se não existir) |
| hooks/gate-destructive.sh | `.claude/hooks/gate-destructive.sh` (chmod +x) | sempre (se não existir) |
| hooks/format-on-edit.sh | `.claude/hooks/format-on-edit.sh` (chmod +x) | sempre (se não existir) |
| hooks/registrar-sessao.sh | `.claude/hooks/registrar-sessao.sh` (chmod +x) | sempre (se não existir) |
| verificar-harness.sh | `.claude/verificar-harness.sh` (chmod +x) | sempre |
| medir-aderencia.sh | `.claude/medir-aderencia.sh` (chmod +x) | sempre |
| pre-commit-config.yaml | `.pre-commit-config.yaml` | se não existir **e houver comandos reais de lint/format/types** |
| dod-command.md | `.claude/commands/dod.md` | sempre (se não existir) |
| harness-manifest.json | `.claude/harness.json` | sempre (sobrescrever se já existir) |
| arch-rules.json | `.harness/arch-rules.json` | sempre (**se não existir** — ver FASE 3) |
| gate-rules.json | `.harness/gate-rules.json` | sempre (**se não existir** — ver FASE 3) |
| check-arch.sh | `.claude/check-arch.sh` (chmod +x) | sempre |
| agents/propor-regra-arch.md | `.claude/agents/propor-regra-arch.md` | sempre (se não existir) — **só Claude Code** |

### Os três scripts, e por que não são um só

O repositório recebe três scripts de checagem, e a diferença entre eles é o
que impede que sejam fundidos:

| Script | Pergunta | Sujeito | Quando roda |
|---|---|---|---|
| `verificar-harness.sh` | o harness está íntegro? | arquivos parados | FASE 5 e sob demanda |
| `check-arch.sh` | o código respeita as regras? | árvore de trabalho | dentro da DoD |
| `medir-aderencia.sh` | o protocolo foi seguido? | histórico do git | quando o time quiser olhar |

Um harness perfeitamente instalado e integralmente ignorado passa no
verificador com nota máxima — é essa lacuna que o medidor fecha.

Ele **não entra na DoD e não é um gate**: sai 0 mesmo com todas as medidas
em alerta. "Aderência caiu de 80% para 60%" não tem conserto no harness,
tem conversa com o time; atrás de um exit 1 isso viraria "alguém quebrou
alguma coisa", e a reação previsível a um vermelho que ninguém causou é
desligar o sensor. Exit 2 fica reservado para "não consegui medir" (sem
git, sem commit, sem fonte de trabalho).

O verificador cobre o medidor pelas checagens de LF e bit de execução, e
nunca o executa: repositório recém-gerado não tem histórico, e cobrar
aderência dele seria reprovar o usuário por algo que ele ainda não teve
chance de fazer.

### O gate é graduado, e o registro é editável de propósito

`.harness/gate-rules.json` tem três níveis:

| Nível | Efeito | Para quê |
|---|---|---|
| `permitir` | exit 0, **precedência sobre `bloquear`** | exceção declarada, ancorada em `^...$` |
| `bloquear` | exit 2, com WHAT/WHY/FIX no stderr | irreversível |
| `avisar` | exit 0 + `risco: medio` no trace | passa, mas não some |

O nível `permitir` existe por causa do **falso bloqueio**, que é o erro mais
caro dos dois: ele ensina a driblar. Um gate que barra `rm -rf node_modules`
treina a pessoa a contornar, e o contorno aprendido num caso obviamente
errado depois passa por cima dos bloqueios certos.

As exceções são **ancoradas** (`^...$`) e proíbem `;`, `|`, `&`, `$` e crase
no caminho. Sem isso, `rm -rf node_modules && rm -rf /` casaria a exceção
pelo começo e o gate liberaria a segunda metade junto — ancorar é o que
separa exceção de buraco.

O nível `avisar` cobre o **falso verde**: comandos que não merecem bloqueio e
não deveriam sumir em silêncio. O caso que motivou o nível é
`git commit --no-verify` — o agente desligando o pre-commit do próprio
harness. Quem grava é o `registrar-sessao.sh`, nunca o gate: **o gate não
escreve em disco**, porque uma escrita que falha o mata, e gate morto devolve
exit 1, que em `PreToolUse` significa "erro não-bloqueante" — o comando
destrutivo passa. O gate falha ABERTO.

**"Mas o agente pode editar o registro e se liberar."** Pode — e já podia
editar o script, com o mesmo shell. Tirar os padrões de dentro do código não
cria a capacidade. A defesa é a regra `G01`, que **executa** o gate a cada
rodada da DoD e exige exit 2; a `G02` faz o par exigindo exit 0 num comando
seguro, porque a G01 sozinha é satisfeita por um gate que bloqueia tudo.
Impedir a edição antes que ela ocorra não era opção: o Cursor
([hooks](https://cursor.com/docs/hooks.md)) não tem evento de pré-edição de
arquivo, e a regra 10 não admite enforcement que só vale num agente. Onde a
prevenção não é portátil, detecta-se.

Se o registro sumir ou ficar ilegível, o gate cai numa lista embutida no
script. Gate sem registro não pode virar gate sem proteção.

### O manifesto (`.claude/harness.json`)

É o único arquivo que a skill sobrescreve sem perguntar, porque é dela: um
registro do que ela gerou, com a versão da skill, a data, o ecossistema
detectado, a DoD e a lista de arquivos. Existe para responder três
perguntas que hoje não têm resposta no repositório:

- **Este harness é de qual versão?** Sem isso, uma segunda execução não
  distingue o que a skill escreveu do que o usuário escreveu depois, e todo
  arquivo vira conflito da FASE 3.
- **O que exatamente foi gerado?** Remover o harness ou auditá-lo hoje exige
  caçar arquivo por arquivo.
- **O que o usuário já recusou?** Repropor na sessão seguinte um item que
  ele recusou é a skill ignorando uma decisão que já foi tomada.

O campo `recusados` é preenchido com os itens recusados ou adiados do Plano
de Remediação — os mesmos que a FASE 4 manda registrar no `SESSION_STATE.md`.

### Os três agentes-alvo

O harness precisa funcionar em **Claude Code, Devin CLI e Cursor**. Os
scripts de hook são os mesmos nos três (`.claude/hooks/*.sh`); o que muda é
o arquivo que os registra e o nome do evento:

| Agente | Registro | Comando de shell | Edição de arquivo |
|---|---|---|---|
| Claude Code | `.claude/settings.json` | `PreToolUse` + matcher `Bash` | `PostToolUse` + matcher `Edit\|Write\|MultiEdit` |
| Devin CLI | `.devin/hooks.v1.json` | `PreToolUse` + matcher `exec` | `PostToolUse` + matcher `edit` |
| Cursor | `.cursor/hooks.json` | `beforeShellExecution` (`failClosed`) | `afterFileEdit` |

Exit 2 significa "bloquear" nos três. O Cursor manda `command`/`file_path`
no topo do JSON e os outros dois em `tool_input` — os scripts leem os dois
formatos. `failClosed` existe porque o padrão do Cursor para hook que falha
é **prosseguir**: sem essa chave, um gate quebrado libera o comando.

**Limite conhecido:** a skill não gera skills nem subagentes para o Devin
CLI. A documentação dele descreve `.devin/` com hooks, skills e agents, mas
não publica os paths; inventar um geraria arquivo que nenhuma ferramenta lê.
`executar-grupo` e `propor-regra-arch` valem hoje só para o Claude Code — a
camada de instrução (`AGENTS.md`) e o `check-arch.sh`, que é shell, esses os
três leem e executam. É por isso que a cobertura de regra arquitetural mora
no runner e não no agente: o runner é portátil, o agente é um incremento.
Registrar isso na FASE 4 quando o usuário usar Devin.

## Camada de enforcement (condicional)

| Item | Destino | Condição |
|---|---|---|
| ci-workflow.yml | `.github/workflows/harness-dod.yml` | se NÃO existir CI **e a DoD tiver comandos reais** |
| `README.md` | `/README.md` | se não existir |
| `.mcp.json` | `/.mcp.json` (raiz) | se MCP detectado em outro path mas não na raiz |
| `editorconfig-base` | `/.editorconfig` | se não existir .editorconfig (qualquer linguagem) |
| `editorconfig-dotnet` | `/.editorconfig` (mesclar sobre o base) | se a linguagem tem template específico (hoje só .NET/C#) |
| `.env` no `.gitignore` | `/.gitignore` (append) | se `.gitignore` não cobrir `.env` |
| `LICENSE` | `/LICENSE` | se não existir (oferecer ao usuário na FASE 4) |

**Lockfile não está aqui de propósito.** Gerar um exige resolver
dependências pela rede (`npm install`, `pip freeze`, `cargo generate-lockfile`),
o que a skill não pode fazer em nome do usuário: a resolução escolhe versões
que passam a valer para o time inteiro. Virou item do grupo B do
[catálogo de remediações](remediacoes.md) — recomendado com o comando exato,
aplicado só se o usuário aceitar.
