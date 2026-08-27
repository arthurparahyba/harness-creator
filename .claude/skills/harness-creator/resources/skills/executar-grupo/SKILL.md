---
name: executar-grupo
description: >
  Executa um grupo do plano de trabalho de ponta a ponta seguindo o
  protocolo do AGENTS.md: init, verificação, review, commit e handoff.
  Use sempre que for implementar o próximo grupo desmarcado, retomar um
  grupo em andamento após reset de contexto, ou fechar um checkpoint —
  mesmo que o pedido do usuário não use a palavra "grupo".
license: MIT
---

# Executar grupo

Procedimento sob demanda para fechar UM grupo do plano de trabalho ativo.
As regras permanentes (WIP=1, MUST NOT, DoD) vivem no `AGENTS.md` da raiz;
este arquivo é só a sequência de execução.

## Passos

1. **Abrir sessão**: se ainda não fez nesta conversa, rode `./init.sh`.
2. **Ler estado**: leia `SESSION_STATE.md`. Se houver grupo em andamento
   não commitado, é ele que você termina — antes de qualquer pedido novo.
3. **Escolher o grupo**: primeiro grupo desmarcado na fonte de trabalho
   ativa — a que o `SESSION_STATE.md` declara em "Change/plano ativo".
   As fontes possíveis são `openspec/changes/<change>/tasks.md` e o
   `TASKS.md` da raiz; havendo grupo desmarcado nas duas e nenhuma
   declarada, PERGUNTE qual seguir em vez de decidir por ordem de arquivo.

   Se o pedido do usuário não estiver coberto por nenhum grupo, PARE e
   proponha antes de editar qualquer arquivo. **Como propor depende da
   fonte escolhida**: em OpenSpec, use a skill `openspec-propose` — nunca
   edite arquivos de `openspec/` à mão, porque são artefatos gerenciados
   pela ferramenta. No `TASKS.md`, acrescente o grupo e confirme com o usuário
   antes de executá-lo. Com as duas disponíveis, recomende uma (contrato,
   comportamento observável ou migração → OpenSpec; o resto → `TASKS.md`),
   deixe a escolha com o usuário e registre-a no `SESSION_STATE.md`.
4. **Implementar**: só as tasks deste grupo. Problema fora do escopo vira
   pendência no `SESSION_STATE.md`, não conserto agora.
5. **Verificar**: rode a linha `Verificação:` do grupo e depois a
   Definition of Done completa (comando `/dod`). Saída de comando é a
   evidência; "parece funcionar" não é.
6. **Commitar**: um commit por grupo — `checkpoint: <nome do grupo>`.
   Nunca commite com verificação falhando.
7. **Handoff**: atualize `SESSION_STATE.md` (hash do commit, testes X/Y,
   bloqueios, próxima ação).
8. **PARAR**: informe "Grupo N concluído. Contexto pode ser reiniciado."
   Não avance para o próximo grupo automaticamente.

## Falhas comuns

| Situação | Ação correta |
|----------|--------------|
| Verificação do grupo falha | Corrigir dentro do grupo; não commitar |
| Falha pré-existente no baseline | Registrar em SESSION_STATE.md; não consertar (fora de escopo) |
| Grupo maior que 5 tasks | Propor divisão ao humano antes de executar |
| Pedido novo no meio do grupo | Registrar como pendência; terminar o grupo atual (WIP=1) |
