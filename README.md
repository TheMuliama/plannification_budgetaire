# Application de planification budgétaire

Application lourde de planification budgétaire destinée principalement aux étudiants.

## Objectif actuel

L'objectif prioritaire est de terminer un **MVP fonctionnel avant le jeudi 5 novembre 2026 à 22h00**.

Le MVP doit permettre à un utilisateur de :

- créer et gérer son compte ;
- gérer ses catégories et sous-catégories ;
- enregistrer ses revenus ;
- enregistrer ses dépenses ;
- définir son budget ;
- définir et suivre son objectif d'épargne ;
- connaître l'état actuel de son budget ;
- recevoir des alertes ;
- projeter l'impact d'une dépense prévue ;
- utiliser ces fonctionnalités depuis l'interface graphique.

Les fonctionnalités secondaires seront traitées uniquement si le MVP est terminé.

---

## Architecture du projet

L'application est organisée en trois grandes couches :

```mermaid
flowchart TD
    Client["Client<br/>Interface graphique"]
    Communication["Communication<br/>Sockets TCP / JSON"]
    Services["Services métier"]
    Repositories["Repositories<br/>Persistance"]
    Database[("SQLite")]

    Client --> Communication
    Communication --> Services
    Services --> Repositories
    Repositories --> Database
```

Le client ne communique pas directement avec la base de données.

Les services métier contiennent les responsabilités propres à l'application, tandis que les repositories assurent l'accès aux données.

## Démarrage local

Depuis la racine du dépôt :

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Démarrer le serveur dans un premier terminal :

```bash
python -m serveur.main
```

Puis démarrer l'application graphique dans un second terminal :

```bash
python client/main.py
```

Le serveur écoute par défaut sur `127.0.0.1:8765` et initialise la base
`persistance/data/budget.db`. Les fichiers SQLite de ce dossier sont ignorés
par Git afin de ne pas publier de données personnelles.

---

## Organisation des modules métier

```mermaid
flowchart TD
    Utilisateurs["Gestionnaire des utilisateurs"]
    Categories["Gestionnaire des catégories"]
    Revenus["Gestionnaire des revenus"]
    Depenses["Gestionnaire des dépenses"]
    Epargne["Gestionnaire des objectifs d'épargne"]
    Budget["Gestionnaire du budget"]
    CalculBudget["Calculateur budgétaire"]
    Alertes["Gestionnaire des alertes"]
    Projection["Moteur de projection"]

    Categories --> Depenses
    Revenus --> Budget
    Epargne --> Budget
    Depenses --> CalculBudget
    Budget --> CalculBudget
    Revenus --> CalculBudget

    CalculBudget --> Alertes
    CalculBudget --> Projection
    Depenses --> Projection
    Epargne --> Projection
```

Ces relations représentent les dépendances métier principales. Elles ne signifient pas nécessairement que les modules doivent être développés strictement les uns après les autres.

---

# Roadmap du MVP

## Gantt

```mermaid
gantt
    title Finalisation du MVP
    dateFormat YYYY-MM-DD
    axisFormat %a %d/%m

    section Fondations
    Persistance / SQLite              :a1, 2026-11-02, 1d
    Repositories                      :a2, 2026-11-02, 2d

    section Modules de base
    Gestionnaire utilisateurs         :b1, 2026-11-02, 1d
    Gestionnaire catégories           :b2, 2026-11-02, 1d
    Gestionnaire revenus              :b3, 2026-11-03, 1d
    Gestionnaire dépenses             :b4, 2026-11-03, 1d
    Objectifs d'épargne               :b5, 2026-11-03, 1d
    Gestionnaire du budget            :b6, 2026-11-03, 1d

    section Calculs
    Calculateur budgétaire            :c1, 2026-11-04, 1d
    Gestionnaire des alertes          :c2, 2026-11-04, 1d
    Moteur de projection              :c3, 2026-11-04, 1d

    section Communication
    Protocole JSON                    :d1, 2026-11-03, 1d
    Communication client-serveur      :d2, 2026-11-04, 1d
    Intégration des services          :d3, 2026-11-04, 1d

    section Interface
    Connexion                         :e1, 2026-11-02, 1d
    Interface revenus / dépenses     :e2, 2026-11-04, 1d
    Interface budget                  :e3, 2026-11-04, 1d
    Dashboard                         :e4, 2026-11-04, 1d
    Intégration interface             :e5, 2026-11-05, 1d

    section Validation
    Tests d'intégration               :f1, 2026-11-05, 1d
    Corrections finales               :f2, 2026-11-05, 1d
    Livraison MVP                     :milestone, f3, 2026-11-05, 0d
```

