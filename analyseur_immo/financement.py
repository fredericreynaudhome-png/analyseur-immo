"""Calculs de financement : mensualité de prêt et tableau d'amortissement."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Financement:
    """Paramètres du prêt immobilier.

    Les taux sont exprimés en fraction annuelle : 0.035 signifie 3,5 %.
    """

    apport: float = 15_000.0
    duree_annees: int = 20
    taux_annuel: float = 0.035
    # Assurance emprunteur, en fraction annuelle du capital emprunté.
    # Laissée à 0 par défaut : à renseigner avec le devis de votre assureur.
    taux_assurance_annuel: float = 0.0


def mensualite(capital: float, taux_annuel: float, duree_annees: int) -> float:
    """Mensualité constante d'un prêt amortissable, hors assurance."""
    if capital <= 0:
        return 0.0
    nb_mois = duree_annees * 12
    if taux_annuel == 0:
        return capital / nb_mois
    t = taux_annuel / 12
    return capital * t / (1 - (1 + t) ** -nb_mois)


def assurance_mensuelle(capital: float, taux_assurance_annuel: float) -> float:
    """Assurance emprunteur mensuelle, calculée sur le capital initial."""
    return max(capital, 0.0) * taux_assurance_annuel / 12


@dataclass(frozen=True)
class LigneAmortissement:
    annee: int
    interets: float
    capital_rembourse: float
    capital_restant: float


def tableau_amortissement(
    capital: float, taux_annuel: float, duree_annees: int
) -> list[LigneAmortissement]:
    """Tableau d'amortissement agrégé par année."""
    m = mensualite(capital, taux_annuel, duree_annees)
    t = taux_annuel / 12
    restant = capital
    lignes = []
    for annee in range(1, duree_annees + 1):
        interets_annee = 0.0
        capital_annee = 0.0
        for _ in range(12):
            interets = restant * t
            part_capital = m - interets
            restant -= part_capital
            interets_annee += interets
            capital_annee += part_capital
        lignes.append(
            LigneAmortissement(annee, interets_annee, capital_annee, max(restant, 0.0))
        )
    return lignes
