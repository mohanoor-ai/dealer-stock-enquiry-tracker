from pathlib import Path
import yaml
from backend_v2.app import app


def test_contract_routes_and_requests_exist():
    contract=yaml.safe_load((Path(__file__).resolve().parents[1]/'openapi.yaml').read_text(encoding='utf-8'))
    actual=app.openapi()
    assert set(contract['paths'])==set(actual['paths'])
    for path,methods in actual['paths'].items():
        verbs={'get','post','put','patch','delete','options','head','trace'}
        assert set(contract['paths'][path]) & verbs == set(methods) & verbs
    assert 'supabaseAccess' in contract['components']['securitySchemes']