**Deadline : jeudi 5 novembre 2026 à 22h00.**

---

# Milestones

## M0 — Fondations du projet

- [x] Architecture générale
- [x] Structure `client / serveur / persistance`
- [x] Responsabilités des modules
- [x] Organisation Git
- [x] Règles de contribution
- [x] Templates d'issues

## M1 — Persistance

- [ ] Finaliser le schéma SQLite
- [ ] Finaliser la connexion à la base
- [ ] Repository utilisateurs
- [ ] Repository catégories
- [ ] Repository revenus
- [ ] Repository dépenses
- [ ] Repository budgets
- [ ] Repository objectifs d'épargne
- [ ] Repository alertes

## M2 — Utilisateurs

- [ ] Création de compte
- [ ] Connexion
- [ ] Suppression de compte
- [ ] Séparation des données entre utilisateurs

## M3 — Catégories

- [ ] Création de catégories
- [ ] Création de sous-catégories
- [ ] Modification
- [ ] Suppression
- [ ] Récupération des catégories d'un utilisateur
- [ ] Tests

## M4 — Revenus et dépenses

### Revenus

- [ ] Ajout d'un revenu
- [ ] Revenu prévisionnel
- [ ] Revenu réellement reçu
- [ ] Modification
- [ ] Suppression

### Dépenses

- [ ] Ajout d'une dépense
- [ ] Dépense prévue
- [ ] Dépense réalisée
- [ ] Association catégorie / sous-catégorie
- [ ] Modification
- [ ] Suppression
- [ ] Historique

## M5 — Objectifs d'épargne

- [ ] Création d'un objectif
- [ ] Montant cible
- [ ] Date cible
- [ ] Montant d'épargne périodique
- [ ] Calcul du plan d'épargne
- [ ] Suivi de la progression
- [ ] Gestion d'un écart par rapport au plan

## M6 — Budget

- [ ] Définition du budget mensuel
- [ ] Catégories et sous-catégories
- [ ] Catégorie d'épargne
- [ ] Dépenses obligatoires
- [ ] Budget flexible
- [ ] Enveloppes hebdomadaires

## M7 — Calcul budgétaire

- [ ] Budget restant
- [ ] État des catégories
- [ ] Budget flexible disponible
- [ ] État des enveloppes hebdomadaires

## M8 — Alertes

- [ ] Seuil de 50 %
- [ ] Seuil de 80 %
- [ ] Dépassement du budget
- [ ] Passage sous le minimum défini par l'utilisateur
- [ ] Alertes liées aux projections

## M9 — Projection

- [ ] Projection de la situation future
- [ ] Simulation d'une dépense prévue
- [ ] Impact sur les catégories
- [ ] Impact sur le budget flexible
- [ ] Impact sur la capacité d'épargne
- [ ] Impact sur l'objectif d'épargne

## M10 — Communication

- [ ] Définir le protocole JSON
- [ ] Envoi des requêtes client
- [ ] Réception des requêtes serveur
- [ ] Traitement des requêtes
- [ ] Réponses serveur
- [ ] Connexion des services métier au serveur

## M11 — Interface MVP

- [ ] Interface de connexion
- [ ] Interface revenus / dépenses
- [ ] Interface budget
- [ ] Dashboard
- [ ] Connexion de l'interface aux services serveur

## M12 — Validation du MVP

- [ ] Tests d'intégration
- [ ] Parcours utilisateur complet
- [ ] Vérification de l'isolation des utilisateurs
- [ ] Vérification de la persistance
- [ ] Vérification de la communication client-serveur
- [ ] Correction des bugs bloquants
- [ ] Validation finale du MVP

## M13 — Fonctionnalités secondaires

À réaliser uniquement après la validation du MVP.

- [ ] Recherche et filtrage
- [ ] Gestion des investissements
- [ ] Documentation utilisateur
- [ ] Documentation technique
- [ ] Améliorations graphiques

---

# Parcours utilisateur minimum

Le parcours suivant doit fonctionner de bout en bout pour considérer le MVP comme fonctionnel :

```mermaid
flowchart TD
    A["Créer un compte"] --> B["Se connecter"]
    B --> C["Créer ses catégories"]
    C --> D["Ajouter ses revenus"]
    D --> E["Définir son objectif d'épargne"]
    E --> F["Définir son budget"]
    F --> G["Ajouter ses dépenses"]
    G --> H["Consulter le budget restant"]
    H --> I["Recevoir une alerte"]
    I --> J["Prévoir une dépense"]
    J --> K["Voir son impact financier"]
    K --> L["Consulter le dashboard"]
```

---

# Flux technique d'une opération

