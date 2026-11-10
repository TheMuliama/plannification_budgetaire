"""Outils partagés pour créer les occurrences récurrentes côté serveur."""

from calendar import monthrange
from datetime import date, timedelta

FREQUENCES = ("Aucune", "Hebdomadaire", "Mensuelle", "Annuelle")


def generer_dates_recurrence(
    debut: date, frequence: str, fin: date | None
) -> list[date]:
    """Calculer les dates inclusives d'une série de transactions.

    Args:
        debut: Date de la première occurrence.
        frequence: Fréquence choisie par l'utilisateur.
        fin: Dernière date autorisée pour la série.

    Returns:
        Les dates de la série, limitées à 120 occurrences.

    Raises:
        ValueError: Si la fréquence ou la période est invalide.
    """
    if frequence not in FREQUENCES:
        raise ValueError("La fréquence de récurrence est invalide.")
    if frequence == "Aucune":
        return [debut]
    if fin is None or fin < debut:
        raise ValueError("La date de fin doit suivre la première transaction.")

    resultat = []
    courante = debut
    jour_ancrage = debut.day
    while courante <= fin:
        resultat.append(courante)
        if len(resultat) >= 120:
            raise ValueError("La série ne peut pas dépasser 120 transactions.")
        if frequence == "Hebdomadaire":
            courante += timedelta(days=7)
        elif frequence == "Mensuelle":
            prochain_mois = courante.month + 1
            annee = courante.year + (prochain_mois - 1) // 12
            mois = (prochain_mois - 1) % 12 + 1
            courante = date(
                annee, mois, min(jour_ancrage, monthrange(annee, mois)[1])
            )
        else:
            annee = courante.year + 1
            courante = date(
                annee,
                courante.month,
                min(jour_ancrage, monthrange(annee, courante.month)[1]),
            )
    return resultat
