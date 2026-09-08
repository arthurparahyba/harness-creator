---
topic: memoria-do-harness
goal: memlog + knowledge no harness gerado
updated: 2026-09-08T16:15
---

- (decisao) memlog em POSIX sh para valer nos 3 agentes, nao bash
- (decisao) append auto-inicia se o arquivo nao existe: friccao zero, nunca falha por falta de init
- (descoberta) o gate destrutivo do proprio repo barrou a limpeza do smoke-test; usei mktemp (dogfooding)
- (descoberta) o gate casa o padrao no TEXTO do comando mesmo quando o padrao vai como DADO de um append; limitacao conhecida do gate
- (decisao) sensores testam COMPORTAMENTO (verbo invalido da exit 2), nao grep de palavra que casava os comentarios
- (achado) o sensor de catalogo pegou memlog.sh fora de arquivos-gerados.md; corrigido
- (nota) Grupo 1 DoD verde: pytest 938, ruff, mypy, check-arch 7 de 7
- (nota) handoff registrado
- (grupo) Grupo 2: base knowledge/
- (decisao) knowledge/ e conhecimento de COMPONENTE (revisavel), oposto ao memlog (append); disciplinas separadas
- (decisao) AGENTS so aponta o knowledge/README.md; o formato (derivado_de, Prova) mora no README, nao inline
- (decisao) obsolescencia por Prova re-rodavel + proveniencia (derivado_de + baseline_commit), do cache epic-context do BMAD
- (decisao) fontes de investigacao numa secao do README, preenchida pelo time; dirige investigacoes futuras
- (achado) sensor do passo 3 (Grupo 48) checa a quebra de linha exata do texto; meu reflow reprovou. Ajustei o texto, nao o sensor (nao remendar guard)
- (nota) Grupo 2 DoD verde: pytest 942, ruff, mypy, check-arch 7 de 7
