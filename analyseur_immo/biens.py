"""Description des biens étudiés : immeuble de rapport et location courte durée.

Tous les montants sont en euros. Les taux sont des fractions (0.07 = 7 %).
Les valeurs par défaut sont des hypothèses de départ, à ajuster bien par bien.
Les numéros RG-xx renvoient à docs/regles-de-gestion.md.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Acquisition:
    """Ce que coûte le projet, commun aux deux types de biens."""

    # Prix affiché ou négocié, frais d'agence inclus (FAI).
    prix: float
    # Frais de notaire dans l'ancien, environ 7,5 à 8 % du prix.
    taux_frais_notaire: float = 0.08
    # Travaux, énergétiques compris, imprévus de 10 % inclus.
    travaux: float = 0.0
    # Mobilier initial (location meublée / courte durée).
    ameublement: float = 0.0

    @property
    def frais_notaire(self) -> float:
        return self.prix * self.taux_frais_notaire

    @property
    def cout_total(self) -> float:
        """RG-11 : coût total du projet."""
        return self.prix + self.frais_notaire + self.travaux + self.ameublement


@dataclass
class ImmeubleDeRapport:
    """Immeuble ou maison découpée en plusieurs lots loués à l'année."""

    nom: str
    acquisition: Acquisition
    # Loyer mensuel hors charges de chaque lot d'habitation.
    loyers_mensuels: list[float] = field(default_factory=list)
    # Local commercial en rez-de-chaussée (RG-36 et RG-37).
    loyer_commercial_mensuel: float = 0.0
    bail_commercial_en_cours: bool = False
    decote_loyer_commercial: float = 0.50
    # Part de l'année sans locataire (1 mois par an et par lot = 1/12).
    taux_vacance: float = 1 / 12
    # Taxe foncière réelle. Si non communiquée (None) : 1 mois de loyer par lot (RG-38).
    taxe_fonciere: Optional[float] = None
    # Charges de copropriété ou communes non récupérables sur les locataires.
    charges_non_recuperables: float = 0.0
    assurance_pno: float = 0.0
    # Agence de gestion (7 à 8 %), en part des loyers encaissés.
    taux_gestion: float = 0.07
    # Garantie loyers impayés, en part des loyers encaissés.
    taux_gli: float = 0.03
    # Provision pour entretien courant, en part des loyers théoriques.
    taux_entretien: float = 0.05

    type_bien = "Immeuble de rapport"
    seuil_rendement_brut = 0.10

    @property
    def loyer_commercial_retenu(self) -> float:
        """RG-36 / RG-37 : compté seulement si un bail est en cours, et décoté."""
        if not self.bail_commercial_en_cours:
            return 0.0
        return self.loyer_commercial_mensuel * (1 - self.decote_loyer_commercial)

    @property
    def loyers_mensuels_retenus(self) -> float:
        return sum(self.loyers_mensuels) + self.loyer_commercial_retenu

    @property
    def revenus_theoriques_annuels(self) -> float:
        return self.loyers_mensuels_retenus * 12

    @property
    def revenus_encaisses_annuels(self) -> float:
        return self.revenus_theoriques_annuels * (1 - self.taux_vacance)

    @property
    def taxe_fonciere_retenue(self) -> float:
        if self.taxe_fonciere is not None:
            return self.taxe_fonciere
        return self.loyers_mensuels_retenus

    @property
    def charges_annuelles(self) -> float:
        encaisses = self.revenus_encaisses_annuels
        return (
            self.taxe_fonciere_retenue
            + self.charges_non_recuperables
            + self.assurance_pno
            + encaisses * (self.taux_gestion + self.taux_gli)
            + self.revenus_theoriques_annuels * self.taux_entretien
        )


@dataclass
class LocationCourteDuree:
    """Logement meublé loué à la nuitée, géré par une conciergerie."""

    nom: str
    acquisition: Acquisition
    prix_nuitee: float = 0.0
    # Part des nuits de l'année effectivement louées, saisonnalité comprise.
    taux_occupation: float = 0.55
    taxe_fonciere: float = 0.0
    # Énergie, eau, internet, abonnements : à la charge du propriétaire.
    charges_fonctionnement: float = 0.0
    charges_copropriete: float = 0.0
    assurance: float = 0.0
    cfe: float = 0.0
    # Commission de la conciergerie (20 à 25 %), en part du chiffre d'affaires.
    taux_conciergerie: float = 0.20
    # Commission de la plateforme (Airbnb, Booking...), en part du chiffre d'affaires.
    taux_plateforme: float = 0.03
    # Provision pour entretien et renouvellement du mobilier.
    taux_entretien: float = 0.05

    type_bien = "Location courte durée"
    seuil_rendement_brut = 0.12

    @property
    def revenus_theoriques_annuels(self) -> float:
        """Chiffre d'affaires attendu au taux d'occupation retenu."""
        return self.prix_nuitee * 365 * self.taux_occupation

    @property
    def loyers_mensuels_retenus(self) -> float:
        return self.revenus_theoriques_annuels / 12

    @property
    def revenus_encaisses_annuels(self) -> float:
        # La vacance est déjà intégrée via le taux d'occupation.
        return self.revenus_theoriques_annuels

    @property
    def charges_annuelles(self) -> float:
        ca = self.revenus_theoriques_annuels
        return (
            self.taxe_fonciere
            + self.charges_fonctionnement
            + self.charges_copropriete
            + self.assurance
            + self.cfe
            + ca * (self.taux_conciergerie + self.taux_plateforme + self.taux_entretien)
        )
