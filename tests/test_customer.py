from lib.db import create_customer, delete_customer, get_customer_by_id, update_customer


def test_create_customer(connection):
    data = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "john_test@example.com",
        "telephone": "123456789"
    }

    customer_id = create_customer(connection, data)
    customer = get_customer_by_id(connection, customer_id)

    assert customer is not None
    assert customer["firstname"] == data["firstname"]


def test_update_customer(connection):
    data = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "jane_test@example.com",
        "telephone": "987654321"
    }

    customer_id = create_customer(connection, data)

    updated_data = {
        "firstname": "Updated",
        "lastname": "User",
        "email": "updated@example.com",
        "telephone": "111111111"
    }

    result = update_customer(connection, customer_id, updated_data)
    customer = get_customer_by_id(connection, customer_id)

    assert result == 1
    assert customer["firstname"] == "Updated"


def test_update_nonexistent_customer(connection):
    result = update_customer(connection, 999999, {
        "firstname": "X",
        "lastname": "Y",
        "email": "x@y.com",
        "telephone": "000"
    })

    assert result == 0


def test_delete_customer(connection):
    data = {
        "firstname": "Temp",
        "lastname": "User",
        "email": "temp@example.com",
        "telephone": "222222222"
    }

    customer_id = create_customer(connection, data)
    result = delete_customer(connection, customer_id)
    customer = get_customer_by_id(connection, customer_id)

    assert result == 1
    assert customer is None


def test_delete_nonexistent_customer(connection):
    result = delete_customer(connection, 999999)
    assert result == 0
