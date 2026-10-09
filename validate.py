import json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
load=lambda p:json.loads((root/p).read_text(encoding="utf-8"))
a=load("data/actors.json");c=load("data/claims.json");e=load("data/evidence.json");r=load("data/relations.json")
ids=[x["id"] for x in a]; assert len(ids)==len(set(ids)),"IDs acteurs dupliques"
A=set(ids); E={x["id"] for x in e}
for x in c: assert x["subject_id"] in A; assert set(x.get("evidence_ids",[]))<=E
for x in r: assert x["source_id"] in A and x["target_id"] in A; assert set(x.get("evidence_ids",[]))<=E
print(f"OK: {len(a)} acteurs, {len(c)} positions, {len(r)} relations, {len(e)} preuves")
