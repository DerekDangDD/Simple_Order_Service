# Simple_Order_Service
Simple REST API to create, update, delete, and view orders and inventory items  

Docker Setup:  
 
1.Add postgres database uri in application/app.py  
2.Build docker image `docker build -t "simple_order" .`  
3.Run docker container `docker run -p 5000:5000 --name="simple_order" -it simple_order /bin/sh`  
4.Run `python3 application/app.py`  

Local Python Setup:  
Requirements: Python3 and pip  
1.Add postgres database uri in application/app.py  
2.Run `python -m pip install -r requirements.txt`  
3.Run `python setup.py install`  
4.Run `python application/app.py`  

REST APIs:

- Create inventory item  
POST http://localhost:3000/inventories  
Creating an item requires: name, description, price and quantity. The item_id  
auto incremented, starting at 1
- Read all inventory items    
GET http://localhost:3000/inventories
- Read single inventory item
GET http://localhost:3000/inventories/1
- Update inventory item
PUT http://localhost:3000/inventories/1  
Any one of theses field may be used to update an inventory item: name, description, price and quantity  

- Delete inventory item
DELETE http://localhost:3000/inventories/1
- Create order
POST http://localhost:3000/orders
Creates an order and adjusts the inventory accordingly. If inventory levels are insufficient, the request is denied

- Read all orders
GET http://localhost:3000/orders
- Read single order
GET http://localhost:3000/orders/1
- Update order
PUT http://localhost:3000/orders/1
Updates an order and adjusts the inventory accordingly. If inventory levels are insufficient, the request is denied

- Delete order
DELETE http://localhost:3000/orders/1

Sample work flow:

Create Item:
```
{
 "name": "item1",
 "description": "item1",
 "price": 4.00,
 "quantity": 40
 }
```

Update Item:
```
{
  "name": "item2",
  "description": "item2",
  "item_id": 1,
  "price": "10.99",
  "quantity": 110
}
```

Create Order:  
*Note: only these status are valid `"pending", "shipped", "fulfilled", "canceled"`
```
{
  "customer_email": "test@gmail.com",
  "date_placed": "2020-02-17 02:11:12",
  "order_id": 1,
  "order_products": [
    {
      "item_id": 2,
      "item_qty": 5,
      "order_id": 1
    },
    {
      "item_id": 3,
      "item_qty": 1,
      "order_id": 1
    }
  ],
  "status": "pending"
}
```

Update Order:
```
{"order_products": [
      {
        "item_id": 2,
        "item_qty": 10,
        "order_id": 1
      },
      {
        "item_id": 3,
        "item_qty": 1,
        "order_id": 1
      },
      {
        "item_id": 4,
        "item_qty": 5,
        "order_id": 1
      }
    ]}
```