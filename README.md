# Cartographie Fos-Jonquières — modèle Fouju

## Installation

Décompresser `Fos_Jonquieres_GitHub.zip`, puis déposer **tout le contenu extrait à la racine du dépôt GitHub**, en remplaçant les fichiers de même chemin. Ne pas déposer le ZIP seul. Le fichier `index.html` doit être à la racine, à côté de `apps`, `assets`, `config` et `data`.

Avec GitHub Pages configuré sur la branche du dépôt et son dossier racine, attendre la publication puis recharger avec Ctrl + F5.

## Vues

- Accueil : accès aux cartes et au réseau.
- Cartes : recherche, filtres, fiches, extraits, relations, synthèse des oppositions et points de vigilance et sources.
- Réseau : moteur, physique, zoom, déplacement des points, panneaux et styles de la version Fouju/Opcore validée.

## Données conservées

Le fichier transmis contenait deux pages HTML et un objet réseau séparé : 86 fiches, 112 nœuds et 211 relations. Les listes n’étaient pas identiques. Elles ont été réunies dans un référentiel de 147 entrées, dont le projet central (146 fiches visibles).

Les noms strictement identiques sont fusionnés. Deux correspondances explicites sont appliquées : « Sauvegarde terres Camargue-Crau » / « Association sauvegarde terres Camargue-Crau » et « Context d’évaluation (CNDP) » / « CNDP ». Les fiches collectives (Collard, experts RTE, biodiversité, syndicats agricoles) restent distinctes des personnes et organismes individuels ; elles ne doivent pas être comptées comme des personnes supplémentaires.

Les positions et certitudes des fiches sont reprises telles quelles, y compris lorsqu’une ancienne description réseau diverge. La description réseau originale reste conservée dans `original_graph`. Pour les entrées uniquement présentes dans le réseau, aucune position ou certitude n’est déduite automatiquement de leur famille. Leurs descriptions restent visibles et leur position est signalée comme non renseignée.

Les 211 relations existantes sont conservées sans ajout. Les acteurs des cartes absents de l’ancien réseau sont inclus, mais restent sans liens tant que ceux-ci ne sont pas documentés. Les groupes détaillés et tailles de l’ancien réseau sont conservés dans les données ; l’affichage utilise les catégories et la règle de taille du modèle Fouju.

Les 11 synthèses, 13 vigilances et 10 notices de sources sont conservées. Les textes n’ont pas fait l’objet d’une vérification factuelle externe. Les extraits rattachés aux thèmes proviennent des fiches du fichier fourni ; aucun URL d’article n’était présent, aucun n’a été inventé. Les marqueurs `[cite: ...]` du réseau d’origine ne constituent pas des URL résolues.

## Modifier les contenus

- `data/actors.json` : identités, rôles et catégories.
- `data/claims.json` : positions, résumés, certitudes, références aux extraits.
- `data/evidence.json` : extraits et références aux sources.
- `data/relations.json` : liens entre acteurs.
- `data/sources.json` : notices, descriptions et URL à compléter.
- `data/cards-content.json` : synthèse des oppositions et vigilances.
- `data/original-input.json` : données d’origine conservées pour comparaison.

## Test local

```bash
python3 validate.py
python3 -m http.server 8000
```

Ouvrir http://localhost:8000. L’ouverture directe en file:// ne permet pas le chargement des JSON.

## Vérifications réalisées

Syntaxe des scripts, unicité des identifiants, références entre fichiers, conservation des données d’origine et comparaison des styles et du moteur avec le modèle accepté. Tests dans un DOM simulé : navigation des trois onglets, recherche, filtres, réinitialisation, fiches acteurs, affichage des extraits, sélection réseau, fermeture du panneau, recentrage et 60 étapes de simulation sans coordonnées invalides. Aucun contrôle visuel dans un navigateur réel n’a été réalisé.
