# Changelog

## [Unreleased]

### Added

- Intégrer les écrans de gestion budgétaire de la branche `feat/interface` :
  tableau de bord, transactions, budgets, alertes, factures, inscription et paramètres.
  Les données restent temporaires en mémoire et la connexion est simulée ;
  le raccordement au serveur et à SQLite reste à réaliser
  ([#10](https://github.com/TheMuliama/plannification_budgetaire/pull/10)).

### Security

- Ajouter les fonctions de hachage et de vérification des mots de passe avec
  Argon2id et un sel aléatoire, destinées au futur service utilisateurs
  ([#2](https://github.com/TheMuliama/plannification_budgetaire/issues/2)).
