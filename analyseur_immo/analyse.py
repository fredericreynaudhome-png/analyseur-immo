"""Analyse de rentabilité d'un bien et comparaison de plusieurs biens.

Version 1 : tous les résultats sont AVANT IMPÔT.
"""

from dataclasses import dataclass
from typing import Union

from .biens import ImmeubleDeRapport, LocationCourteDuree
from .financement import Financement, assurance_mensuelle, mensualite

Bien = Union[ImmeubleDeRapport, LocationCourteDuree]


@dataclass(frozen=True)
class Resultat:
    nom: str
    type_bien: str
    cout_total: float
    montant_emprunte: float
    revenus_annuels: float
    charges_annuelles: float
    credit_annuel: float
    rendement_brut: float
    rendement_net: float
    cashflow_mensuel: float
    seuil_rendement_brut: float

    @property
    def atteint_le_seuil(self) -> bool:
        return self.rendement_brut >= self.seuil_rendement_brut

    @property
    def cashflow_positif(self) -> bool:
        return self.cashflow_mensuel > 0

    @property
    def effort_epargne_mensuel(self) -> float:
        """Somme à remettre chaque mois de sa poche (0 si le bien s'autofinance)."""
        return max(-self.cashflow_mensuel, 0.0)


def analyser(bien: Bien, financement: Financement = Financement()) -> Resultat:
    """Calcule les indicateurs de rentabilité d'un bien."""
    cout_total = bien.acquisition.cout_total
    emprunt = max(cout_total - financement.apport, 0.0)

    credit_mensuel = mensualite(
        emprunt, financement.taux_annuel, financement.duree_annees
    ) + assurance_mensuelle(emprunt, financement.taux_assurance_annuel)
    credit_annuel = credit_mensuel * 12

    revenus = bien.revenus_encaisses_annuels
    charges = bien.charges_annuelles

    # Rendement brut : convention des annonces (revenus théoriques / prix d'achat).
    rendement_brut = bien.revenus_theoriques_annuels / bien.acquisition.prix
    # Rendement net : revenus encaissés moins charges, rapportés au coût total.
    rendement_net = (revenus - charges) / cout_total

    return Resultat(
        nom=bien.nom,
        type_bien=bien.type_bien,
        cout_total=cout_total,
        montant_emprunte=emprunt,
        revenus_annuels=revenus,
        charges_annuelles=charges,
        credit_annuel=credit_annuel,
        rendement_brut=rendement_brut,
        rendement_net=rendement_net,
        cashflow_mensuel=(revenus - charges - credit_annuel) / 12,
        seuil_rendement_brut=bien.seuil_rendement_brut,
    )


def comparer(
    biens: list[Bien],
    financement: Financement = Financement(),
    seulement_au_seuil: bool = False,
) -> list[Resultat]:
    """Analyse plusieurs biens et les classe du meilleur au moins bon cashflow."""
    resultats = [analyser(b, financement) for b in biens]
    if seulement_au_seuil:
        resultats = [r for r in resultats if r.atteint_le_seuil]
    return sorted(resultats, key=lambda r: r.cashflow_mensuel, reverse=True)


def tableau_texte(resultats: list[Resultat]) -> str:
    """Mise en forme lisible dans un terminal."""
    entete = (
        f"{'Bien':<28}{'Type':<24}{'Coût total':>12}"
        f"{'Brut':>8}{'Net':>8}{'Cashflow/mois':>15}  Seuil"
    )
    lignes = [entete, "-" * len(entete)]
    for r in resultats:
        lignes.append(
            f"{r.nom:<28}{r.type_bien:<24}{r.cout_total:>12,.0f}"
            f"{r.rendement_brut:>8.1%}{r.rendement_net:>8.1%}"
            f"{r.cashflow_mensuel:>15,.0f}  {'oui' if r.atteint_le_seuil else 'non'}"
        )
    return "\n".join(lignes).replace(",", " ")
