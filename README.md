# analyseur-immo

Analyseur de rentabilité pour l'investissement locatif : immeubles de rapport et location courte durée.

## Ce que fait la version 1

Pour chaque bien, le moteur calcule, **avant impôt** :

- le coût total de l'opération (prix, frais de notaire, travaux, ameublement) et le montant emprunté ;
- le **rendement brut** (loyers théoriques / prix d'achat, la convention des annonces) ;
- le **rendement net** (revenus encaissés moins charges / coût total) ;
- le **cashflow mensuel** après remboursement du crédit, et l'effort d'épargne s'il est négatif ;
- si le bien atteint le seuil de rendement brut visé : **10 %** pour un immeuble de rapport, **12 %** pour la location courte durée.

Il compare plusieurs biens et les classe du meilleur au moins bon cashflow.

## Hypothèses par défaut (modifiables bien par bien)

| Paramètre | Valeur |
|---|---|
| Apport | 15 000 € |
| Prêt | 20 ans à 3,5 %, assurance emprunteur à 0 (à renseigner) |
| Frais de notaire | 8 % du prix |
| Immeuble : vacance | 1 mois par an |
| Immeuble : gestion / GLI / entretien | 7 % / 3 % / 5 % des loyers |
| Courte durée : taux d'occupation | 55 % |
| Courte durée : conciergerie / plateforme / entretien | 20 % / 3 % / 5 % du chiffre d'affaires |

## Utilisation

```bash
pip install pytest
python exemple.py        # compare trois biens fictifs
python -m pytest         # vérifie les formules
```

## Organisation du code

- `analyseur_immo/financement.py` : mensualité, assurance, tableau d'amortissement
- `analyseur_immo/biens.py` : description d'un immeuble de rapport et d'une location courte durée
- `analyseur_immo/analyse.py` : indicateurs de rentabilité, comparaison, affichage
- `tests/` : tests automatisés sur des cas vérifiables à la main

## Feuille de route

1. ~~Moteur de calcul et tests~~
2. Portefeuille de biens enregistrés (CSV ou SQLite)
3. Scénarios : taux, vacance, travaux ; fiscalité LMNP au réel / SCI à l'IS
4. Interface web locale (Streamlit)
5. Tests relancés automatiquement par GitHub à chaque modification
