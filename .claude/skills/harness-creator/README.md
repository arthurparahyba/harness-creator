# Harness Creator

Skill que gera o harness completo de um repositório para agentes de IA de
código — combinando descoberta automática de stack com templates de
protocolo fixo. **Funciona com qualquer linguagem**: Python, JavaScript/
TypeScript, .NET/C#, Java, Go, Rust, Ruby, PHP e outras.

> **Quer só saber o que ela mexe no seu repositório?**
> [MUDANCAS-NO-REPOSITORIO.md](MUDANCAS-NO-REPOSITORIO.md) lista, de forma
> objetiva, tudo que ela cria, modifica, propõe e nunca faz.

## Para desenvolvedores: o que muda no seu dia a dia com IA

Se você nunca ouviu falar de harness engineering, aqui está o que essa
skill faz pelo seu repositório — em termos práticos.

### Antes (sem harness)

Você abre o Claude Code, Cursor ou Devin no seu repo e pede: "implementa
login com JWT". O agente:

1. Explora o repo por 10 minutos tentando entender a stack
2. Cria arquivos em lugares errados (não sabe sua convenção de pastas)
3. Não roda testes (não sabe o comando)
4. Faz `git push --force` sem pedir (ninguém bloqueou)
5. Commita código sem formatar — diff cheio de ruído
6. Você descobre 3 dias depois que quebrou algo que o agente não verificou
7. Na próxima sessão, o agente não lembra de nada e recomeça do zero

### Depois (com harness gerado por esta skill)

Você abre o agente no mesmo repo. Ele roda `./init.sh` automaticamente
e em 3 minutos sabe: stack, comandos de teste, lint, build, estado atual
do trabalho. Quando você pede "implementa login com JWT":

1. O agente lê SESSION_STATE.md e vê que há um grupo em andamento —
   termina antes de começar algo novo
2. Confirma que o pedido está coberto pelo plano de trabalho (não inventa
   tarefas fora do escopo)
3. Implementa em **grupos de 2-5 tasks**, verificando cada grupo antes de
   avançar (WIP=1 — nada fica meio-feito)
4. Toda vez que edita um arquivo, o hook de auto-formatação roda
   automaticamente — diff limpo
5. Se tenta rodar `rm -rf` ou `git push --force`, o gate hook **bloqueia**
   antes de executar
6. Antes de commitar, o pre-commit roda lint e build (segundos)
7. Para concluir, roda a Definition of Done — os comandos reais do seu
   repo (ex: `dotnet test`, `pytest`, `mvn verify`, `npm test`) — e só
   commita se tudo passar
8. Atualiza SESSION_STATE.md com o hash do commit, testes (X/Y), próxima
   ação
9. PARE e diz "Grupo concluído. Contexto pode ser reiniciado."

### O que você ganha concretamente

- **Menos tempo de setup**: o agente começa trabalhando, não explorando
- **Zero operações destrutivas**: hooks bloqueiam antes de executar
- **Diff limpo**: formatação automática a cada edit
- **Evidência de conclusão**: "passou" = comando passou, não "parece funcionar"
- **Continuidade entre sessões**: estado persistido, não recomeça do zero
- **Escopo controlado**: agente não avança sem verificar, não inventa tarefas
- **Sensores rodando**: testes, lint e build como gate antes de commitar
- **Review automatizado**: subagente de code review antes de commitar
- **Multi-linguagem**: mesma skill funciona em Python, .NET, Java, JS/TS,
  Go, Rust, Ruby e PHP — sem adaptação manual

### Como ela prova que funcionou

Nada é declarado pronto sem execução. Depois de gravar, a skill valida
cada artefato: JSON e YAML têm de parsear, os scripts têm de estar
executáveis e com quebra de linha LF, a Definition of Done tem de ser
idêntica em todos os arquivos onde aparece, e o gate hook é **executado de
verdade** — precisa devolver exit 2 para um `rm -rf` simulado e exit 0
para um `pytest`. Se você aceitou instalar sensores, ela os roda e cola a
saída.

Se qualquer uma dessas verificações falhar, isso é defeito da geração —
não pendência sua.

### Em uma frase

**A skill transforma um repositório "aberto" num repositório "harnessado" —
onde o agente de IA trabalha dentro de regras, sensores e fronteiras que
garantem qualidade, segurança e continuidade, em vez de operar livremente
e causar danos.**


---

## Ecossistemas suportados

A unidade de detecção é o **ecossistema**, não a linguagem: Maven e Gradle
são Java e divergem em todos os comandos que a skill preenche, e Angular,
React e Node são JS/TS e também. Cada um destes foi verificado gerando o
harness num repositório real da stack e executando o resultado.

| Ecossistema | Detectado por |
|---|---|
| Node / TypeScript | `package.json` |
| React | `react` em `dependencies` |
| Angular | `angular.json` |
| Java / Maven | `pom.xml` |
| Java / Gradle | `build.gradle` |
| .NET / C# | `.sln`, `.csproj` |
| Go | `go.mod` |
| Python | `pyproject.toml`, `setup.py` |
| Rust | `Cargo.toml` |
| Ruby | `Gemfile` |
| PHP | `composer.json` |
| Monorepo JS | `workspaces`, `pnpm-workspace.yaml`, `nx.json`, `turbo.json` |

