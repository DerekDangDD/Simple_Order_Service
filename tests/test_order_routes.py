import flask
import json
from application.app import app
import pytest
from database_models.models import InventoryItem, db
import mock

def test_inventory_create(monkeypatch):
    monkeypatch.setattr(db, "session", mock.MagicMock())
    tester = app.test_client()
    response = tester.post('/inventories', json={
    "name": "test1",
    "description": "test desc",
    "price": 1,
    "quantity": 2
    })
    assert response.status_code == 200
    assert response.json['name'] == "test1"
    assert response.json['description'] == "test desc"
    assert response.json['price'] == "1"
    assert response.json['quantity'] == 2

def test_inventory_create_invalid_JSON():
    tester = app.test_client()
    response = tester.post('/inventories', json={"TEST":"TEST"})
    assert response.status_code == 400

def test_inventory_create_no_JSON():
    tester = app.test_client()
    response = tester.post('/inventories')
    assert response.status_code == 400

@pytest.mark.parametrize("test_name, test_price, test_qty", [("test", -1, 1), ("test", 1, -1), ("test", -1, -1),
                                                             ("", 1, 1), (None, 1, 1)])
def test_inventory_create_negative_price(test_name, test_price, test_qty):
    tester = app.test_client()
    response = tester.post('/inventories', json={
    "name": test_name,
    "description": "test desc",
    "price": test_price,
    "quantity": test_qty
    })
    assert response.status_code == 400

def test_inventory_get_all(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.all.return_value = [InventoryItem("test123",
                                        "test",
                                      1,
                                      1)]
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories')
    assert response.status_code == 200
    assert response.json == [{'description': 'test', 'item_id': None,
                              'name': 'test123', 'price': '1', 'quantity': 1}]

def test_inventory_get_all_none(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.all.return_value = []
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories')
    assert response.status_code == 200
    assert response.json == []

def test_inventory_get_all_exception(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.all.side_effect = Exception()
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories')
    assert response.status_code == 400
    assert response.json['error_msg'] == 'Failed to get inventory items'

def test_inventory_get_item(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.get.return_value = InventoryItem("test123", "test", 1, 1)
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories/1')
    assert response.status_code == 200
    assert response.json == {'description': 'test', 'item_id': None,
                             'name': 'test123', 'price': '1', 'quantity': 1}

def test_inventory_get_item_none(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.get.return_value = None
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories/1')
    assert response.status_code == 404
    assert response.json["error_msg"] == "Item not found"

def test_inventory_get_item_exception(monkeypatch):
    mock_query = mock.MagicMock()
    mock_query.get.side_effect = Exception()
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.get('/inventories/1')
    assert response.status_code == 400
    assert response.json['error_msg'] == 'Failed to get inventory item'

def test_inventory_update(monkeypatch):
    monkeypatch.setattr(db, "session", mock.MagicMock())
    mock_query = mock.MagicMock()
    mock_query.get.return_value = InventoryItem("test", "test", 2, 2)
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.put('/inventories/1', json={
              "description": "test",
              "name": "test123",
              "price": 1,
              "quantity": 1
            })
    assert response.status_code == 200
    assert response.json == {'item_id': None, 'name': 'test123',
                             'description': 'test', 'price': '1', 'quantity': 1}

def test_inventory_update_no_payload(monkeypatch):
    monkeypatch.setattr(db, "session", mock.MagicMock())
    mock_query = mock.MagicMock()
    mock_query.get.return_value = InventoryItem("test", "test", 2, 2)
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.put('/inventories/1')
    assert response.status_code == 400
    assert response.json == {"warn_msg": "no update payload"}

def test_inventory_delete_item(monkeypatch):
    monkeypatch.setattr(db, "session", mock.MagicMock())
    mock_query = mock.MagicMock()
    mock_query.get.return_value = InventoryItem("test123", "test", 1, 1)
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.delete('/inventories/1')
    assert response.status_code == 200
    assert response.json == {'description': 'test', 'item_id': None,
                             'name': 'test123', 'price': '1', 'quantity': 1}

def test_inventory_delete_item_None(monkeypatch):
    monkeypatch.setattr(db, "session", mock.MagicMock())
    mock_query = mock.MagicMock()
    mock_query.get.return_value = None
    monkeypatch.setattr(InventoryItem, "query", mock_query)
    tester = app.test_client()
    response = tester.delete('/inventories/1')
    assert response.status_code == 404
    assert response.json == {"error_msg": "Item not found"}

