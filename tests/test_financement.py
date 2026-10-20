import pytest

from analyseur_immo import mensualite, tableau_amortissement
from analyseur_immo.financement import assurance_mensuelle


def test_mensualite_cas_connu():
    # 100 000 € sur 20 ans à 3,5 % : mensualité de référence 579,96 €
    assert mensualite(100_000, 0.035, 20) == pytest.approx(579.96, abs=0.01)


def test_mensualite_taux_zero():
    assert mensualite(24_000, 0.0, 2) == pytest.approx(1_000)


def test_mensualite_sans_emprunt():
    assert mensualite(0, 0.035, 20) == 0


def test_assurance_mensuelle():
    # 0,30 % par an sur 100 000 € = 300 €/an = 25 €/mois
    assert assurance_mensuelle(100_000, 0.003) == pytest.approx(25)


def test_tableau_amortissement_rembourse_tout_le_capital():
    lignes = tableau_amortissement(100_000, 0.035, 20)
    assert len(lignes) == 20
    assert sum(l.capital_rembourse for l in lignes) == pytest.approx(100_000, abs=0.5)
    assert lignes[-1].capital_restant == pytest.approx(0, abs=0.5)
    # Les intérêts diminuent d'année en année
    assert lignes[0].interets > lignes[-1].interets
