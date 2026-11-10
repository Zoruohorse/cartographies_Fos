#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parent
def read(path):
    return json.loads((root/path).read_text(encoding='utf-8'))
actors,claims,relations,evidence,sources,timeline=[read('data/'+n+'.json') for n in ('actors','claims','relations','evidence','sources','timeline')]
taxonomy=read('config/taxonomy.json')
content=read('data/content.json')
cards_content=read('data/cards-content.json')

# Validation étendue, 10 novembre 2026 : référentiel sourcé et navigation.
import re
from datetime import date
from urllib.parse import urlsplit
def qualified_sources(ids, owner):
    assert ids, f'Preuves absentes : {owner}'
    for eid in ids:
        assert eid in ev_by_id, f'Preuve inconnue {eid} : {owner}'
        ev = ev_by_id[eid]
        src_ids = list(ev.get('source_ids', [])) + ([ev['source_id']] if ev.get('source_id') else [])
        assert src_ids, f'Source absente {eid}'
        for sid in src_ids:
            assert sid in src_by_id and urlsplit(src_by_id[sid]['url']).scheme in ('http', 'https'), f'URL manquante : {sid}'
actors_by_id={x['id']:x for x in actors}
assert len(actors_by_id)==len(actors), "Acteur en double"
claim_by_id={x['id']:x for x in claims}
assert len(claim_by_id)==len(claims), "Position en double"
ev_by_id={x['id']:x for x in evidence}
src_by_id={x['id']:x for x in sources}
assert len(ev_by_id)==len(evidence)
assert len(src_by_id)==len(sources)
assert len({x['id'] for x in relations})==len(relations)
assert len(actors)==161 and len(claims)==160 and len(relations)==226
assert len(evidence)==301 and len(sources)==139
assert {x['subject_id'] for x in claims}==set(actors_by_id)-{'project_fos'}
for item in claims:
    assert item['subject_id'] in actors_by_id and item['value'] in taxonomy['stances'],item['id']
    qualified_sources(item['evidence_ids'],item['id'])
for item in relations:
    assert item['source_id'] in actors_by_id and item['target_id'] in actors_by_id,item['id']
    qualified_sources(item['evidence_ids'],item['id'])
for item in evidence:
    assert item.get('source_id') in src_by_id or any(x in src_by_id for x in item.get('source_ids',[])),item['id']
for section in (content['milestones'],content['fact_sheet'],cards_content['griefs'],cards_content['vigilance']):
    for item in section:
        qualified_sources(item['evidence_ids'],item.get('id',item.get('title')))
for x in timeline:
    assert x['actor_id'] in actors_by_id, x['id']
    if x['status']=='confirmed':
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',x['date']),x['id']
        assert date.fromisoformat(x['date'])<=date(2026,11,10),x['id']
assert len({x['actor_id'] for x in timeline})==len(timeline)==160
assert len([x for x in timeline if x['status']=='confirmed'])==93
page=(root/'apps/cards/index.html').read_text(encoding='utf-8')
for tab in ('carto','griefs','vigilance','timeline','evolution'):
    assert f'data-tab="{tab}"' in page and f'id="tab-{tab}"' in page,tab
assert len(re.findall(r'data-tab="[^"]+"',page))==5
graph=(root/'assets/js/evolution.js').read_text(encoding='utf-8')
for mode in ('new','cumulative','stance'):
    assert f'data-mode="{mode}"' in graph,mode
assert 'data-scope="direct"' in graph and 'data-scope="all"' in graph
assert len(cards_content['griefs'])==17 and len(cards_content['vigilance'])==25
assert len(content['milestones'])==21 and len(content['fact_sheet'])==9
audit=read('data/audit-fos5-20261110.json')
assert audit['total_rows']==100 and audit['after']['evidence']==len(evidence)
print('VALIDATION ÉTENDUE OK : 100 ressources examinées ; 161 nœuds, 160 positions, 226 relations, 301 preuves, 139 sources, 5 onglets.')
