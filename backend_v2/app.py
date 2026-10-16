"""Live V2 API. The baseline remains available through start.py --legacy."""
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
from uuid import uuid4
from fastapi import FastAPI, Depends, Request, Response, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from backend_v2 import auth, schemas as s, service
from backend_v2.database import build_engine, session_factory
from backend_v2.models import Base, Vehicle, Enquiry, Task, AuditEvent
from backend_v2 import limits, ai, telemetry

log = logging.getLogger('dealer.v2')


def create_app(database_url=None):
    auth.configuration()
    engine = build_engine(database_url)
    sessions = session_factory(engine)

    @asynccontextmanager
    async def lifespan(app):
        telemetry.configure()
        if os.environ.get('APP_ENV', 'local') == 'local':
            from alembic.config import Config
            from alembic import command
            root = Path(__file__).resolve().parents[1]
            config = Config(str(root / 'alembic.ini'))
            config.set_main_option('script_location', str(root / 'migrations'))
            with engine.begin() as connection:
                config.attributes['connection'] = connection
                command.upgrade(config, 'head')
        yield
        engine.dispose()

    app = FastAPI(title='Dealer Desk API', version='2.0.0', lifespan=lifespan)
    app.state.engine, app.state.sessions = engine, sessions

    def session():
        with sessions() as db:
            with db.begin():
                yield db

    @app.middleware('http')
    async def request_context(request, call_next):
        request.state.request_id = uuid4().hex
        start = time.monotonic()
        try:
            size = int(request.headers.get('content-length', '0'))
        except ValueError:
            return JSONResponse({'error': {'code': 'body', 'message': 'Invalid request size', 'request_id': request.state.request_id}}, status_code=400)
        if size > 250000:
            return JSONResponse({'error': {'code': 'body', 'message': 'Request too large', 'request_id': request.state.request_id}}, status_code=413)
        with telemetry.trace.get_tracer('dealer.requests').start_as_current_span('http.request') as span:
            response = await call_next(request)
            span.set_attribute('http.response.status_code', response.status_code)
            span.set_attribute('http.request.method', request.method)
        meter = telemetry.metrics.get_meter('dealer.requests')
        meter.create_counter('http.requests').add(1, {'status': str(response.status_code)})
        response.headers['X-Request-ID'] = request.state.request_id
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        if request.url.path.startswith(('/api', '/auth')):
            response.headers['Cache-Control'] = 'no-store'
        # Paths are route templates; no customer text, tokens, query values or record bodies.
        route = request.scope.get('route')
        log.info('request id=%s route=%s status=%s duration_ms=%d', request.state.request_id,
                 getattr(route, 'path', 'static'), response.status_code, (time.monotonic() - start) * 1000)
        return response

    @app.exception_handler(service.Problem)
    async def problem(request, exc):
        error = dict(code=exc.code, message=exc.message, request_id=request.state.request_id)
        if exc.current_revision is not None:
            error['current_revision'] = exc.current_revision
        return JSONResponse({'error': error}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return JSONResponse({'error': {'code': 'validation', 'message': 'Check field types, bounds and required values', 'request_id': request.state.request_id}}, status_code=422)

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        return JSONResponse({'error': {'code': 'database', 'message': 'Database unavailable. Try again.', 'request_id': request.state.request_id}}, status_code=503)

    @app.get('/live')
    def live():
        return {'status': 'ok', 'version': app.version}

    @app.get('/health')
    def health():
        try:
            with sessions() as db:
                db.execute(select(Vehicle.id).limit(1))
            return {'status': 'ok', 'version': app.version}
        except SQLAlchemyError:
            return JSONResponse({'status': 'unavailable', 'version': app.version}, status_code=503)

    @app.get('/auth/config')
    def auth_config():
        return {'mode': auth.mode(), 'public_demo': os.environ.get('PUBLIC_DEMO') == 'true'}

    class Login(s.Input):
        email: str = Field(min_length=3, max_length=254)
        password: str = Field(min_length=1, max_length=1024)

    def token_response(response, data):
        if not data.get('access_token') or not data.get('refresh_token'):
            raise service.Problem(503, 'auth_response', 'Sign-in service returned an invalid session')
        response.set_cookie('dealer_refresh', data['refresh_token'], httponly=True,
                            secure=os.environ.get('APP_ENV') == 'hosted', samesite='strict', path='/auth', max_age=604800)
        return {'access_token': data['access_token'], 'expires_in': data.get('expires_in', 3600)}

    @app.post('/auth/login')
    def login(data: Login, request: Request, response: Response):
        auth.origin(request)
        if auth.mode() != 'supabase':
            raise service.Problem(409, 'local_mode', 'Local mode does not use account sign-in')
        limits.consume(sessions, 'login', data.email.strip().lower(), 10, 300)
        limits.consume(sessions, 'login_global', 'all', 1000, 86400)
        return token_response(response, auth.supabase('POST', 'token?grant_type=password', data=data.model_dump()))

    @app.post('/auth/refresh')
    def refresh(request: Request, response: Response):
        auth.origin(request)
        token = request.cookies.get('dealer_refresh')
        if auth.mode() != 'supabase' or not token or len(token) > 8192:
            raise service.Problem(401, 'unauthorized', 'Sign in to continue')
        return token_response(response, auth.supabase('POST', 'token?grant_type=refresh_token', data={'refresh_token': token}))

    @app.post('/auth/logout')
    def logout(request: Request, response: Response):
        auth.origin(request)
        response.delete_cookie('dealer_refresh', path='/auth')
        token = request.headers.get('Authorization', '')
        if auth.mode() == 'supabase' and token.startswith('Bearer '):
            auth.supabase('POST', 'logout', token=token[7:])
        return {'signed_out': True}

    @app.get('/auth/me')
    def me(request: Request):
        return auth.principal(request)

    @app.get('/api/vehicles', dependencies=[Depends(auth.principal)])
    def vehicles(q: str = Query('', max_length=100), status: s.Status | None = None,
                 include_archived: bool = False, offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db=Depends(session)):
        return service.page(db, Vehicle, offset, limit, q=q, status=status, include_archived=include_archived)

    @app.post('/api/vehicles', status_code=201, dependencies=[Depends(auth.operator)])
    def create_vehicle(data: s.VehicleCreate, db=Depends(session)):
        return service.create(db, Vehicle, data)

    @app.get('/api/vehicles/{vehicle_id}', dependencies=[Depends(auth.principal)])
    def vehicle(vehicle_id: int, db=Depends(session)):
        return service.serialize(service.record(db, Vehicle, vehicle_id))

    @app.patch('/api/vehicles/{vehicle_id}', dependencies=[Depends(auth.operator)])
    def edit_vehicle(vehicle_id: int, data: s.VehicleUpdate, db=Depends(session)):
        return service.change(db, Vehicle, vehicle_id, data)

    @app.get('/api/enquiries', dependencies=[Depends(auth.principal)])
    def enquiries(vehicle_id: int | None = Query(None, gt=0), status: s.EnquiryStatus | None = None,
                  offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db=Depends(session)):
        return service.page(db, Enquiry, offset, limit, vehicle_id=vehicle_id, status=status)

    @app.post('/api/enquiries', status_code=201, dependencies=[Depends(auth.operator)])
    def create_enquiry(data: s.EnquiryCreate, db=Depends(session)):
        return service.create(db, Enquiry, data)

    @app.get('/api/enquiries/{enquiry_id}', dependencies=[Depends(auth.principal)])
    def enquiry(enquiry_id: int, db=Depends(session)):
        return service.serialize(service.record(db, Enquiry, enquiry_id))

    @app.patch('/api/enquiries/{enquiry_id}', dependencies=[Depends(auth.operator)])
    def edit_enquiry(enquiry_id: int, data: s.EnquiryUpdate, db=Depends(session)):
        return service.change(db, Enquiry, enquiry_id, data)

    @app.get('/api/tasks', dependencies=[Depends(auth.principal)])
    def tasks(enquiry_id: int | None = Query(None, gt=0), completed: bool | None = None, overdue: bool | None = None,
              offset: int = Query(0, ge=0), limit: int = Query(25, ge=1, le=100), db=Depends(session)):
        return service.page(db, Task, offset, limit, enquiry_id=enquiry_id, completed=completed, overdue=overdue)

    @app.post('/api/tasks', status_code=201, dependencies=[Depends(auth.operator)])
    def create_task(data: s.TaskCreate, db=Depends(session)):
        return service.create(db, Task, data)

    @app.get('/api/tasks/{task_id}', dependencies=[Depends(auth.principal)])
    def task(task_id: int, db=Depends(session)):
        return service.serialize(service.record(db, Task, task_id))

    @app.patch('/api/tasks/{task_id}', dependencies=[Depends(auth.operator)])
    def edit_task(task_id: int, data: s.TaskUpdate, db=Depends(session)):
        return service.change(db, Task, task_id, data)

    @app.get('/api/dashboard', dependencies=[Depends(auth.principal)])
    def dashboard(db=Depends(session)):
        return service.dashboard(db)

    @app.get('/api/changes', dependencies=[Depends(auth.principal)])
    def changes(after: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=100), db=Depends(session)):
        rows = db.scalars(select(AuditEvent).where(AuditEvent.id > after).order_by(AuditEvent.id).limit(limit+1)).all()
        items = [{'sequence': e.id, 'entity': e.entity, 'entity_id': e.entity_id, 'revision': e.revision,
                  'occurred_at': service.serialize(e)['occurred_at']} for e in rows[:limit]]
        return {'items': items, 'next_sequence': items[-1]['sequence'] if items else after, 'has_more': len(rows) > limit}

    @app.get('/api/export', dependencies=[Depends(auth.operator)])
    def export(db=Depends(session)):
        return {'format': 'dealer-desk-v2', 'vehicles': [service.serialize(r) for r in db.scalars(select(Vehicle))],
                'enquiries': [service.serialize(r) for r in db.scalars(select(Enquiry))], 'tasks': [service.serialize(r) for r in db.scalars(select(Task))]}

    @app.post('/api/vehicles/{vehicle_id}/draft')
    def listing_draft(vehicle_id: int, user=Depends(auth.operator), db=Depends(session)):
        if os.environ.get('AI_PROVIDER', 'disabled') != 'disabled':
            limits.consume(sessions, 'ai', user['id'], int(os.environ.get('AI_DAILY_LIMIT', '10')), 86400)
        return ai.draft(service.record(db, Vehicle, vehicle_id))

    dist = Path(__file__).resolve().parents[1] / 'frontend-v2' / 'dist'
    if dist.exists():
        app.mount('/', StaticFiles(directory=dist, html=True), name='frontend')
    else:
        @app.get('/', include_in_schema=False)
        def source_mode():
            return {'message': 'API ready. Build frontend-v2 with npm ci && npm run build, or run its Vite server.'}
    return app


app = create_app()
