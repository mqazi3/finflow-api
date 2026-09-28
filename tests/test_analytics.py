from datetime import date, datetime, timedelta

import pytest

from app.models.transaction import Transaction

from tests.helpers import (
    API,
    create_account,
    create_transaction,
    register_and_login,
)


@pytest.fixture
def user(client):
    headers = register_and_login(client, "alice")
    account = create_account(client, headers, balance=1000)
    return headers, account["id"]


def get_analytics(client, headers):
    response = client.get(f"{API}/analytics/transactions", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def test_transaction_analytics_totals(client, user):
    headers, account_id = user
    create_transaction(client, headers, account_id, 12000, category="Expense")
    create_transaction(client, headers, account_id, 300, category="Expense")
    create_transaction(client, headers, account_id, 2500, category="Income")

    analytics = get_analytics(client, headers)

    assert analytics == {
        "total_transactions": 3,
        "total_deposits": 2500,
        "total_withdrawals": 12300,
        "current_balance": 1000 - 12000 - 300 + 2500,
        "flagged_transactions": 1,
    }


def test_analytics_are_cached(client, user, fake_redis):
    headers, _ = user

    get_analytics(client, headers)

    assert fake_redis.get("analytics:user:1") is not None
    assert 0 < fake_redis.ttl("analytics:user:1") <= 60


def test_cache_is_cleared_on_create_update_and_delete(client, user):
    headers, account_id = user

    transaction = create_transaction(client, headers, account_id, 12000)
    assert get_analytics(client, headers)["flagged_transactions"] == 1

    client.put(
        f"{API}/transactions/{transaction['id']}",
        json={"amount": 50, "merchant": "Apple", "category": "Expense"},
        headers=headers,
    )
    after_update = get_analytics(client, headers)
    assert after_update["flagged_transactions"] == 0
    assert after_update["total_withdrawals"] == 50
    assert after_update["current_balance"] == 950

    create_transaction(client, headers, account_id, 20)
    assert get_analytics(client, headers)["total_transactions"] == 2

    client.delete(f"{API}/transactions/{transaction['id']}", headers=headers)
    after_delete = get_analytics(client, headers)
    assert after_delete["total_transactions"] == 1
    assert after_delete["current_balance"] == 980


def test_analytics_work_when_redis_is_down(client, user, broken_redis):
    headers, account_id = user

    # Writes still succeed; cache invalidation failure is logged, not raised
    create_transaction(client, headers, account_id, 100)

    analytics = get_analytics(client, headers)
    assert analytics["total_transactions"] == 1
    assert analytics["current_balance"] == 900


def test_category_and_merchant_summaries(client, user):
    headers, account_id = user
    create_transaction(client, headers, account_id, 30, merchant="Starbucks", category="Expense")
    create_transaction(client, headers, account_id, 20, merchant="Starbucks", category="Expense")
    create_transaction(client, headers, account_id, 500, merchant="Employer", category="Income")

    categories = {
        row["category"]: row
        for row in client.get(f"{API}/analytics/categories", headers=headers).json()
    }
    assert categories["Expense"] == {"category": "Expense", "total_amount": -50, "transaction_count": 2}
    assert categories["Income"]["total_amount"] == 500

    merchants = client.get(f"{API}/analytics/merchants", headers=headers).json()
    assert merchants[0] == {"merchant": "Employer", "total_amount": 500, "transaction_count": 1}
    assert merchants[1] == {"merchant": "Starbucks", "total_amount": -50, "transaction_count": 2}


def test_top_merchants_are_positive_sorted_and_limited(client, user):
    headers, account_id = user
    create_transaction(client, headers, account_id, 30, merchant="Starbucks", category="Expense")
    create_transaction(client, headers, account_id, 400, merchant="Apple", category="expense")
    create_transaction(client, headers, account_id, 90, merchant="Target", category="EXPENSE")
    create_transaction(client, headers, account_id, 5000, merchant="Employer", category="Income")

    response = client.get(
        f"{API}/analytics/top-merchants", params={"limit": 2}, headers=headers
    )

    assert response.status_code == 200
    assert response.json() == [
        {"merchant": "Apple", "total_spent": 400, "transaction_count": 1},
        {"merchant": "Target", "total_spent": 90, "transaction_count": 1},
    ]


def test_top_merchants_limit_is_validated(client, user):
    headers, _ = user

    response = client.get(
        f"{API}/analytics/top-merchants", params={"limit": 0}, headers=headers
    )

    assert response.status_code == 422


def test_monthly_summary_date_filters(client, user, db_session):
    headers, account_id = user
    today = create_transaction(client, headers, account_id, 100, merchant="Today")
    old = create_transaction(client, headers, account_id, 40, merchant="Old")

    # Place one transaction late in the day and the other in an earlier year
    late_today = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=23)
    last_year = late_today - timedelta(days=400)
    db_session.get(Transaction, today["id"]).created_at = late_today
    db_session.get(Transaction, old["id"]).created_at = last_year
    db_session.commit()

    def monthly(params):
        response = client.get(f"{API}/analytics/monthly", params=params, headers=headers)
        assert response.status_code == 200, response.text
        return response.json()

    # end_date is inclusive: a transaction at 23:00 on the end date counts
    this_month = monthly({"start_date": date.today().isoformat(), "end_date": date.today().isoformat()})
    assert this_month == [
        {"month": late_today.strftime("%Y-%m"), "total_amount": -100, "transaction_count": 1}
    ]

    everything = monthly({})
    assert [row["month"] for row in everything] == [
        last_year.strftime("%Y-%m"),
        late_today.strftime("%Y-%m"),
    ]
