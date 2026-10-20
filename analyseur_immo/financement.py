"""Financement : mensualité, assurance, tableau d'amortissement, endettement (HCSF)."""

from dataclasses import dataclass

# Règles HCSF (Haut Conseil de stabilité financière)
DUREE_MAX_ANNEES = 25
TAUX_ENDETTEMENT_MAX = 0.35


@dataclass(frozen=True)
class Financement:
    """Paramètres du prêt et de la situation de l'emprunteur.

    Les taux sont exprimés en fraction annuelle : 0.035 signifie 3,5 %.
    """

    # L'apport couvre en priorité les frais de notaire ; le reste du projet est emprunté.
    apport: float = 15_000.0
    duree_annees: int = 20
    # Taux nominal du crédit. À remplacer par le taux moyen du marché du moment.
    taux_annuel: float = 0.035
    # Assurance emprunteur, en fraction annuelle du capital emprunté.
    taux_assurance_annuel: float = 0.003

    # Situation de l'emprunteur, pour le taux d'endettement (hypothèse à rappeler).
    revenus_mensuels_nets: float = 4_000.0
    autres_credits_mensuels: float = 0.0
    # Part des loyers futurs que retiennent les banques dans les revenus.
    part_loyers_retenue: float = 0.70

    # Enveloppe de financement (coût total du projet).
    enveloppe_cible: float = 260_000.0
    enveloppe_maximum: float = 300_000.0

    def __post_init__(self):
        if not 0 < self.duree_annees <= DUREE_MAX_ANNEES:
            raise ValueError(
                f"La durée du prêt doit être comprise entre 1 et {DUREE_MAX_ANNEES} ans (règle HCSF)."
            )


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


def taux_endettement(
    mensualite_projet: float, loyers_mensuels: float, financement: Financement
) -> float:
    """Taux d'endettement après opération, loyers retenus à 70 % dans les revenus."""
    charges = mensualite_projet + financement.autres_credits_mensuels
    revenus = (
        financement.revenus_mensuels_nets
        + loyers_mensuels * financement.part_loyers_retenue
    )
    return charges / revenus if revenus > 0 else float("inf")


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
