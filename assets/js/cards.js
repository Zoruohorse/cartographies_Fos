import{loadRepository,esc,norm,actorClaim,evidenceHtml}from'./data-loader.js';const d=await loadRepository();const cardActors=d.actors.filter(a=>a.id!==d.meta.network_center_id);let cat='all',stance='all',q='';title.textContent=d.meta.title;subtitle.textContent=d.meta.subtitle;notice.textContent=d.meta.data_notice;const stanceColor=s=>d.taxonomy.stances[s]?.color||'#64748b';function filters(){categories.innerHTML=Object.entries(d.taxonomy.categories).filter(([k])=>k!=='project').map(([k,v])=>`<button class="filter ${cat===k?'active':''}" data-cat="${k}"><span>${esc(v.label)}</span><b>${k==='all'?cardActors.length:cardActors.filter(a=>a.categories.includes(k)).length}</b></button>`).join('');stances.innerHTML=Object.entries(d.taxonomy.stances).map(([k,v])=>`<button class="filter ${stance===k?'active':''}" data-stance="${k}"><span>${esc(v.label)}</span><b>${k==='all'?d.claims.length:d.claims.filter(c=>c.value===k).length}</b></button>`).join('')}function render(){const list=cardActors.filter(a=>{const c=actorClaim(d,a.id);const text=norm([a.name,a.description,c?.summary,...(c?.evidence_ids||[]).map(id=>d.evidenceById.get(id)?.text)].join(' '));return(cat==='all'||a.categories.includes(cat))&&(stance==='all'||c?.value===stance)&&(!q||text.includes(q))});count.textContent=`${list.length} acteurs affichés sur ${cardActors.length}`;grid.innerHTML=list.map(a=>{const c=actorClaim(d,a.id);return `<article class="card" data-id="${a.id}" style="--stance:${stanceColor(c?.value)}"><h3>${esc(a.name)}</h3><div class="role">${esc(a.description)}</div><p class="position">${esc(c?.summary||'Position non renseignée')}</p><div class="footer"><span class="badge">${esc(d.taxonomy.stances[c?.value]?.label||'Non qualifié')}</span><span>Certitude : ${esc(d.taxonomy.certainty_levels[c?.certainty]?.label||'Non qualifiée')}</span></div></article>`}).join('')}function open(id){const a=d.actorById.get(id),c=actorClaim(d,id);const rel=d.relations.filter(r=>r.source_id===id||r.target_id===id);detail.innerHTML=`<h2>${esc(a.name)}</h2><p class="role">${esc(a.description)}</p><h3>Position</h3><p>${esc(c?.summary||'Non renseignée')}</p><p><b>Certitude :</b> ${esc(d.taxonomy.certainty_levels[c?.certainty]?.label||'Non qualifiée')}</p><h3>Preuves et sources</h3>${evidenceHtml(d,c?.evidence_ids)}<h3>Relations documentables</h3>${rel.length?rel.map(r=>{const other=d.actorById.get(r.source_id===id?r.target_id:r.source_id);return `<div class="relation"><button data-open="${other?.id}">${esc(other?.name||'Acteur inconnu')}</button><div><b>${esc(d.taxonomy.relation_types[r.type]?.label||r.type)}</b></div><p>${esc(r.summary)}</p><small>Certitude : ${esc(d.taxonomy.certainty_levels[r.certainty]?.label||r.certainty)} · ${r.evidence_ids.length} preuve(s)</small></div>`}).join(''):'<p class="muted">Aucune relation.</p>'}`;dialog.showModal()}document.addEventListener('click',e=>{const c=e.target.closest('[data-cat]'),s=e.target.closest('[data-stance]'),card=e.target.closest('.card'),op=e.target.closest('[data-open]');if(c){cat=c.dataset.cat;filters();render()}if(s){stance=s.dataset.stance;filters();render()}if(card)open(card.dataset.id);if(op)open(op.dataset.open)});search.addEventListener('input',e=>{q=norm(e.target.value);render()});reset.onclick=()=>{cat='all';stance='all';q='';search.value='';filters();render()};document.querySelector('.close').onclick=()=>dialog.close();filters();render();


