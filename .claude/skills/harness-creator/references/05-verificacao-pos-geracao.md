# FASE 5 — Verificação pós-geração

**Objetivo:** Validar que a camada de enforcement está consistente e
funcional após gravar os arquivos.
**Precondições:** Fase 4 aprovada, arquivos gravados.

---

## Checklist de verificação

1. **JSON válido**: validar `.claude/settings.json`, `.devin/hooks.v1.json`,
   `.cursor/hooks.json` e `.mcp.json` (se gerado) com
   `python -c "import json; json.load(open(...))"`
2. **YAML válido**: validar `.pre-commit-config.yaml` com
   `python -c "import yaml; yaml.safe_load(open(...))"` (se pyyaml disponível)
3. **Scripts executáveis**: confirmar `chmod +x` em `init.sh` e
   `.claude/hooks/*.sh`
4. **Quebras de linha LF nos scripts**: `.claude/hooks/*.sh` e `init.sh`
   NÃO podem ter CRLF. Com `\r` no fim das linhas, o shebang vira
   `/bin/bash^M` ("bad interpreter") e `set -euo pipefail` falha com
   "invalid option name" — o script morre com **exit 1**, que em
   `PreToolUse` significa "erro não-bloqueante": o comando destrutivo
   **executa mesmo assim**. O gate falha aberto sem ninguém perceber.
   ```
   file .claude/hooks/*.sh init.sh    # nenhum deve dizer "CRLF"
   ```
   Se houver CRLF, converter para LF antes de qualquer outra coisa.
5. **Gate hook funcional**: testar os dois caminhos com input simulado:
   ```
   echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/test"}}' \
     | bash .claude/hooks/gate-destructive.sh
   # Deve retornar exit 2 (BLOCKED). Exit 1 = gate quebrado, falha ABERTO.

   echo '{"tool_name":"Bash","tool_input":{"command":"pytest"}}' \
     | bash .claude/hooks/gate-destructive.sh
   # Deve retornar exit 0 (comando seguro passa)
   ```
   Testar só o bloqueio esconde um gate que bloqueia tudo; testar só o
   caminho feliz esconde um gate que não bloqueia nada.
6. **Nenhum marcador de preenchimento sobrou.** Verificar pela lista
   nominal de marcadores de cada template, NÃO com um grep genérico de
   `<...>`: o protocolo contém placeholders **ilustrativos** que devem
   permanecer (`<change-ativa>`, `<nome-da-funcionalidade>`, `<objetivo>`,
   `<hash>`, `<task>`). Um grep cego os acusa e faz você "consertar" o
   que está certo. Os que NÃO podem sobrar:
   `<runner>`, `<setup-steps>`, `<dod-steps>`,
   `<dod-command>`, `<pre-commit-hooks>`, `<formatter_command>`,
   `<formatter_bin>`, `<file_glob>`, `<caminho>`, `<branch-base>`,
   `<como-propor-mudanca-de-plano>`, `<ferramentas-do-harness>`,
   `<checks-do-repo>`, `<versao-da-skill>`, `<data-iso>`, `<ecossistema>`,
   `<comando de ...>`, `<comandos de ...>`, `<restrição N>`.
   Esta lista é verificada por `tests/test_skill.py` contra os templates
   reais: marcador renomeado num template e não aqui quebra o teste.
   Cuidado com o caso inverso: se um marcador aparecer também num
   comentário do template, a substituição vaza para fora do comentário e
   corrompe o arquivo — foi exatamente assim que o workflow de CI quebrou
   na primeira geração. É o item 12 (YAML do CI) que pega isso.
7. **Tempo da DoD**: cronometrar a DoD completa uma vez e reportar o número.
   ```
   time <comando da DoD>
   ```
   O protocolo manda rodá-la a cada grupo. Uma DoD de 20 minutos (suíte
   grande de Gradle, .NET, monorepo) não é rodada a cada grupo por ninguém:
   o agente pula, o humano pula, e o WIP=1 vira texto. Acima de ~3 minutos,
   levar à FASE 4 a proposta de dividir em duas — a rápida do grupo e a
   completa antes do push — e registrar as duas nos MESMOS arquivos onde a
   DoD já aparece. Não decidir sozinho: qual sensor sai da verificação por
   grupo é escolha do usuário. Se a DoD não puder ser executada aqui
   (faltam deps, precisa de rede), reportar isso em vez de estimar.
8. **Consistência da DoD**: o comando da DoD deve ser IDÊNTICO em:
   - AGENTS.md (seção "Definition of Done")
   - openspec/config.yaml (se gerado)
   - init.sh (passo de baseline)
   - .claude/commands/dod.md
   - .pre-commit-config.yaml (hooks)
   - .github/workflows/harness-dod.yml (se gerado)
   Reportar divergências se houver.
9. **`.claude/settings.json` tem wrapper `hooks`**: validar que o JSON
   tem a chave `"hooks"` no nível raiz (não os eventos diretamente no
   raiz). Sem o wrapper, scanners não detectam os hooks.
