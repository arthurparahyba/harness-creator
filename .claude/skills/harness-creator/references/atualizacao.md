# Atualização de um harness já existente

Catálogo consultado quando o repositório tem `.claude/harness.json`. Não é
uma fase: é a variação que as FASES 1 e 3 aplicam quando descobrem que a
skill já passou por ali.

---

## Por que gerar de novo não serve

Um repositório com manifesto já tomou decisões. Rodar o fluxo do zero em
cima dele produz três danos concretos:

1. **Repropõe o que o usuário recusou.** O campo `recusados` existe
   justamente porque repropor uma decisão tomada é a skill ignorando o
   usuário. Numa geração do zero esse campo nunca é lido.
2. **Pede aprovação de arquivo que já está certo.** A FASE 4 apresenta
   vinte artefatos; numa atualização, dezoito costumam estar idênticos ao
   que a skill geraria hoje. O usuário revisa vinte para decidir sobre dois.
3. **Trata edição do usuário como conflito genérico.** Sem o manifesto,
   a FASE 3 não distingue "arquivo que a skill escreveu" de "arquivo que o
   usuário escreveu", e a regra de não sobrescrever congela até o que
   deveria ser atualizado.

O resultado prático de não ter esse caminho é o harness envelhecer no
repositório: atualizar custa uma execução inteira, então ninguém atualiza,
e os defeitos corrigidos na skill continuam vivos em todo repo que já a
usou.

## O que ler no manifesto, antes de qualquer outra coisa

```
python3 -c "import json;print(json.load(open('.claude/harness.json'))['harness'])"
```

| Campo | Para que serve na atualização |
|---|---|
| `versao` | Contra a `metadata.version` do SKILL.md: define o que mudou entre as duas |
| `gerado_em` | Idade do harness; ajuda a explicar divergências ao usuário |
| `ecossistema` | Se mudou, a stack do repo mudou — a atualização vira geração normal |
| `dod` | A DoD anterior. Se a do repo hoje é outra, alguém a editou à mão |
| `arquivos` | Tudo que a skill escreveu. O que não está aqui é do usuário |
| `recusados` | **Não repropor.** Decisão já tomada |

Se o manifesto não parseia ou lista arquivo que não existe mais, ele está
mentindo sobre o repositório: trate como geração normal e diga isso ao
usuário — o manifesto é substituído ao fim, então o estado se corrige.

## Classificação de cada arquivo

O manifesto guarda os caminhos, não o conteúdo, então não há como saber de
cor se um arquivo listado continua como a skill o deixou. Compare com o
template preenchido para hoje — é a única evidência disponível:

| Situação | O que fazer |
|---|---|
| Listado em `arquivos`, idêntico ao que a skill geraria hoje | Nada. Não entra no plano de aprovação |
| Listado em `arquivos`, e a skill de hoje geraria diferente | Atualizar. Mostrar o diff na FASE 4 |
| Listado em `arquivos`, mas divergente também do template antigo | O usuário editou. **Não sobrescrever**: mostrar o diff e perguntar |
| Não listado em `arquivos` | É do usuário. Regra normal da [FASE 3](03-resolucao-conflitos.md) |
| Listado em `arquivos` e ausente do disco | Foi removido. Perguntar antes de recriar — remoção pode ter sido deliberada |

A terceira linha é a que exige cuidado. Um `AGENTS.md` que a skill gerou e o
time depois enriqueceu com convenções reais é mais valioso que o template:
sobrescrevê-lo destrói trabalho humano para instalar texto genérico.

## Descoberta reduzida

A FASE 1 completa não se repete. Reinvestigue apenas o que muda com o
tempo e o que a skill passou a saber ler desde a versão registrada:

- Comandos de teste, lint e tipos (o manifesto guarda a DoD antiga)
- Ecossistema e versões de runtime
- Itens de descoberta que **não existiam** na versão do manifesto — são
  exatamente os que nunca foram investigados neste repo
- Arquivos de hook dos três agentes-alvo: o repo pode ter ganho um agente
  novo desde a geração

O resto do Relatório de Descoberta pode ser transcrito do manifesto,
declarando a fonte como tal.

## Apresentação na FASE 4

A aprovação continua sendo a única do fluxo, e continua sendo antes de
gravar. O que muda é o conteúdo:

```
ATUALIZAÇÃO DE HARNESS
Instalado: versão 2.2, gerado em 2026-05-14, ecossistema Python
Skill atual: versão 2.4

Atualiza (3)      arquivos que a skill gerou e hoje geraria diferente
Preserva (14)     idênticos ou editados por você — nenhum toque
Novo (2)          artefatos que a versão 2.2 ainda não gerava
Não repropõe (2)  itens recusados na geração anterior
```

Um diff por arquivo atualizado, não o conteúdo integral: o usuário já
aprovou esses arquivos uma vez, e o que ele precisa julgar agora é a
mudança.

## Ao final

O manifesto é reescrito com a versão nova, a data nova e a lista completa
do que existe agora — incluindo os arquivos preservados, que continuam
sendo da skill. Os `recusados` da execução anterior são **mantidos** e
somados aos novos: uma recusa não expira porque a skill mudou de versão.

A verificação da [FASE 5](05-verificacao-pos-geracao.md) roda igual. Um
harness atualizado pela metade é pior que um desatualizado inteiro, e o
único jeito de saber em qual dos dois o repositório está é executando os
checks.
