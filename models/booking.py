from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class BookingDates(BaseModel):
    model_config = ConfigDict(extra="ignore")

    checkin: date
    checkout: date

    @field_validator("checkout")
    @classmethod
    def checkout_must_be_after_checkin(cls, checkout: date, info):
        checkin = info.data.get("checkin")

        if checkin is not None and checkout <= checkin:
            raise ValueError("checkout must be after checkin")

        return checkout


class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")

    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None