"""Course-style FastAPI routes, validation classes and plain functions."""
import logging
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict
from backend import database as db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dealer')


class VehicleInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1900, le=2100)
    price_pence: int = Field(ge=0, le=100000000, strict=True)


class VehicleState(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['available','reserved','sold']
    archived: bool = False


class EnquiryInput(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    vehicle_id: int = Field(gt=0)
    customer: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1000)
    follow_up: date | None = None


class FollowUp(BaseModel):
    model_config = ConfigDict(extra='forbid')
    completed: bool


@asynccontextmanager
async def lifespan(app):
    db.initialize()
    yield


app = FastAPI(title='Dealer Stock & Enquiry Tracker', version='1.0.0', lifespan=lifespan)


def vehicle_or_404(vehicle_id):
    result = db.rows('SELECT * FROM vehicles WHERE id=?', (vehicle_id,))
    if not result:
        raise HTTPException(404, 'Vehicle not found')
    return result[0]


@app.get('/health')
def health():
    db.rows('SELECT 1')
    return {'status':'ok'}


@app.get('/api/vehicles')
def list_vehicles(q: str = '', include_archived: bool = False):
    records = db.rows('SELECT * FROM vehicles ORDER BY id DESC')
    result = []
    for vehicle in records:
        matches = q.lower() in f'{vehicle["make"]} {vehicle["model"]}'.lower()
        if matches and (include_archived or not vehicle['archived']):
            result.append(vehicle)
    return result


@app.post('/api/vehicles', status_code=201)
def create_vehicle(vehicle: VehicleInput):
    record_id = db.write('INSERT INTO vehicles(make,model,year,price_pence) VALUES (?,?,?,?)',
                         (vehicle.make,vehicle.model,vehicle.year,vehicle.price_pence))
    logger.info('vehicle_created id=%s', record_id)
    return vehicle_or_404(record_id)


@app.put('/api/vehicles/{vehicle_id}')
def edit_vehicle(vehicle_id: int, vehicle: VehicleInput):
    vehicle_or_404(vehicle_id)
    db.write('UPDATE vehicles SET make=?,model=?,year=?,price_pence=? WHERE id=?',
             (vehicle.make,vehicle.model,vehicle.year,vehicle.price_pence,vehicle_id))
    return vehicle_or_404(vehicle_id)


@app.patch('/api/vehicles/{vehicle_id}')
def update_vehicle_state(vehicle_id: int, state: VehicleState):
    vehicle_or_404(vehicle_id)
    db.write('UPDATE vehicles SET status=?,archived=? WHERE id=?',
             (state.status,int(state.archived),vehicle_id))
    return vehicle_or_404(vehicle_id)


@app.get('/api/enquiries')
def list_enquiries():
    return db.rows('SELECT * FROM enquiries ORDER BY id DESC')


@app.post('/api/enquiries', status_code=201)
def create_enquiry(enquiry: EnquiryInput):
    vehicle = vehicle_or_404(enquiry.vehicle_id)
    if vehicle['archived']:
        raise HTTPException(409, 'Vehicle is archived')
    record_id = db.write('INSERT INTO enquiries(vehicle_id,customer,message,follow_up) VALUES (?,?,?,?)',
                         (enquiry.vehicle_id,enquiry.customer,enquiry.message,
                          enquiry.follow_up.isoformat() if enquiry.follow_up else ''))
    return db.rows('SELECT * FROM enquiries WHERE id=?', (record_id,))[0]


@app.patch('/api/enquiries/{enquiry_id}')
def complete_follow_up(enquiry_id: int, follow_up: FollowUp):
    if not db.rows('SELECT id FROM enquiries WHERE id=?', (enquiry_id,)):
        raise HTTPException(404, 'Enquiry not found')
    db.write('UPDATE enquiries SET completed=? WHERE id=?', (int(follow_up.completed),enquiry_id))
    return db.rows('SELECT * FROM enquiries WHERE id=?', (enquiry_id,))[0]


@app.get('/api/dashboard')
def dashboard():
    counts = {'available':0,'reserved':0,'sold':0,'stock_value_pence':0,'open_enquiries':0}
    for vehicle in list_vehicles():
        counts[vehicle['status']] += 1
        if vehicle['status'] != 'sold':
            counts['stock_value_pence'] += vehicle['price_pence']
    for enquiry in list_enquiries():
        if not enquiry['completed']:
            counts['open_enquiries'] += 1
    return counts


frontend = Path(__file__).resolve().parents[1] / 'frontend'
app.mount('/', StaticFiles(directory=frontend, html=True), name='frontend')
