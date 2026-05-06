from app.lambda_handler import handler


def test_lambda_handler_health() -> None:
    event = {
        "version": "2.0",
        "routeKey": "GET /api/health",
        "rawPath": "/api/health",
        "rawQueryString": "",
        "headers": {"host": "example.execute-api.us-east-1.amazonaws.com"},
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test-api",
            "domainName": "example.execute-api.us-east-1.amazonaws.com",
            "domainPrefix": "example",
            "http": {
                "method": "GET",
                "path": "/api/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest",
            },
            "requestId": "test",
            "routeKey": "GET /api/health",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1767225600000,
        },
        "isBase64Encoded": False,
    }

    response = handler(event, {})

    assert response["statusCode"] == 200
    assert response["body"] == '{"status":"ok"}'
