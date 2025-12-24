def test_suggest_property_code(client, db, login_user):
    response = client.get("/item/suggest", query_string={
        "field": "property_code",
        "value": "62"
    })

    assert response.status_code == 200
    assert "suggestions" in response.json


def test_edit_item_forbidden_for_normal_user(client, login_user):
    res = client.get("/item/edit_item_1")
    assert res.status_code in (302, 403)
