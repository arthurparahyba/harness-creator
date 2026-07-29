# Repositórios de exemplo

Repositórios mínimos, mas realistas, de cada ecossistema que a skill
suporta. Servem para **gerar o harness em cima deles e executar o
resultado** — é o que [`../test_geracao.py`](../test_geracao.py) faz.

## Por que existem

`test_skill.py` valida os *templates*: JSON e YAML que parseiam, ausência
de CRLF, links entre as fases. Isso não é suficiente. O glob
`*.{js,ts,jsx,tsx}` que a skill documentou por meses é sintaticamente
impecável no template e **completamente inerte** depois de gerado, porque
`case` não faz brace expansion. Nenhuma inspeção de template pegaria isso;
só rodar o hook gerado contra um `.ts` de verdade pega.

Daí a regra: toda mudança em `resources/` deve ser exercitada aqui.

## O que tem em cada um

Cada fixture tem o mínimo para ser reconhecível como aquele ecossistema, e
nada além disso: manifesto, config de lint/formatter/tipos, lockfile,
`.gitignore`, um arquivo de código com uma função de verdade e um teste
que a exercita.

| Fixture | Ecossistema | Detectado por |
|---|---|---|
| `node/` | Node + TypeScript | `package.json` com `scripts.test` |
| `react/` | React + Vite | `react` em `dependencies`, `.tsx` |
| `angular/` | Angular | `angular.json`, `.spec.ts`, `strictTemplates` |
| `java-maven/` | Java com Maven | `pom.xml`, `checkstyle.xml`, spotless |
| `java-gradle/` | Java com Gradle | `build.gradle`, `config/checkstyle/` |
| `dotnet/` | .NET / C# | `.sln` + dois `.csproj`, xunit |
| `go/` | Go | `go.mod`, `_test.go`, `.golangci.yml` |
| `monorepo/` | Workspaces JS | `workspaces` na raiz, scripts nos pacotes |

Maven e Gradle são fixtures separadas de propósito: são o mesmo idioma e
divergem em **todos** os comandos que a skill preenche. Vale o mesmo para
Angular, React e Node. O `monorepo/` existe porque nele os scripts vivem
nos pacotes e não na raiz — o caso em que a DoD fica sem um comando único
que valide o repositório inteiro.

## O que os testes verificam em cada uma

Para cada fixture, o harness é gerado num diretório temporário e então:

- o JSON e o YAML gerados parseiam;
- nenhum marcador de preenchimento sobrou em linha ativa;
- a Definition of Done é idêntica no `AGENTS.md` e no `/dod`;
- o `AGENTS.md` com escopo não duplica o protocolo da raiz;
- o gate hook devolve exit 2 para `rm -rf`, `git push --force`,
  `npm publish` e `dotnet nuget push`;
- o gate hook **não** bloqueia o primeiro comando da DoD daquela stack —
  um gate que barra o próprio `mvn test` é desligado no primeiro dia;
- o hook de formatação alcança um arquivo de código real da fixture
  (`Contador.tsx`, `Estoque.java`, `frete.go`…) e ignora o manifesto.

## Maturidade medida

Reproduza com `python tests/medir.py` (requer Node; grava
`tests/medicao.json`). Este repositório usa o
[harness-score](https://paladini.io/harness-score/) para acompanhar a
eficácia da geração — **a skill entregue não depende dele**.

| Ecossistema | Antes | Depois | Depois (antes do Grupo 28) |
|---|---|---|---|
| `node` | L0 · 36/108 | **L4 · 98/108** | L4 · 103/108 |
| `react` | L0 · 36/108 | **L4 · 98/108** | L4 · 103/108 |
| `angular` | L0 · 36/108 | **L4 · 98/108** | L4 · 103/108 |
| `java-maven` | L0 · 36/108 | **L4 · 98/108** | L4 · 103/108 |
| `go` | L0 · 36/108 | **L4 · 98/108** | L4 · 103/108 |
| `monorepo` | L0 · 30/108 | L4 · 92/108 | L4 · 97/108 |
| `java-gradle` | L0 · 27/108 | L2 · 89/108 | L2 · 94/108 |
| `dotnet` | L0 · 22/108 | L2 · 81/108 | L2 · 86/108 |

A última coluna é o que a geração pontuava **antes de o Grupo 28 remover o
subagente `code-reviewer`**. A queda de 5 pontos em toda linha é conhecida e
esperada: `V6 — Regras arquiteturais` usava `.claude/agents/code-reviewer.md`
como equivalência e, sem ele, passou de `eq` para `fail`. O harness gerado
deixou de cobrir regra arquitetural — ver `eval/mapa-equivalencias.md`.

Os 5 pontos que faltam em toda linha são `LICENSE` (escolha do usuário, a
skill oferece mas não decide) e interpolação de env em config MCP
(inaplicável — as fixtures não usam MCP).

O `monorepo` fica em 97 porque o script de teste na raiz é uma
**recomendação**, não algo que a skill gere: `gerar.py` não a aplica.
Aplicando-a, o repositório vai a 98 — os 6 pontos de `SNS-01` são
exatamente o que a recomendação vale.

`java-gradle` e `dotnet` param em L2 por limitação do medidor, não do
harness: o scanner exige `pom.xml` para reconhecer teste em Java e não
reconhece `dotnet test`, `dotnet format` nem analyzers Roslyn. Repare que
a pontuação bruta chega a 89 e 81, e que o ganho é o mesmo +62 das
demais — o harness gerado é igualmente completo.

## Como adicionar um ecossistema

Crie o diretório com o mínimo do ecossistema, acrescente uma entrada em
`STACKS` no [`../gerar.py`](../gerar.py) — incluindo `formatavel` e
`nao_formatavel` apontando para arquivos que existem na sua fixture — e
rode `pytest -q`. Os testes se parametrizam sozinhos sobre `STACKS`.

Estas fixtures não são compiladas nem instaladas: nenhum `npm install`,
`mvn`, `dotnet` ou `go` roda contra elas. São arquivos estáticos, e os
testes exercitam o harness, não o build do projeto de exemplo.
