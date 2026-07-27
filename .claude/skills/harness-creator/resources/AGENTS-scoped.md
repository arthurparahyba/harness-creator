<!-- AGENTS.md COM ESCOPO — vive no diretório de código principal, NÃO na raiz.
     Conhecimento perto do código: só as restrições que valem para este
     subdiretório. Todo o protocolo de sessão fica no AGENTS.md da raiz e
     NUNCA é repetido aqui — duplicado, ele diverge na primeira edição.
     Preencher com convenções REAIS descobertas na FASE 1 — jamais genéricas. -->

# `<caminho>/` — regras de escopo

Estas regras valem para todo arquivo sob `<caminho>/`. O protocolo de
sessão está no `AGENTS.md` da raiz.

## Restrições
- MUST NOT: <restrição 1 — a mesma de "Regras de trabalho" do AGENTS.md raiz>
- MUST NOT: <restrição 2>
- MUST NOT: <restrição 3>

## Convenções deste diretório
- <padrão de acesso a dados, camadas ou nomenclatura descoberto na FASE 1>
- <onde vivem os testes deste código>

## Verificação local
Antes de fechar o grupo, o subconjunto deste diretório deve passar:

```
<comando que valida apenas este subdiretório, ex: pytest tests/unit>
```
