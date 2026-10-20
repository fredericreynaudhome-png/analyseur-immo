"""Analyseur de rentabilité pour l'investissement locatif."""

from .analyse import Resultat, analyser, comparer, tableau_texte
from .biens import Acquisition, ImmeubleDeRapport, LocationCourteDuree
from .financement import (
    Financement,
    mensualite,
    tableau_amortissement,
    taux_endettement,
)

__all__ = [
    "Acquisition",
    "Financement",
    "ImmeubleDeRapport",
    "LocationCourteDuree",
    "Resultat",
    "analyser",
    "comparer",
    "mensualite",
    "tableau_amortissement",
    "tableau_texte",
    "taux_endettement",
]
