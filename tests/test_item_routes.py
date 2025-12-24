def test_add_item_redirect_without_login(client):
    response = client.get("/item/add_item")
    assert response.status_code == 302  # redirect به login
