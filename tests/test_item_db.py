import sys
import os
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from models import Item

def test_add_item_db(client, db, admin_login):
    response = client.post("/item/add_item", data={
        "project_code": "P1",
        "property_code": "123",
        "user": "Ali"
    }, follow_redirects=True)

    item = Item.query.first()
    assert item is not None
    assert item.property_code == "123"
