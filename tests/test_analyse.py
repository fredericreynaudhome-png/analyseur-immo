import pytest

from analyseur_immo import (
    Acquisition,
    Financement,
    ImmeubleDeRapport,
    LocationCourteDuree,
    analyser,
    comparer,
)

SANS_CREDIT = Financement(apport=1_000_000)


def immeuble_simple(**kwargs):
    """Immeuble facile à vérifier à la main : 3 lots à 300 €, aucune charge."""
    valeurs = dict(
        nom="Test",
        acquisition=Acquisition(prix=100_000, taux_frais_notaire=0.08),
        loyers_mensuels=[300, 300, 300],
        taux_vacance=0,
        taux_gestion=0,
        taux_gli=0,
        taux_entretien=0,
    )
    valeurs.update(kwargs)
    return ImmeubleDeRapport(**valeurs)


def test_cout_total():
    acq = Acquisition(prix=100_000, taux_frais_notaire=0.08, travaux=20_000, ameublement=5_000)
    assert acq.cout_total == pytest.approx(133_000)


def test_rendement_brut_sur_prix_d_achat():
    r = analyser(immeuble_simple(), SANS_CREDIT)
    # 10 800 € de loyers / 100 000 € de prix
    assert r.rendement_brut == pytest.approx(0.108)
    assert r.atteint_le_seuil


def test_rendement_net_et_cashflow_sans_credit():
    r = analyser(immeuble_simple(taxe_fonciere=1_080), SANS_CREDIT)
    # (10 800 - 1 080) / 108 000
    assert r.rendement_net == pytest.approx(0.09)
    assert r.cashflow_mensuel == pytest.approx(810)
    assert r.montant_emprunte == 0


def test_vacance_et_gestion():
    r = analyser(immeuble_simple(taux_vacance=0.10, taux_gestion=0.10), SANS_CREDIT)
    # Encaissé : 10 800 x 0,9 = 9 720 ; gestion : 972
    assert r.revenus_annuels == pytest.approx(9_720)
    assert r.charges_annuelles == pytest.approx(972)


def test_cashflow_avec_credit():
    fin = Financement(apport=8_000, duree_annees=20, taux_annuel=0.035)
    r = analyser(immeuble_simple(), fin)
    # Emprunt de 100 000 € : mensualité 579,96 €
    assert r.montant_emprunte == pytest.approx(100_000)
    assert r.cashflow_mensuel == pytest.approx(900 - 579.96, abs=0.01)
    assert r.effort_epargne_mensuel == 0


def test_effort_d_epargne_si_cashflow_negatif():
    fin = Financement(apport=8_000)
    r = analyser(immeuble_simple(loyers_mensuels=[250, 250]), fin)
    assert r.cashflow_mensuel < 0
    assert r.effort_epargne_mensuel == pytest.approx(-r.cashflow_mensuel)


def test_location_courte_duree():
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


def test_comparer_classe_par_cashflow_et_filtre():
    bon = immeuble_simple(nom="Bon")
    moyen = immeuble_simple(nom="Moyen", loyers_mensuels=[300, 300, 200])
    faible = immeuble_simple(nom="Faible", loyers_mensuels=[300, 300])
    resultats = comparer([faible, bon, moyen], SANS_CREDIT)
    assert [r.nom for r in resultats] == ["Bon", "Moyen", "Faible"]

    au_seuil = comparer([faible, bon, moyen], SANS_CREDIT, seulement_au_seuil=True)
    assert [r.nom for r in au_seuil] == ["Bon"]
