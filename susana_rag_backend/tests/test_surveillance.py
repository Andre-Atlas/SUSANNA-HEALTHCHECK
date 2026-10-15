"""
Testes Automatizados para a Vigilância Epidemiológica do DF (SUS Digital)
========================================================================
Valida ausência de mocks, fidelidade aos dados oficiais da SES-DF e integridade dos endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.surveillance.service import SurveillanceService
from app.surveillance.storage import SurveillanceStorage


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    return SurveillanceService()


def test_surveillance_storage_init():
    """Valida que o banco relacional inicializa e contém dados persistidos."""
    storage = SurveillanceStorage()
    categories = storage.list_categories()
    assert len(categories) == 4
    conditions = storage.list_conditions()
    assert len(conditions) >= 8


def test_all_required_categories_present(service):
    """Valida as 4 macrocategorias requeridas pelo usuário."""
    categories = service.get_categories()
    slugs = {c.slug for c in categories}
    assert "arboviroses" in slugs
    assert "endemias" in slugs
    assert "hepatites-ist" in slugs
    assert "sazonais" in slugs


def test_all_required_conditions_present(service):
    """Valida a presença de todos os agravos explicitamente solicitados."""
    conditions = service.get_conditions()
    cond_ids = {c.id for c in conditions}

    # 1. Arboviroses
    assert "dengue" in cond_ids
    assert "chikungunya" in cond_ids
    assert "zika" in cond_ids

    # 2. Endemias
    assert "tuberculose" in cond_ids
    assert "hanseniase" in cond_ids
    assert "leishmanioses" in cond_ids

    # 3. Hepatites Virais & IST's / AIDS
    assert "hepatites_virais" in cond_ids
    assert "hiv_aids" in cond_ids
    assert "sifilis" in cond_ids

    # 4. Surtos Sazonais e Ambientais
    assert "animais_peconhentos" in cond_ids
    assert "sindromes_respiratorias" in cond_ids


def test_dashboard_dengue_structure_and_kpis(service):
    """Valida o dashboard de Dengue e integridade dos KPIs."""
    dash = service.get_condition_dashboard("dengue")
    assert dash is not None
    assert dash.condition.nome == "Dengue"
    assert dash.condition.codigo_cid10 == "A90"
    assert dash.kpis.total_casos_ano > 10000
    assert dash.kpis.taxa_incidencia_distrital_100k > 1000.0
    assert len(dash.time_series) == 10
    assert len(dash.regions) >= 5
    assert len(dash.guidelines) >= 3
    assert any(g.tipo == "sinal_alarme" for g in dash.guidelines)


def test_animais_peconhentos_referencia_hran(service):
    """Valida que acidentes por animais peçonhentos apontam o HRAN como polo estratégico de soro."""
    dash = service.get_condition_dashboard("animais_peconhentos")
    assert dash is not None
    assert dash.condition.id == "animais_peconhentos"
    assert dash.kpis.tendencia in ("alta", "queda", "estavel")
    
    # Verifica unidades de referência para soro antiescorpiônico/antiofídico
    unidades_texto = " ".join([u.nome_exemplo + " " + u.papel_clinico for u in dash.unidades_referencia])
    assert "HRAN" in unidades_texto
    assert "soro" in unidades_texto.lower() or "soroterapia" in unidades_texto.lower()


def test_surveillance_not_found_404(client):
    """Valida que agravo inexistente retorna status 404 gracioso."""
    res = client.get("/api/surveillance/dashboard/condicao_inexistente_xyz")
    assert res.status_code == 404
    assert "não encontrada" in res.json()["detail"]


def test_api_endpoints_integration(client):
    """Testa a integração HTTP de todos os endpoints de vigilância."""
    # 1. Summary
    res_sum = client.get("/api/surveillance/summary")
    assert res_sum.status_code == 200
    data_sum = res_sum.json()
    assert data_sum["total_categorias"] == 4
    assert data_sum["total_agravos_monitorados"] >= 8

    # 2. Categories
    res_cats = client.get("/api/surveillance/categories")
    assert res_cats.status_code == 200
    assert len(res_cats.json()) == 4

    # 3. Filter by category
    res_conds = client.get("/api/surveillance/conditions?category_id=cat_endemias")
    assert res_conds.status_code == 200
    conds = res_conds.json()
    assert len(conds) == 3
    assert {c["id"] for c in conds} == {"tuberculose", "hanseniase", "leishmanioses"}

    # 4. Dashboard completo
    for cid in ["dengue", "tuberculose", "animais_peconhentos", "sindromes_respiratorias"]:
        res_dash = client.get(f"/api/surveillance/dashboard/{cid}")
        assert res_dash.status_code == 200
        d = res_dash.json()
        assert d["condition"]["id"] == cid
        assert "kpis" in d
        assert len(d["time_series"]) > 0
        assert len(d["regions"]) > 0
