from datetime import date
from fastapi.testclient import TestClient
from backend_v2.app import create_app


def test_live_v2_http_journey(tmp_path,monkeypatch):
    monkeypatch.setenv('APP_ENV','local');monkeypatch.setenv('AUTH_MODE','local')
    app=create_app('sqlite:///'+(tmp_path/'http.sqlite3').as_posix())
    with TestClient(app) as client:
        v=client.post('/api/vehicles',json={'make':'Demo','model':'City','year':2020,'price_pence':100})
        assert v.status_code==201
        vid=v.json()['id']
        e=client.post('/api/enquiries',json={'vehicle_id':vid,'customer':'Fictional buyer','message':'Visit'})
        assert e.status_code==201
        t=client.post('/api/tasks',json={'enquiry_id':e.json()['id'],'due_date':date.today().isoformat()})
        assert t.status_code==201
        assert client.get('/api/dashboard').json()['open_tasks']==1
        assert client.patch(f"/api/tasks/{t.json()['id']}",json={'revision':1,'completed':True}).status_code==200
        assert client.patch(f'/api/vehicles/{vid}',json={'revision':1,'status':'reserved'}).status_code==200
        assert client.patch(f'/api/vehicles/{vid}',json={'revision':1,'status':'sold'}).status_code==409
        assert client.get('/api/changes').json()['next_sequence']>0
        assert client.get('/health').status_code==200
        assert 'private' not in client.get('/api/vehicles/999').text
