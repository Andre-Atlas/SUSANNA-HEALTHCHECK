from app.services.scope_service import ScopeService


def test_scope_in_and_intent():
    decision = ScopeService().classify("Onde fica uma UBS em Samambaia?")
    assert decision.scope == "in_scope"
    assert decision.intent == "unit_search"


def test_scope_out():
    decision = ScopeService().classify("Qual doença eu tenho?")
    assert decision.scope == "out_of_scope"
    assert decision.intent == "clinical"


def test_scope_clarification():
    decision = ScopeService().classify("Olá")
    assert decision.scope == "needs_clarification"


def test_scope_inherits_previous_intent_for_follow_up():
    decision = ScopeService().classify("E no sábado?", previous_intent="vaccination")
    assert decision.scope == "in_scope"
    assert decision.intent == "vaccination"


def test_extracts_ra_from_question():
    assert ScopeService().extract_ra("Quero vacinação em Samambaia") == "Samambaia"
