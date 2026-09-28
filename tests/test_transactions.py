import pytest

from tests.helpers import (
    API,
    create_account,
    create_transaction,
    get_balance,
    register_and_login,
)


@pytest.fixture
def user(client):
    headers = register_and_login(client, "alice")
    account = create_account(client, headers, balance=1000)
    return headers, account["id"]


def test_expense_is_stored_negative_and_reduces_balance(client, user):
    headers, account_id = user

    transaction = create_transaction(client, headers, account_id, 250, category="Expense")

    assert transaction["amount"] == -250
    assert get_balance(client, headers, account_id) == 750


def test_expense_match_is_case_insensitive(client, user):
    headers, account_id = user

    transaction = create_transaction(client, headers, account_id, 40, category="expense")

    assert transaction["amount"] == -40


def test_income_is_stored_positive_and_increases_balance(client, user):
    headers, account_id = user

    transaction = create_transaction(client, headers, account_id, 2000, category="Income")

    assert transaction["amount"] == 2000
    assert get_balance(client, headers, account_id) == 3000


def test_negative_input_is_normalized_by_category(client, user):
    headers, account_id = user

    income = create_transaction(client, headers, account_id, -300, category="Income")
    expense = create_transaction(client, headers, account_id, -50, category="Expense")

    assert income["amount"] == 300
    assert expense["amount"] == -50


def test_large_transactions_are_flagged(client, user):
    headers, account_id = user

    small = create_transaction(client, headers, account_id, 10000)
    large = create_transaction(client, headers, account_id, 10000.01)

    assert small["is_flagged"] is False
    assert large["is_flagged"] is True


def test_description_is_saved(client, user):
    headers, account_id = user

    created = create_transaction(
        client, headers, account_id, 20, description="Office supplies"
    )
    fetched = client.get(f"{API}/transactions/{created['id']}", headers=headers).json()

    assert fetched["description"] == "Office supplies"


def test_unknown_account_returns_404(client, user):
    headers, _ = user

    response = client.post(
        f"{API}/transactions/",
        json={"account_id": 9999, "amount": 10, "merchant": "X", "category": "Expense"},
        headers=headers,
    )

    assert response.status_code == 404


def test_update_recalculates_balance_and_flag(client, user):
    headers, account_id = user
    transaction = create_transaction(client, headers, account_id, 12000)
    assert transaction["is_flagged"] is True
    assert get_balance(client, headers, account_id) == -11000

    response = client.put(
        f"{API}/transactions/{transaction['id']}",
        json={
            "amount": 50,
            "merchant": "Apple",
            "category": "Expense",
            "description": "Cable",
        },
        headers=headers,
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["amount"] == -50
    assert updated["is_flagged"] is False
    assert updated["merchant"] == "Apple"
    assert updated["description"] == "Cable"
    assert get_balance(client, headers, account_id) == 950


def test_update_from_expense_to_income(client, user):
    headers, account_id = user
    transaction = create_transaction(client, headers, account_id, 100, category="Expense")

    client.put(
        f"{API}/transactions/{transaction['id']}",
        json={"amount": 100, "merchant": "Refund", "category": "Income"},
        headers=headers,
    )

    assert get_balance(client, headers, account_id) == 1100


def test_delete_reverses_balance(client, user):
    headers, account_id = user
    transaction = create_transaction(client, headers, account_id, 2000, category="Income")
    assert get_balance(client, headers, account_id) == 3000

    response = client.delete(f"{API}/transactions/{transaction['id']}", headers=headers)

    assert response.status_code == 200
    assert get_balance(client, headers, account_id) == 1000
    missing = client.get(f"{API}/transactions/{transaction['id']}", headers=headers)
    assert missing.status_code == 404


def test_missing_transaction_returns_404(client, user):
    headers, _ = user

    assert client.get(f"{API}/transactions/9999", headers=headers).status_code == 404
    assert client.delete(f"{API}/transactions/9999", headers=headers).status_code == 404


def test_filtering_search_and_count(client, user):
    headers, account_id = user
    create_transaction(client, headers, account_id, 30, merchant="Starbucks", category="Expense")
    create_transaction(client, headers, account_id, 80, merchant="Target", category="Expense")
    create_transaction(client, headers, account_id, 500, merchant="Employer", category="Income")

    def listed(params):
        response = client.get(f"{API}/transactions/", params=params, headers=headers)
        assert response.status_code == 200
        return sorted(t["merchant"] for t in response.json())

    assert listed({"category": "Income"}) == ["Employer"]
    assert listed({"min_amount": 0}) == ["Employer"]
    assert listed({"max_amount": -50}) == ["Target"]
    assert listed({"search": "star"}) == ["Starbucks"]

    count = client.get(
        f"{API}/transactions/count", params={"category": "Expense"}, headers=headers
    ).json()
    assert count["total_transactions"] == 2


def test_pagination_returns_newest_first(client, user):
    headers, account_id = user
    for i in range(5):
        create_transaction(client, headers, account_id, 10, merchant=f"M{i}")

    first_page = client.get(
        f"{API}/transactions/", params={"limit": 2}, headers=headers
    ).json()
    second_page = client.get(
        f"{API}/transactions/", params={"skip": 2, "limit": 2}, headers=headers
    ).json()

    assert [t["merchant"] for t in first_page] == ["M4", "M3"]
    assert [t["merchant"] for t in second_page] == ["M2", "M1"]


def test_pagination_limits_are_validated(client, user):
    headers, _ = user

    assert client.get(f"{API}/transactions/", params={"limit": 0}, headers=headers).status_code == 422
    assert client.get(f"{API}/transactions/", params={"limit": 101}, headers=headers).status_code == 422
    assert client.get(f"{API}/transactions/", params={"skip": -1}, headers=headers).status_code == 422
