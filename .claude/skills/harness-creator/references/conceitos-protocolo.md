# Conceitos do protocolo

Glossário para responder dúvidas do usuário sobre os conceitos do
harness gerado.

---

- **Grupo como unidade de checkpoint**: tasks agrupadas em 2-5 unidades
  coesas; o grupo (não a task) é a fronteira de verificação + commit +
  possível reset de sessão. Alinha escopo, verificação e fronteira de
  sessão numa única fronteira física.
- **WIP=1**: um grupo por vez; nada novo antes de o atual estar
  verificado e commitado. Evita overreach e código meio-feito.
- **"PARE após o commit do grupo"**: devolve o controle ao humano/
  orquestrador para reset deliberado de contexto em ponto limpo,
  evitando context anxiety e fronteiras de sessão em lugar ruim.
- **Degradação graciosa**: o harness não depende do OpenSpec. Fonte de
  trabalho com precedência (tasks.md da change ativa → TASKS.md raiz);
  removido o OpenSpec, tudo continua operando.
- **DoD como evidência**: "concluído" = comandos passando, nunca
  julgamento subjetivo do agente.
- **Duas camadas de harness**: instrução (AGENTS.md, init.sh) diz o que
  fazer; enforcement (hooks, pre-commit) garante que acontece. Sem
  enforcement, a DoD é só um texto que o agente pode ignorar.
- **Hooks multi-plataforma**: os mesmos scripts `.claude/hooks/*.sh`
  funcionam nos três agentes-alvo — Claude Code (`.claude/settings.json`,
  matchers `Bash`/`Edit`), Devin CLI (`.devin/hooks.v1.json`, matchers
  `exec`/`edit`) e Cursor (`.cursor/hooks.json`, eventos
  `beforeShellExecution`/`afterFileEdit`) — porque exit 2 significa
  "bloquear" nos três. O que muda é o arquivo de registro, o nome do
  evento e o formato do JSON de entrada (o Cursor manda `command` no topo,
  os outros dois dentro de `tool_input`); os scripts leem os dois.
  Nenhum deles depende de Python instalado: a extração do JSON tem
  fallback em awk, senão o gate bloquearia todo comando num repo Go ou
  .NET sem Python.
