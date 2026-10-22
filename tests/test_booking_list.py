import allure
import pytest
from datetime import date
from pydantic import ValidationError

from config import BASE_URL
from models.booking import Booking


@allure.title("Get booking IDs")
@allure.feature("Booking API")
@allure.story("List bookings")
def test_get_booking_ids(http_session):
    with allure.step("Send GET request to booking list"):
        response = http_session.get(f"{BASE_URL}/booking", timeout=10)

    with allure.step("Verify HTTP status"):
        assert response.status_code == 200

    with allure.step("Verify booking list structure"):
        bookings = response.json()
        assert isinstance(bookings, list)

        for booking in bookings:
            assert isinstance(booking, dict)
            assert "bookingid" in booking
            assert isinstance(booking["bookingid"], int)


@allure.title("Nonexistent booking returns 404")
@allure.feature("Booking API")
@allure.story("Error handling")
def test_get_nonexistent_booking_returns_404(http_session):
    with allure.step("Request a nonexistent booking"):
        response = http_session.get(
            f"{BASE_URL}/booking/999999999",
            timeout=10,
        )

    with allure.step("Verify HTTP status is 404"):
        assert response.status_code == 404


@allure.title("Get booking details")
@allure.feature("Booking API")
@allure.story("Retrieve booking")
def test_get_booking_details(api_client, booking_id):
    with allure.step(f"Request booking {booking_id}"):
        response = api_client.get(f"/booking/{booking_id}")

    with allure.step("Attach booking response"):
        allure.attach(
            response.text,
            name="Booking response",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Verify HTTP status"):
        assert response.status_code == 200

    with allure.step("Validate booking against Pydantic model"):
        booking = Booking.model_validate(response.json())

    with allure.step("Verify required name fields"):
        assert booking.firstname
        assert booking.lastname
    with allure.step("Attach booking response"):
        allure.attach(
            response.text,
            name="Booking response",
            attachment_type=allure.attachment_type.JSON,
        )


@allure.title("Verify booking field types")
@allure.feature("Booking API")
@allure.story("Data validation")
def test_get_booking_details_field_types(api_client, booking_id):
    with allure.step(f"Request booking {booking_id}"):
        response = api_client.get(f"/booking/{booking_id}")

    with allure.step("Verify HTTP status"):
        assert response.status_code == 200
        booking = response.json()

    with allure.step("Verify field types"):
        assert isinstance(booking["firstname"], str)
        assert isinstance(booking["lastname"], str)
        assert isinstance(booking["totalprice"], int)
        assert isinstance(booking["depositpaid"], bool)
        assert isinstance(booking["bookingdates"], dict)
        assert (
                "additionalneeds" not in booking
                or isinstance(booking["additionalneeds"], str)
        )


@allure.title("Verify booking dates structure")
@allure.feature("Booking API")
@allure.story("Data validation")
def test_get_booking_dates_structure(api_client, booking_id):
    with allure.step(f"Request booking {booking_id}"):
        response = api_client.get(f"/booking/{booking_id}")

    with allure.step("Verify HTTP status and extract dates"):
        assert response.status_code == 200
        bookingdates = response.json()["bookingdates"]

    with allure.step("Verify check-in and check-out fields"):
        assert isinstance(bookingdates, dict)
        assert "checkin" in bookingdates
        assert "checkout" in bookingdates
        assert isinstance(bookingdates["checkin"], str)
        assert isinstance(bookingdates["checkout"], str)


@allure.title("Verify booking dates are valid and ordered")
@allure.feature("Booking API")
@allure.story("Data validation")
def test_booking_dates_are_valid_and_ordered(api_client, booking_id):
    with allure.step(f"Request booking {booking_id}"):
        response = api_client.get(f"/booking/{booking_id}")

    with allure.step("Verify HTTP status"):
        assert response.status_code == 200
        bookingdates = response.json()["bookingdates"]

    with allure.step("Parse and compare dates"):
        checkin = date.fromisoformat(bookingdates["checkin"])
        checkout = date.fromisoformat(bookingdates["checkout"])
        assert checkout > checkin


@allure.title("Reject invalid total price")
@allure.feature("Booking API")
@allure.story("Model validation")
def test_booking_model_rejects_invalid_totalprice():
    invalid_booking = {
        "firstname": "John",
        "lastname": "Smith",
        "totalprice": "not-a-number",
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-10-21",
            "checkout": "2026-10-25",
        },
        "additionalneeds": "",
    }

    with allure.step("Validate booking with invalid total price"):
        with pytest.raises(ValidationError):
            Booking.model_validate(invalid_booking)


@allure.title("Reject invalid booking dates")
@allure.feature("Booking API")
@allure.story("Model validation")
def test_booking_model_rejects_invalid_dates():
    invalid_booking = {
        "firstname": "John",
        "lastname": "Smith",
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-10-25",
            "checkout": "2026-10-21",
        },
        "additionalneeds": "",
    }

    with allure.step("Validate booking with checkout before check-in"):
        with pytest.raises(ValidationError):
            Booking.model_validate(invalid_booking)
