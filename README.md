# Application de planification budgétaire

Application lourde de planification budgétaire destinée principalement aux étudiants.

## État actuel

Le MVP est fonctionnel. Son architecture métier a été réalignée sur les neuf
modules définis au début du projet : les calculs sont réalisés côté serveur,
le client se limite à la saisie et à la présentation, et les repositories se
limitent aux opérations SQLite.

Le MVP permet à un utilisateur de :

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
`persistance/data/budget.db`. Les nouvelles bases SQLite de ce dossier sont
ignorées par Git afin de ne pas publier de données personnelles. Le dépôt peut
néanmoins fournir un instantané de démonstration explicitement suivi, qui doit
contenir uniquement des données fictives.

## Installation du serveur avec Docker

Construire et démarrer uniquement le serveur :

```bash
docker compose up --build -d
```

Le port `8765` du serveur est alors disponible uniquement sur l'interface
locale de la machine. Les données SQLite sont conservées dans le volume Docker
`budget_data`. Le client graphique reste lancé depuis l'environnement local :

```bash
python client/main.py
```

Arrêter le serveur sans supprimer ses données :

```bash
docker compose down
```

## Compte de démonstration

Le compte destiné à la présentation et aux tests du professeur est :

```text
Identifiant : richard.latchoumane@univ-reunion.fr
Mot de passe : Richard-2026!
```

Il contient un scénario d'utilisation normal de juin à novembre 2026 :
48 budgets mensuels, 14 revenus, 59 dépenses réalisées ou prévues, deux
objectifs d'épargne et dix versements. Les données couvrent également les
alertes à 80 %, l'évolution sur six mois et les opérations récurrentes.

Le scénario peut être recréé sans modifier les autres comptes avec :

```bash
python -m scripts.peupler_compte_richard
```

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
    Categories --> Budget
    Revenus --> Budget
    Epargne --> Budget
    Depenses --> CalculBudget
    Budget --> CalculBudget
    Revenus --> CalculBudget
    Epargne --> CalculBudget

    CalculBudget --> Alertes
    CalculBudget --> Projection
    Depenses --> Projection
    Epargne --> Projection
    Projection --> Alertes
```

Ces relations représentent les dépendances métier principales. Elles ne
signifient pas nécessairement que les modules doivent être développés
strictement les uns après les autres.

| Module | Rôle effectif | Dépendances métier |
| --- | --- | --- |
| `GestionnaireUtilisateurs` | Comptes, authentification et mots de passe | Aucune |
| `GestionnaireCategories` | Catégories, sous-catégories et validation des classements | Aucune |
| `GestionnaireRevenus` | Revenus prévus/reçus et totaux par période | Aucune |
| `GestionnaireObjectifsEpargne` | Objectifs, versements, plans, écarts et scénarios | Aucune |
| `GestionnaireBudget` | Construction du budget mensuel, allocations et épargne prévue | Revenus, objectifs, catégories |
| `GestionnaireDepenses` | Dépenses prévues/réalisées et validation de leurs rattachements | Catégories, budget |
| `CalculateurBudget` | Solde, consommation, budget flexible, enveloppes et capacité d'épargne | Budget, revenus, dépenses, objectifs |
| `MoteurProjection` | Impact futur des dépenses prévues sur le budget et l'épargne | Calculateur, dépenses, objectifs |
| `GestionnaireAlertes` | Alertes de consommation à partir de 80 % et risques projetés | Calculateur, projection |

`GestionnaireSessions` reste un composant de sécurité et non un module métier.
Les anciens services parallèles de solde et d'analyse d'épargne ont été
absorbés par `CalculateurBudget`.

Le serveur expose notamment les états calculés avec `budgets.etat`,
`dashboard.obtenir`, `alertes.lister` et `projection.simuler`. Les séries de
revenus et de dépenses récurrentes sont développées côté serveur afin qu'un
client ne puisse pas contourner les validations financières.

La suite automatisée couvre les services, la persistance, le protocole et les
principaux parcours intégrés. Elle s'exécute avec :

```bash
python -m pytest -q
```

---

# Roadmap historique du MVP

Cette roadmap décrit la planification initiale. L'état effectif et les
dépendances actuellement implémentées sont décrits dans la section précédente.

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

Les fonctionnalités secondaires ne doivent pas compromettre cette échéance.
