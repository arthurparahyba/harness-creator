#!/usr/bin/env bash
# compare-harness.sh — Delta antes/depois da skill harness-creator
#
# Uso:
#   ./eval/score-harness.sh /repo --json > antes.json
#   # (roda a skill harness-creator no repo)
#   ./eval/score-harness.sh /repo --json > depois.json
#   ./eval/compare-harness.sh antes.json depois.json [--md]
#
# Saida: lift do Indice de Prontidao, lift por subsistema, capacidades
# adquiridas / perdidas, e o que a skill NAO resolveu (lacuna residual).

set -o pipefail

if [[ $# -lt 2 ]]; then
  echo "uso: $0 antes.json depois.json [--md]" >&2
  exit 2
fi

python3 - "$@" <<'PY'
import json, sys

before_p, after_p = sys.argv[1], sys.argv[2]
md = "--md" in sys.argv[3:]

b = json.load(open(before_p))
a = json.load(open(after_p))

bi = {c["id"]: c for c in b["checks"]}
ai = {c["id"]: c for c in a["checks"]}

gained  = [i for i in ai if ai[i]["status"] in ("pass", "eq") and bi.get(i, {}).get("status") == "fail"]
lost    = [i for i in ai if ai[i]["status"] == "fail" and bi.get(i, {}).get("status") in ("pass", "eq")]
residual= [i for i in ai if ai[i]["status"] == "fail"]
equiv   = [i for i in ai if ai[i]["status"] == "eq"]

def order(ids):
    seq = [c["id"] for c in a["checks"]]
    return sorted(ids, key=seq.index)

delta = a["score"] - b["score"]
crit_delta = a["critical_ok"] - b["critical_ok"]
# Eficacia = fracao das lacunas iniciais que a skill fechou
gaps_before = sum(1 for c in b["checks"] if c["status"] == "fail")
closure = (len(gained) / gaps_before * 100) if gaps_before else 100.0
crit_gaps_before = sum(1 for c in b["checks"] if c["status"] == "fail" and c["severity"] == "crit")
crit_closed = sum(1 for i in gained if ai[i]["severity"] == "crit")
crit_closure = (crit_closed / crit_gaps_before * 100) if crit_gaps_before else 100.0

H = "## " if md else ""
B = "**" if md else ""

print(f"{H}Delta de prontidao — {b['repo']}")
print()
print(f"  Indice de Prontidao : {b['score']}  ->  {a['score']}   ({delta:+d} pontos)")
print(f"  Capacidades criticas: {b['critical_ok']}/{b['critical_total']}  ->  {a['critical_ok']}/{a['critical_total']}   ({crit_delta:+d})")
print(f"  Nivel               : {b['level']}  ->  {a['level']}")
print()
print(f"  {B}Taxa de fechamento de lacunas{B}      : {closure:.0f}%  ({len(gained)}/{gaps_before})")
print(f"  {B}Taxa de fechamento de CRITICAS{B}     : {crit_closure:.0f}%  ({crit_closed}/{crit_gaps_before})")
print(f"  Capacidades por equivalencia         : {len(equiv)}  (nome diverge do curso)")
print(f"  Lacuna residual (pos-skill)          : {len(residual)}")
if lost:
    print(f"  REGRESSAO                            : {len(lost)}")
print()

print(f"{H}Por subsistema")
for k in a["subsystems"]:
    pb, pa = b["subsystems"][k]["pct"], a["subsystems"][k]["pct"]
    bar = "#" * (pa // 10) + "." * (10 - pa // 10)
    print(f"  {k:<16} [{bar}] {pb:3d}% -> {pa:3d}%  ({pa - pb:+d})")
print()

def dump(title, ids, show_fix=False):
    if not ids:
        return
    print(f"{H}{title} ({len(ids)})")
    for i in order(ids):
        c = ai[i]
        line = f"  {i}  {c['description']}"
        if show_fix and c.get("fix"):
            line += f"\n       -> {c['fix']}"
        elif c.get("evidence"):
            line += f"   ({c['evidence']})"
        print(line)
    print()

dump("Capacidades adquiridas pela skill", gained)
dump("Cobertas por artefato nao-canonico", equiv)
dump("Lacuna residual — a skill NAO resolveu", residual, show_fix=True)
dump("REGRESSAO — capacidade perdida", lost)

# Veredito
if crit_gaps_before and crit_closed < crit_gaps_before:
    print("VEREDITO: a skill nao levou o repo ao minimo operavel (criticas em aberto).")
elif closure >= 80:
    print("VEREDITO: a skill fecha a maior parte das lacunas de prontidao neste repo.")
elif closure >= 50:
    print("VEREDITO: ganho substancial, mas resta remediacao manual relevante.")
else:
    print("VEREDITO: ganho limitado neste repo — investigar por que a descoberta nao pegou.")
PY
