"""Porte d'entrée utilisée par la veille hebdomadaire « Veille immobilière cashflow ».

La veille décrit ses biens candidats dans un fichier JSON (format dans
docs/format-entree.md), puis lance :

    python -m analyseur_immo.veille candidats.json --taux 0.034 --duree 25

Le programme applique les règles de gestion (docs/regles-de-gestion.md) et
affiche les résultats en tableau Markdown, ou en JSON avec --format json.
Chaque bien est analysé au prix affiché et, s'il est renseigné, au prix cible
de négociation (RG-66).
"""

import argparse
import json
import sys
from dataclasses import fields, replace
from pathlib import Path

from .analyse import Resultat, analyser
from .biens import Acquisition, ImmeubleDeRapport, LocationCourteDuree
from .financement import Financement

STRATEGIES = {
    "immeuble": ImmeubleDeRapport,
    "courte_duree": LocationCourteDuree,
}
CHAMPS_ACQUISITION = {f.name for f in fields(Acquisition)}
CHAMPS_GENERAUX = {"id", "strategie", "nom", "prix_cible", "ville", "url"}


class ErreurDonnees(ValueError):
    """Fichier d'entrée incomplet ou incorrect."""


def charger_bien(donnees: dict):
    """Transforme la description d'un candidat en bien analysable."""
    strategie = donnees.get("strategie")
    if strategie not in STRATEGIES:
        raise ErreurDonnees(
            f"{donnees.get('id', '?')} : stratégie « {strategie} » inconnue "
            f"(attendu : {', '.join(STRATEGIES)})."
        )
    if "prix" not in donnees:
        raise ErreurDonnees(f"{donnees.get('id', '?')} : prix manquant.")

    classe = STRATEGIES[strategie]
    champs_bien = {f.name for f in fields(classe)} - {"nom", "acquisition"}
    inconnus = set(donnees) - CHAMPS_GENERAUX - CHAMPS_ACQUISITION - champs_bien
    if inconnus:
        raise ErreurDonnees(
            f"{donnees.get('id', '?')} : champ(s) inconnu(s) {sorted(inconnus)}."
        )

    acquisition = Acquisition(
        **{k: v for k, v in donnees.items() if k in CHAMPS_ACQUISITION}
    )
    return classe(
        nom=donnees.get("nom") or donnees.get("id", "Bien sans nom"),
        acquisition=acquisition,
        **{k: v for k, v in donnees.items() if k in champs_bien},
    )


def _resultat_en_dict(r: Resultat) -> dict:
    return {
        "cout_total": round(r.cout_total),
        "montant_emprunte": round(r.montant_emprunte),
        "revenus_annuels": round(r.revenus_annuels),
        "charges_annuelles": round(r.charges_annuelles),
        "mensualite_credit": round(r.mensualite_credit),
        "rendement_brut_pct": round(r.rendement_brut * 100, 1),
        "rendement_net_pct": round(r.rendement_net * 100, 1),
        "cashflow_mensuel": round(r.cashflow_mensuel),
        "taux_endettement_pct": round(r.taux_endettement * 100, 1),
        "enveloppe": r.enveloppe,
        "atteint_seuil_brut": r.atteint_le_seuil,
        "eligible_top4": r.eligible_top4,
        "alertes": r.alertes,
    }


def analyser_candidat(donnees: dict, financement: Financement) -> dict:
    """Analyse un candidat au prix affiché et au prix cible s'il existe."""
    bien = charger_bien(donnees)
    sortie = {
        "id": donnees.get("id"),
        "nom": bien.nom,
        "strategie": bien.type_bien,
        "seuil_brut_pct": round(bien.seuil_rendement_brut * 100),
        "prix": donnees["prix"],
        "prix_affiche": analyser(bien, financement),
    }
    prix_cible = donnees.get("prix_cible")
    if prix_cible:
        sortie["prix_negocie"] = prix_cible
        bien_negocie = replace(bien, acquisition=replace(bien.acquisition, prix=prix_cible))
        sortie["prix_cible"] = analyser(bien_negocie, financement)
    return sortie


