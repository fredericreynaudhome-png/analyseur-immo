"""Description des biens étudiés : immeuble de rapport et location courte durée.

Tous les montants sont en euros. Les taux sont des fractions (0.07 = 7 %).
Les valeurs par défaut sont des hypothèses de départ, à ajuster bien par bien.
"""

from dataclasses import dataclass, field


@dataclass
class Acquisition:
    """Ce que coûte l'achat, commun aux deux types de biens."""

    prix: float
    # Frais de notaire dans l'ancien, environ 7,5 à 8 % du prix.
    taux_frais_notaire: float = 0.08
    travaux: float = 0.0
    ameublement: float = 0.0

    @property
    def frais_notaire(self) -> float:
        return self.prix * self.taux_frais_notaire

    @property
    def cout_total(self) -> float:
        return self.prix + self.frais_notaire + self.travaux + self.ameublement


@dataclass
class ImmeubleDeRapport:
    """Immeuble ou maison découpée en plusieurs lots loués à l'année."""

    nom: str
    acquisition: Acquisition
    # Loyer mensuel hors charges de chaque lot.
    loyers_mensuels: list[float] = field(default_factory=list)
    # Part de l'année sans locataire (1 mois par an = 1/12).
    taux_vacance: float = 1 / 12
    taxe_fonciere: float = 0.0
    # Charges non récupérables sur les locataires (parties communes, eau, etc.).
    charges_non_recuperables: float = 0.0
    assurance_pno: float = 0.0
    # Agence de gestion, en part des loyers encaissés.
    taux_gestion: float = 0.07
    # Garantie loyers impayés, en part des loyers encaissés.
    taux_gli: float = 0.03
    # Provision pour entretien courant, en part des loyers théoriques.
    taux_entretien: float = 0.05

    type_bien = "Immeuble de rapport"
    seuil_rendement_brut = 0.10

    @property
    def revenus_theoriques_annuels(self) -> float:
        return sum(self.loyers_mensuels) * 12

    @property
    def revenus_encaisses_annuels(self) -> float:
        return self.revenus_theoriques_annuels * (1 - self.taux_vacance)

    @property
    def charges_annuelles(self) -> float:
        encaisses = self.revenus_encaisses_annuels
        return (
            self.taxe_fonciere
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
    # Part des nuits de l'année effectivement louées.
    taux_occupation: float = 0.55
    taxe_fonciere: float = 0.0
    # Énergie, eau, internet, abonnements : à la charge du propriétaire.
    charges_fonctionnement: float = 0.0
    charges_copropriete: float = 0.0
    assurance: float = 0.0
    cfe: float = 0.0
    # Commission de la conciergerie, en part du chiffre d'affaires.
    taux_conciergerie: float = 0.20
    # Commission de la plateforme (Airbnb, Booking...), en part du chiffre d'affaires.
    taux_plateforme: float = 0.03
    # Provision pour renouvellement du linge, petit mobilier, entretien.
    taux_entretien: float = 0.05

    type_bien = "Location courte durée"
    seuil_rendement_brut = 0.12

    @property
    def revenus_theoriques_annuels(self) -> float:
        """Chiffre d'affaires attendu au taux d'occupation retenu."""
        return self.prix_nuitee * 365 * self.taux_occupation

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
