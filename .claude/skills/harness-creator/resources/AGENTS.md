# AGENTS.md

## Projeto
<2-3 linhas: o que é a aplicação, stack com versões exatas>
<Preencher via descoberta — nunca de memória. Fontes: manifestos, CI>

## Fontes de trabalho
Existe no MÁXIMO UM plano ativo por vez (WIP=1), e o `SESSION_STATE.md`
declara qual, no campo "Change/plano ativo". Enquanto ele estiver ativo é a
única fonte: não abra grupo na outra. As fontes possíveis são:
- `openspec/changes/<change-ativa>/tasks.md`
- `tasks/<funcionalidade-ativa>/tasks.md`

Uma pasta por funcionalidade nas duas, e por isso a mesma forma: o plano
nasce, vive e fica na pasta dela. Repositório com harness antigo pode ter o
plano num `TASKS.md` único na raiz — continua válido como fonte; o próximo
plano é que vai para `tasks/`.

Se o `SESSION_STATE.md` não declarar nenhum e as duas tiverem grupo
desmarcado, PERGUNTE qual seguir — ordem de arquivo não é decisão.

<como-propor-mudanca-de-plano>
Nunca invente tarefas fora da fonte de trabalho ativa.

## Início de nova funcionalidade/tarefa (OBRIGATÓRIO, antes de qualquer ação)
1. Se ainda não fez nesta conversa: rode `./init.sh` — instala deps, roda
   testes (baseline), mostra estado
2. Leia `SESSION_STATE.md` — se houver uma funcionalidade em
   implementação com grupo em andamento (não commitado), termine esse
   grupo antes de qualquer outra coisa, inclusive antes do pedido novo
3. O pedido está coberto pela fonte de trabalho ativa (grupo já
   planejado)? Se NÃO estiver, pare — não implemente direto. **Estude
   antes de propor**: cheque `knowledge/` primeiro (se já está lá e a Prova
   passa, use); senão investigue onde a mudança encosta, o que já existe que
   faça parte disso, e o que o pedido não diz, e registre em `knowledge/` o
   que for durável. Apresente o
   achado junto da proposta — plano sem estudo é chute com formatação de
   plano, e o custo dele aparece três grupos depois.
   Proponha antes de editar qualquer arquivo, do jeito descrito em "Fontes de
   trabalho".
4. Antes de implementar qualquer coisa nova (primeiro grupo de uma
   funcionalidade nova), crie e mude para uma feature branch atualizada a
   partir de `<branch-base>`:
   ```
   git checkout <branch-base>
   git remote | grep -q . && git pull        # repo sem remoto: pular
   git checkout -b <prefixo-de-branch><nome-da-funcionalidade>
   ```
   Não é necessário criar branch nova para continuar um grupo já em
   andamento na branch atual (ver passo 2).
5. Identifique o próximo grupo desmarcado na fonte de trabalho ativa

## Estrutura do plano de trabalho
Cada change/funcionalidade tem seu próprio `tasks.md`, na pasta dela —
`tasks/<funcionalidade>/tasks.md` ou `openspec/changes/<change>/tasks.md`.
Independente de onde vive, o plano segue este formato:
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
- MUST NOT: <restrição 1 — derivada de convenção real do repo>
- MUST NOT: <restrição 2>
- MUST NOT: tocar em arquivos fora do escopo do grupo atual

## Definition of Done
Concluído = TODOS passam:
```
<comandos reais do repo, encadeados com &&, priorizando o que o CI exige>
<ex Python: pytest && ruff check . && mypy --strict src/>
<ex .NET: dotnet build <sln> -c Release && dotnet test <sln> --no-build && dotnet format <sln> --verify-no-changes>
<ex Java: mvn verify && ./gradlew spotlessCheck>
<ex JS/TS: npm test && npm run lint && npx tsc --noEmit>
```
Saída de comando é evidência; "parece funcionar" não é.

## Ferramentas deste harness
<ferramentas-do-harness>

## Conhecimento do repositório
Conhecimento caro de descobrir (uma solução da empresa, um componente
não-óbvio) mora em `knowledge/` — não se re-investiga a cada sessão. Antes de
investigar algo, cheque lá; se faltar ou a Prova estiver velha, investigue e
registre. Método, formato e canais de investigação: `knowledge/README.md`.

## Commits
- Um commit por grupo concluído: `checkpoint: <nome do grupo>`
- Nunca commitar com verificação falhando.
<politica-de-entrega>

## Ao concluir cada grupo (OBRIGATÓRIO)
Não existe um evento de "fim de sessão" que o agente consiga detectar —
por isso todo commit de grupo é tratado como um possível fim de sessão:
1. Atualize `SESSION_STATE.md`: commit hash, testes (X/Y), bloqueios,
   próxima ação — só o ESTADO. A jornada (o que foi feito e por quê) já está no
   memlog da funcionalidade (`tasks/<funcionalidade>/memlog.md`), apendada ao
   longo do trabalho; não a repita aqui.
2. Se o grupo ficou incompleto (nada commitado ainda), registre o
   estado parcial em SESSION_STATE.md mesmo assim
3. Após o commit do grupo: PARE e informe "Grupo N concluído.
   Contexto pode ser reiniciado." Não prossiga automaticamente para o
   próximo grupo.
