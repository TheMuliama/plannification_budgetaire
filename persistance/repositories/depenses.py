"""Accès aux données des dépenses."""

import sqlite3
from typing import Any


class RepositoryDepenses:
    """Lire et écrire les dépenses en les isolant par utilisateur."""

    def __init__(self, connexion: sqlite3.Connection) -> None:
        self._connexion = connexion

    def ajouter_depense(self, **donnees: Any) -> dict[str, Any]:
        """Créer une dépense reliée à un budget accessible.

        Args:
            **donnees: Valeurs validées de la dépense.

        Returns:
            La dépense enregistrée.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "INSERT INTO depenses (utilisateur_id,budget_id,categorie_id,sous_categorie_id,"
                "montant,date,description,statut) VALUES (?,?,?,?,?,?,?,?)",
                tuple(
                    donnees[cle]
                    for cle in (
                        "utilisateur_id",
                        "budget_id",
                        "categorie_id",
                        "sous_categorie_id",
                        "montant",
                        "date",
                        "description",
                        "statut",
                    )
                ),
            )
        resultat = self.obtenir_depense(donnees["utilisateur_id"], curseur.lastrowid)
        assert resultat is not None
        return resultat

    def ajouter_depenses_recurrentes(
        self, depenses: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Enregistrer les dépenses récurrentes et leurs budgets mensuels.

        Les budgets manquants sont créés à partir du modèle fourni.
        Les budgets existants sont réutilisés sans modification.
        Toutes les écritures sont effectuées dans une transaction SQLite
        afin d'éviter les enregistrements partiels.

        Args:
            depenses: Liste des dépenses préparées par le service métier.
                Chaque dépense peut contenir les informations d'un budget
                à créer dans la clé ``_budget_a_creer``.

        Returns:
            La liste des dépenses enregistrées avec leurs identifiants
            définitifs et les budgets associés.

        Raises:
            sqlite3.IntegrityError: Si une contrainte de la base de données
                n'est pas respectée.
            sqlite3.Error: Si une erreur survient lors des opérations SQL.
        """
        identifiants = []
        nouveaux_budgets = {}

        with self._connexion:
            for depense in depenses:
                budget_id = depense["budget_id"]
                modele = depense.get("_budget_a_creer")

                if modele is not None:
                    cle = (
                        depense["utilisateur_id"],
                        modele["annee"],
                        modele["mois"],
                        modele["categorie_id"],
                        modele["sous_categorie_id"],
                    )

                    if cle not in nouveaux_budgets:
                        ligne = self._connexion.execute(
                            """
                            SELECT id FROM budgets
                            WHERE utilisateur_id = ?
                              AND annee = ?
                              AND mois = ?
                              AND categorie_id = ?
                              AND sous_categorie_id IS ?
                            ORDER BY id
                            LIMIT 1
                            """,
                            cle,
                        ).fetchone()

                        if ligne is None:
                            curseur = self._connexion.execute(
                                """
                                INSERT INTO budgets (
                                    utilisateur_id,
                                    annee,
                                    mois,
                                    categorie_id,
                                    sous_categorie_id,
                                    montant_alloue,
                                    obligatoire
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    depense["utilisateur_id"],
                                    modele["annee"],
                                    modele["mois"],
                                    modele["categorie_id"],
                                    modele["sous_categorie_id"],
                                    modele["montant_alloue"],
                                    int(modele["obligatoire"]),
                                ),
                            )
                            nouveaux_budgets[cle] = curseur.lastrowid
                        else:
                            nouveaux_budgets[cle] = ligne[0]

                    budget_id = nouveaux_budgets[cle]

                curseur = self._connexion.execute(
                    """
                    INSERT INTO depenses (
                        utilisateur_id,
                        budget_id,
                        categorie_id,
                        sous_categorie_id,
                        montant,
                        date,
                        description,
                        statut
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        depense["utilisateur_id"],
                        budget_id,
                        depense["categorie_id"],
                        depense["sous_categorie_id"],
                        depense["montant"],
                        depense["date"],
                        depense["description"],
                        depense["statut"],
                    ),
                )

                identifiants.append(
                    (depense["utilisateur_id"], curseur.lastrowid)
                )

        resultat = []

        for utilisateur_id, depense_id in identifiants:
            depense = self.obtenir_depense(utilisateur_id, depense_id)
            assert depense is not None
            resultat.append(depense)

        return resultat

    def obtenir_depense(
        self, utilisateur_id: int, depense_id: int
    ) -> dict[str, Any] | None:
        """Récupérer une dépense accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de la dépense.
            depense_id: Identifiant de la dépense recherchée.

        Returns:
            La dépense trouvée, ou ``None`` si elle est inaccessible.
        """
        ligne = self._connexion.execute(
            "SELECT * FROM depenses WHERE utilisateur_id=? AND id=?",
            (utilisateur_id, depense_id),
        ).fetchone()
        return dict(ligne) if ligne is not None else None

    def consulter_depenses(
        self, utilisateur_id: int, statut: str | None = None
    ) -> list[dict[str, Any]]:
        """Consulter les dépenses d'un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire des dépenses.
            statut: Statut facultatif utilisé comme filtre.

        Returns:
            Les dépenses correspondant au filtre.
        """
        requete, valeurs = (
            "SELECT * FROM depenses WHERE utilisateur_id=?",
            [utilisateur_id],
        )
        if statut is not None:
            requete += " AND statut=?"
            valeurs.append(statut)
        lignes = self._connexion.execute(
            requete + " ORDER BY date DESC,id DESC", valeurs
        ).fetchall()
        return [dict(ligne) for ligne in lignes]

    def modifier_depense(
        self, utilisateur_id: int, depense_id: int, **donnees: Any
    ) -> dict[str, Any] | None:
        """Modifier une dépense accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de la dépense.
            depense_id: Identifiant de la dépense à modifier.
            **donnees: Nouvelles valeurs de la dépense.

        Returns:
            La dépense modifiée, ou ``None`` si elle est inaccessible.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "UPDATE depenses SET budget_id=?,categorie_id=?,sous_categorie_id=?,montant=?,"
                "date=?,description=?,statut=? WHERE utilisateur_id=? AND id=?",
                (
                    donnees["budget_id"],
                    donnees["categorie_id"],
                    donnees["sous_categorie_id"],
                    donnees["montant"],
                    donnees["date"],
                    donnees["description"],
                    donnees["statut"],
                    utilisateur_id,
                    depense_id,
                ),
            )
        return (
            self.obtenir_depense(utilisateur_id, depense_id)
            if curseur.rowcount
            else None
        )

    def supprimer_depense(self, utilisateur_id: int, depense_id: int) -> bool:
        """Supprimer une dépense accessible à un utilisateur.

        Args:
            utilisateur_id: Identifiant du propriétaire de la dépense.
            depense_id: Identifiant de la dépense à supprimer.

        Returns:
            ``True`` si une dépense a été supprimée.
        """
        with self._connexion:
            curseur = self._connexion.execute(
                "DELETE FROM depenses WHERE utilisateur_id=? AND id=?",
                (utilisateur_id, depense_id),
            )
        return curseur.rowcount > 0
