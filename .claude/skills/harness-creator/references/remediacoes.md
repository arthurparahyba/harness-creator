# Catálogo de remediações

Tudo que pode melhorar o repositório para trabalho com agentes, e de quem
é a decisão.

A fonte das lacunas é o **Relatório de Descoberta da FASE 1**: cada item
marcado `NÃO ENCONTRADO` é uma entrada em potencial deste catálogo. Não
escreva a lista de memória nem presuma o que falta — derive do que a
investigação do repositório realmente mostrou.

---

## Os três grupos

| Grupo | O que é | Decisão |
|---|---|---|
| **A — Gerado** | Arquivos de harness que a skill cria sozinha | Aprovação única da FASE 4 |
| **B — Recomendado** | Mexe em dependências, configuração ou código do projeto | Confirmação item a item |
| **C — Informativo** | Só o humano pode decidir (segredo vazado, licença, CI corporativo) | Só reportar |

A fronteira entre A e B é: **o artefato é só do harness, ou muda o
contrato do projeto?** Criar `.claude/hooks/gate-destructive.sh` não afeta
quem não usa agente. Adicionar `pytest` ao `pyproject.toml` muda o que o
time instala, o que o CI roda e o que "quebrado" significa. O primeiro a
skill faz; o segundo ela propõe.

---

## Grupo A — gerado pela skill (não precisa recomendar)

AGENTS.md na raiz e com escopo, skill `executar-grupo`, comando `/dod`,
subagente `code-reviewer`, hooks de agent loop com `settings.json`,
`init.sh`, `SESSION_STATE.md`, fonte de trabalho, `.editorconfig`,
lockfile, `.gitignore`, README mínimo e conversão de credencial de MCP
para `${VAR}`.

Ver [arquivos-gerados.md](arquivos-gerados.md).

---

## Grupo B — recomendado, com confirmação

### Sensores — a lacuna mais cara

Sem test runner, linter e type checker, **o agente não tem como verificar
o próprio trabalho**. A consequência é concreta e em cadeia: a Definition
of Done fica vazia, o `/dod` não tem o que executar, o pre-commit e o CI
não são gerados (ver regra de honestidade na
[FASE 2](02-preenchimento-templates.md)), e "concluído" volta a ser
opinião do agente em vez de saída de comando. Nenhum arquivo de harness
compensa isso.

Quando a FASE 1 não encontrar sensores, esta é a primeira recomendação,
antes de qualquer outra. Recomendar pelo **ecossistema** detectado, com
os comandos e arquivos de config exatos de [ecossistemas.md](ecossistemas.md).

Recomendar junto os **primeiros testes**, e não só o runner: runner
configurado com zero testes dá ao agente um verde que ele não mereceu.
Propor alvos concretos — as funções puras do repositório, que testam sem
infraestrutura. Localize-as na FASE 1 e cite-as pelo nome; recomendação
genérica ("escreva testes") não é acionável.

Cuidado recorrente: se o entrypoint importa dependência de sistema no
nível do módulo (display, GPU, rede), o teste não roda sem stub.
Recomendar junto um `tests/conftest.py` (ou equivalente) que substitua
essas dependências — senão o usuário aceita a recomendação e recebe um
`ImportError`.

### Ponto de entrada único em monorepo

Se os comandos de teste e lint vivem só nos pacotes, não existe um comando
que valide o repositório inteiro — e a DoD precisa de um. Recomendar o
script raiz que delega: `npm test --workspaces`, `turbo test`,
`nx run-many -t test`, `pnpm -r test`, ou o agregador equivalente.

### Arquivo `.env` desprotegido

Existe `.env` na árvore sem `.env.example`. Recomendar: criar o
`.env.example` com as chaves e valores vazios, e conferir se o `.env`
está rastreado pelo git (`git ls-files --error-unmatch .env`).
**Nunca remover nem reescrever o `.env` por conta própria** — pode ser a
única cópia de credenciais que o usuário tem.

### `.cursorrules` legado

Recomendar a migração para arquivos de regra com escopo, que carregam só
quando o caminho é relevante. Não apagar o arquivo antigo sem confirmação.

### Credencial literal em arquivo de harness

A skill converte para `${VAR}` (grupo A), mas a parte que importa é do
humano: **o segredo exposto precisa ser rotacionado**, e se já foi
commitado ele continua no histórico do git. Reportar sempre com essa
frase, não como detalhe.

---

## Grupo C — só reportar

- **LICENSE**: escolha jurídica. Oferecer as opções (proprietária, MIT,
  Apache-2.0, pular) e gerar só a escolhida.
- **CI corporativo**: se já existe pipeline, propor o step da DoD; nunca
  editar (ver [FASE 3](03-resolucao-conflitos.md)).
- **Runner self-hosted**: a skill não tem como descobrir a política da
  organização.

---

## Formato do Plano de Remediação (apresentar na FASE 4)

Ordenar pelo que **destrava outra coisa** primeiro: sensores vêm antes de
tudo porque habilitam a DoD, o pre-commit e o CI. Cada item declara o
custo real, não só o ganho:

```
PLANO DE REMEDIAÇÃO

[1] Instalar sensores de teste e lint
    Por que:   sem eles o agente não verifica o próprio trabalho, e a
               DoD, o pre-commit e o CI não podem ser gerados
    Muda:      pyproject.toml (novas dev-deps), tests/ (diretório novo)
    Comando:   pip install pytest ruff  +  a config abaixo
    Testes propostos: centro_logico(), extrair_json()  [funções puras]
    Atenção:   o entrypoint importa pyautogui/PIL — precisa de conftest
    Risco:     nenhum código de produção é alterado
    [ ] aceitar   [ ] recusar   [ ] adiar

[2] ...
```

Regras de apresentação:

- **Uma linha por arquivo faltante é ruído.** Agrupar por ação: "instalar
  sensores" é um item, não quatro.
- Declarar sempre o que a aceitação **modifica** no repositório. O usuário
  está aprovando uma mudança no projeto dele.
- Explicar o ganho em termos do que o agente passa a poder ou a não poder
  fazer — nunca em pontuação de ferramenta externa.
- Nunca aplicar item recusado ou adiado, e não repropor na mesma sessão.
- Registrar os adiados no `SESSION_STATE.md`, em pendências.
- Se o usuário aceitar sensores, **refazer o preenchimento da DoD** com os
  comandos novos antes de gravar, e gerar o enforcement que passou a ter
  o que verificar.
