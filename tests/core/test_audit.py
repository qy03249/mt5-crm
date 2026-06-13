from app.core.audit import build_operation_log_params


def test_operation_log_params_redacts_sensitive_fields():
    params = build_operation_log_params(
        query_params={"page": "1"},
        body={
            "username": "admin",
            "password": "Admin@123456",
            "nested": {"access_token": "secret-token"},
        },
    )

    assert params == {
        "query": {"page": "1"},
        "body": {
            "username": "admin",
            "password": "***",
            "nested": {"access_token": "***"},
        },
    }