Exemple : l'utilisateur ajoute une dépense.

```mermaid
sequenceDiagram
    actor Utilisateur
    participant Client
    participant Socket as Serveur Socket
    participant Service as Service métier
    participant Repository
    participant DB as SQLite

    Utilisateur->>Client: Ajouter une dépense
    Client->>Socket: Requête JSON
    Socket->>Service: Données de la dépense
    Service->>Repository: Enregistrer la dépense
    Repository->>DB: INSERT
    DB-->>Repository: Résultat
    Repository-->>Service: Dépense enregistrée
    Service-->>Socket: Réponse
    Socket-->>Client: Réponse JSON
    Client-->>Utilisateur: Mise à jour de l'interface
```

---

# Dépendances principales

```mermaid
flowchart TD
    M1["M1<br/>Persistance"]
    M2["M2<br/>Utilisateurs"]
    M3["M3<br/>Catégories"]
    M4["M4<br/>Revenus & dépenses"]
    M5["M5<br/>Objectifs d'épargne"]
    M6["M6<br/>Budget"]
    M7["M7<br/>Calcul budgétaire"]
    M8["M8<br/>Alertes"]
    M9["M9<br/>Projection"]
    M10["M10<br/>Communication"]
    M11["M11<br/>Interface"]
    M12["M12<br/>Validation"]

    M1 --> M2
    M1 --> M3
    M2 --> M4
    M3 --> M4
    M2 --> M5
    M3 --> M6
    M4 --> M6
    M5 --> M6
    M4 --> M7
    M6 --> M7
    M7 --> M8
    M5 --> M9
    M7 --> M9
    M4 --> M9
    M2 --> M10
    M4 --> M10
    M6 --> M10
    M8 --> M10
    M9 --> M10
    M10 --> M11
    M11 --> M12
```

> Ce schéma représente les dépendances principales. Les issues peuvent néanmoins être développées en parallèle lorsque leur dépendance n'est pas bloquante.

---

# Organisation Git

```mermaid
flowchart LR
    Main["main"]
    Issue["Issue"]
    Branch["Branche dédiée"]
    Development["Développement"]
    Tests["Tests"]
    PR["Pull Request"]
    Review["Relecture"]
    Merge["Squash & Merge"]

    Main --> Issue
    Issue --> Branch
    Branch --> Development
    Development --> Tests
    Tests --> PR
    PR --> Review
    Review --> Merge
    Merge --> Main
```

Chaque fonctionnalité importante doit être associée à une issue.

Pour chaque issue :

1. définir le périmètre ;
2. identifier les dépendances ;
3. attribuer un responsable ;
4. créer une branche dédiée ;
5. développer ;
6. tester ;
7. créer une Pull Request ;
8. faire relire le travail ;
9. fusionner dans `main`.

---

# Priorités

## Priorité 1 — MVP

Tout ce qui est nécessaire au parcours utilisateur minimum :

- persistance ;
- utilisateurs ;
- catégories ;
- revenus ;
- dépenses ;
- objectifs d'épargne ;
- budget ;
- calcul budgétaire ;
- alertes ;
- projection ;
- communication ;
- interface ;
- tests.

## Priorité 2 — Après le MVP

- recherche et filtrage ;
- investissements ;
- documentation avancée ;
- améliorations graphiques.

**Si une fonctionnalité secondaire menace la livraison du MVP, elle doit être reportée.**

---

# Définition du MVP terminé

```mermaid
flowchart TD
    A["Serveur fonctionnel"]
    B["Base SQLite fonctionnelle"]
    C["Authentification fonctionnelle"]
    D["Catégories fonctionnelles"]
    E["Revenus et dépenses fonctionnels"]
    F["Objectif d'épargne fonctionnel"]
    G["Budget fonctionnel"]
    H["Calculs budgétaires fonctionnels"]
    I["Alertes fonctionnelles"]
    J["Projection fonctionnelle"]
    K["Communication client-serveur fonctionnelle"]
    L["Interface fonctionnelle"]
    M["Tests critiques passants"]
    N["MVP validé"]

    A --> N
    B --> N
    C --> N
    D --> N
    E --> N
    F --> N
    G --> N
    H --> N
    I --> N
    J --> N
    K --> N
    L --> N
    M --> N
```

Le MVP est terminé lorsque le parcours utilisateur minimum fonctionne de bout en bout et qu'aucun bug bloquant connu ne subsiste.

---

# Deadline

**Jeudi 5 novembre 2026 — 22h00**

La priorité absolue est la **livraison d'un MVP fonctionnel**.

Les fonctionnalités secondaires ne doivent pas compromettre cette échéance.
