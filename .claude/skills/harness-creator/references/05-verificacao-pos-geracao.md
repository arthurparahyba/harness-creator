# FASE 5 — Verificação pós-geração

**Objetivo:** Provar que a camada de enforcement está consistente e funcional
depois de gravar os arquivos.
**Precondições:** Fase 4 aprovada, arquivos gravados.

---

## 1. Rode o verificador

As checagens mecânicas estão em `.claude/verificar-harness.sh`, gravado junto
com o harness. Rode-o e **cole a saída** — ela é a evidência desta fase:

```
sh .claude/verificar-harness.sh
```

Ele cobre 11 checagens, todas com o mesmo resultado a cada execução:

| Checagem | Por que ela existe |
|---|---|
| JSON dos configs parseia | JSON quebrado desliga o hook em silêncio |
| Scripts sem CRLF | com `\r` o shebang vira `/bin/sh^M` e o script morre com **exit 1** — que em `PreToolUse` significa "erro não-bloqueante": o comando destrutivo executa mesmo assim. O gate falha **aberto** |
| Scripts executáveis | sem o bit, o agente registra um hook que nunca roda |
| Gate bloqueia destrutivo (exit 2) | testar só isto esconde um gate que bloqueia tudo |
| Gate libera comando seguro (exit 0) | testar só isto esconde um gate que não bloqueia nada |
| `settings.json` tem wrapper `hooks` | sem o wrapper na raiz, nenhum scanner enxerga os hooks |
| Hooks registrados existem e executam | registro apontando para arquivo ausente é o pior caso silencioso: no Claude Code e no Devin o hook morre e o comando passa; no Cursor o `failClosed` transforma isso em bloqueio de tudo |
| Ponte `CLAUDE.md` alcança cada `AGENTS.md` | é a única checagem que separa "harness gravado" de "harness carregado": sem ela nada falha, o agente apenas ignora o protocolo |
| Manifesto só lista arquivo existente | listando arquivo que não foi gravado, ele mente sobre o estado do repositório e a atualização futura age sobre ficção |
| `.gitignore` cobre `.env` | — |
| Nenhum marcador preenchível sobrou | marcador vivo é template entregue pela metade |

Se alguma falhar, **isso é defeito da geração, não pendência do usuário**:
corrija antes de seguir. O script sai com código 1 nesse caso.

Ele não exige Python: onde Python existe, valida JSON com o parser de
verdade; onde não existe, cai para balanceamento de chaves e **diz isso na
saída**. Exigir Python transformaria a verificação em erro de setup nos repos
Go, .NET e Java que a skill precisa atender.

---


## 1.1 As regras arquiteturais aprovam o harness recém-gerado

Rode `bash .claude/check-arch.sh` e **cole a saída**. Numa geração limpa ele
tem de terminar em `nenhuma violada` e exit 0.

Se a semente reprovar aqui, o primeiro contato do usuário com o registro de
regras é um vermelho que ele não causou — e a reação natural a isso é apagar
o arquivo, que mata a catraca antes de ela girar uma vez.

## 2. O que o script não decide

Os itens abaixo dependem de julgamento ou de rodar comandos do projeto, então
continuam com você.

1. **YAML válido**: `.pre-commit-config.yaml` e o workflow de CI. Onde houver
   parser (`python -c "import yaml; yaml.safe_load(open(...))"`), use; senão,
   confira à mão que a indentação sobreviveu à substituição de marcador.
   Cuidado com o caso que já quebrou uma vez: marcador que aparece **também**
   num comentário do template faz a substituição vazar para fora do comentário
   e corromper o arquivo.

2. **Tempo da DoD**: cronometre a DoD completa uma vez e reporte o número.
   ```
   time <comando da DoD>
   ```
   O protocolo manda rodá-la a cada grupo. Uma DoD de 20 minutos (suíte grande
   de Gradle, .NET, monorepo) não é rodada a cada grupo por ninguém: o agente
   pula, o humano pula, e o WIP=1 vira texto. Acima de ~3 minutos, leve à FASE
   4 a proposta de dividir em duas — a rápida do grupo e a completa antes do
   push — e registre as duas nos MESMOS arquivos onde a DoD já aparece. Não
   decida sozinho: qual sensor sai da verificação por grupo é escolha do
   usuário. Se a DoD não puder ser executada aqui (faltam deps, precisa de
   rede), reporte isso em vez de estimar.