// Les synthèses sont propres à la vue cartes : aucun changement du chargeur réseau.
const byId = id => document.getElementById(id);
const tabButtons = [...document.querySelectorAll('[role="tab"]')];
function switchCardsTab(name, focus = false) {
  if (!tabButtons.some(button => button.dataset.tab === name)) return;
  tabButtons.forEach(button => {
    const active = button.dataset.tab === name;
    button.classList.toggle('active', active);
    button.setAttribute('aria-selected', String(active));
    button.tabIndex = active ? 0 : -1;
    if (active && focus) button.focus();
  });
  document.querySelectorAll('[role="tabpanel"]').forEach(panel => {
    const active = panel.id === `tab-${name}`;
    panel.hidden = !active;
    panel.classList.toggle('active', active);
  });
}
tabButtons.forEach((button, index) => {
  button.addEventListener('click', () => switchCardsTab(button.dataset.tab));
  button.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabButtons.length;
    if (event.key === 'ArrowLeft') next = (index + tabButtons.length - 1) % tabButtons.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabButtons.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      switchCardsTab(tabButtons[next].dataset.tab, true);
    }
  });
});

function documentaryHtml(item) {
  const evidenceIds = item.evidence_ids || [];
  const cited = new Set(evidenceIds.flatMap(id => {
    const evidence = d.evidenceById.get(id);
    return evidence?.source_ids || evidence?.sourceIds || (evidence?.source_id ? [evidence.source_id] : []);
  }));
  const sources = [...new Set(item.source_ids || [])].filter(id => !cited.has(id)).map(id => d.sourceById.get(id)).filter(Boolean);
  return (evidenceIds.length ? evidenceHtml(d, evidenceIds) : '') + (sources.length ? `<article class="proof"><div>Sources complémentaires</div><small>${sources.map(source => source.url ? `<a target="_blank" rel="noopener" href="${esc(source.url)}">${esc(source.title || source.publisher)}</a>` : esc(source.title || source.publisher)).join(' · ')}</small></article>` : '');
}

function renderCardsSources() {
  byId('sources-count').textContent = `${d.sources.length} notices de sources issues du fichier fourni. Les URL absentes restent à compléter.`;
  byId('sources-list').innerHTML = d.sources.map(source => {
    const metadata = [source.publisher, source.source_type, source.published_at || source.date, source.sourceStatus].filter(Boolean).map(esc).join(' · ');
    const title = source.url ? `<a class="source-link" target="_blank" rel="noopener" href="${esc(source.url)}">${esc(source.title)}</a>` : esc(source.title);
    return `<article class="source-item" id="source-${esc(source.id)}"><h3>${title}</h3><div class="source-meta">${metadata}</div>${source.description ? `<p>${esc(source.description)}</p>` : ''}${source.url ? '' : '<span class="source-status">URL à compléter</span>'}</article>`;
  }).join('') || '<p class="muted">Aucune source renseignée.</p>';
}

async function loadCardsContent() {
  try {
    const response = await fetch('../../data/cards-content.json?v=20261009-fos');
    if (!response.ok) throw new Error(`cards-content.json : HTTP ${response.status}`);
    const content = await response.json();
    byId('griefs-intro').textContent = content.intro || '';
    byId('griefs-grid').innerHTML = (content.griefs || []).map(item => `<article class="grief-card"><h2>${esc(item.title)}</h2><p>${esc(item.text)}</p>${(item.evidence_ids?.length || item.source_ids?.length) ? '<h3>Éléments documentaires</h3>' + documentaryHtml(item) : ''}</article>`).join('') || '<div class="list-card">Aucun axe d’opposition renseigné.</div>';
    const items = content.vigilance || [];
    byId('vigilance-count').textContent = `${items.length} points issus du fichier Fos-Jonquières. Les formulations du document fourni sont conservées.`;
    byId('vigilance-list').innerHTML = items.map(item => `<article class="vigilance-item"><h3>${esc(item.title)}</h3><div class="vigilance-meta">${esc(item.id)}</div><p>${esc(item.text)}</p>${item.available_elements && item.available_elements !== 'Voir preuves associées' ? `<p><b>Éléments disponibles :</b> ${esc(item.available_elements)}</p>` : ''}${documentaryHtml(item) || '<p class="muted">Aucune référence documentaire rattachée à ce point dans le corpus.</p>'}</article>`).join('') || '<p class="muted">Aucun point de vigilance renseigné.</p>';
  } catch (error) {
    byId('griefs-intro').textContent = 'La synthèse n’a pas pu être chargée. Vérifiez la présence du fichier data/cards-content.json.';
    byId('vigilance-list').innerHTML = '<p class="muted">Les points de vigilance n’ont pas pu être chargés. Vérifiez la présence du fichier data/cards-content.json.</p>';
    console.error(error);
  }
}
renderCardsSources();
await loadCardsContent();
