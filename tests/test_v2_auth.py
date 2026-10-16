import pytest
from starlette.requests import Request
from backend_v2 import auth
from backend_v2.service import Problem


def request(token='',host='localhost',method='GET',origin=None):
    headers=[(b'host',host.encode())]
    if token:headers.append((b'authorization',token.encode()))
    if origin:headers.append((b'origin',origin.encode()))
    return Request({'type':'http','method':method,'path':'/api/vehicles','headers':headers,'scheme':'http','server':(host,80),'query_string':b''})


def test_hosted_cannot_disable_auth(monkeypatch):
    monkeypatch.setenv('APP_ENV','hosted');monkeypatch.setenv('AUTH_MODE','local')
    with pytest.raises(RuntimeError):auth.configuration()


def test_local_mode_rejects_remote_host(monkeypatch):
    monkeypatch.setenv('APP_ENV','local');monkeypatch.setenv('AUTH_MODE','local')
    assert auth.operator(request())['role']=='operator'
    with pytest.raises(Problem):auth.operator(request(host='public.example'))


def test_roles_ignore_user_metadata(monkeypatch):
    monkeypatch.setenv('AUTH_MODE','supabase')
    monkeypatch.setattr(auth,'supabase',lambda *a,**k:{'id':'user-1','user_metadata':{'dealer_role':'operator'}})
    with pytest.raises(Problem) as error:auth.operator(request('Bearer test'))
    assert error.value.status==403
    monkeypatch.setattr(auth,'supabase',lambda *a,**k:{'id':'user-1','app_metadata':{'dealer_role':'operator'}})
    assert auth.operator(request('Bearer test'))['id']=='user-1'


def test_demo_read_access_never_allows_writes(monkeypatch):
    monkeypatch.setenv('AUTH_MODE','supabase');monkeypatch.setenv('PUBLIC_DEMO','true')
    assert auth.principal(request())['role']=='viewer'
    with pytest.raises(Problem):auth.operator(request())
    with pytest.raises(Problem):auth.principal(request(method='POST'))


def test_refresh_origin_must_match(monkeypatch):
    monkeypatch.setenv('APP_ORIGIN','https://dealer.example')
    auth.origin(request(origin='https://dealer.example'))
    with pytest.raises(Problem):auth.origin(request(origin='https://other.example'))
