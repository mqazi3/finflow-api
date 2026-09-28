"""Every read and write must be limited to the logged-in user's own data."""

from tests.helpers import (
    API,
    create_account,
    create_transaction,
    get_balance,
    register_and_login,
)


def setup_two_users(client):
    alice = register_and_login(client, "alice")
    bob = register_and_login(client, "bob")

    account = create_account(client, alice, balance=1000)
    transaction = create_transaction(client, alice, account["id"], 100)

    return alice, bob, account, transaction


def test_accounts_list_only_shows_own_accounts(client):
    alice, bob, account, _ = setup_two_users(client)

    assert client.get(f"{API}/accounts/", headers=bob).json() == []
    assert len(client.get(f"{API}/accounts/", headers=alice).json()) == 1


def test_cannot_read_another_users_transaction(client):
    _, bob, _, transaction = setup_two_users(client)

    response = client.get(f"{API}/transactions/{transaction['id']}", headers=bob)

    assert response.status_code == 404


def test_transaction_list_and_count_only_include_own(client):
    _, bob, _, _ = setup_two_users(client)

    assert client.get(f"{API}/transactions/", headers=bob).json() == []
    count = client.get(f"{API}/transactions/count", headers=bob).json()
    assert count["total_transactions"] == 0


def test_cannot_update_another_users_transaction(client):
    alice, bob, account, transaction = setup_two_users(client)

    response = client.put(
        f"{API}/transactions/{transaction['id']}",
        json={"amount": 1, "merchant": "Hacked", "category": "Income"},
        headers=bob,
    )

    assert response.status_code == 404
    unchanged = client.get(
        f"{API}/transactions/{transaction['id']}", headers=alice
    ).json()
    assert unchanged["merchant"] == "Store"
    assert get_balance(client, alice, account["id"]) == 900


def test_cannot_delete_another_users_transaction(client):
    alice, bob, account, transaction = setup_two_users(client)

    response = client.delete(f"{API}/transactions/{transaction['id']}", headers=bob)

    assert response.status_code == 404
    still_there = client.get(f"{API}/transactions/{transaction['id']}", headers=alice)
    assert still_there.status_code == 200
    assert get_balance(client, alice, account["id"]) == 900


def test_cannot_post_transaction_to_another_users_account(client):
    alice, bob, account, _ = setup_two_users(client)

    response = client.post(
        f"{API}/transactions/",
        json={
            "account_id": account["id"],
            "amount": 500,
            "merchant": "Bob's shop",
            "category": "Expense",
        },
        headers=bob,
    )

    assert response.status_code == 404
    assert get_balance(client, alice, account["id"]) == 900


def test_analytics_only_cover_own_data(client):
    _, bob, _, _ = setup_two_users(client)

    analytics = client.get(f"{API}/analytics/transactions", headers=bob).json()

    assert analytics["total_transactions"] == 0
    assert analytics["total_withdrawals"] == 0
    assert analytics["current_balance"] == 0
    assert client.get(f"{API}/analytics/categories", headers=bob).json() == []
    assert client.get(f"{API}/analytics/merchants", headers=bob).json() == []
    assert client.get(f"{API}/analytics/top-merchants", headers=bob).json() == []
