"""Tests des règles de gestion. Chaque test cite la règle RG-xx qu'il vérifie."""

import pytest

from analyseur_immo import (
    Acquisition,
    Financement,
    ImmeubleDeRapport,
    LocationCourteDuree,
    analyser,
    comparer,
)
from analyseur_immo.analyse import (
    ENVELOPPE_A_CONFIRMER,
    ENVELOPPE_CIBLE,
    ENVELOPPE_HORS,
)

SANS_CREDIT = Financement(apport=1_000_000)
CREDIT_SIMPLE = Financement(apport=8_000, duree_annees=20, taux_annuel=0.035, taux_assurance_annuel=0)


def immeuble_simple(**kwargs):
    """Immeuble facile à vérifier à la main : coût total 108 000 €, 3 lots à 300 €, aucune charge."""
    valeurs = dict(
        nom="Test",
        acquisition=Acquisition(prix=100_000, taux_frais_notaire=0.08),
        loyers_mensuels=[300, 300, 300],
        taux_vacance=0,
        taxe_fonciere=0,
        taux_gestion=0,
        taux_gli=0,
        taux_entretien=0,
    )
    valeurs.update(kwargs)
    return ImmeubleDeRapport(**valeurs)


# --- Coût du projet ---------------------------------------------------------

def test_rg11_cout_total():
    acq = Acquisition(prix=100_000, taux_frais_notaire=0.08, travaux=20_000, ameublement=5_000)
    assert acq.cout_total == pytest.approx(133_000)


# --- Financement --------------------------------------------------------------

def test_rg20_l_apport_couvre_le_notaire_le_reste_est_emprunte():
    r = analyser(immeuble_simple(), CREDIT_SIMPLE)
    assert r.montant_emprunte == pytest.approx(100_000)


def test_rg23_assurance_par_defaut_0_30_pourcent():
    fin = Financement(apport=8_000, taux_annuel=0.035)
    r = analyser(immeuble_simple(), fin)
    # 579,96 € de mensualité + 25 € d'assurance (0,30 % de 100 000 € / 12)
    assert r.mensualite_credit == pytest.approx(604.96, abs=0.01)


def test_rg21_duree_maximum_25_ans():
    Financement(duree_annees=25)
    with pytest.raises(ValueError):
        Financement(duree_annees=26)


def test_rg26_taux_d_endettement_loyers_a_70_pourcent():
    r = analyser(immeuble_simple(), CREDIT_SIMPLE)
    # 579,96 / (4 000 + 900 x 70 %) = 579,96 / 4 630
    assert r.taux_endettement == pytest.approx(579.96 / 4_630, abs=1e-4)
    assert r.respecte_hcsf


def test_rg26_depassement_hcsf_signale():
    fin = Financement(
        apport=8_000, taux_annuel=0.035, taux_assurance_annuel=0, autres_credits_mensuels=1_100
    )
    r = analyser(immeuble_simple(), fin)
    # (579,96 + 1 100) / 4 630 = 36,3 %
    assert r.taux_endettement == pytest.approx(0.3628, abs=1e-3)
    assert not r.respecte_hcsf
    assert any("endettement" in a for a in r.alertes)


@pytest.mark.parametrize(
    "prix, statut",
    [(100_000, ENVELOPPE_CIBLE), (250_000, ENVELOPPE_A_CONFIRMER), (300_000, ENVELOPPE_HORS)],
)
def test_rg27_enveloppe_de_financement(prix, statut):
    # Coûts totaux : 108 000 €, 270 000 €, 324 000 €
    bien = immeuble_simple(acquisition=Acquisition(prix=prix))
    assert analyser(bien, SANS_CREDIT).enveloppe == statut


# --- Immeuble de rapport -----------------------------------------------------

def test_rg31_33_vacance_et_gestion():
    r = analyser(immeuble_simple(taux_vacance=0.10, taux_gestion=0.10), SANS_CREDIT)
    # Encaissé : 10 800 x 0,9 = 9 720 ; gestion : 972
    assert r.revenus_annuels == pytest.approx(9_720)
    assert r.charges_annuelles == pytest.approx(972)


def test_rg36_local_commercial_sans_bail_non_compte():
    bien = immeuble_simple(loyer_commercial_mensuel=600, bail_commercial_en_cours=False)
    assert bien.revenus_theoriques_annuels == pytest.approx(10_800)