def analyser_candidats(candidats: list[dict], financement: Financement) -> list[dict]:
    """Analyse tous les candidats, classés par cashflow au meilleur prix disponible."""
    analyses = [analyser_candidat(c, financement) for c in candidats]

    def cle(a):
        return a.get("prix_cible", a["prix_affiche"]).cashflow_mensuel

    return sorted(analyses, key=cle, reverse=True)


def en_json(analyses: list[dict], financement: Financement) -> str:
    sortie = {
        "hypotheses": {
            "apport": financement.apport,
            "duree_annees": financement.duree_annees,
            "taux_credit_pct": round(financement.taux_annuel * 100, 2),
            "taux_assurance_pct": round(financement.taux_assurance_annuel * 100, 2),
            "revenus_mensuels_nets": financement.revenus_mensuels_nets,
        },
        "biens": [
            {
                **{k: v for k, v in a.items() if k not in ("prix_affiche", "prix_cible")},
                "prix_affiche": _resultat_en_dict(a["prix_affiche"]),
                **(
                    {"prix_cible": _resultat_en_dict(a["prix_cible"])}
                    if "prix_cible" in a
                    else {}
                ),
            }
            for a in analyses
        ],
    }
    return json.dumps(sortie, ensure_ascii=False, indent=2)


def _pct(x: float, decimales: int = 1) -> str:
    return f"{x * 100:.{decimales}f} %".replace(".", ",")


def _euros(x: float) -> str:
    return f"{x:_.0f} €".replace("_", " ")


def en_markdown(analyses: list[dict], financement: Financement) -> str:
    lignes = [
        f"Hypothèses : apport {_euros(financement.apport)}, prêt {financement.duree_annees} ans "
        f"à {_pct(financement.taux_annuel, 2)}, assurance {_pct(financement.taux_assurance_annuel, 2)}, "
        f"revenus {_euros(financement.revenus_mensuels_nets)} nets/mois. Avant impôt.",
        "",
        "| Bien | Stratégie | Prix | Coût total | Brut | Mensualité | Cashflow/mois "
        "| Endettement | Top 4 | Alertes |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for a in analyses:
        for cle, champ_prix, libelle in (
            ("prix_affiche", "prix", "affiché"),
            ("prix_cible", "prix_negocie", "cible"),
        ):
            if cle not in a:
                continue
            r = a[cle]
            lignes.append(
                f"| {a['nom']} | {a['strategie']} | {_euros(a[champ_prix])} ({libelle}) "
                f"| {_euros(r.cout_total)} "
                f"| {_pct(r.rendement_brut)} | {_euros(r.mensualite_credit)} "
                f"| {_euros(r.cashflow_mensuel)} | {_pct(r.taux_endettement)} "
                f"| {'oui' if r.eligible_top4 else 'non'} | {' ; '.join(r.alertes) or '-'} |"
            )
    return "\n".join(lignes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fichier", help="fichier JSON des biens candidats")
    parser.add_argument("--taux", type=float, help="taux du crédit, ex. 0.034 pour 3,4 %%")
    parser.add_argument("--duree", type=int, help="durée du prêt en années (25 maximum)")
    parser.add_argument("--assurance", type=float, help="taux d'assurance, ex. 0.003")
    parser.add_argument("--revenus", type=float, help="revenus mensuels nets de l'emprunteur")
    parser.add_argument("--apport", type=float, help="apport en euros")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args(argv)

    options = {
        "taux_annuel": args.taux,
        "duree_annees": args.duree,
        "taux_assurance_annuel": args.assurance,
        "revenus_mensuels_nets": args.revenus,
        "apport": args.apport,
    }
    try:
        financement = Financement(**{k: v for k, v in options.items() if v is not None})
        candidats = json.loads(Path(args.fichier).read_text(encoding="utf-8"))
        if isinstance(candidats, dict):
            candidats = candidats.get("biens", [])
        analyses = analyser_candidats(candidats, financement)
    except (ErreurDonnees, ValueError, OSError) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1

    sortie = en_json if args.format == "json" else en_markdown
    print(sortie(analyses, financement))
    return 0


if __name__ == "__main__":
    sys.exit(main())
