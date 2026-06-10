from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv


# Load the environment variables from the .env file
load_dotenv()

app = FastAPI(title="CreditPassport Trust Engine")

# Safely pull the variables from the environment
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Fail fast: If the server boots up without a key, crash immediately to protect the app
if not SECRET_KEY:
    raise ValueError("FATAL ERROR: SECRET_KEY is missing. Check your .env file.")

# This defines the exact data structure we expect from your Flutter app
class ScorePayload(BaseModel):
    overall_score: float
    consistency: float
    savings_ratio: float
    investment_multiplier: float
    transaction_count: int

@app.post("/api/v1/sign-score")
async def sign_score(payload: ScorePayload):
    try:
        # 1. Generate a unique, professional-looking Verification ID
        verification_id = f"CP-{str(uuid.uuid4())[:8].upper()}"
        
        # 2. Package the score data with issuance and expiration timestamps
        to_encode = payload.dict()
        to_encode.update({
            "verification_id": verification_id,
            "iss": "CreditPassport_Trust_Engine",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=90) # Passport valid for 90 days
        })
        
        # 3. Cryptographically sign the data payload
        signature = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # 4. Generate the URL a landlord would scan to verify the document
        verify_url = f"https://verify.creditpassport.app/check/{verification_id}"
        
        return {
            "status": "success",
            "verification_id": verification_id,
            "cryptographic_signature": signature,
            "verify_url": verify_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cryptographic signing failed: {str(e)}")