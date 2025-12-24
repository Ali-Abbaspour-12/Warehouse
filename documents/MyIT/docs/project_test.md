
```text
test/
│   conftest.py
│   test_item_db.py
│   test_item_routes.py
│   test_suggest.py
│
├───uploads
└───__pycache__
        conftest.cpython-310-pytest-9.0.2.pyc
        test_item_db.cpython-310-pytest-9.0.2.pyc
        test_item_routes.cpython-310-pytest-9.0.2.pyc
        test_suggest.cpython-310-pytest-9.0.2.pyc

```

---

```text
def test_add_item_redirect_without_login(client):
    response = client.get("/item/add_item")
    assert response.status_code == 302  # redirect به login


```

![](images/Test_routing.png)