
from uuid import uuid4


def build_booking_payload() -> dict:
    unique_id = uuid4().hex[:8]

    return {
        "firstname": f"Test{unique_id}",
        "lastname": "Automation",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2027-05-10",
            "checkout": "2027-05-12",
        },
        "additionalneeds": "Breakfast",
    }
