
import json

import allure

from data.booking_data import build_booking_payload


@allure.title("Create booking")
@allure.description("Verify that a booking can be created and its data is returned.")
@allure.feature("Booking API")
@allure.story("Create booking")
def test_create_booking(api_client):
    with allure.step("Prepare booking data"):
        payload = build_booking_payload()
        allure.attach(
            json.dumps(payload, indent=2),
            name="Booking request payload",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Send POST request to create booking"):
        response = api_client.post("/booking", json=payload)
        allure.attach(
            response.text,
            name="Create booking response",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Verify HTTP status is 200"):
        assert response.status_code == 200

    with allure.step("Verify booking ID is returned"):
        result = response.json()
        assert isinstance(result["bookingid"], int)

    with allure.step("Verify returned booking data"):
        assert result["booking"] == payload


@allure.title("Retrieve created booking")
@allure.description("Verify that a newly created booking can be retrieved by its ID.")
@allure.feature("Booking API")
@allure.story("Retrieve booking")
def test_created_booking_can_be_retrieved(api_client):
    with allure.step("Prepare booking data"):
        payload = build_booking_payload()
        allure.attach(
            json.dumps(payload, indent=2),
            name="Booking request payload",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Create booking"):
        create_response = api_client.post("/booking", json=payload)
        assert create_response.status_code == 200
        allure.attach(
            create_response.text,
            name="Create booking response",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Extract booking ID"):
        booking_id = create_response.json()["bookingid"]
        assert isinstance(booking_id, int)

    with allure.step("Retrieve booking by ID"):
        get_response = api_client.get(f"/booking/{booking_id}")
        allure.attach(
            get_response.text,
            name="Retrieved booking response",
            attachment_type=allure.attachment_type.JSON,
        )

    with allure.step("Verify retrieved booking"):
        assert get_response.status_code == 200
        assert get_response.json() == payload
