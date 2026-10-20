# Règles de gestion

Ce document décrit **ce que calcule le programme et comment**, en langage métier.
Chaque règle porte un identifiant (`RG-xx`) que l'on peut citer dans une demande d'évolution ou une pull request.

Version couverte : **v1, analyse avant impôt**.

---

## 1. Conventions

| Règle | Énoncé |
|---|---|
| RG-01 | Tous les montants sont en euros. Les revenus et charges sont saisis **par an**, sauf les loyers des lots et le prix de la nuitée. |
| RG-02 | Les taux sont saisis en fraction : `0.07` signifie 7 %. |
| RG-03 | Tous les résultats sont **avant impôt** : ni impôt sur le revenu, ni prélèvements sociaux, ni impôt sur les sociétés, ni amortissement comptable. |
| RG-04 | Le calcul porte sur une **année type** de croisière : pas d'inflation, pas de revalorisation des loyers, pas de différé de prêt. |

## 2. Coût de l'acquisition

| Règle | Énoncé |
|---|---|
| RG-10 | **Frais de notaire** = prix × taux de frais de notaire. Valeur par défaut : 8 % (ancien). |
| RG-11 | **Coût total** = prix + frais de notaire + travaux + ameublement. |
| RG-12 | Le prix saisi est le prix payé, **frais d'agence inclus** le cas échéant. |

## 3. Financement

| Règle | Énoncé |
|---|---|
| RG-20 | **Montant emprunté** = coût total − apport. Il ne peut pas être négatif : un apport supérieur au coût total donne un emprunt nul. |
| RG-21 | Le prêt est **amortissable à mensualités constantes** : mensualité = C × t / (1 − (1 + t)^−n), où C est le capital emprunté, t le taux annuel / 12 et n la durée en mois. |
| RG-22 | Si le taux est nul, mensualité = capital / nombre de mois. |
| RG-23 | **Assurance emprunteur** mensuelle = capital emprunté initial × taux annuel d'assurance / 12. Elle est constante sur toute la durée. |
| RG-24 | **Coût annuel du crédit** = (mensualité + assurance) × 12. |
| RG-25 | Le tableau d'amortissement est calculé mois par mois et présenté **par année** : intérêts payés, capital remboursé, capital restant dû. |

Valeurs par défaut : apport 15 000 €, 20 ans, 3,5 %, assurance à 0 % (à renseigner avec un devis réel).

## 4. Immeuble de rapport

Bien découpé en plusieurs lots loués à l'année, en gestion déléguée.

| Règle | Énoncé |
|---|---|
| RG-30 | **Revenus théoriques** annuels = somme des loyers mensuels hors charges de tous les lots × 12. |
| RG-31 | **Revenus encaissés** annuels = revenus théoriques × (1 − taux de vacance). Valeur par défaut : 1 mois par an, soit 1/12. |
| RG-32 | **Charges annuelles** = taxe foncière + charges non récupérables + assurance propriétaire non occupant + frais de gestion + garantie loyers impayés + provision d'entretien. |
| RG-33 | Les **frais de gestion** (7 % par défaut) et la **garantie loyers impayés** (3 % par défaut) s'appliquent aux revenus **encaissés** : on ne paie pas l'agence sur un lot vide. |
| RG-34 | La **provision d'entretien** (5 % par défaut) s'applique aux revenus **théoriques** : un logement vide s'use et s'entretient quand même. |
| RG-35 | Les charges récupérables sur les locataires ne sont pas saisies : elles sont neutres pour le propriétaire. |

## 5. Location courte durée

Logement meublé loué à la nuitée, géré par une conciergerie.

| Règle | Énoncé |
|---|---|
| RG-40 | **Chiffre d'affaires** annuel = prix de la nuitée × 365 × taux d'occupation. Valeur par défaut : 55 %. |
| RG-41 | La vacance est **déjà intégrée** dans le taux d'occupation : revenus encaissés = chiffre d'affaires. |
| RG-42 | **Charges annuelles** = taxe foncière + charges de fonctionnement (énergie, eau, internet) + charges de copropriété + assurance + CFE + commission de conciergerie + commission de plateforme + provision d'entretien. |
| RG-43 | Les commissions de **conciergerie** (20 %), de **plateforme** (3 %) et la provision d'**entretien** (5 %) s'appliquent au chiffre d'affaires. |
| RG-44 | Les frais de ménage refacturés aux voyageurs ne sont pas modélisés : ils sont supposés neutres. |

## 6. Indicateurs de rentabilité

| Règle | Énoncé |
|---|---|
| RG-50 | **Rendement brut** = revenus théoriques annuels / **prix d'achat**. C'est la convention des annonces immobilières, utile pour un premier tri. |
| RG-51 | **Rendement net** = (revenus encaissés − charges annuelles) / **coût total**. Il ne tient pas compte du crédit. |
| RG-52 | **Cashflow mensuel** = (revenus encaissés − charges annuelles − coût annuel du crédit) / 12. |
| RG-53 | **Effort d'épargne** mensuel = la somme à remettre de sa poche chaque mois, soit −cashflow si le cashflow est négatif, sinon 0. |
| RG-54 | Un bien a un **cashflow positif** si son cashflow mensuel est strictement supérieur à 0. |

## 7. Seuils et comparaison

| Règle | Énoncé |
|---|---|
| RG-60 | **Seuil de rendement brut** : 10 % pour un immeuble de rapport, 12 % pour une location courte durée. Un bien l'atteint si son rendement brut est supérieur ou égal au seuil. |
| RG-61 | La comparaison **classe les biens par cashflow mensuel décroissant**. |
| RG-62 | Sur option, la comparaison **écarte les biens qui n'atteignent pas leur seuil** de rendement brut. |

## 8. Limites connues de la v1

- Pas de fiscalité (LMNP au réel, SCI à l'IS) : prévue à l'étape 3.
- Pas de scénarios de sensibilité (taux, vacance, travaux) : prévus à l'étape 3.
- Pas de saisonnalité en courte durée : un seul taux d'occupation sur l'année.
- Pas de prise en compte de la revente ni de l'enrichissement par remboursement du capital.

---

## Tenir ce document à jour

Toute modification d'une règle de calcul doit, dans **la même pull request** :

1. modifier ce document (ajouter, modifier ou supprimer la règle concernée) ;
2. ajouter ou adapter un test qui vérifie la règle sur un cas calculable à la main.
