# Changelog

## [Unreleased]

### Changed

- Réaligner l'architecture sur les neuf modules métier d'origine : le
  calculateur centralise désormais le solde, les états budgétaires et la
  capacité d'épargne, tandis que les projections et alertes consomment ces
  états côté serveur.

- Déplacer la génération des transactions récurrentes vers le serveur et
  rattacher chaque dépense au budget correspondant à son propre mois.

- Limiter le client à la saisie et à la présentation des tableaux de bord,
  budgets et alertes déjà calculés par les services métier.

- Aligner le port publié par Docker Compose sur le port `8765` utilisé par le
  client et documenter l'installation du serveur conteneurisé.

### Added

- Exposer les états mensuels, le tableau de bord, les alertes à partir de
  80 %, les projections et la gestion complète des catégories et objectifs
  dans le protocole JSON/TCP.

- Ajouter des versements d'épargne persistants, déduits du solde disponible et
  intégrés aux contrôles empêchant les dépenses à découvert.

- Ajouter les transactions récurrentes hebdomadaires, mensuelles ou annuelles,
  avec une date de fin et le statut prévu pour les occurrences futures.

- Raccorder les sous-catégories aux budgets et aux dépenses dans l'interface.

- Afficher pour chaque objectif le reste à épargner, le minimum mensuel, le
  revenu utilisable et l'épargne maximale disponible.

- Catégoriser les revenus (salaire, remboursement, cadeau, prime ou autre)
  sans les rattacher aux budgets de dépenses, avec migration des bases existantes.

- Ajouter un calendrier et un suivi visuel de progression aux objectifs d'épargne.

- Ajouter un serveur JSON/TCP, un routage vers les services et des sessions
  opaques empêchant le client de choisir l'identifiant d'un autre utilisateur.

- Raccorder l'inscription, la connexion, les transactions et les budgets de
  l'interface graphique au serveur et à SQLite.

- Ajouter à l'interface la création, la modification, la suppression et
  l'alimentation réelle des objectifs d'épargne.

- Ajouter les calculs de consommation, les enveloppes hebdomadaires, les
  alertes par seuil et la simulation d'une dépense prévue.

- Ajouter la gestion et le suivi des objectifs d'épargne, avec calcul d'un plan
  périodique et propositions de réajustement.

- Ajouter la gestion des dépenses prévues et réalisées, reliées à un budget et
  isolées par utilisateur.

- Ajouter la gestion persistante des budgets mensuels, avec validation des
  catégories et isolation des données de chaque utilisateur.

- Ajouter la persistance des comptes utilisateurs, avec création, lecture et
  suppression contrôlées par SQLite
  ([#3](https://github.com/TheMuliama/plannification_budgetaire/issues/3)).

- Ajouter la création, la modification, la suppression et la consultation des
  revenus prévus ou reçus, avec validation et isolation par utilisateur
  ([#6](https://github.com/TheMuliama/plannification_budgetaire/issues/6)).

- Intégrer les écrans de gestion budgétaire de la branche `feat/interface` :
  tableau de bord, transactions, budgets, alertes, inscription et paramètres,
  désormais raccordés au serveur et à SQLite
  ([#10](https://github.com/TheMuliama/plannification_budgetaire/pull/10)).

### Security

- Permettre le changement de mot de passe et la suppression du compte après
  une nouvelle vérification du secret de l'utilisateur.

- Raccorder la création et l'authentification des comptes au hachage Argon2id,
  sans exposer le mot de passe enregistré dans les réponses du service
  ([#4](https://github.com/TheMuliama/plannification_budgetaire/issues/4)).

- Ajouter les fonctions de hachage et de vérification des mots de passe avec
  Argon2id et un sel aléatoire, destinées au futur service utilisateurs
  ([#2](https://github.com/TheMuliama/plannification_budgetaire/issues/2)).

### Fixed

- Remplacer le simulateur de dépense de l'écran Épargne par un parcours réel
  d'alimentation des objectifs et afficher le solde disponible sur le tableau de bord.

- Interdire côté serveur toute dépense réalisée qui rendrait le solde négatif,
  y compris lors de la modification d'une dépense existante.

- Rendre les calendriers des transactions et objectifs réellement interactifs.

- Trier l'historique des transactions par date et masquer les alertes avant 80 %.

- Harmoniser les couleurs et la présentation de l'écran Épargne et projection.

- Limiter les budgets, alertes et projections au mois courant et empêcher la
  conversion incohérente d'un revenu en dépense lors d'une modification.

- Valider et normaliser les noms des catégories et sous-catégories, avec des
  tests respectant les clés étrangères du schéma SQLite
  ([#7](https://github.com/TheMuliama/plannification_budgetaire/issues/7)).
