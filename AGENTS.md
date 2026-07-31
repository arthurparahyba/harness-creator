# AGENTS.md

## Projeto
Repositório da skill `harness-creator`: gera o harness de outros repositórios
para agentes de IA. O produto é `.claude/skills/harness-creator/` (SKILL.md,
references/, resources/). Python 3.11+ só para os sensores (pytest, ruff,
mypy strict). Fonte: pyproject.toml, .claude/skills/harness-creator/SKILL.md.


## Fontes de trabalho (nesta ordem de precedência)
O plano de trabalho vive em UM destes lugares — use o primeiro que existir:
1. `openspec/changes/<change-ativa>/tasks.md`
2. `TASKS.md` na raiz do repositório

Para criar ou modificar o plano, acrescente o grupo ao `TASKS.md` no
formato descrito abaixo e confirme com o usuário antes de executá-lo.
Nunca invente tarefas fora da fonte de trabalho ativa.

## Início de nova funcionalidade/tarefa (OBRIGATÓRIO, antes de qualquer ação)
1. Se ainda não fez nesta conversa: rode `./init.sh` — instala deps, roda
   testes (baseline), mostra estado
2. Leia `SESSION_STATE.md` — se houver uma funcionalidade em
   implementação com grupo em andamento (não commitado), termine esse
   grupo antes de qualquer outra coisa, inclusive antes do pedido novo
3. O pedido está coberto pela fonte de trabalho ativa (grupo já
   planejado)? Se NÃO estiver, pare — não implemente direto. Proponha
   antes de editar qualquer arquivo, do jeito descrito em "Fontes de
   trabalho".
4. Antes de implementar qualquer coisa nova (primeiro grupo de uma
   funcionalidade nova), crie e mude para uma feature branch atualizada a
   partir de `main`:
   ```
   git checkout main
   git remote | grep -q . && git pull        # repo sem remoto: pular
   git checkout -b feature/<nome-da-funcionalidade>
   ```
   Não é necessário criar branch nova para continuar um grupo já em
   andamento na branch atual (ver passo 2).
5. Identifique o próximo grupo desmarcado na fonte de trabalho ativa

## Estrutura do plano de trabalho
Cada change/funcionalidade tem seu próprio `tasks.md`. Independente de
onde vive, o plano segue este formato:
- Um grupo é um checkpoint DENTRO da funcionalidade em implementação —
  não a funcionalidade inteira. Tasks organizadas em GRUPOS coesos de
  2-5 tasks (`## Grupo N - <objetivo>`), todos pertencentes à mesma
  funcionalidade/change.
- Cada grupo termina com linha `Verificação:` contendo comando
  executável que valida o grupo inteiro
- Dependências declaradas ENTRE grupos
- Se o plano existente não estiver em grupos, proponha o agrupamento
  ao humano ANTES de executar

## Regras de trabalho
- MUST NOT: implementar um pedido do usuário direto no código antes de
  confirmar que ele está coberto pela fonte de trabalho ativa (ver
  "Início de nova funcionalidade/tarefa"). Vale mesmo se o pedido vier
  em linguagem natural, no meio da conversa, e parecer pequeno.
- WIP=1: um grupo por vez. Nada novo antes de o grupo atual estar
  verificado e commitado.
- Problema fora do escopo: registre em SESSION_STATE.md como
  pendência, NÃO conserte agora.
- MUST NOT: parafrasear texto de protocolo em `resources/` — templates são transcritos VERBATIM
- MUST NOT: gravar qualquer arquivo com CRLF — quebra o shebang dos hooks e o gate falha aberto
- MUST NOT: tocar em arquivos fora do escopo do grupo atual

## Definition of Done
Concluído = TODOS passam:
```
pytest -q && ruff check . && mypy && bash .claude/check-arch.sh
```
Saída de comando é evidência; "parece funcionar" não é.

## Ferramentas deste harness
- Para fechar um grupo do plano: skill `executar-grupo` (passo a passo).
- Para verificar a Definition of Done: comando `/dod`.
- Hooks de agent loop ativos: gate de comandos destrutivos, formatação
  automática a cada edição, e registro de sessão.
- Para conferir se o protocolo vem sendo seguido:
  `sh .claude/medir-aderencia.sh` (diagnóstico, não gate).

## Commits
- Um commit por grupo concluído: `checkpoint: <nome do grupo>`
- Nunca commitar com verificação falhando.
- Política de entrega: push da feature branch, CI verde, e merge direto
  `--no-ff` na `main`. Este repositório não usa PR (fonte: `git log
  --merges`, ausência de PULL_REQUEST_TEMPLATE e de CODEOWNERS).

## Ao concluir cada grupo (OBRIGATÓRIO)
Não existe um evento de "fim de sessão" que o agente consiga detectar —
por isso todo commit de grupo é tratado como um possível fim de sessão:
1. Atualize `SESSION_STATE.md`: commit hash, testes (X/Y), bloqueios,
   próxima ação
2. Se o grupo ficou incompleto (nada commitado ainda), registre o
   estado parcial em SESSION_STATE.md mesmo assim
3. Após o commit do grupo: PARE e informe "Grupo N concluído.
   Contexto pode ser reiniciado." Não prossiga automaticamente para o
   próximo grupo.
