#!/usr/bin/env python3
"""Contrôles du corpus Fos ; lacunes historiques signalées sans les maquiller."""
import json
import re
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit

root=Path(__file__).resolve().parent
def read(path):
    return json.loads((root/path).read_text(encoding='utf-8'))

actors,claims,relations,evidence,sources,timeline=[
    read('data/'+name+'.json') for name in
    ('actors','claims','relations','evidence','sources','timeline')
]
taxonomy=read('config/taxonomy.json')
content=read('data/content.json')
cards=read('data/cards-content.json')
audit=read('data/audit-fos5-20261110.json')
legacy=read('data/legacy-source-gaps-20261110.json')

def indexed(items,what):
    result={x['id']:x for x in items}
    assert len(result)==len(items),f'Identifiants doublons : {what}'
    return result

A=indexed(actors,'acteurs')
C=indexed(claims,'positions')
R=indexed(relations,'relations')
E=indexed(evidence,'preuves')
S=indexed(sources,'sources')
T=indexed(timeline,'apparitions')

assert len(A)==161 and len(C)==160 and len(R)==226
assert len(E)==301 and len(S)==139 and len(T)==160
assert {x['subject_id'] for x in claims}==set(A)-{'project_fos'}
assert all(urlsplit(s['url']).scheme in ('http','https') for s in sources)
for c in claims:
    assert c['subject_id'] in A and c['value'] in taxonomy['stances'],c['id']
    assert all(eid in E for eid in c.get('evidence_ids',[])),c['id']
for r in relations:
    assert r['source_id'] in A and r['target_id'] in A,r['id']
    assert all(eid in E for eid in r.get('evidence_ids',[])),r['id']
for e in evidence:
    assert not e.get('source_id') or e['source_id'] in S,e['id']
    assert all(sid in S for sid in e.get('source_ids',[])),e['id']

def resolvable(eid):
    assert eid in E,eid
    e=E[eid]
    ids=list(e.get('source_ids',[])) + ([e['source_id']] if e.get('source_id') else [])
    return any(sid in S and urlsplit(S[sid].get('url','')).scheme in ('http','https') for sid in ids)

# Le nouveau lot doit être intégralement qualifié, contrairement à certains extraits historiques.
new_evidence=[e for e in evidence if e['id'].startswith('evidence_fos5_')]
assert len(new_evidence)==37, len(new_evidence)
assert all(resolvable(e['id']) for e in new_evidence)
for section in (content['milestones'],content['fact_sheet'],cards['griefs']):
    for item in section:
        assert item.get('evidence_ids') and all(resolvable(eid) for eid in item['evidence_ids']),item['id']
for item in cards['vigilance']:
    assert all(resolvable(eid) for eid in item.get('evidence_ids',[])),item['id']

assert len(cards['griefs'])==17 and len(cards['vigilance'])==25
assert len(content['milestones'])==21 and len(content['fact_sheet'])==9
for event in timeline:
    assert event['actor_id'] in A,event['id']
    assert event['source_ids'] and all(sid in S for sid in event['source_ids']),event['id']
    assert all(eid in E for eid in event.get('evidence_ids',[])),event['id']
    if event['status']=='confirmed':
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',event['date']),event['id']
        assert date.fromisoformat(event['date'])<=date(2026,11,10),event['id']
    else:
        assert event['status']=='undated' and event['date'] is None,event['id']
assert sum(x['status']=='confirmed' for x in timeline)==93

html=(root/'apps/cards/index.html').read_text(encoding='utf-8')
for tab in ('carto','griefs','vigilance','timeline','evolution'):
    assert f'data-tab="{tab}"' in html and f'id="tab-{tab}"' in html,tab
assert len(re.findall(r'data-tab="[^"]+"',html))==5
evo=(root/'assets/js/evolution.js').read_text(encoding='utf-8')
for mode in ('new','cumulative','stance'):
    assert f'data-mode="{mode}"' in evo,mode
assert 'data-scope="direct"' in evo and 'data-scope="all"' in evo
assert audit['total_rows']==100 and audit['after']['evidence']==len(E)
assert audit['sha256']=='1199b664c4c6a1c7ab98f74f7ff044abe8efccfa5c54a32d7032af09a78202d1'

def no_evidence(items):
    return sorted(x['id'] for x in items if not x.get('evidence_ids'))
def legacy_without_source():
    return sorted(x['id'] for x in evidence if not resolvable(x['id']))
assert sorted(legacy['historical_claims_without_evidence'])==no_evidence(claims)
assert sorted(legacy['historical_relations_without_evidence'])==no_evidence(relations)
assert sorted(legacy['historical_vigilances_without_evidence'])==no_evidence(cards['vigilance'])
assert sorted(legacy['legacy_evidence_without_resolvable_source'])==legacy_without_source()
assert legacy['counts']['new_fos5_evidence_without_url']==0
print('VALIDATION OK : 100 ressources, 9 nouveaux acteurs, 37 nouvelles preuves qualifiées, 5 onglets.')
print('ALERTE passif historique non qualifié :',legacy['counts'])
