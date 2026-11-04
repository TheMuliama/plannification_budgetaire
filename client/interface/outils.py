"""Outils de présentation partagés par les écrans du client."""


def centrer_fenetre(fenetre, parent, largeur: int, hauteur: int) -> None:
    """Centrer une fenêtre de dimensions fixes par rapport à son parent.

    Args:
        fenetre: Fenêtre à repositionner.
        parent: Fenêtre de référence.
        largeur: Largeur souhaitée en pixels.
        hauteur: Hauteur souhaitée en pixels.
    """
    parent.update_idletasks()

    position_x = parent.winfo_rootx() + (parent.winfo_width() - largeur) // 2
    position_y = parent.winfo_rooty() + (parent.winfo_height() - hauteur) // 2

    fenetre.geometry(f"{largeur}x{hauteur}+{max(0, position_x)}+{max(0, position_y)}")
