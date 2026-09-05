# Planos de trabalho

Um plano por funcionalidade, cada um na sua pasta:

    tasks/<funcionalidade>/tasks.md

Mesma forma do OpenSpec (`openspec/changes/<change>/tasks.md`), de propósito:
as duas fontes ficam simétricas e o agente resolve as duas do mesmo jeito.
Qual está ATIVO é o `SESSION_STATE.md` que declara, no campo "Change/plano
ativo" — nunca a ordem em que os arquivos aparecem no disco.

Uma pasta por FUNCIONALIDADE, não por grupo. Os grupos declaram dependência
entre si; ler a sequência inteira de uma vez é o que torna a dependência
visível. Espalhar um grupo por arquivo perderia isso sem ganhar nada.

Este `README.md` é documentação: nenhuma ferramenta o lê como plano. Plano é
só o que está em `tasks/<funcionalidade>/tasks.md`.

## Formato

O mesmo definido no `AGENTS.md`, seção "Estrutura do plano de trabalho":

```
## Grupo 1 - <objetivo coeso, ex: Modelo e persistência de usuário>
- [ ] 1.1 <task atômica>
- [ ] 1.2 <task atômica>
- [ ] 1.3 <testes do que foi feito no grupo>
Verificação: <comando executável que valida o grupo inteiro>

## Grupo 2 - <objetivo> (depende: Grupo 1)
- [ ] 2.1 <task>
- [ ] 2.2 <task>
Verificação: <comando>
```

Ao terminar a funcionalidade, a pasta fica onde está: ela é o histórico do
que foi decidido e verificado, e é o que a próxima sessão lê para entender
por que o código está como está.
