#!/bin/bash
# init.sh — ritual de abertura de TODA sessão de agente.
# Objetivo: estado executável em <3 min, sem exploração.
# Adapte os comandos ao seu repo (fontes: manifestos, Makefile, CI).
set -e

echo "=== [1/4] Dependências ==="
# npm ci                      # Node
# pip install -r requirements.txt --quiet   # Python
# dotnet restore SOLUCAO.sln        # .NET
# mvn install -DskipTests     # Java/Maven
# ./gradlew build -x test     # Java/Gradle
# go mod download             # Go
# cargo fetch                 # Rust
<comando de instalação do repo>

echo "=== [2/4] Sanity check do ambiente ==="
# node --version && npm run lint --silent || echo "AVISO: lint com problemas"
# dotnet --version            # .NET
# java -version               # Java
# go version                  # Go
# rustc --version             # Rust
<comandos de sanity do repo>

echo "=== [3/4] Baseline de testes (estado REAL antes de trabalhar) ==="
# Não pare no primeiro teste falho: o baseline precisa ser completo.
# npm test                    # Node
# pytest                      # Python
# dotnet test SOLUCAO.sln           # .NET
# mvn test                     # Java/Maven
# ./gradlew test               # Java/Gradle
# go test ./...               # Go
# cargo test                  # Rust
<comando de teste do repo> || echo "AVISO: falhas pré-existentes acima — registrar, não consertar"

echo "=== [4/4] Estado persistido ==="
[ -f SESSION_STATE.md ] && cat SESSION_STATE.md || echo "(sem SESSION_STATE.md — sessão limpa)"
echo "---"
# Fontes de trabalho: mostrar as DUAS sempre que existirem. Esconder uma
# atrás de `elif` fazia o plano dela sumir do único passo que o agente lê em
# toda sessão — um TASKS.md com grupo aberto ficava invisível só porque havia
# um diretório openspec/. Quem declara qual está ATIVA é o SESSION_STATE.md
# (AGENTS.md, "Fontes de trabalho"); este script mostra, não decide.
ATIVO=$(sed -n 's|^- Change/plano ativo:[[:space:]]*||p' SESSION_STATE.md 2>/dev/null | head -1)
echo "Plano ativo (SESSION_STATE.md): ${ATIVO:-(nenhum declarado — declare antes de abrir grupo)}"
if [ -d openspec/changes ]; then
  echo "-- Changes OpenSpec:"
  ls openspec/changes | grep -v archive || echo "   (nenhuma)"
fi
if [ -f TASKS.md ]; then
  echo "-- TASKS.md:"
  head -40 TASKS.md
fi
if [ ! -d openspec/changes ] && [ ! -f TASKS.md ]; then
  echo "(sem fonte de trabalho — nem openspec/changes/ nem TASKS.md)"
fi
echo "---"
# `set -e` no topo derruba o script inteiro se isto falhar — e um repo pode
# legitimamente ainda não ter git (scaffold novo, worktree exportado).
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git log --oneline -5
  git status --short
else
  echo "(sem repositório git — nenhum histórico para mostrar)"
fi

echo ""
echo "=== Init concluído. Próximo passo: grupo desmarcado na fonte de trabalho ativa. ==="
