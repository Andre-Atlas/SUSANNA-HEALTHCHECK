"""Vacinas pendentes calculadas a partir do perfil."""
from __future__ import annotations

from datetime import date

from app.vaccines.schedule import VaccineRecord, compute_pending

TODAY = date(2026, 10, 15)


def _ids(items):
    return {p.vaccine_id: p for p in items}


def _rec(vid, dose=1, when="2026-01-01"):
    return VaccineRecord(id="r", vaccine_id=vid, dose_num=dose, data_aplicacao=when, created_at=when)


def test_no_birth_date_returns_nothing():
    assert compute_pending(None, [], [], TODAY) == []


def test_baby_three_months_first_doses_due():
    pend = _ids(compute_pending("2026-07-15", [], [], TODAY))
    for vid in ("vac_penta_2m", "vac_vip_2m", "vac_rotavirus_2m", "vac_meningo_c_3m"):
        assert vid in pend
        assert pend[vid].dose_num == 1
    assert pend["vac_penta_2m"].status in ("atrasada", "agora")
    assert pend["vac_bcg"].status == "atrasada"


def test_record_moves_series_to_next_dose():
    pend = _ids(compute_pending("2026-07-15", [], [_rec("vac_penta_2m", 1, "2026-09-15")], TODAY))
    assert pend["vac_penta_2m"].dose_num == 2
    assert pend["vac_penta_2m"].status == "proxima"


def test_pregnant_adult_gets_dtpa_and_influenza():
    pend = _ids(compute_pending("1995-02-10", ["gestante"], [], TODAY))
    assert "vac_dtpa_gestante" in pend
    assert "vac_influenza_anual" in pend


def test_elderly_and_diabetic_get_influenza_yearly():
    assert "vac_influenza_anual" in _ids(compute_pending("1958-01-01", [], [], TODAY))
    assert "vac_influenza_anual" in _ids(compute_pending("1996-01-01", ["diabetes"], [], TODAY))
    assert "vac_influenza_anual" not in _ids(compute_pending("1996-01-01", [], [], TODAY))
    taken = _ids(compute_pending("1958-01-01", [], [_rec("vac_influenza_anual", 1, "2026-05-01")], TODAY))
    assert "vac_influenza_anual" not in taken


def test_dt_booster_recurs_after_ten_years():
    recent = _ids(compute_pending("1990-01-01", [], [_rec("vac_dt_adulto", 1, "2020-01-01")], TODAY))
    assert "vac_dt_adulto" not in recent
    old = _ids(compute_pending("1990-01-01", [], [_rec("vac_dt_adulto", 1, "2015-01-01")], TODAY))
    assert old["vac_dt_adulto"].status == "atrasada"


def test_adolescent_hpv_window():
    assert "vac_hpv_adol" in _ids(compute_pending("2015-06-01", [], [], TODAY))
    assert "vac_hpv_adol" not in _ids(compute_pending("2005-06-01", [], [], TODAY))
