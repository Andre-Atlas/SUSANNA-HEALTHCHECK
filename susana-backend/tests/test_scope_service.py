from app.services.scope_service import ScopeService


def test_scope_in():
    scope, intent = ScopeService().classify("Onde fica uma UBS em Samambaia?")
    assert scope == "in_scope" and intent == "unit_search"


def test_scope_out():
    scope, intent = ScopeService().classify("Qual doença eu tenho?")
    assert scope == "out_of_scope" and intent == "clinical"


def test_scope_clarification():
    scope, intent = ScopeService().classify("Olá")
    assert scope == "needs_clarification" and intent == "unknown"