Nenhum template é específico de uma linguagem: todos usam placeholders
`<>` preenchidos via descoberta. Os comandos de teste, lint, tipos e
formatação de cada ecossistema, os nomes de lockfile e o padrão de arquivo
do hook de formatação vivem numa única tabela, em
[references/ecossistemas.md](references/ecossistemas.md) — de propósito,
para não haver duas fontes da mesma verdade divergindo com o tempo.

---

## Benefícios por conceito de Harness Engineering

A tabela abaixo explica o valor de cada peça. A lista canônica de arquivos,
destinos e condições está em
[references/arquivos-gerados.md](references/arquivos-gerados.md).

| Conceito | O que a skill gera | Benefício |
|----------|-------------------|-----------|
| **AGENTS.md** (contexto) | Arquivo raiz com descrição do projeto, comandos reais, convenções | O agente sabe o que é o projeto e como trabalhar nele sem explorar o repo |
| **AGENTS.md com escopo** | Arquivo no diretório de código com as restrições daquele diretório | Conhecimento perto do código; a raiz não vira um arquivo gigante carregado a cada request |
| **Skill `executar-grupo`** | `.claude/skills/executar-grupo/SKILL.md` com o procedimento de fechar um grupo | Procedimento carregado sob demanda, não em todo request |
| **Workflow de CI** | `.github/workflows/harness-dod.yml` com um step por comando da DoD (só se o repo não tiver CI) | Enforcement remoto: `--no-verify` não contorna. Um step por sensor faz o build vermelho já dizer qual falhou |
| **Gate de integridade** | Step no CI que confere os hooks e executa o gate | O harness não é desfeito em silêncio — apagar um hook deixa o CI vermelho |
| **Verificação pós-geração** | FASE 5 valida cada artefato e executa o gate hook | O resultado é evidência de comando, não afirmação — a mesma regra que a skill impõe ao agente |
| **Plano de Remediação** | Lista do que a skill **não** gera sozinha (instalar pytest/ruff, primeiros testes, `.env.example`), com comando exato e impacto | Você fica sabendo tudo que falta, não só o que a skill sabe escrever; instalar dependência é decisão sua, então confirma item a item |
| **Definition of Done (DoD)** | Os MESMOS comandos reais no AGENTS.md, no `/dod`, no init.sh, no pre-commit e no CI | "Concluído" é evidência de comando passando. A redundância é deliberada: DoD divergente faz o agente verificar uma coisa e o CI cobrar outra |
| **Grupos / Checkpoints** | Estrutura de tasks em grupos coesos de 2-5 unidades com `Verificação:` | Escopo, verificação e commit alinhados numa fronteira física |
| **WIP=1** | Regra no AGENTS.md que proíbe avançar antes do grupo atual estar verificado e commitado | Evita código meio-feito e overreach do agente |
| **init.sh** (ritual de abertura) | Script que instala deps, roda baseline de testes e mostra estado persistido | Sessão começa em <3 min com estado executável, sem exploração |
| **SESSION_STATE.md** (continuidade) | Arquivo de estado atualizado a cada commit de grupo | Agente retoma trabalho de onde parou após reset de contexto |
| **Hooks de agent loop** (enforcement) | `gate-destructive.sh` bloqueia o irreversível — `rm -rf`, `git push --force`, `DROP TABLE`, publicação de pacote (`npm publish`, `mvn deploy`, `dotnet nuget push`) e `terraform destroy` — e `format-on-edit.sh` formata a cada edit | O comando destrutivo não chega a executar; `npm test` e `mvn test` passam sem atrito, porque gate que atrapalha é gate que o time desliga |
| **Mesmos hooks nos três agentes** | Um registro por agente (Claude Code, Devin CLI e Cursor) apontando para os mesmos scripts, que leem os dois formatos de entrada e não dependem de Python instalado | A proteção não fica valendo só no agente que o autor do harness usava; trocar de ferramenta não desliga o gate |
| **Pre-commit portátil** | `.pre-commit-config.yaml` com lint/format/build da linguagem detectada | Sensores baratos rodam antes do commit existir — feedback mais cedo possível |
| **Comando `/dod`** | `.claude/commands/dod.md` com o mesmo comando da DoD | Agente verifica conclusão com um comando, sem relembrar os passos |
| **Subagente code-reviewer** | `.claude/agents/code-reviewer.md` com checklist SOLID/Clean Code/DDD | Review automatizado antes de commitar grupo |
| **OpenSpec config** | `openspec/config.yaml` com regras de execução (se `openspec/` existir) | Spec-Driven Development com workflow integrado ao harness |
| **Lockfile** | Geração do lockfile apropriado à linguagem detectada, se não existir | Instalações reproduzíveis — sensores testam a mesma árvore de deps em todo lugar |
| **`.editorconfig`** (universal) | `editorconfig-base` com regras universais + mescla de regras específicas (ex: .NET analyzers) | Linter e formatter configurados via um arquivo, para qualquer linguagem |
| **`.gitignore` + `.env`** | Append de `.env` / `.env.*` se não estiverem cobertos | Credenciais nunca commitadas por acidente |
| **LICENSE** | Oferta de licença apropriada se não existir | Repo pronto para distribuição |
| **MCP hygiene** | `.mcp.json` na raiz se detectado em outro path, com credencial literal convertida para `${VAR}` | Config centralizada, e um segredo nunca é copiado para um lugar mais visível do que já estava |
| **Degradação graciosa** | Fonte de trabalho com precedência (OpenSpec → TASKS.md), respeitada também pela skill `executar-grupo` | Harness funciona com ou sem OpenSpec; removida a ferramenta, tudo continua operando |

---

