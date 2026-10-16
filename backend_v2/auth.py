"""Supabase validates access tokens; application roles come only from app_metadata."""
import os
import httpx
from fastapi import Request
from backend_v2.service import Problem


def mode():
    return os.environ.get('AUTH_MODE', 'local')


def configuration():
    hosted = os.environ.get('APP_ENV', 'local') == 'hosted'
    if mode() not in {'local', 'supabase'}:
        raise RuntimeError('AUTH_MODE must be local or supabase')
    if hosted and mode() != 'supabase':
        raise RuntimeError('Hosted mode requires Supabase authentication')
    if hosted and not os.environ.get('DATABASE_URL', '').startswith(('postgresql://', 'postgresql+psycopg://')):
        raise RuntimeError('Hosted mode requires an external PostgreSQL database')
    if mode() == 'supabase':
        url = os.environ.get('SUPABASE_URL', '')
        key = os.environ.get('SUPABASE_PUBLISHABLE_KEY', '')
        if not url.startswith('https://') or not key:
            raise RuntimeError('Configure HTTPS SUPABASE_URL and its publishable key')
        if hosted and not os.environ.get('APP_ORIGIN', '').startswith('https://'):
            raise RuntimeError('Hosted mode requires HTTPS APP_ORIGIN')


def supabase(method, path, token=None, data=None):
    headers = {'apikey': os.environ['SUPABASE_PUBLISHABLE_KEY']}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    try:
        response = httpx.request(method, os.environ['SUPABASE_URL'].rstrip('/') + '/auth/v1/' + path,
                                 headers=headers, json=data, timeout=10, follow_redirects=False)
    except httpx.HTTPError:
        raise Problem(503, 'auth_unavailable', 'Sign-in service unavailable. Try again.')
    if response.status_code == 429:
        raise Problem(429, 'auth_limit', 'Too many sign-in requests. Try later.')
    if response.status_code >= 500:
        raise Problem(503, 'auth_unavailable', 'Sign-in service unavailable. Try again.')
    if response.status_code >= 400:
        raise Problem(401, 'unauthorized', 'Session expired or sign-in details invalid')
    if response.status_code == 204:
        return {}
    try:
        return response.json()
    except ValueError:
        raise Problem(503, 'auth_unavailable', 'Sign-in service returned an invalid response')


def principal(request: Request):
    if mode() == 'local':
        host = request.url.hostname
        if os.environ.get('APP_ENV', 'local') != 'local' or host not in {'localhost', '127.0.0.1', 'testserver'}:
            raise Problem(403, 'local_only', 'Local mode only accepts localhost requests')
        return {'id': 'local', 'role': 'operator'}
    value = request.headers.get('Authorization', '')
    if not value and request.method == 'GET' and os.environ.get('PUBLIC_DEMO') == 'true':
        return {'id': 'public-demo', 'role': 'viewer'}
    if not value.startswith('Bearer ') or not 1 <= len(value[7:]) <= 8192:
        raise Problem(401, 'unauthorized', 'Sign in to continue')
    user = supabase('GET', 'user', token=value[7:])
    if not user.get('id'):
        raise Problem(401, 'unauthorized', 'Invalid session')
    role = user.get('app_metadata', {}).get('dealer_role', 'viewer')
    if role not in {'viewer', 'operator'}:
        role = 'viewer'
    return {'id': user['id'], 'role': role}


def operator(request: Request):
    user = principal(request)
    if user['role'] != 'operator':
        raise Problem(403, 'forbidden', 'Operator permission required')
    return user


def origin(request):
    expected = os.environ.get('APP_ORIGIN') or str(request.base_url).rstrip('/')
    if request.headers.get('Origin') != expected:
        raise Problem(403, 'origin', 'Request origin rejected')
