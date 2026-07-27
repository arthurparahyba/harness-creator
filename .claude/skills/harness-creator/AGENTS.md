<!-- AGENTS.md COM ESCOPO — vive no diretório de código principal, NÃO na raiz.
     Conhecimento perto do código: só as restrições que valem para este
     subdiretório. Todo o protocolo de sessão fica no AGENTS.md da raiz e
     NUNCA é repetido aqui — duplicado, ele diverge na primeira edição.
     Preencher com convenções REAIS descobertas na FASE 1 — jamais genéricas. -->

# `.claude/skills/harness-creator/` — regras de escopo

Estas regras valem para todo arquivo sob `.claude/skills/harness-creator/`. O protocolo de
sessão está no `AGENTS.md` da raiz.

## Restrições
- MUST NOT: parafrasear o texto dos templates em `resources/` — só os marcadores `<>` mudam
- MUST NOT: gravar com CRLF — os testes reprovam e o gate hook falha aberto
- MUST NOT: renomear marcador em `resources/` sem atualizar `references/` — o teste de órfãos reprova

## Convenções deste diretório
- `references/0N-*.md` é uma fase do fluxo; `references/*.md` sem número é catálogo
consultado sob demanda. Marcador de preenchimento nunca aparece em comentário
de cabeçalho do próprio template — a substituição vaza e corrompe o arquivo.
- Os sensores estão em `tests/test_skill.py`, na raiz.

## Verificação local
Antes de fechar o grupo, o subconjunto deste diretório deve passar:

```
pytest -q
```
