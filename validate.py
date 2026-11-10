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


# Validation renforcée après le lot Fos(5), 10 novembre 2026.
from datetime import date
from urllib.parse import urlsplit
import re
S=load("data/sources.json");T=load("data/timeline.json");D=load("data/content.json")
Q=load("data/cards-content.json");Tax=load("config/taxonomy.json")
Audit=load("data/audit-fos5-20261110.json")
def uniq(rows,label):
 out={x["id"]:x for x in rows}
 assert len(out)==len(rows), "doublon "+label
 return out
src=uniq(S,"sources");events=uniq(T,"timeline");ev=uniq(e,"preuves")
assert len(A)==161 and len(c)==160 and len(r)==226 and len(e)==301 and len(S)==139
assert len(T)==160 and len(D["milestones"])==21 and len(D["fact_sheet"])==9
assert len(Q["griefs"])==17 and len(Q["vigilance"])==25
for event in T:
 assert event["actor_id"] in A,event["id"]
 assert event["stance"] in Tax["stances"] and event["stance"]!="all",event["id"]
 assert event["scope"] in ("direct","context","excluded"),event["id"]
 assert event["source_ids"] is not None,event["id"]
 assert set(event["evidence_ids"]) <= ev.keys(),event["id"]
 assert set(event["source_ids"]) <= src.keys(),event["id"]
 if event["status"]=="confirmed":
  assert event["date"],event["id"]
  if event["date_precision"]=="month":
   assert re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])",event["date"])
  else:
   assert event["date_precision"]=="day",event["id"]
   date.fromisoformat(event["date"])
  assert event["date"]<="2026-11-10",event["id"]
 else:
  assert event["status"]=="undated" and event["date"] is None,event["id"]
for row in D["milestones"]+D["fact_sheet"]+Q["griefs"]+Q["vigilance"]:
 for eid in row.get("evidence_ids",[]):
  assert eid in ev,eid
  e0=ev[eid]
  source_ids=set(e0.get("source_ids",[]))
  if e0.get("source_id"): source_ids.add(e0["source_id"])
  assert any((sid in src and urlsplit(src[sid].get("url","")).scheme in ("http","https")) for sid in source_ids),eid
for item in S:
 if item["id"].startswith("source_fos5_"):
  assert urlsplit(item.get("url","")).scheme=="https",item["id"]
for row in Audit["row_by_row"]:
 assert 2 <= row["excel_row"] <=101,row["excel_row"]
assert len(Audit["row_by_row"])==100
assert sorted(x["excel_row"] for x in Audit["row_by_row"])==list(range(2,102))
assert sum(x["status"]=="confirmed" for x in T)==93
for name in ("carto","griefs","vigilance","timeline","evolution"):
 page=(root/"apps/cards/index.html").read_text(encoding="utf-8")
 assert f'data-tab="{name}"' in page and f'<section id="tab-{name}"' in page,name
for file in ("assets/js/evolution.js","assets/css/evolution.css"):
 assert (root/file).is_file(),file
widget=(root/"assets/js/evolution.js").read_text(encoding="utf-8")
for mode in ("new","cumulative","stance"):
 assert f'data-mode="{mode}"' in widget,mode
assert "timeline:\"data/timeline.json\"" in (root/"assets/js/data-loader.js").read_text(encoding="utf-8")
print("FOS LOT5 OK : 100 lignes, 161 noeuds, 160 positions, 226 relations, 21 jalons, 9 repères, 93 acteurs datés, 5 onglets.")
