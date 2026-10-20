"""Analyse de rentabilité d'un bien et comparaison de plusieurs biens.

Tous les résultats sont AVANT IMPÔT. Les numéros RG-xx renvoient à
docs/regles-de-gestion.md.
"""

from dataclasses import dataclass
from typing import Union

from .biens import ImmeubleDeRapport, LocationCourteDuree
from .financement import (
    TAUX_ENDETTEMENT_MAX,
    Financement,
    assurance_mensuelle,
    mensualite,
    taux_endettement,
)

Bien = Union[ImmeubleDeRapport, LocationCourteDuree]

# RG-63 : en dessous de ce cashflow mensuel, le bien est considéré « quasi nul ».
CASHFLOW_MENSUEL_MINIMUM = 50.0

ENVELOPPE_CIBLE = "dans l'enveloppe cible"
ENVELOPPE_A_CONFIRMER = "au-delà de l'enveloppe cible, finançabilité à confirmer"
ENVELOPPE_HORS = "hors enveloppe"


@dataclass(frozen=True)
class Resultat:
    nom: str
    type_bien: str
    cout_total: float
    montant_emprunte: float
    revenus_annuels: float
    charges_annuelles: float
    mensualite_credit: float
    rendement_brut: float
    rendement_net: float
    cashflow_mensuel: float
    taux_endettement: float
    enveloppe: str
    seuil_rendement_brut: float

    @property
    def credit_annuel(self) -> float:
        return self.mensualite_credit * 12

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

    @property
    def respecte_hcsf(self) -> bool:
        return self.taux_endettement <= TAUX_ENDETTEMENT_MAX

    @property
    def eligible_top4(self) -> bool:
        """RG-64 : seuil de rendement brut atteint ET vrai cashflow."""
        return self.atteint_le_seuil and self.cashflow_mensuel >= CASHFLOW_MENSUEL_MINIMUM

    @property
    def alertes(self) -> list[str]:
        """RG-65 : points à signaler, sans exclure le bien."""
        alertes = []
        if not self.respecte_hcsf:
            alertes.append(f"taux d'endettement {self.taux_endettement:.1%} > 35 %")
        if self.enveloppe != ENVELOPPE_CIBLE:
            alertes.append(self.enveloppe)
        return alertes


def statut_enveloppe(cout_total: float, financement: Financement) -> str:
    """RG-27 : position du coût total par rapport à l'enveloppe de financement."""
    if cout_total <= financement.enveloppe_cible:
        return ENVELOPPE_CIBLE
    if cout_total <= financement.enveloppe_maximum:
        return ENVELOPPE_A_CONFIRMER
    return ENVELOPPE_HORS


def analyser(bien: Bien, financement: Financement = Financement()) -> Resultat:
    """Calcule les indicateurs de rentabilité d'un bien."""
    cout_total = bien.acquisition.cout_total
    emprunt = max(cout_total - financement.apport, 0.0)

    mensualite_credit = mensualite(
        emprunt, financement.taux_annuel, financement.duree_annees
    ) + assurance_mensuelle(emprunt, financement.taux_assurance_annuel)

    revenus = bien.revenus_encaisses_annuels
    charges = bien.charges_annuelles

    return Resultat(
        nom=bien.nom,
        type_bien=bien.type_bien,
        cout_total=cout_total,
        montant_emprunte=emprunt,
        revenus_annuels=revenus,
        charges_annuelles=charges,
        mensualite_credit=mensualite_credit,
        # RG-50 : rendement brut sur le coût total du projet.
        rendement_brut=bien.revenus_theoriques_annuels / cout_total,
        # RG-51 : rendement net sur le coût total du projet.
        rendement_net=(revenus - charges) / cout_total,
        # RG-52
        cashflow_mensuel=revenus / 12 - charges / 12 - mensualite_credit,
        # RG-26
        taux_endettement=taux_endettement(
            mensualite_credit, bien.loyers_mensuels_retenus, financement
        ),
        enveloppe=statut_enveloppe(cout_total, financement),
        seuil_rendement_brut=bien.seuil_rendement_brut,
    )


def comparer(
    biens: list[Bien],
    financement: Financement = Financement(),
    seulement_au_seuil: bool = False,
    seulement_eligibles: bool = False,
) -> list[Resultat]:
    """Analyse plusieurs biens et les classe du meilleur au moins bon cashflow."""
    resultats = [analyser(b, financement) for b in biens]
    if seulement_au_seuil:
        resultats = [r for r in resultats if r.atteint_le_seuil]
    if seulement_eligibles:
        resultats = [r for r in resultats if r.eligible_top4]
    return sorted(resultats, key=lambda r: r.cashflow_mensuel, reverse=True)


def tableau_texte(resultats: list[Resultat]) -> str:
    """Mise en forme lisible dans un terminal."""
    entete = (
        f"{'Bien':<28}{'Coût total':>12}{'Brut':>8}{'Net':>8}"
        f"{'Crédit/mois':>13}{'Cashflow/mois':>15}{'Endett.':>9}  Top 4  Alertes"
    )
    lignes = [entete, "-" * len(entete)]
    for r in resultats:
        lignes.append(
            f"{r.nom:<28}{r.cout_total:>12_.0f}"
            f"{r.rendement_brut:>8.1%}{r.rendement_net:>8.1%}"
            f"{r.mensualite_credit:>13_.0f}{r.cashflow_mensuel:>15_.0f}"
            f"{r.taux_endettement:>9.1%}  {'oui' if r.eligible_top4 else 'non':<5}  "
            f"{' ; '.join(r.alertes) or '-'}"
        )
    return "\n".join(lignes).replace("_", " ")
