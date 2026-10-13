from backend import database

def test_stock_enquiry_workflow(client):
    data = {'make':'Fictional','model':'Example','year':2020,'price_pence':1250000}
    response = client.post('/api/vehicles',json=data)
    assert response.status_code == 201
    vehicle = response.json()
    record_id = vehicle['id']
    assert database.rows('SELECT * FROM vehicles WHERE id=?',(record_id,))[0]['price_pence'] == 1250000
    assert len(client.get('/api/vehicles?q=fiction').json()) == 1
    data['price_pence']=1200000
    assert client.put(f'/api/vehicles/{record_id}',json=data).json()['price_pence'] == 1200000
    enquiry = client.post('/api/enquiries',json={'vehicle_id':record_id,'customer':'Demo buyer','message':'Please arrange a demo','follow_up':'2026-10-20'})
    assert enquiry.status_code == 201
    enquiry_id = enquiry.json()['id']
    assert client.get('/api/dashboard').json()['open_enquiries'] == 1
    assert client.patch(f'/api/enquiries/{enquiry_id}',json={'completed':True}).status_code == 200
    assert client.get('/api/dashboard').json()['open_enquiries'] == 0
    assert client.patch(f'/api/vehicles/{record_id}',json={'status':'sold'}).status_code == 200
    assert client.get('/api/dashboard').json()['stock_value_pence'] == 0
    client.patch(f'/api/vehicles/{record_id}',json={'status':'sold','archived':True})
    assert client.get('/api/vehicles').json() == []
    assert len(client.get('/api/vehicles?include_archived=true').json()) == 1
    assert client.post('/api/enquiries',json={'vehicle_id':record_id,'customer':'Demo','message':'Hi'}).status_code == 409
    client.patch(f'/api/vehicles/{record_id}',json={'status':'available','archived':False})
    assert len(client.get('/api/vehicles').json()) == 1
