from unittest.mock import Mock

import allure
import pytest
import requests

from clients.api_client import ApiClient


@allure.title("GET request uses the correct URL and timeout")
@allure.feature("API Client")
@allure.story("HTTP requests")
def test_get_uses_correct_url_and_timeout():
    client = ApiClient("https://example.com/")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"bookingid": 123}'
    client.session.request = Mock(return_value=mock_response)

    client.get("/booking/123")

    client.session.request.assert_called_once_with(
        "GET",
        "https://example.com/booking/123",
        timeout=10.0,
    )


@allure.title("POST request passes JSON body")
@allure.feature("API Client")
@allure.story("HTTP requests")
def test_post_passes_json_body():
    client = ApiClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"bookingid": 123}'
    client.session.request = Mock(return_value=mock_response)

    payload = {"firstname": "Test", "lastname": "User"}
    client.post("/booking", json=payload)

    client.session.request.assert_called_once_with(
        "POST",
        "https://example.com/booking",
        json=payload,
        timeout=10.0,
    )


@allure.title("GET request propagates timeout")
@allure.feature("API Client")
@allure.story("Error handling")
def test_get_propagates_timeout():
    client = ApiClient("https://example.com")
    client.session.request = Mock(
        side_effect=requests.exceptions.Timeout
    )

    with pytest.raises(requests.exceptions.Timeout):
        client.get("/booking/123")


@allure.title("Client closes the session")
@allure.feature("API Client")
@allure.story("Resource management")
def test_close_closes_session():
    client = ApiClient("https://example.com")
    client.session.close = Mock()

    client.close()

    client.session.close.assert_called_once_with()


@allure.title("{http_method} uses the shared request method")
@allure.feature("API Client")
@allure.story("HTTP requests")
@pytest.mark.parametrize(
    ("method_name", "http_method", "kwargs"),
    [
        ("put", "PUT", {"json": {"firstname": "Updated"}}),
        ("patch", "PATCH", {"json": {"firstname": "Updated"}}),
        ("delete", "DELETE", {}),
    ],
)
def test_http_methods_use_request(
        method_name,
        http_method,
        kwargs,
):
    client = ApiClient("https://example.com")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"bookingid": 123}'
    client.session.request = Mock(return_value=mock_response)

    getattr(client, method_name)("/booking/123", **kwargs)

    client.session.request.assert_called_once_with(
        http_method,
        "https://example.com/booking/123",
        **kwargs,
        timeout=10.0,
    )
