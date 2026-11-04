# Changelog

## [Unreleased]

### Added

- Ajouter un serveur JSON/TCP, un routage vers les services et des sessions
  opaques empêchant le client de choisir l'identifiant d'un autre utilisateur.

- Raccorder l'inscription, la connexion, les transactions et les budgets de
  l'interface graphique au serveur et à SQLite.

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
  tableau de bord, transactions, budgets, alertes, factures, inscription et paramètres.
  Les données restent temporaires en mémoire et la connexion est simulée ;
  le raccordement au serveur et à SQLite reste à réaliser
  ([#10](https://github.com/TheMuliama/plannification_budgetaire/pull/10)).

### Security

- Raccorder la création et l'authentification des comptes au hachage Argon2id,
  sans exposer le mot de passe enregistré dans les réponses du service
  ([#4](https://github.com/TheMuliama/plannification_budgetaire/issues/4)).

- Ajouter les fonctions de hachage et de vérification des mots de passe avec
  Argon2id et un sel aléatoire, destinées au futur service utilisateurs
  ([#2](https://github.com/TheMuliama/plannification_budgetaire/issues/2)).

### Fixed

- Valider et normaliser les noms des catégories et sous-catégories, avec des
  tests respectant les clés étrangères du schéma SQLite
  ([#7](https://github.com/TheMuliama/plannification_budgetaire/issues/7)).
