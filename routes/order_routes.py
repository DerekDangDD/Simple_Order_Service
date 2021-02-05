from flask import request, jsonify
from flask import current_app as app
from database_models.models import Order, InventoryItem, db, OrderProduct
from datetime import datetime
import requests
import traceback


@app.route('/orders', methods=['POST'])
def create_order():
    """
    Checks if each product in the order is in stock. Creates the Order and it's associated OrderProducts accordingly.

    Returns:
        JSON of the created order
    """

    update_qty = []
    for order_product in request.json['order_products']:
        try:
            remaining_stock = get_remaining_stock(order_product['item_id'], order_product['item_qty'])
            if remaining_stock < 0:
                msg = {"msg": "{} does not have the required amount in stock".format(order_product['order_id'])}
                return msg, 400
            update_qty.append(remaining_stock)
        except Exception:
            msg = {"error_msg": "Failed to check inventory",
                   "stack_trace": traceback.format_exc()}
            return msg, 400

    try:
        new_order = Order(request.json['customer_email'],
                          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          request.json['status'])
        db.session.add(new_order)
        db.session.commit()
    except Exception:
        msg = {"error_msg": "Failed to create new order",
               "stack_trace": traceback.format_exc()}
        return msg, 400
    try:
        for order_product, qty in zip(request.json['order_products'], update_qty):
            new_order_product = OrderProduct(new_order.order_id,
                                             order_product['item_id'],
                                             order_product['item_qty'])
            r = requests.put("{}inventories/{}".format(request.url_root,
                                                       order_product['item_id']),
                             json={
                                 "quantity": qty
                             })
            if r.status_code != 200:
                raise Exception(r.status_code)
            db.session.add(new_order_product)

        db.session.commit()
    except Exception:
        db.session.delete(new_order)
        msg = {"error_msg": "Failed to update inventory stock",
               "stack_trace": traceback.format_exc()}
        return msg, 400

    return requests.get("{}orders/{}".format(request.url_root, new_order.order_id)).json()


@app.route('/orders', methods=['GET'])
def get_all_orders():
    """
    Gets all the orders

    Returns:
        JSON of all the orders
    """

    try:
        all_orders = Order.query.all()
        if not all_orders:
            msg = {"warning_log": "No Orders found"}
            return msg
        result = []
        for order in all_orders:
            r = requests.get("{}orders/{}".format(request.url_root,
                                                  order.order_id))
            result.append(r.json())
            print(r.json())
        return jsonify(result)
    except Exception:
        msg = {"error_msg": "Failed to update inventory stock",
               "stack_trace": traceback.format_exc()}
        return msg, 400


@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """
    Gets a specific Order
    Args:
        order_id: Order ID

    Returns:
        Order JSON
    """
    order = Order.query.get(order_id)
    if not order:
        msg = {"error_log": "Order not found"}
        return msg, 404
    order_products = order.order_products
    order_products_dict_list = []
    for order_product in order_products:
        order_products_dict_list.append(order_product.serialize())
    result = order.serialize()
    result['order_products'] = order_products_dict_list
    return jsonify(result)


@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    """
    Updates a specific Order. Checks and updates the inventory if the quantity is changed.
    Args:
        order_id: Order id

    Returns:
        Updated Order
    """

    order = Order.query.get(order_id)
    if not order:
        msg = {"error_log": "Order not found"}
        return msg, 404
    order_dict = request.json
    if "customer_email" in order_dict:
        order.customer_email = order_dict['customer_email']
    update_qty = []
    if "order_products" in order_dict:
        for order_product in order_dict['order_products']:
            item_id = order_product['item_id']
            old_order_product = OrderProduct.query.get((order_id, item_id))
            if not old_order_product:
                qty_diff = order_product['item_qty']
            else:
                qty_diff = order_product['item_qty'] - old_order_product.item_qty
            remaining_stock = get_remaining_stock(order_product['item_id'], qty_diff)
            if remaining_stock < 0:
                msg = {"msg": "item_id: {} does not have the required amount in stock".format(order_product['item_id'])}
                return msg, 400
            update_qty.append((item_id, qty_diff))
            if not old_order_product:
                db.session.add(OrderProduct(order_id, item_id, order_product['item_qty']))
            else:
                old_order_product.item_qty = order_product['item_qty']

        for (item_id, qty_diff) in update_qty:
            modify_stocks(item_id, qty_diff)
    if "status" in order_dict:
        order.status = order_dict['status']

    db.session.commit()
    print(order.serialize())
    return jsonify(order.serialize())


def get_remaining_stock(item_id, quantity):
    """
    Gets the remaining stock of the item after removing the qty
    Args:
        item_id: item id
        quantity: item qty

    Returns:

    """
    inventory_item = InventoryItem.query.get(item_id)
    if not inventory_item:
        raise Exception("Item not found")
    inventory_item_dict = inventory_item.serialize()
    inventory_stock = inventory_item_dict['quantity']
    return inventory_stock - quantity

def modify_stocks(item_id, qty_diff):
    inventory_item = InventoryItem.query.get(item_id)
    inventory_item_dict = inventory_item.serialize()
    inventory_stock = inventory_item_dict['quantity'] - qty_diff
    r = requests.put("{}inventories/{}".format(request.url_root,
                                               item_id),
                     json={
                         "quantity": inventory_stock
                     })
    return r

def return_inventory_items(order_product):
    item_id = order_product.item_id
    returned_qty = order_product.item_qty

    inventory_item = InventoryItem.query.get(item_id)
    inventory_item_dict = inventory_item.serialize()
    inventory_stock = inventory_item_dict['quantity']

    r = requests.put("{}inventories/{}".format(request.url_root,
                                               order_product.item_id),
                     json={
                         "quantity": inventory_stock + returned_qty
                     })
    return r


@app.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        msg = {"error_msg": "Order not found"}
        return msg, 404
    order_products = order.order_products
    for order_product in order_products:
        response = return_inventory_items(order_product)
        if response.status_code != 200:
            msg = {"error_msg": "Failed to delete order due to status code: {}".format(response.status_code)}
            return msg
        db.session.delete(order_product)
    db.session.commit()
    db.session.delete(order)
    db.session.commit()
    return jsonify(order.serialize())
