# Règles de gestion

Ce document décrit **ce que calcule le programme et comment**, en langage métier.
Chaque règle porte un identifiant (`RG-xx`) que l'on peut citer dans une demande d'évolution ou une pull request. Les tests automatisés portent le numéro de la règle qu'ils vérifient.

Version couverte : **v2, analyse avant impôt, alignée sur la tâche planifiée « Veille immobilière cashflow »**.

---

## 1. Conventions

| Règle | Énoncé |
|---|---|
| RG-01 | Tous les montants sont en euros. Les revenus et charges sont saisis **par an**, sauf les loyers des lots et le prix de la nuitée, saisis par mois et par nuit. |
| RG-02 | Les taux sont saisis en fraction : `0.07` signifie 7 %. |
| RG-03 | Tous les résultats sont **avant impôt** : ni impôt sur le revenu, ni prélèvements sociaux, ni impôt sur les sociétés, ni amortissement comptable. La structure juridique (LMNP, SCI à l'IS…) n'est pas tranchée. |
| RG-04 | Le calcul porte sur une **année type** de croisière : pas d'inflation, pas de revalorisation des loyers, pas de différé de prêt. |
| RG-05 | Aucune donnée n'est inventée : une donnée non communiquée est soit laissée à sa valeur par défaut documentée ici, soit estimée et **étiquetée comme estimation** dans le rapport. |

## 2. Coût du projet

| Règle | Énoncé |
|---|---|
| RG-10 | **Frais de notaire** = prix × taux de frais de notaire. Valeur par défaut : 8 % (ancien). |
| RG-11 | **Coût total du projet** = prix FAI + frais de notaire + travaux + mobilier initial. |
| RG-12 | Le prix saisi est le **prix frais d'agence inclus (FAI)**, affiché ou négocié. |
| RG-13 | Les **travaux** incluent les travaux énergétiques nécessaires pour atteindre au moins le DPE D, et 10 % d'imprévus. Leur chiffrage est fait en amont (ratios €/m²) et saisi comme un montant. |

## 3. Financement

| Règle | Énoncé |
|---|---|
| RG-20 | L'**apport** (15 000 € par défaut) couvre en priorité les frais de notaire. **Montant emprunté** = coût total − apport, jamais négatif. |
| RG-21 | Le prêt est **amortissable à mensualités constantes** : mensualité = C × t / (1 − (1 + t)^−n), où C est le capital emprunté, t le taux annuel / 12 et n la durée en mois. Durée par défaut : 20 ans ; **durée maximale : 25 ans** (règle HCSF), au-delà le programme refuse le calcul. |
| RG-22 | Si le taux est nul, mensualité = capital / nombre de mois. |
| RG-23 | **Assurance emprunteur** mensuelle = capital emprunté initial × taux annuel d'assurance / 12, constante sur toute la durée. Valeur par défaut : **0,30 % par an**. |
| RG-24 | **Mensualité du crédit** = mensualité du prêt + assurance emprunteur. |
| RG-25 | Le tableau d'amortissement est calculé mois par mois et présenté **par année** : intérêts payés, capital remboursé, capital restant dû. |
| RG-26 | **Taux d'endettement après opération** = (mensualité du crédit + autres crédits en cours) / (revenus mensuels nets + 70 % des loyers mensuels du bien). Il doit rester **inférieur ou égal à 35 %** (règle HCSF, assurance comprise). Hypothèse par défaut : 4 000 € de revenus nets mensuels, aucun autre crédit. |
| RG-27 | **Enveloppe de financement**, sur le coût total du projet : jusqu'à 260 000 € = « dans l'enveloppe cible » ; jusqu'à 300 000 € = « au-delà de l'enveloppe cible, finançabilité à confirmer » ; au-delà = « hors enveloppe ». |
| RG-28 | Le **taux du crédit** (3,5 % par défaut) est un paramètre : la veille hebdomadaire le remplace par le taux moyen du marché sur 20 ou 25 ans. |

## 4. Immeuble de rapport

Bien découpé en plusieurs lots loués à l'année, en gestion déléguée à une agence.

| Règle | Énoncé |
|---|---|
| RG-30 | **Revenus théoriques** annuels = (somme des loyers mensuels hors charges des lots d'habitation + loyer commercial retenu) × 12. |
| RG-31 | **Revenus encaissés** annuels = revenus théoriques × (1 − taux de vacance). Valeur par défaut : **1 mois par an et par lot**, soit 1/12. |
| RG-32 | **Charges annuelles** = taxe foncière + charges non récupérables (copropriété, parties communes) + assurance propriétaire non occupant + frais de gestion + garantie loyers impayés + provision d'entretien. |
| RG-33 | Les **frais de gestion** (7 % par défaut, fourchette 7-8 %) et la **garantie loyers impayés** (3 %) s'appliquent aux revenus **encaissés** : on ne paie pas l'agence sur un lot vide. |
| RG-34 | La **provision d'entretien** (5 %) s'applique aux revenus **théoriques** : un logement vide s'use et s'entretient quand même. |
| RG-35 | Les charges récupérables sur les locataires ne sont pas saisies : elles sont neutres pour le propriétaire. |
| RG-36 | Un **local commercial** en rez-de-chaussée n'est compté que s'il est **occupé avec un bail en cours**. Sinon son loyer vaut 0. |
| RG-37 | Le loyer d'un local commercial occupé subit une **décote de 50 %**, dans le rendement comme dans le cashflow, pour tenir compte du risque de vacance. |
| RG-38 | Si la **taxe foncière** n'est pas communiquée, elle est estimée à **un mois de loyer par lot**, soit les loyers mensuels retenus. |

## 5. Location courte durée

Logement meublé loué à la nuitée, géré par une conciergerie.

| Règle | Énoncé |
|---|---|
| RG-40 | **Chiffre d'affaires** annuel = prix moyen de la nuitée × 365 × taux d'occupation annuel. Valeur par défaut : 55 %. La saisonnalité est intégrée dans le prix moyen et le taux d'occupation. |
| RG-41 | La vacance est **déjà intégrée** dans le taux d'occupation : revenus encaissés = chiffre d'affaires. |
| RG-42 | **Charges annuelles** = taxe foncière + charges de fonctionnement (énergie, eau, internet, abonnements) + charges de copropriété + assurance + CFE + commission de conciergerie + commission de plateforme + provision d'entretien et de renouvellement du mobilier. |
| RG-43 | Les commissions de **conciergerie** (20 % par défaut, fourchette 20-25 %), de **plateforme** (3 %) et la provision d'**entretien** (5 %) s'appliquent au chiffre d'affaires. |
| RG-44 | Les frais de ménage refacturés aux voyageurs ne sont pas modélisés : ils sont supposés neutres. |
| RG-45 | Le **mobilier initial** fait partie du coût total du projet (RG-11). |
| RG-46 | Pour le taux d'endettement (RG-26), le chiffre d'affaires mensuel moyen est traité comme un loyer et retenu à 70 %. |

## 6. Indicateurs de rentabilité

| Règle | Énoncé |
|---|---|
| RG-50 | **Rendement brut** = revenus théoriques annuels (loyers hors charges ou chiffre d'affaires) / **coût total du projet** (prix FAI + notaire + travaux + mobilier). C'est une définition exigeante : à loyer égal, plus il y a de travaux, plus le rendement baisse. |
| RG-51 | **Rendement net** = (revenus encaissés − charges annuelles) / coût total du projet. Il ne tient pas compte du crédit. |
| RG-52 | **Cashflow mensuel avant impôt** = (revenus encaissés − charges annuelles) / 12 − mensualité du crédit (assurance comprise). |
| RG-53 | **Effort d'épargne** mensuel = la somme à remettre de sa poche chaque mois, soit −cashflow si le cashflow est négatif, sinon 0. |
| RG-54 | Un bien a un **cashflow positif** si son cashflow mensuel est strictement supérieur à 0. |

## 7. Seuils et sélection

| Règle | Énoncé |
|---|---|
| RG-60 | **Seuil de rendement brut** : 10 % pour un immeuble de rapport, 12 % pour une location courte durée. Un bien l'atteint si son rendement brut est supérieur ou égal au seuil. Cible : 10 à 12 %. |
| RG-61 | La comparaison **classe les biens par cashflow mensuel décroissant**. |
| RG-62 | Sur option, la comparaison **écarte les biens qui n'atteignent pas leur seuil** de rendement brut. |
| RG-63 | Un cashflow inférieur à **50 € par mois** est considéré comme « quasi nul ». |
| RG-64 | Un bien est **éligible au top 4** s'il atteint son seuil de rendement brut **et** dégage un cashflow d'au moins 50 € par mois. Un bien au cashflow négatif ou quasi nul n'entre pas dans le top 4, même si son rendement brut atteint le seuil. |
| RG-65 | Le dépassement du taux d'endettement de 35 % et le dépassement de l'enveloppe cible ne retirent pas le bien du classement : ils produisent une **alerte** affichée avec le résultat. |

## 8. Limites connues

- Pas de fiscalité (LMNP au réel, SCI à l'IS) : prévue dans une étape ultérieure.
- Pas de scénarios de sensibilité (taux, vacance, travaux) ni de calcul de prix cible de négociation : à venir.
- Pas de prise en compte de la revente ni de l'enrichissement par remboursement du capital.
- Hors programme, restent du ressort de la veille : la recherche des annonces, l'analyse de la demande locative, la vérification des restrictions de location courte durée et du DPE, le chiffrage des travaux.

---

## Historique

| Version | Changements |
|---|---|
| v1 | Moteur de calcul initial. Rendement brut sur le prix d'achat. |
| v2 | Alignement sur la tâche planifiée : rendement brut sur le coût total (RG-50), assurance 0,30 % (RG-23), durée maximale 25 ans (RG-21), taux d'endettement HCSF (RG-26), enveloppe de financement (RG-27), local commercial (RG-36, RG-37), taxe foncière estimée (RG-38), éligibilité au top 4 (RG-63, RG-64), alertes (RG-65). |

## Tenir ce document à jour

Toute modification d'une règle de calcul doit, dans **la même pull request** :

1. modifier ce document (ajouter, modifier ou supprimer la règle concernée, et compléter l'historique) ;
2. ajouter ou adapter un test qui vérifie la règle sur un cas calculable à la main, en citant son numéro ;
3. si la règle est aussi décrite dans les consignes de la tâche planifiée, mettre ces consignes à jour.
