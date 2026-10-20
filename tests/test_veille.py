"""Tests de la porte d'entrée utilisée par la veille hebdomadaire."""

import json

import pytest

from analyseur_immo import Financement
from analyseur_immo.veille import ErreurDonnees, analyser_candidats, charger_bien, main

SANS_CREDIT = Financement(apport=1_000_000)

IMMEUBLE = {
    "id": "t1",
    "strategie": "immeuble",
    "prix": 100_000,
    "loyers_mensuels": [300, 300, 300],
    "taux_vacance": 0,
    "taxe_fonciere": 0,
    "taux_gestion": 0,
    "taux_gli": 0,
    "taux_entretien": 0,
}


def test_charger_un_immeuble():
    bien = charger_bien(IMMEUBLE)
    assert bien.acquisition.cout_total == pytest.approx(108_000)
    assert bien.nom == "t1"


def test_charger_une_location_courte_duree():
    bien = charger_bien(
        {"id": "t2", "strategie": "courte_duree", "prix": 100_000, "prix_nuitee": 100}
    )
    assert bien.type_bien == "Location courte durée"


def test_strategie_inconnue_refusee():
    with pytest.raises(ErreurDonnees):
        charger_bien({"id": "x", "strategie": "parking", "prix": 1})


def test_champ_inconnu_refuse():
    # Une faute de frappe ne doit pas être ignorée silencieusement.
    with pytest.raises(ErreurDonnees, match="loyer"):
        charger_bien({**IMMEUBLE, "loyer": 900})


def test_prix_manquant_refuse():
    sans_prix = {k: v for k, v in IMMEUBLE.items() if k != "prix"}
    with pytest.raises(ErreurDonnees):
        charger_bien(sans_prix)


def test_rg66_analyse_au_prix_cible():
    [analyse] = analyser_candidats([{**IMMEUBLE, "prix_cible": 90_000}], SANS_CREDIT)
    # Prix affiché : 10 800 / 108 000 ; prix cible : 10 800 / 97 200
    assert analyse["prix_affiche"].rendement_brut == pytest.approx(0.10)
    assert analyse["prix_cible"].rendement_brut == pytest.approx(10_800 / 97_200)


def test_sans_prix_cible_une_seule_analyse():
    [analyse] = analyser_candidats([IMMEUBLE], SANS_CREDIT)
    assert "prix_cible" not in analyse


def test_ligne_de_commande_json(tmp_path, capsys):
    fichier = tmp_path / "candidats.json"
    fichier.write_text(json.dumps({"biens": [IMMEUBLE]}), encoding="utf-8")
    assert main([str(fichier), "--taux", "0.03", "--duree", "25", "--format", "json"]) == 0
    sortie = json.loads(capsys.readouterr().out)
    assert sortie["hypotheses"]["duree_annees"] == 25
    assert sortie["hypotheses"]["taux_credit_pct"] == 3.0
    assert sortie["biens"][0]["prix_affiche"]["rendement_brut_pct"] == 10.0


def test_ligne_de_commande_refuse_une_duree_de_30_ans(tmp_path, capsys):
    fichier = tmp_path / "candidats.json"
    fichier.write_text(json.dumps([IMMEUBLE]), encoding="utf-8")
    assert main([str(fichier), "--duree", "30"]) == 1
    assert "25" in capsys.readouterr().err
