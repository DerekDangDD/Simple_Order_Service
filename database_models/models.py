from application.app import db
from sqlalchemy.orm import relationship

class InventoryItem(db.Model):
    __tablename__ = 'InventoryItem'
    item_id = db.Column('item_id', db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(256))
    price = db.Column(db.Numeric(precision=9,scale=2))
    quantity = db.Column(db.Integer)


    def __init__(self, name, description, price, quantity):
        if not name:
            raise Exception("Name should not be empty")
        if price < 0 or quantity < 0:
            raise Exception("Can't be negative")
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return '<item_id {}>'.format(self.item_id)

    def serialize(self):
        return {
            'item_id': self.item_id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),
            'quantity': self.quantity
        }

class Order(db.Model):
    __tablename__ = 'Order'
    order_id = db.Column('order_id', db.Integer, primary_key = True)
    customer_email = db.Column(db.String(100))
    date_placed = db.Column(db.DateTime)
    status = db.Column(db.Enum("pending", "shipped", "fulfilled", "canceled", name="status_enum"))
    order_products = relationship("OrderProduct", backref="order_source")


    def __init__(self, customer_email, date_placed, status):
        self.customer_email = customer_email
        self.date_placed = date_placed
        self.status = status

    def __repr__(self):
        return '<order_id {}>'.format(self.order_id)

    def serialize(self):
        return {
            'order_id': self.order_id,
            'customer_email': self.customer_email,
            'date_placed': str(self.date_placed),
            'status': self.status
        }

class OrderProduct(db.Model):
    __tablename__ = 'Order_Product'
    order_id = db.Column(db.Integer, db.ForeignKey('Order.order_id'), primary_key = True)
    item_id = db.Column(db.Integer, db.ForeignKey('InventoryItem.item_id'), primary_key = True)
    item_qty = db.Column(db.Integer)

    def __init__(self, order_id, item_id, qty):
        self.order_id = order_id
        self.item_id = item_id
        self.item_qty = qty

    def serialize(self):
        return {
            'order_id': self.order_id,
            'item_id': self.item_id,
            'item_qty': self.item_qty
        }


db.create_all()