def test_rg37_local_commercial_occupe_decote_de_moitie():
    bien = immeuble_simple(loyer_commercial_mensuel=600, bail_commercial_en_cours=True)
    # (900 + 600 x 50 %) x 12
    assert bien.revenus_theoriques_annuels == pytest.approx(14_400)


def test_rg38_taxe_fonciere_non_communiquee_un_mois_de_loyer_par_lot():
    bien = immeuble_simple(taxe_fonciere=None)
    assert bien.taxe_fonciere_retenue == pytest.approx(900)
    assert analyser(bien, SANS_CREDIT).charges_annuelles == pytest.approx(900)


# --- Location courte durée ---------------------------------------------------

def test_rg40_43_location_courte_duree():
    bien = LocationCourteDuree(
        nom="Studio",
        acquisition=Acquisition(prix=100_000, taux_frais_notaire=0),
        prix_nuitee=100,
        taux_occupation=0.5,
        taux_conciergerie=0.20,
        taux_plateforme=0,
        taux_entretien=0,
    )
    r = analyser(bien, SANS_CREDIT)
    # 100 € x 365 x 50 % = 18 250 € ; conciergerie 3 650 €
    assert r.revenus_annuels == pytest.approx(18_250)
    assert r.charges_annuelles == pytest.approx(3_650)
    assert r.rendement_brut == pytest.approx(0.1825)
    assert r.seuil_rendement_brut == 0.12


# --- Indicateurs ---------------------------------------------------------------

def test_rg50_rendement_brut_sur_cout_total():
    r = analyser(immeuble_simple(), SANS_CREDIT)
    # 10 800 € de loyers / 108 000 € de coût total
    assert r.rendement_brut == pytest.approx(0.10)
    assert r.atteint_le_seuil


def test_rg50_les_travaux_font_baisser_le_rendement_brut():
    bien = immeuble_simple(acquisition=Acquisition(prix=100_000, travaux=27_000))
    # 10 800 / 135 000
    assert analyser(bien, SANS_CREDIT).rendement_brut == pytest.approx(0.08)


def test_rg51_52_rendement_net_et_cashflow_sans_credit():
    r = analyser(immeuble_simple(taxe_fonciere=1_080), SANS_CREDIT)
    # (10 800 - 1 080) / 108 000
    assert r.rendement_net == pytest.approx(0.09)
    assert r.cashflow_mensuel == pytest.approx(810)


def test_rg52_cashflow_avec_credit():
    r = analyser(immeuble_simple(), CREDIT_SIMPLE)
    assert r.cashflow_mensuel == pytest.approx(900 - 579.96, abs=0.01)
    assert r.effort_epargne_mensuel == 0


def test_rg53_effort_d_epargne_si_cashflow_negatif():
    r = analyser(immeuble_simple(loyers_mensuels=[250, 250]), CREDIT_SIMPLE)
    assert r.cashflow_mensuel < 0
    assert r.effort_epargne_mensuel == pytest.approx(-r.cashflow_mensuel)


# --- Sélection ------------------------------------------------------------------

def test_rg64_cashflow_quasi_nul_exclu_du_top4():
    # 10 800 - 10 440 = 360 € par an, soit 30 € par mois
    r = analyser(immeuble_simple(taxe_fonciere=10_440), SANS_CREDIT)
    assert r.atteint_le_seuil
    assert r.cashflow_mensuel == pytest.approx(30)
    assert not r.eligible_top4


def test_rg64_bien_eligible():
    assert analyser(immeuble_simple(), SANS_CREDIT).eligible_top4


def test_rg61_62_comparer_classe_par_cashflow_et_filtre():
    bon = immeuble_simple(nom="Bon")
    moyen = immeuble_simple(nom="Moyen", loyers_mensuels=[300, 300, 200])
    faible = immeuble_simple(nom="Faible", loyers_mensuels=[300, 300])
    resultats = comparer([faible, bon, moyen], SANS_CREDIT)
    assert [r.nom for r in resultats] == ["Bon", "Moyen", "Faible"]

    au_seuil = comparer([faible, bon, moyen], SANS_CREDIT, seulement_au_seuil=True)
    assert [r.nom for r in au_seuil] == ["Bon"]

    eligibles = comparer([faible, bon, moyen], SANS_CREDIT, seulement_eligibles=True)
    assert [r.nom for r in eligibles] == ["Bon"]