3. **Equivalência da DoD** — não igualdade literal. Cada arquivo declara a
   mesma DoD no formato que o seu consumidor entende, e exigir texto idêntico
   é impossível por construção: o `init.sh` roda só o baseline, o
   `.pre-commit-config.yaml` é uma lista de hooks e o workflow de CI é um
   `- run:` por sensor. Item que ninguém consegue cumprir é pior que item
   nenhum — o agente marca como ok sem ter verificado.

   O que precisa bater é o **conjunto de sensores e a ordem**:

   | Arquivo | Forma | Cobertura esperada |
   |---|---|---|
   | `AGENTS.md` ("Definition of Done") | cadeia com `&&` | completa — é a fonte |
   | `.claude/commands/dod.md` | a mesma cadeia | completa |
   | `.github/workflows/harness-dod.yml` | um `- run:` por sensor | completa, mesma ordem |
   | `openspec/config.yaml` (se gerado) | a mesma cadeia | completa |
   | `.pre-commit-config.yaml` | um hook por sensor | os que rodam sem rede |
   | `init.sh` | passo de baseline | subconjunto: o runner de teste |

   Reporte como divergência: sensor presente na fonte e ausente num consumidor
   de cobertura completa, ou ordem trocada entre eles. Diferença de formato
   não é divergência. Se a FASE 4 aprovou a divisão da DoD (item 2), compare
   contra a divisão aprovada, não contra a cadeia única.

4. **Subagente e skill têm frontmatter**: `.claude/agents/*.md` e
   `.claude/skills/*/SKILL.md` precisam de `name:` e `description:`, e a
   `description:` tem de dizer QUANDO usar, não só o que é — descrição vaga
   nunca dispara.

5. **AGENTS.md com escopo não duplica o protocolo**: fora do comentário de
   cabeçalho, o arquivo do subdiretório não pode conter grupos, WIP=1, DoD nem
   handoff — só restrições e convenções daquele diretório. Protocolo duplicado
   diverge do da raiz na primeira edição.

6. **Lockfile**, só se o usuário **aceitou** a remediação (grupo B: exige
   rede, não é gerado sozinho). O nome precisa ser o convencional do
   ecossistema — `uv.lock`, `poetry.lock`, `package-lock.json`, `Cargo.lock`,
   `go.sum`… Nome fora da convenção não é instalado por ninguém. Recusada ou
   adiada, registre como recusa na lista final, não como falha da geração.

7. **Remediações aceitas realmente rodam.** Se o usuário aceitou sensores,
   execute-os uma vez e cole a saída:
   ```
   pytest -q          # ou o runner da linguagem
   ruff check .       # ou o linter da linguagem
   ```
   Instalar a ferramenta e configurar o arquivo não é entregar o sensor —
   entregar é ele executando. Falhas típicas que só aparecem aqui: o
   entrypoint importa dependência de sistema e o teste morre com
   `ImportError` (falta o stub no `conftest.py`), ou o linter aponta dezenas
   de violações pré-existentes.
   Violação pré-existente **não é regressão**: reporte a contagem, diga
   quantas são auto-corrigíveis e deixe a decisão de corrigir com o usuário —
   consertar código de produção não estava na aprovação.

---

## Relatório final

A skill exige evidência de comando para declarar qualquer coisa concluída —
vale para ela mesma. O relatório é a saída do verificador mais a dos itens
acima, não uma afirmação de que deu certo.

Separe o que ainda falta em duas listas, porque o usuário age diferente em
cada uma: o que ele **recusou ou adiou**, com a consequência prática de cada
recusa ("sem test runner, o `/dod` continua sem o que executar"), e o que
**ninguém pode fechar aqui** (licença por decidir, segredo a rotacionar). Sem
essa separação, um harness incompleto parece falha da skill quando na verdade
é uma escolha informada do usuário.

---

## ➡️ Fase 5 concluída — siga direto para a Fase 6
