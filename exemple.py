"""Exemple : comparer trois biens fictifs.

Lancer avec :  python exemple.py
"""

from analyseur_immo import (
    Acquisition,
    Financement,
    ImmeubleDeRapport,
    LocationCourteDuree,
    comparer,
    tableau_texte,
)

financement = Financement(apport=15_000, duree_annees=20, taux_annuel=0.035)

biens = [
    ImmeubleDeRapport(
        nom="Immeuble 4 lots (fictif)",
        acquisition=Acquisition(prix=220_000, travaux=25_000),
        loyers_mensuels=[480, 450, 450, 520],
        taxe_fonciere=2_200,
        charges_non_recuperables=900,
        assurance_pno=600,
    ),
    ImmeubleDeRapport(
        nom="Maison 3 lots (fictif)",
        acquisition=Acquisition(prix=150_000, travaux=15_000),
        loyers_mensuels=[420, 400, 380],
        taxe_fonciere=1_500,
        charges_non_recuperables=600,
        assurance_pno=450,
    ),
    LocationCourteDuree(
        nom="T2 bord de mer (fictif)",
        acquisition=Acquisition(prix=140_000, travaux=8_000, ameublement=10_000),
        prix_nuitee=95,
        taux_occupation=0.55,
        taxe_fonciere=900,
        charges_fonctionnement=1_800,
        charges_copropriete=1_200,
        assurance=300,
        cfe=300,
    ),
]

if __name__ == "__main__":
    print("Analyse avant impôt — apport 15 000 €, prêt 20 ans à 3,5 %\n")
    print(tableau_texte(comparer(biens, financement)))
