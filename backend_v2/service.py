"""Transactional business rules, independent of HTTP and external providers."""
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
import os
from sqlalchemy import select, update, func
from backend_v2.models import Vehicle, Enquiry, Task, AuditEvent


class Problem(Exception):
    def __init__(self, status, code, message, current_revision=None):
        self.status, self.code, self.message = status, code, message
        self.current_revision = current_revision


def today():
    return datetime.now(ZoneInfo(os.environ.get('DEALER_TIMEZONE', 'Europe/London'))).date()


def record(session, model, record_id):
    result = session.get(model, record_id)
    if result is None:
        raise Problem(404, 'not_found', 'Record not found')
    return result


def serialize(row):
    result = {}
    for column in row.__table__.columns:
        value = getattr(row, column.name)
        if isinstance(value, datetime):
            value = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
            value = value.isoformat()
        elif isinstance(value, date):
            value = value.isoformat()
        result[column.name] = value
    return result


def event(session, row, action):
    entity = {Vehicle: 'vehicle', Enquiry: 'enquiry', Task: 'task'}[type(row)]
    session.add(AuditEvent(entity=entity, entity_id=row.id, revision=row.revision, action=action))


def create(session, model, data):
    values = data.model_dump()
    if model is Enquiry:
        vehicle = record(session, Vehicle, data.vehicle_id)
        if vehicle.archived:
            raise Problem(409, 'archived', 'Vehicle is archived')
    if model is Task:
        enquiry = record(session, Enquiry, data.enquiry_id)
        if enquiry.status == 'closed':
            raise Problem(409, 'closed', 'Enquiry is closed')
        if data.due_date < today():
            raise Problem(422, 'past_date', 'Choose today or a later date')
    row = model(**values)
    session.add(row)
    session.flush()
    event(session, row, 'created')
    session.flush()
    return serialize(row)


def change(session, model, record_id, data):
    row = record(session, model, record_id)
    if row.revision != data.revision:
        raise Problem(409, 'stale_revision', 'Record changed. Refresh before editing.', row.revision)
    values = data.model_dump(exclude_unset=True)
    values.pop('revision')
    if model is Vehicle and 'status' in values:
        allowed = {'available': {'available', 'reserved', 'sold'}, 'reserved': {'reserved', 'available', 'sold'}, 'sold': {'sold', 'available'}}
        if values['status'] not in allowed[row.status]:
            raise Problem(409, 'transition', 'Sold stock must return to available before reservation')
    if model is Enquiry:
        allowed = {'new': {'new', 'contacted', 'closed'}, 'contacted': {'contacted', 'new', 'closed'}, 'closed': {'closed', 'contacted'}}
        if values['status'] not in allowed[row.status]:
            raise Problem(409, 'transition', 'Reopen closed enquiries as contacted')
    if model is Task:
        if 'due_date' in values and values['due_date'] < today():
            raise Problem(422, 'past_date', 'Choose today or a later date')
        if values.get('completed') is False and record(session, Enquiry, row.enquiry_id).status == 'closed':
            raise Problem(409, 'closed', 'Reopen the enquiry before its task')
    values.update(revision=data.revision + 1, updated_at=datetime.now(timezone.utc))
    result = session.execute(update(model).where(model.id == record_id, model.revision == data.revision).values(**values).execution_options(synchronize_session=False))
    if result.rowcount != 1:
        raise Problem(409, 'stale_revision', 'Record changed. Refresh before editing.')
    session.expire(row)
    session.refresh(row)
    event(session, row, 'updated')
    session.flush()
    return serialize(row)


def page(session, model, offset=0, limit=25, **filters):
    query = select(model)
    if model is Vehicle:
        if not filters.get('include_archived', False):
            query = query.where(Vehicle.archived.is_(False))
        if filters.get('q'):
            q = filters['q'].lower().replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            query = query.where(func.lower(Vehicle.make + ' ' + Vehicle.model).like('%' + q + '%', escape='\\'))
    for name in ['status', 'vehicle_id', 'enquiry_id', 'completed']:
        if filters.get(name) is not None and hasattr(model, name):
            query = query.where(getattr(model, name) == filters[name])
    if model is Task and filters.get('overdue') is not None:
        overdue = (Task.completed.is_(False)) & (Task.due_date < today())
        query = query.where(overdue if filters['overdue'] else ~overdue)
    total = session.scalar(select(func.count()).select_from(query.subquery()))
    rows = session.scalars(query.order_by(model.id.desc()).offset(offset).limit(limit)).all()
    return {'items': [serialize(row) for row in rows], 'total': total, 'offset': offset, 'limit': limit}


def dashboard(session):
    result = dict(available=0, reserved=0, sold=0, stock_value_pence=0, open_enquiries=0, open_tasks=0, overdue_tasks=0)
    for status, count, value in session.execute(select(Vehicle.status, func.count(), func.sum(Vehicle.price_pence)).where(Vehicle.archived.is_(False)).group_by(Vehicle.status)):
        result[status] = count
        if status != 'sold':
            result['stock_value_pence'] += value or 0
    result['open_enquiries'] = session.scalar(select(func.count()).select_from(Enquiry).where(Enquiry.status != 'closed'))
    tasks = session.scalars(select(Task).join(Enquiry).where(Task.completed.is_(False), Enquiry.status != 'closed')).all()
    result['open_tasks'] = len(tasks)
    result['overdue_tasks'] = sum(task.due_date < today() for task in tasks)
    return result
