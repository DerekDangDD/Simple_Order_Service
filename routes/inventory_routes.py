from flask import request, jsonify
from flask import current_app as app
from database_models.models import InventoryItem, db
import traceback

@app.route('/inventories', methods=['POST'])
def create_inventory_item():
    try:
        if request.json['price'] < 0 or request.json["quantity"] < 0:
            msg = {"error_msg": "value cannot be negative"}
            return msg, 400
        new_inventory = InventoryItem(request.json['name'],
                                      request.json['description'],
                                      request.json['price'],
                                      request.json['quantity'])

        db.session.add(new_inventory)
        db.session.commit()
    except Exception:
        msg = {"error_msg": "Failed to create inventory item",
               "stack_trace": traceback.format_exc()}
        print(msg)
        return msg, 400

    return jsonify(new_inventory.serialize())

# Get all inventory items
@app.route('/inventories', methods=['GET'])
def get_all_inventory_item():
    try:
        all_inventory_items = InventoryItem.query.all()
        print(all_inventory_items)
        return jsonify([item.serialize() for item in all_inventory_items])
    except Exception:
        msg = {"error_msg": "Failed to get inventory items",
               "stack_trace": traceback.format_exc()}
        return msg, 400

@app.route('/inventories/<item_id>', methods=['GET'])
def get_inventory_item(item_id):
    try:
        inventory_item = InventoryItem.query.get(item_id)
        if not inventory_item:
            msg = {"error_msg": "Item not found"}
            return msg, 404
        return jsonify(inventory_item.serialize())
    except Exception:
        msg = {"error_msg": "Failed to get inventory item",
               "stack_trace": traceback.format_exc()}
        return msg, 400

@app.route('/inventories/<item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    inventory_item = InventoryItem.query.get(item_id)
    if not inventory_item:
        msg = {"error_msg": "Item not found"}
        return msg
    request_dict = request.json
    if not request_dict:
        msg = {"warn_msg": "no update payload"}
        return msg, 400
    if "name" in request_dict:
        inventory_item.name = request_dict['name']
    if "description"in request_dict:
        inventory_item.description = request_dict['description']
    if "price" in request_dict:
        inventory_item.price = request_dict['price']
    if "quantity" in request_dict:
        inventory_item.quantity = request.json['quantity']

    db.session.commit()
    print(inventory_item.serialize())
    return jsonify(inventory_item.serialize())

@app.route('/inventories/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    inventory_item = InventoryItem.query.get(item_id)
    if not inventory_item:
        msg = {"error_msg": "Item not found"}
        return msg, 404
    db.session.delete(InventoryItem.query.get(item_id))
    db.session.commit()
    return jsonify(inventory_item.serialize())