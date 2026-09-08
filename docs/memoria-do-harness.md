# Memória do harness — arquitetura

Design do sistema de memória que o harness-creator gera para o repositório
alvo. Traduz o modelo de memória do BMAD (estudado em `../bmad-estudo/`) para as
restrições do harness: vale nos três agentes-alvo (Claude Code, Cursor, Devin),
é portátil (shell + markdown) e não depende de ferramenta de investigação
específica.

Implementação em `tasks/memoria-do-harness/`. Este documento é a referência; o
plano executável é lá.

## O problema

O handoff entre sessões (`SESSION_STATE.md`) mistura duas coisas: o ESTADO atual
(plano ativo, último commit, próxima ação) e a NARRATIVA acumulada ("o que mudou
em cada grupo"). O resultado incha — no repositório da própria skill o arquivo
passou de 40 KB — e o `init.sh` faz `cat` dele inteiro em toda abertura. Além
disso, não há captura barata ao longo do trabalho, nem conhecimento de código
persistido: o agente re-investiga a mesma solução da empresa toda vez, gastando
tempo e tokens.

## Princípios

- Quatro coisas distintas, nunca uma só: **estado** (sobrescreve) · **jornada**
  (apenda) · **conhecimento** (revisa) · **regra** (enforça).
- Invariante → *script*; julgamento → *o modelo escreve*.
- Log **cego**: não se relê durante a sessão; lê-se uma vez no resume.
- `AGENTS.md` **aponta, não inline** — o índice carrega, o corpo sob demanda.
- **Comportamento, não ferramenta**: o protocolo nomeia o verbo; ferramenta é
  afordância.
- **Evidência > afirmação**: conhecimento carrega prova, e a prova re-rodável é
  o detector de obsolescência.

## As quatro camadas

| # | Camada | Guarda | Quem escreve | Disciplina | Status |
|---|---|---|---|---|---|
| 1 | Estado | situação cross-feature | modelo, sobrescrevendo | pequeno, sempre carregado | reuso (encolhe) |
| 2 | memlog | a jornada, por feature | script (`memlog.sh`) | append-only, cego | **novo** |
| 3 | `knowledge/` | como componentes funcionam + canais | modelo, revisando | current-best, com prova | **novo** |
| 4 | arch-rules | invariantes verificáveis | modelo via catraca | roda na DoD | reuso (ganha memlog) |

### 1. Estado — `SESSION_STATE.md`
Só a situação atual: plano ativo, último commit, em-andamento, bloqueios,
próxima ação. Sobrescrito a cada checkpoint. É o que o `init.sh` despeja. A
narrativa sai daqui para o memlog.

### 2. memlog — `tasks/<funcionalidade>/memlog.md`
Caderno de bordo append-only da funcionalidade, alimentado por cada grupo ao
longo do trabalho. Escrito só via `.claude/memlog.sh` (`init`/`append`), com
três invariantes (do BMAD):

1. **append-only e cronológico** — sem editar/apagar; a ordem é a estrutura.
2. **write-only/cego** — cada chamada ecoa `{"entries":N}`; o agente não relê
   durante a sessão (só no resume).
3. **sem status de ciclo de vida** — "sessão concluída" é uma entrada, não um
   campo mutável; o estado se descobre pelas últimas entradas.

Escrita atômica (temp + `mv`). **Commitado** junto de cada checkpoint — vira o
"porquê cru" arquivado da feature.

### 3. `knowledge/` — conhecimento de componente (planejado, Grupos 2–3)
Base na raiz, cross-feature, para o conhecimento caro descoberto investigando
(ex.: "o que é o TaaC, como evoluir, como resolver problemas"). Dois tipos:

- **Componente** (`knowledge/<x>.md`): o que é / como funciona / como evoluir +
  frontmatter de proveniência (`derivado_de`, `baseline_commit`) + seção
  **Prova** (comando re-rodável, ou ponteiro para o teste que já cobre).
- **Capacidade/fonte** (`knowledge/_fontes.md`): canais de investigação (MCPs,
  páginas de doc, comandos) — dirige as investigações futuras; é o customizável.

`knowledge/README.md` guarda o método e o formato; o `AGENTS.md` só aponta.

Disciplina oposta à do memlog: aqui se **revisa** (a verdade corrente), não se
apenda. O memlog alimenta a base — a jornada registra o achado; a curadoria
promove o entendimento durável para `knowledge/`.

### 4. arch-rules — regra executável (já existe)
A catraca (`executar-grupo`, passo 6) já promove achados de revisão para
`.harness/arch-rules.json`, verificados pelo `check-arch.sh` na DoD. Ganha o
memlog como input adicional (Grupo 3).

## O espectro de durabilidade

```
entrada de memlog  →  conhecimento em prosa  →  conhecimento + prova  →  arch-rule
   (efêmera)            (durável)                 (validável)              (enforçada)
```

Cada degrau é mais validado e mais permanente. A prova re-rodável é o pivô: onde
ela existe, é também o detector de obsolescência (se a prova ainda passa, o
conhecimento ainda vale — melhor que comparar datas de arquivo).

## Os fluxos

- **Abertura** (`init.sh`): carrega o estado + (planejado) o índice de
  `knowledge/`. Barato.
- **Durante o grupo**: apenda achados no memlog. Ao topar com algo desconhecido
  → (planejado) checa `knowledge/`; usa se a prova passa, investiga e registra
  se falta ou está velho.
- **Checkpoint**: sobrescreve o estado; commita o memlog; a catraca promove o
  durável (para `knowledge/` e/ou `arch-rules`).
- **Resume**: estado + últimas entradas do memlog + `knowledge/` sob demanda.

## Decisões travadas

1. memlog **commitado** (não efêmero): o handoff é o produto, e este repo
   valoriza histórico legível.
2. `knowledge/` na **raiz** (descobrível).
3. Frescor: **prova re-rodável > proveniência/mtime > suspeita**.
4. **Sem `how-it-works`**: a investigação é tool-agnóstica; o protocolo nomeia o
   verbo, não a ferramenta. Se um dia uma skill de investigação existir, ela é
   afordância e emite o formato do `knowledge/` — não é bundle.
5. Estado permanece no `SESSION_STATE.md` (a realidade multi-feature precisa de
   um ponteiro cross-feature único).

## Portabilidade

Tudo é markdown + shell POSIX + prosa. `memlog.sh` é POSIX (`#!/bin/sh`), sem
dependência de linguagem do repo alvo. Nenhuma ferramenta específica de agente.

## Validação no PetClinic (Grupo 4)

Prova ponta a ponta do loop **investigar → conhecimento → reuso**, num clone real
do spring-petclinic (`818c413`, Java/Gradle) com o harness novo instalado.

**Tarefa A** (feita à mão, exercitando o harness): investiguei como o PetClinic
troca de banco (H2 → MySQL/Postgres via Spring profile — a propriedade
`database` interpola `db/${database}/schema.sql`), escrevi
`knowledge/database-profiles.md` com Prova re-rodável, e registrei a jornada com
o `memlog.sh` **gerado**. A Prova roda: `grep '^database=' application*.properties`
e `ls db/*/schema.sql`.

**Tarefa B** (sessão headless `claude -p`, limpa, sem memória da A — US$ 0,75,
19 turnos, 131 s): pedido para adicionar suporte a Oracle. Seguindo o passo 3 do
AGENTS, ela:

1. **Leu `knowledge/database-profiles.md`** (o reuso).
2. **Rodou a Prova dele** e confirmou que passa — a Prova serviu de teste de
   frescor, como projetado.
3. Declarou: *"não reinvestiguei o mecanismo"* — o ganho de tempo/token.
4. Leu também o `memlog` da investigação.
5. **Achou a receita do `knowledge/` INCOMPLETA** ("Nenhum código muda" omite o
   driver JDBC — sem `ojdbc11` o profile sobe e morre) e propôs **corrigir o
   próprio `knowledge/database-profiles.md`**: a curadoria acontecendo — o
   conhecimento melhora a cada reuso.

O conhecimento foi usado, validado pela Prova, poupou re-investigação, e ainda
disparou a própria melhoria — as quatro coisas que o design promete.

**Ressalvas honestas:** sem JDK, a build do PetClinic não roda (validou-se a
maquinaria, que é shell/markdown). O harness foi instalado por cópia de
artefatos (não geração limpa), então o SESSION_STATE saiu em branco e o clone
ficou sem git — a sessão B apontou os dois corretamente. É n=1: prova que o
caminho funciona, não uma taxa.
