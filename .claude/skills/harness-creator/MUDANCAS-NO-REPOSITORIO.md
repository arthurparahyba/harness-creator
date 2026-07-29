# O que esta skill faz no seu repositório

Guia objetivo de **toda** alteração que a `harness-creator` cria, modifica
ou propõe — e por que cada uma existe.

Em uma frase: ela transforma um repositório "aberto", onde o agente de IA
explora no escuro e age sem limites, num repositório onde ele tem contexto,
fronteiras e como verificar o próprio trabalho.

---

## Conteúdo

- As duas coisas que ela faz
- O que ela CRIA
- O que ela MODIFICA (sem sobrescrever)
- O que ela PROPÕE (você decide item a item)
- O que ela NUNCA faz
- O que muda na prática
- O que você precisa fazer

---

## As duas coisas que ela faz

| | O que é | Quando acontece |
|---|---|---|
| **Cria** | Arquivos que só existem para o harness. Não afetam quem não usa agente. | Depois de uma aprovação única |
| **Propõe** | Mudanças no projeto — instalar dependência, escrever teste, ajustar config. | Você aceita ou recusa item a item |

A fronteira é simples: **o artefato é só do harness, ou muda o contrato do
projeto?** Criar um hook não muda nada para quem clona o repo e roda o
build. Adicionar `pytest` ao `pyproject.toml` muda o que o time instala, o
que o CI roda e o que "quebrado" significa. O primeiro ela faz; o segundo
ela propõe.

Nada é declarado pronto sem execução: no fim ela valida cada arquivo que
gravou e roda o gate hook de verdade, para o resultado ser evidência e não
afirmação.

Este documento explica **por que** cada peça existe. A lista exata de
arquivos, destinos e condições de geração é uma só, em
[references/arquivos-gerados.md](references/arquivos-gerados.md) — se as
duas discordarem, vale a de lá.

---

## O que ela CRIA

### Camada 1 — contexto e protocolo (o agente sabe o que fazer)

**`AGENTS.md`** na raiz. O arquivo que todo agente lê primeiro. Contém o
que é o projeto, a stack com versões, os comandos reais de teste e build,
e o protocolo de trabalho. Sem ele, o agente gasta os primeiros minutos de
toda sessão explorando o repo para descobrir o que você já sabe.

**`AGENTS.md` no diretório de código** (ex.: `src/AGENTS.md`). As
restrições que valem só ali — padrão de acesso a dados, onde ficam os
testes, o que nunca editar. Fica perto do código de propósito: regra que
vale para um diretório não precisa ser carregada em toda pergunta que você
faz. O protocolo permanece só na raiz e nunca é duplicado aqui.

**`CLAUDE.md`**, ao lado de cada `AGENTS.md` gerado — na raiz e no
diretório de código. Uma linha: `@AGENTS.md`. Existe porque o Claude Code
carrega `CLAUDE.md` e **não** carrega `AGENTS.md`, em nenhum dos dois
níveis. Sem essa ponte o protocolo é gravado no repositório e nunca entra
na sessão — o modo mais silencioso de o harness falhar, porque nada quebra:
o agente apenas não conhece as regras. O `@` é import, não cópia, então o
conteúdo continua num lugar só e os agentes que leem `AGENTS.md` direto
(Devin, Codex) não são afetados.

**`.claude/skills/executar-grupo/SKILL.md`**. O procedimento de fechar uma
unidade de trabalho — rodar o init, pegar a próxima tarefa, verificar,
revisar, commitar, parar. É conhecimento sob demanda: só carrega quando o
agente vai de fato executar, em vez de ocupar contexto o tempo todo.

**`init.sh`**. O ritual de abertura de sessão: instala dependências, roda
os testes para estabelecer o estado real, e mostra onde o trabalho parou.
O objetivo é o agente ter estado executável em menos de três minutos, sem
explorar nada.

**`SESSION_STATE.md`**. A memória entre sessões: último commit verificado,
testes passando, o que ficou pendente, qual a próxima ação. É o que evita
o agente recomeçar do zero quando o contexto é reiniciado.

