def test_negative_price_and_blank_make(client):
    data = {'make':'Demo','model':'One','year':2020,'price_pence':-1}
    assert client.post('/api/vehicles',json=data).status_code == 422
    data.update(price_pence=100,make='   ')
    assert client.post('/api/vehicles',json=data).status_code == 422

def test_missing_records(client):
    assert client.patch('/api/vehicles/999',json={'status':'sold'}).status_code == 404
    assert client.post('/api/enquiries',json={'vehicle_id':999,'customer':'Demo','message':'Hi'}).status_code == 404

def test_invalid_status_and_fractional_money(client):
    assert client.patch('/api/vehicles/999',json={'status':'unknown'}).status_code == 422
    assert client.post('/api/vehicles',json={'make':'Demo','model':'One','year':2020,'price_pence':1.5}).status_code == 422
