import os

import psycopg
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv

# Load .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
API_TOKEN = os.getenv("API_TOKEN")

print("API_TOKEN loaded is:", repr(API_TOKEN))

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your .env file.")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN is not set. Check your .env file.")

app = FastAPI()


# ---------- DB helper ----------
def get_conn():
    # autocommit=True so we don't have to manually commit after inserts
    return psycopg.connect(DATABASE_URL, autocommit=True)


# ---------- (Optional) Model for reference only ----------
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
    payload: dict,
    authorization: str | None = Header(default=None),
):
    """
    Accepts the JSON body Fluent Forms sends for the newsletter form and
    normalizes it into:
      - email
      - first_name
      - how_did_you_hear
      - favorite_music
      - consent_marketing (bool)
    Then inserts into newsletter_signups.
    """
    check_auth(authorization)

    # Fluent sends both top-level fields and nested __submission.user_inputs
    submission = payload.get("__submission", {}) or {}
    user_inputs = submission.get("user_inputs", {}) or {}

    # Email can be in several places; prefer user_inputs.customer_email
    email = (
        user_inputs.get("customer_email")
        or payload.get("customer_email")
        or payload.get("email")
    )
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    # First name, how_did_you_hear, favorite_music – prefer user_inputs
    first_name = (
        user_inputs.get("first_name")
        or payload.get("first_name")
    )

    how_did_you_hear = (
        user_inputs.get("how_did_you_hear")
        or payload.get("how_did_you_hear")
    )

    favorite_music = (
        user_inputs.get("favorite_music")
        or payload.get("favorite_music")
    )

    # consent_marketing might be string, list, or missing
    consent_raw = (
        user_inputs.get("consent_marketing")
        or payload.get("consent_marketing")
    )
    consent = False
    if consent_raw is not None:
        # If it's a list like ["I agree..."], take the first element
        if isinstance(consent_raw, list) and consent_raw:
            text = str(consent_raw[0]).strip().lower()
        else:
            text = str(consent_raw).strip().lower()
        # Treat any non-empty, non-false-ish text as True
        consent = text not in ("", "0", "false", "no", "off")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO newsletter_signups
                    (email, first_name, how_did_you_hear, favorite_music, consent_marketing)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    email,
                    first_name,
                    how_did_you_hear,
                    favorite_music,
                    consent,
                ),
            )

    return {"ok": True}


@app.post("/api/intake/band-application")
def intake_band_application(
    payload: dict,
    authorization: str | None = Header(default=None),
):
    check_auth(authorization)

    submission = payload.get("__submission", {}) or {}
    user_inputs = submission.get("user_inputs", {}) or {}

    contact_name = user_inputs.get("contact_name") or payload.get("contact_name")
    contact_email = user_inputs.get("contact_email") or payload.get("contact_email")
    contact_role = user_inputs.get("contact_role") or payload.get("contact_role")

    band_name = user_inputs.get("band_name") or payload.get("band_name")
    band_genre = user_inputs.get("band_genre") or payload.get("band_genre")
    band_city = user_inputs.get("band_city") or payload.get("band_city")
    band_instagram = user_inputs.get("band_instagram") or payload.get("band_instagram")

    band_url = user_inputs.get("band_url") or payload.get("band_url")
    band_streaming = user_inputs.get("band_streaming") or payload.get("band_streaming")

    about_band = user_inputs.get("about_band") or payload.get("about_band")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO band_applications (
                    contact_name, contact_email, contact_role,
                    band_name, band_genre, band_city,
                    band_instagram, band_url, band_streaming,
                    about_band
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    contact_name,
                    contact_email,
                    contact_role,
                    band_name,
                    band_genre,
                    band_city,
                    band_instagram,
                    band_url,
                    band_streaming,
                    about_band,
                ),
            )

    return {"ok": True}
