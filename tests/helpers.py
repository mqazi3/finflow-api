"""Shared request helpers for the test suite."""

API = "/api/v1"


def register_and_login(client, username="alice", password="password123"):
    """Create a user and return Authorization headers for them."""
    response = client.post(
        f"{API}/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text

    response = client.post(
        f"{API}/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_account(client, headers, balance=1000, name="Checking"):
    response = client.post(
        f"{API}/accounts/",
        json={"name": name, "account_type": "checking", "balance": balance},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def create_transaction(
    client,
    headers,
    account_id,
    amount,
    merchant="Store",
    category="Expense",
    description=None,
):
    response = client.post(
        f"{API}/transactions/",
        json={
            "account_id": account_id,
            "amount": amount,
            "merchant": merchant,
            "category": category,
            "description": description,
        },
        headers=headers,
    )
    assert response.status_code == 200, response.text
    return response.json()


def get_balance(client, headers, account_id):
    response = client.get(f"{API}/accounts/", headers=headers)
    assert response.status_code == 200, response.text
    return next(a["balance"] for a in response.json() if a["id"] == account_id)
