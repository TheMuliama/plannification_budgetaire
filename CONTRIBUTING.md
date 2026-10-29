# Contribuer à la planification budgétaire

Ce guide définit les règles communes pour proposer, développer et relire les contributions. Les échanges, la documentation et les descriptions de commits sont rédigés en français ; les types de commits et les préfixes de branches restent en anglais.

## 1. Préparer une contribution

Consulter les [issues](https://github.com/TheMuliama/plannification_budgetaire/issues) et les pull requests ouvertes pour éviter les doublons.

- Pour une fonctionnalité ou une modification importante, ouvrir une issue avant de développer et convenir du périmètre avec l'équipe.
- Pour un bug, indiquer les étapes de reproduction, le résultat attendu, le résultat obtenu et l'environnement utilisé.
- Pour une proposition, décrire le besoin et les critères permettant de considérer le travail comme terminé.
- Signaler dans l'issue que l'on prend le sujet en charge.
- Une correction mineure de documentation peut être proposée directement par pull request.

Une contribution doit répondre à un objectif précis. Séparer les changements sans rapport en plusieurs pull requests.

## 2. Organisation du projet

Respecter les responsabilités des dossiers existants :

| Dossier | Responsabilité |
| --- | --- |
| `client/interface/` | Interface utilisateur |
| `client/communication/` | Communication du client avec le serveur |
| `serveur/communication/` | Réception et traitement des échanges réseau |
| `serveur/services/` | Règles métier : budgets, dépenses, revenus, projections… |
| `serveur/securite/` | Fonctions de sécurité |
| `persistance/repositories/` | Accès aux données |
| `persistance/schema.sql` | Définition du schéma de base de données |
| `tests/` | Tests automatisés |

Conserver l'orthographe actuelle de `persistance/` dans les chemins et les imports. Toute réorganisation doit faire l'objet d'une discussion préalable.

## 3. Branches et déroulement du travail

`main` est la branche d'intégration commune. Toute modification passe par une branche de travail puis une pull request vers `main`. Nous n'utilisons pas de branche `develop` permanente.

### Nommer une branche

Format commun : `<type>/<numero-issue>-<description-courte>`.

- Utiliser des minuscules, sans accents ni espaces, et des tirets entre les mots.
- Choisir un préfixe parmi `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `chore` ou `style`.
- Omettre le numéro lorsqu'aucune issue n'est nécessaire.
- Créer une branche par objectif et la supprimer après fusion.

Exemples fictifs :

```text
feat/42-ajout-budget-mensuel
fix/57-calcul-solde
docs/guide-installation
```

Le préfixe décrit l'objectif de la branche. Les commits qu'elle contient peuvent avoir des types différents, par exemple `feat` et `test`.

### Démarrer et publier son travail

Avec un accès en écriture au dépôt :

```bash
git clone https://github.com/TheMuliama/plannification_budgetaire.git
cd plannification_budgetaire
git switch main
git pull --ff-only origin main
git switch -c feat/42-ajout-budget-mensuel
```

Après avoir modifié et vérifié les fichiers :

```bash
git add -p
git diff --cached
git commit -m "feat(budget): ajouter la création d'un budget mensuel"
git push -u origin feat/42-ajout-budget-mensuel
```

Sans accès en écriture, utiliser un fork et ouvrir la pull request vers le dépôt d'origine.

Si `main` évolue pendant le travail, intégrer ses changements dans la branche :

```bash
git fetch origin
git merge origin/main
```

Résoudre les conflits, puis relancer les vérifications. Ne pas réécrire l'historique d'une branche partagée sans coordination avec les autres contributeurs.

## 4. Convention des commits

Nous suivons [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), présenté dans le [guide de Stéphane Robert](https://www.stephane-robert.info/docs/developper/conventional-commits/).

```text
type(portee): description

Corps facultatif expliquant le contexte et la raison du changement.

Refs: #42
```

La portée est facultative. Employer un nom court : `client`, `serveur`, `persistance`, `budget`, `categories`, `securite` ou `deps`.

| Type | Usage |
| --- | --- |
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction d'un bug |
| `docs` | Documentation |
| `refactor` | Réorganisation du code sans changement de comportement |
| `test` | Ajout ou modification de tests |
| `perf` | Amélioration des performances |
| `style` | Formatage du code sans effet sur son comportement |
| `build` | Dépendances ou construction du projet |
| `ci` | Intégration continue |
| `chore` | Maintenance non couverte par les autres types |
| `revert` | Annulation d'un changement |

Règles propres au projet : description en français, à l'infinitif, sans point final ; titre idéalement inférieur à 72 caractères ; un objectif cohérent par commit. Éviter les messages vagues comme « update » ou « corrections ».

```text
fix(budget): exclure les dépenses annulées du solde
docs: expliquer la configuration locale
test(categories): vérifier l'isolation entre utilisateurs
```

Pour une incompatibilité, utiliser `!` et expliquer la migration dans un pied de message `BREAKING CHANGE:`. Exemple hypothétique :

```text
feat(persistance)!: stocker les montants en centimes

BREAKING CHANGE: les montants sont désormais des entiers en centimes.
Migrer les données existantes avant de démarrer cette version.
```

Le corps explique notamment les choix et leurs conséquences. Les types supplémentaires et les règles de langue sont des choix d'équipe, pas des obligations de la spécification.

## 5. Qualité du code et vérifications

- Suivre le style des modules voisins : indentation Python de quatre espaces, noms explicites en `snake_case`, annotations de types et docstrings utiles.
- Garder les règles métier dans les services et l'accès aux données dans les repositories.
- Déclarer les nouvelles dépendances d'exécution dans `requirements.txt` et documenter les outils de développement nécessaires.
- Ajouter des tests pertinents pour les nouveaux comportements et les corrections de bugs.
- Pour les calculs budgétaires, vérifier les valeurs nulles, les limites, les arrondis et les totaux.
- Pour les données par utilisateur, vérifier qu'un utilisateur ne peut pas consulter ou modifier celles d'un autre.
- Utiliser des données fictives et une base de test isolée. Ne pas publier de mots de passe, de factures réelles ou de données financières personnelles, notamment dans `persistance/data/`.
- Documenter les changements de schéma et la procédure de migration lorsqu'elle est nécessaire.

Depuis la racine du dépôt, préparer un environnement local sous Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest
git diff --check
```

Les tests existants utilisent `pytest`, qui doit actuellement être installé séparément. Le projet est en construction : si une vérification échoue, indiquer la commande, le résultat et les éventuels échecs déjà présents sur `main`. Pour l'interface, compléter les tests par un scénario manuel et, si utile, une capture d'écran.

## 6. Changelog

Le fichier `CHANGELOG.md`, à la racine, suit [Keep a Changelog 1.0.0](https://keepachangelog.com/en/1.0.0/). Il décrit les changements notables pour les utilisateurs et les personnes qui installent ou maintiennent l'application.

### Pendant le développement

**Chaque pull request apportant un changement notable met à jour la section `Unreleased` dans sa propre branche.** L'entrée est fusionnée avec le code sur `main`. Il n'existe qu'un changelog commun au projet, pas un fichier distinct par branche.

- Décrire l'effet concret, sans recopier la liste des commits.
- Utiliser les rubriques `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` et `Security` selon le besoin ; garder les descriptions en français.
- Ne créer que les rubriques contenant des entrées.
- Ajouter si possible un lien vers l'issue ou la pull request.
- Une correction typographique, un test ou un refactoring sans effet notable ne nécessite généralement pas d'entrée ; expliquer ce choix dans la PR.
- Ne pas créer de version ni dater `Unreleased` dans une branche de fonctionnalité.

Exemple fictif d'entrée :

```markdown
## [Unreleased]

### Added

- Création de budgets mensuels avec une limite de dépenses.

### Fixed

- Les dépenses annulées ne sont plus comptées dans le solde disponible.
```

Si deux branches modifient les mêmes lignes, intégrer la dernière version de `main`, conserver les deux changements pertinents et regrouper les rubriques identiques. Ne jamais résoudre le conflit en supprimant les entrées de l'autre contribution.

### Au moment d'une livraison

La personne responsable prépare une PR de livraison depuis `main` :

1. Relire `Unreleased` et vérifier que les entrées correspondent aux changements intégrés.
2. Regrouper les doublons et expliquer les incompatibilités et migrations éventuelles.
3. Déplacer ces entrées sous un titre de version daté : `## [X.Y.Z] - AAAA-MM-JJ`.
4. Conserver `Unreleased` au-dessus pour les prochains changements et actualiser les liens de comparaison entre versions.
5. Après validation et fusion, créer le tag `vX.Y.Z` sur le commit de livraison et publier la release correspondante.

Les versions les plus récentes apparaissent en premier. Une version publiée n'est pas renommée pour y intégrer de nouveaux développements.

## 7. Pull requests et relecture

Ouvrir une PR vers `main`, éventuellement en brouillon dès le début pour recueillir des retours. Son titre suit la même convention que les commits.

La description précise :

- le problème ou besoin et le comportement obtenu ;
- l'issue associée, avec `Closes #42` si la PR la résout entièrement ;
- les vérifications effectuées et leurs résultats ;
- les conséquences éventuelles sur les données et la configuration ;
- l'entrée de changelog ajoutée, ou la raison de son absence.

Avant de demander la relecture :

- [ ] Le périmètre est clair et le diff ne contient aucun changement accidentel.
- [ ] Les commits respectent la convention.
- [ ] Les tests pertinents ont été exécutés et les résultats sont indiqués.
- [ ] La documentation et le changelog sont à jour si nécessaire.
- [ ] Aucun secret ni donnée personnelle n'est inclus.
- [ ] Les conflits avec `main` sont résolus.

Une autre personne de l'équipe relit la PR avant fusion. Les remarques portent sur le code et sont formulées avec respect. Les discussions bloquantes doivent être résolues et les vérifications disponibles doivent réussir.

Le mode de fusion recommandé est **Squash and merge** : vérifier que le message du commit final suit Conventional Commits et conserve toute mention `BREAKING CHANGE` utile. Après fusion, supprimer la branche de travail et synchroniser son `main` local.

Ces règles constituent la convention de l'équipe. Leur contrôle automatique et la protection de `main` doivent être configurés séparément dans GitHub.
