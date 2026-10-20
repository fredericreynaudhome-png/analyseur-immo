# analyseur-immo

Analyseur de rentabilité pour l'investissement locatif : immeubles de rapport et location courte durée.
Ses règles de calcul sont alignées sur la veille hebdomadaire « Veille immobilière cashflow ».

## Ce que fait le programme

Pour chaque bien, il calcule, **avant impôt** :

- le coût total du projet (prix FAI, frais de notaire, travaux, mobilier) et le montant emprunté ;
- la mensualité du crédit, assurance comprise ;
- le **rendement brut** (loyers ou chiffre d'affaires / coût total du projet) et le **rendement net** ;
- le **cashflow mensuel** et l'effort d'épargne s'il est négatif ;
- le **taux d'endettement** après opération (règle HCSF de 35 %, loyers retenus à 70 %) ;
- la position par rapport à l'**enveloppe de financement** (260 000 € cible, 300 000 € maximum) ;
- l'**éligibilité au top 4** : seuil de rendement brut atteint (10 % immeuble, 12 % courte durée) et cashflow d'au moins 50 € par mois.

Il compare plusieurs biens et les classe du meilleur au moins bon cashflow.

Le détail de chaque calcul est décrit dans les **[règles de gestion](docs/regles-de-gestion.md)**.

## Hypothèses par défaut (modifiables bien par bien)

| Paramètre | Valeur |
|---|---|
| Apport | 15 000 €, qui couvre d'abord les frais de notaire |
| Prêt | 20 ans (25 maximum) à 3,5 %, à remplacer par le taux du marché |
| Assurance emprunteur | 0,30 % par an |
| Revenus de l'emprunteur | 4 000 € nets par mois, aucun autre crédit |
| Frais de notaire | 8 % du prix |
| Immeuble : vacance | 1 mois par an et par lot |
| Immeuble : gestion / GLI / entretien | 7 % / 3 % / 5 % des loyers |
| Immeuble : taxe foncière non communiquée | 1 mois de loyer par lot |
| Immeuble : local commercial | compté seulement avec un bail en cours, décoté de 50 % |
| Courte durée : taux d'occupation | 55 % |
| Courte durée : conciergerie / plateforme / entretien | 20 % / 3 % / 5 % du chiffre d'affaires |

## Utilisation

```bash
pip install pytest
python exemple.py        # compare trois biens fictifs
python -m pytest         # vérifie les règles de gestion
```

## Organisation du code

- `analyseur_immo/financement.py` : mensualité, assurance, amortissement, taux d'endettement
- `analyseur_immo/biens.py` : description d'un immeuble de rapport et d'une location courte durée
- `analyseur_immo/analyse.py` : indicateurs, éligibilité, alertes, comparaison, affichage
- `docs/regles-de-gestion.md` : règles de gestion numérotées
- `tests/` : un test par règle, sur des cas vérifiables à la main

## Feuille de route

1. ~~Moteur de calcul et tests~~
2. ~~Alignement sur la veille hebdomadaire~~
3. Branchement de la veille hebdomadaire sur ce programme
4. Prix cible de négociation et scénarios (taux, vacance, travaux)
5. Fiscalité : LMNP au réel, SCI à l'IS
6. Interface web locale (Streamlit)
7. Tests relancés automatiquement par GitHub à chaque modification
