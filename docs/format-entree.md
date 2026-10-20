# Format du fichier des biens candidats

La veille hebdomadaire décrit les biens qu'elle a trouvés dans un fichier JSON, puis lance :

```bash
python -m analyseur_immo.veille candidats.json --taux 0.034 --duree 25
python -m analyseur_immo.veille candidats.json --taux 0.034 --duree 25 --format json
```

Sortie par défaut : un tableau Markdown, prêt à être repris dans le rapport. Avec `--format json` : tous les chiffres détaillés, pour le fichier de suivi.

## Options de la commande

| Option | Rôle | Par défaut |
|---|---|---|
| `--taux` | taux du crédit du marché, en fraction (`0.034` = 3,4 %) | 0.035 |
| `--duree` | durée du prêt en années, 25 au maximum | 20 |
| `--assurance` | taux annuel d'assurance emprunteur | 0.003 |
| `--revenus` | revenus mensuels nets de l'emprunteur | 4000 |
| `--apport` | apport en euros | 15000 |
| `--format` | `markdown` ou `json` | markdown |

## Structure du fichier

```json
{
  "biens": [
    { "id": "...", "strategie": "immeuble", "prix": 165000, "...": "..." },
    { "id": "...", "strategie": "courte_duree", "prix": 120000, "...": "..." }
  ]
}
```

Une simple liste `[ {...}, {...} ]` est aussi acceptée. Un exemple complet se trouve dans `exemples/candidats.json`.

**Tout champ inconnu provoque une erreur** : une faute de frappe ne doit pas fausser silencieusement un calcul. Un champ absent prend la valeur par défaut des [règles de gestion](regles-de-gestion.md).

## Champs communs

| Champ | Obligatoire | Description |
|---|---|---|
| `id` | conseillé | identifiant du bien, le même que dans `biens_suivis.csv` |
| `strategie` | oui | `immeuble` ou `courte_duree` |
| `nom`, `ville`, `url` | non | informations d'affichage |
| `prix` | oui | prix affiché FAI |
| `prix_cible` | non | prix cible de négociation : le bien est alors analysé aux deux prix (RG-66) |
| `taux_frais_notaire` | non | 0.08 par défaut |
| `travaux` | non | montant des travaux, énergétiques et imprévus compris |
| `ameublement` | non | mobilier initial |

## Champs de l'immeuble de rapport (`immeuble`)

| Champ | Description |
|---|---|
| `loyers_mensuels` | liste des loyers mensuels hors charges, un par lot d'habitation, ex. `[520, 480, 450]` |
| `loyer_commercial_mensuel` | loyer du local commercial |
| `bail_commercial_en_cours` | `true` seulement si le local est occupé avec un bail en cours |
| `decote_loyer_commercial` | 0.50 par défaut |
| `taux_vacance` | 1/12 par défaut |
| `taxe_fonciere` | à omettre si non communiquée : estimée à un mois de loyer par lot |
| `charges_non_recuperables` | charges annuelles de copropriété ou communes non récupérables |
| `assurance_pno` | assurance propriétaire non occupant, annuelle |
| `taux_gestion`, `taux_gli`, `taux_entretien` | 0.07, 0.03 et 0.05 par défaut |

## Champs de la location courte durée (`courte_duree`)

| Champ | Description |
|---|---|
| `prix_nuitee` | prix moyen de la nuitée sur l'année |
| `taux_occupation` | taux d'occupation annuel, 0.55 par défaut |
| `taxe_fonciere`, `charges_fonctionnement`, `charges_copropriete`, `assurance`, `cfe` | montants annuels |
| `taux_conciergerie`, `taux_plateforme`, `taux_entretien` | 0.20, 0.03 et 0.05 par défaut |
