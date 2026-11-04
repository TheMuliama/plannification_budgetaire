"""Point d'entrée de la couche serveur."""

import argparse
from pathlib import Path

from persistance.database import Database
from serveur.application import construire_serveur


def main() -> None:
    """Démarrer le serveur de l'application.

    Returns:
        None.
    """
    analyseur=argparse.ArgumentParser(description="Serveur de planification budgétaire")
    analyseur.add_argument("--base",default="persistance/data/budget.db")
    analyseur.add_argument("--adresse",default="127.0.0.1")
    analyseur.add_argument("--port",type=int,default=8765)
    options=analyseur.parse_args()
    chemin=Path(options.base); chemin.parent.mkdir(parents=True,exist_ok=True)
    connexion=Database().connecter(str(chemin))
    connexion.executescript(Path("persistance/schema.sql").read_text(encoding="utf-8"))
    try: construire_serveur(connexion).demarrer(options.port,options.adresse)
    finally: connexion.close()


if __name__ == "__main__":
    main()