10. **Os três registros apontam para script existente**: para cada config
    de hook gerada (`.claude/settings.json`, `.devin/hooks.v1.json`,
    `.cursor/hooks.json`), resolver cada `command` referenciado e confirmar
    que o arquivo existe e é executável.
    ```
    grep -ho '\.claude/hooks/[a-z-]*\.sh' \
      .claude/settings.json .devin/hooks.v1.json .cursor/hooks.json \
      | sort -u | xargs -I{} test -x {} || echo "hook registrado nao existe"
    ```
    Registro apontando para arquivo ausente é o pior caso silencioso: no
    Claude Code e no Devin o hook morre e o comando passa; no Cursor o
    `failClosed` do gate transforma isso em bloqueio de tudo.
11. **`.gitignore` cobre `.env`**: confirmar que `.env` está no
    `.gitignore` após o append.
12. **Workflow de CI é YAML válido** (se gerado) e seus `- run:` são os
    MESMOS comandos da DoD, na mesma ordem.
13. **Subagente e skill têm frontmatter**: validar que `.claude/agents/*.md`
    e `.claude/skills/*/SKILL.md` têm `name:` e `description:`, e que a
    `description:` diz QUANDO usar (não só o que é) — descrição vaga nunca
    dispara.
14. **AGENTS.md com escopo não duplica o protocolo**: fora do comentário
    de cabeçalho, o arquivo do subdiretório não pode conter grupos,
    WIP=1, DoD nem handoff — só restrições e convenções daquele
    diretório. Protocolo duplicado diverge do da raiz na primeira edição.
15. **Ponte `CLAUDE.md` alcança o `AGENTS.md`**: existe um `CLAUDE.md` ao
    lado de CADA `AGENTS.md` gerado (raiz e subdiretório), e cada um
    importa o irmão — `@AGENTS.md` fora de crase e fora de bloco de código,
    senão o import não é parseado e vira texto literal. Confirmar também
    que a ponte não virou cópia: se o `CLAUDE.md` contém o protocolo em vez
    da linha de import, são duas fontes que divergem na primeira edição.
    ```
    grep -n '^@AGENTS.md' CLAUDE.md <dir-principal>/CLAUDE.md
    ```
    Esta é a única checagem que separa "harness gravado" de "harness
    carregado": sem ela nada falha, o agente apenas ignora o protocolo.
16. **Manifesto confere com o disco**: `.claude/harness.json` parseia, não
    tem marcador `<>` sobrando, e **todo caminho listado em `arquivos`
    existe de verdade**. O manifesto é o que permite atualizar ou remover o
    harness depois; listando arquivo que não foi gravado, ele passa a
    mentir sobre o próprio estado do repositório.
    ```
    python -c "import json;[open(a) for a in json.load(open('.claude/harness.json'))['harness']['arquivos']]"
    ```
17. **Lockfile tem nome convencional**: o arquivo gerado é reconhecido
    pelo ecossistema (`uv.lock`, `poetry.lock`, `requirements.txt`,
    `package-lock.json`, `Cargo.lock`, `go.sum`, …). Nome fora da
    convenção não é instalado por ninguém.
18. **Nenhuma credencial literal em `.mcp.json`**: valores de chaves tipo
    `token`/`key`/`secret`/`password` usam `${VAR}`.

19. **Remediações aceitas realmente rodam.** Se o usuário aceitou
    sensores, execute-os uma vez e cole a saída:
    ```
    pytest -q          # ou o runner da linguagem
    ruff check .       # ou o linter da linguagem
    ```
    Instalar a ferramenta e configurar o arquivo não é entregar o
    sensor — entregar é ele executando. Falhas típicas que só aparecem
    aqui: o entrypoint importa dependência de sistema e o teste morre
    com `ImportError` (falta o stub no `conftest.py`), ou o linter
    aponta dezenas de violações pré-existentes.
    Violação pré-existente **não é regressão**: reporte a contagem, diga
    quantas são auto-corrigíveis e deixe a decisão de corrigir com o
    usuário — consertar código de produção não estava na aprovação.

## Relatório final

A skill exige evidência de comando para declarar qualquer coisa concluída
— vale para ela mesma. O relatório é a saída dos itens acima, não uma
afirmação de que deu certo: diga quais checks rodaram, o que cada um
devolveu, e cole a saída dos sensores aceitos.

Se algum item da checklist falhar, isso é **defeito da geração, não
pendência do usuário**: corrija antes de seguir.

Separe o que ainda falta em duas listas, porque o usuário age diferente em
cada uma: o que ele **recusou ou adiou**, com a consequência prática de
cada recusa ("sem test runner, o `/dod` continua sem o que executar"), e o
que **ninguém pode fechar aqui** (licença por decidir, segredo a
rotacionar). Sem essa separação, um harness incompleto parece falha da
skill quando na verdade é uma escolha informada do usuário.

---

## ➡️ Fase 5 concluída — siga direto para a Fase 6
