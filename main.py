import os

import psycopg
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_TOKEN = os.getenv("API_TOKEN", "hawktuah_2421_secret_token")

print("API_TOKEN loaded is:", repr(API_TOKEN))  

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your .env file.")


app = FastAPI()


# ---------- DB helper ----------
def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True)


# ---------- Request models ----------
class NewsletterPayload(BaseModel):
    email: EmailStr
    first_name: str | None = None
    how_did_you_hear: str | None = None
    favorite_music: str | None = None
    consent_marketing: bool | None = False


class BandApplicationPayload(BaseModel):
    contact_name: str | None = None
    contact_email: EmailStr
    contact_role: str | None = None

    band_name: str
    band_genre: str | None = None
    band_city: str | None = None
    band_instagram: str | None = None
    band_website: str | None = None
    band_spotify: str | None = None

    about_band: str | None = None


# ---------- Auth helper ----------
def check_auth(authorization: str | None):
    print("Authorization header received:", repr(authorization))
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth")
    token = authorization.split(" ", 1)[1]
    print("Token from header:", repr(token))
    print("Token from env:", repr(API_TOKEN))
    if token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------- Endpoints ----------
@app.post("/api/intake/newsletter")
def intake_newsletter(
    payload: NewsletterPayload,
    authorization: str | None = Header(default=None),
):
    check_auth(authorization)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO newsletter_signups
                    (email, first_name, how_did_you_hear, favorite_music, consent_marketing)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    payload.email,
                    payload.first_name,
                    payload.how_did_you_hear,
                    payload.favorite_music,
                    payload.consent_marketing or False,
                ),
            )

    return {"ok": True}


@app.post("/api/intake/band-application")
def intake_band_application(
    payload: BandApplicationPayload,
    authorization: str | None = Header(default=None),
):
    check_auth(authorization)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO band_applications (
                    contact_name, contact_email, contact_role,
                    band_name, band_genre, band_city, band_country,
                    band_instagram, band_website, band_spotify,
                    about_band, why_interested, preferred_months
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    payload.contact_name,
                    payload.contact_email,
                    payload.contact_role,
                    payload.band_name,
                    payload.band_genre,
                    payload.band_city,
                    payload.band_instagram,
                    payload.band_website,
                    payload.band_spotify,
                    payload.about_band,
                ),
            )

    return {"ok": True}