**`TASKS.md`** (ou `openspec/config.yaml`, se você usa o
[OpenSpec](https://github.com/Fission-AI/OpenSpec) — CLI
`npx @fission-ai/openspec`). O plano
de trabalho em grupos de 2 a 5 tarefas, cada grupo terminando com um
comando que o valida. O grupo — não a tarefa — é a fronteira de
verificação, de commit e de reinício de sessão.

O harness não depende do OpenSpec: a fonte de trabalho tem precedência
(`openspec/changes/<change>/tasks.md` → `TASKS.md` na raiz) e a skill
`executar-grupo` resolve isso na hora de executar. Com OpenSpec, ela
propõe pelo `/opsx:propose` e nunca edita `openspec/` à mão; sem, ela
acrescenta o grupo ao `TASKS.md`. Se você remover o OpenSpec do
repositório, tudo continua funcionando.

### Camada 2 — enforcement (o agente é obrigado a fazer)

Sem esta camada, tudo acima é texto que o agente pode ignorar.

**`.claude/hooks/gate-destructive.sh`** + `.claude/settings.json`. Um hook
que roda **antes** de todo comando de shell e bloqueia o que é
irreversível: `rm -rf`, `git push --force`, `git reset --hard`,
`DROP TABLE`, e também publicação de artefato (`npm publish`,
`mvn deploy`, `dotnet nuget push`, `cargo publish`) e `terraform destroy`.
O comando não chega a executar. Comandos do dia a dia — `npm test`,
`mvn test`, `go test` — passam sem atrito, o que importa: gate que
atrapalha é gate que o time desliga na primeira semana.

**`.claude/hooks/format-on-edit.sh`**. Roda o formatter do projeto a cada
arquivo editado. Diff limpo, sem ruído de formatação escondendo a mudança
real na hora do review.

**`.devin/hooks.v1.json`** e **`.cursor/hooks.json`**. Os mesmos dois hooks
registrados para o Devin CLI e para o Cursor. Os scripts são idênticos nos
três agentes; mudam só o arquivo de registro e o nome do evento. É o que
faz o gate valer em qualquer um deles — registrar num só deixa os outros
dois trabalhando sem proteção, e nada avisa.

**`.claude/commands/dod.md`**. O comando `/dod`, que roda a Definition of
Done inteira. "Concluído" passa a significar "estes comandos passaram", e
não o julgamento do agente.

**`.pre-commit-config.yaml`**. Lint e build rodando antes de o commit
existir — o feedback mais barato e mais cedo possível.

**`.github/workflows/harness-dod.yml`**. A DoD rodando no CI, que é o
único enforcement que ninguém contorna (`--no-verify` não alcança). São
os mesmos comandos do `AGENTS.md`, **um por step** — assim o step vermelho
já aponta qual sensor falhou, em vez de você ler um log inteiro. E inclui
um passo que confere se os hooks continuam no lugar e ainda bloqueiam:
remover um hook não quebra build nenhum, então sem essa checagem o harness
seria desfeito em silêncio.

### Higiene

`.editorconfig` se não existir, o lockfile de dependências no nome
convencional do ecossistema (nome inventado não é instalado por ferramenta
nenhuma), `.mcp.json` na raiz se houver MCP em outro caminho, e um
`README.md` mínimo se o repositório não tiver nenhum.

---

## O que ela MODIFICA (sem sobrescrever)

**`.gitignore`**: acrescenta `.env` e `.env.*` ao final, se ainda não
estiverem cobertos. Só append — o conteúdo existente nunca é tocado.

**`AGENTS.md`/`CLAUDE.md` que já existe**: o conteúdo descritivo útil é
preservado; o protocolo do template prevalece apenas nas seções que se
sobrepõem, e o diff é mostrado antes. Se o `CLAUDE.md` existe mas não
alcança o `AGENTS.md`, ela propõe acrescentar a linha `@AGENTS.md` no
topo — nunca sobrescreve o que você escreveu.

**`.claude/settings.json` com hooks já configurados**: os hooks novos são
mesclados com os seus, nunca substituídos.

**Configuração MCP com credencial literal**: o valor é trocado por
`${VARIAVEL}` antes de qualquer cópia, com a lista de variáveis a exportar
e o aviso de que o segredo original precisa ser rotacionado.

---

## O que ela PROPÕE (você decide item a item)

Nem toda lacuna se resolve com arquivo de harness. Num repositório sem
testes, o agente não tem como verificar o que ele mesmo fez — e nenhum
`AGENTS.md`, por melhor que seja, substitui isso. Esses casos viram um
**Plano de Remediação**, com o comando exato e o que a aceitação muda no
repositório.

| Proposta | Por que | O que muda |
|---|---|---|
| **Instalar sensores** (test runner, linter, type checker, formatter) | Sem eles a DoD fica vazia e o `/dod` não tem o que executar | Novas dependências de desenvolvimento |
| **Escrever os primeiros testes** | Runner com zero testes dá ao agente um verde que ele não mereceu | Um diretório de testes novo |
| **Script de teste na raiz** (monorepo) | Sem ponto de entrada único, não há como verificar o repo inteiro | Uma linha no manifesto da raiz |
| **`.env.example`** | Documenta as chaves sem expor valores | Um arquivo novo |
| **Migrar `.cursorrules` legado** | Regras antigas sem escopo consomem contexto em toda pergunta | Arquivos de regra reorganizados |
| **Rotacionar credencial exposta** | Segredo commitado continua no histórico do git | Ação sua, fora do repositório |
| **`LICENSE`** | Decisão jurídica, não técnica | Você escolhe qual |
| **Passo da DoD num CI que já existe** | A skill nunca edita pipeline alheio | Sugestão, aplicada por você |

Itens recusados não são aplicados nem repropostos. Itens adiados ficam
registrados no `SESSION_STATE.md`.

---

## O que ela NUNCA faz

- **Não sobrescreve** arquivo seu. Se já existe, ou mescla mostrando o
  diff, ou apresenta o template como sugestão.
- **Não inventa comando.** Se não achou como se testa o projeto, escreve
  `# TODO: definir comando de teste` e diz isso — nunca escreve `pytest`
  num repositório sem um único teste.
- **Não gera enforcement vazio.** Sem comandos reais de teste ou lint, ela
  não cria pre-commit nem CI: um pipeline que passa verde sem verificar
  nada é pior que pipeline nenhum, porque dá confiança falsa.
- **Não gera artefato estranho à stack** para parecer mais completa — por
  exemplo, um `package.json` num repositório .NET. Se o arquivo não serve
  ao projeto, ele não é criado.
- **Não grava nada sem aprovação.** Há uma única pausa no fluxo, e é antes
  da primeira escrita.
- **Não depende de ferramenta externa** para fazer o trabalho. Sem rede,
  sem instalar nada, sem serviço de terceiro: a skill lê o seu
  repositório, escreve os arquivos e executa o que escreveu.

---

## O que muda na prática

Cada camada resolve um problema concreto do dia a dia com agentes. Vale a
pena ler pelo que deixa de acontecer:

| Antes | Depois |
|---|---|
| O agente passa os primeiros minutos explorando o repositório | Ele lê o `AGENTS.md` e roda `./init.sh`: sabe a stack, os comandos e onde o trabalho parou |
| Roda `git push --force` ou `rm -rf` porque ninguém bloqueou | O comando é interceptado antes de executar |
| Commita código não formatado, e o diff enche de ruído | O formatter roda a cada arquivo editado |
| Diz "pronto" sem rodar nada | "Pronto" exige que os comandos da DoD passem, e a saída é a evidência |
| Deixa três coisas pela metade ao mesmo tempo | Uma unidade de trabalho por vez, verificada e commitada antes da próxima |
| Na sessão seguinte, recomeça do zero | Lê o `SESSION_STATE.md` e continua de onde parou |
| Inventa tarefas fora do combinado | Confirma que o pedido está no plano antes de editar qualquer arquivo |

O limite honesto: as três primeiras linhas dependem só dos arquivos que a
skill gera. A quarta — "pronto" ser verificável — depende de o
repositório ter testes e linter. Se não tiver, é a primeira coisa que ela
propõe, porque sem isso o agente continua sem como conferir o próprio
trabalho.

---

## O que você precisa fazer

Invocar a skill. Ela investiga o repositório, monta tudo e mostra —
arquivos completos e Plano de Remediação — numa única pausa. Você aprova o
conjunto e responde às propostas. Ela grava, valida o que gravou, executa
o gate hook para provar que bloqueia e roda os sensores que você aceitou,
colando a saída.

Depois disso, o primeiro commit é `checkpoint: harness inicial`.
