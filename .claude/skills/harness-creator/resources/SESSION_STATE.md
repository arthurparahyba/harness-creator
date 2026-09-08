# SESSION_STATE.md
<!-- Handoff entre sessões. Atualizado pelo agente ao FIM de toda sessão.
     Guarda só o ESTADO atual — a JORNADA (o que foi feito e por quê) mora no
     memlog da funcionalidade (tasks/<funcionalidade>/memlog.md), apendada ao
     longo do trabalho. Se a sessão terminou em fronteira limpa (grupo
     commitado), a maioria dos campos fica trivial — esse é o estado ideal. -->

- Commit verificado: <hash> 
- Testes: <X/Y passando> (<falhas pré-existentes, se houver, e onde>)
- Change/plano ativo: <a ÚNICA fonte em uso agora: nome da change OpenSpec
  ou TASKS.md; se as duas existem, dizer quem escolheu e por quê>
- Em andamento: <Grupo N — % e o que falta, OU "nada — fronteira limpa">
- Não commitado: <arquivos com mudança parcial, OU "nada">
- Bloqueios / pendências fora de escopo:
  - <item descoberto mas não tratado (WIP=1)>
- Próxima ação: <primeira coisa que a próxima sessão deve fazer>
