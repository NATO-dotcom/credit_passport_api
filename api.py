# api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime, timedelta, timezone
import os
from typing import List
import statistics
from db import passport_db

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class Transaction(BaseModel):
    id: str
    date: datetime
    description: str
    amount: float
    is_inflow: bool

class SignedScoreResponse(BaseModel):
    status: str
    verification_id: str
    transaction_count: int
    overall_score: float
    consistency: float
    savings_ratio: float
    investment_multiplier: float
    cryptographic_signature: str
    verify_url: str

def calculate_trust_scores(transactions: List[Transaction]):
    inflows = [t for t in transactions if t.is_inflow]
    outflows = [t for t in transactions if not t.is_inflow]

    total_in = sum(t.amount for t in inflows)
    total_out = sum(t.amount for t in outflows)
    saved_capital = total_in - total_out

    savings_ratio = 0.0
    if total_in > 0 and saved_capital > 0:
        savings_ratio = (saved_capital / total_in) * 100.0

    consistency = 0.0
    if len(inflows) > 2:
        inflows.sort(key=lambda x: x.date)
        gaps = [(inflows[i].date - inflows[i-1].date).days for i in range(1, len(inflows))]
        variance = statistics.stdev(gaps)
        consistency = max(0.0, 100.0 - (variance * 3.0))
    elif len(inflows) in [1, 2]:
        consistency = 50.0 

    investment_keywords = ["m-shwari", "kcb mobi", "cba", "unit trust", "insurance", "saving"]
    invested_amount = 0.0
    for t in outflows:
        if any(keyword in t.description.lower() for keyword in investment_keywords):
            invested_amount += t.amount

    investment_multiplier = 0.0
    if saved_capital > 0:
        investment_multiplier = min(100.0, (invested_amount / saved_capital) * 100.0)

    overall_score = (consistency + savings_ratio + investment_multiplier) / 3

    return {
        "overall_score": round(overall_score, 1),
        "consistency": round(consistency, 1),
        "savings_ratio": round(savings_ratio, 1),
        "investment_multiplier": round(investment_multiplier, 1)
    }

@router.post("/v1/sign-transactions", response_model=SignedScoreResponse)
async def sign_transactions(transactions: List[Transaction]):
    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions provided")

    try:
        verification_id = f"CP-{str(uuid.uuid4())[:8].upper()}"
        scores = calculate_trust_scores(transactions)
        
        to_encode = scores.copy()
        to_encode.update({
            "verification_id": verification_id,
            "transaction_count": len(transactions),
            "iss": "CreditPassport_Trust_Engine",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(days=90)
        })
        
        signature = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        # Save to our central db file
        passport_db[verification_id] = signature
        
        # Update this to your active Fedora IP!
        local_ip = "192.168.122.84" 
        verify_url = f"http://{local_ip}:8000/check/{verification_id}"
        
        return SignedScoreResponse(
            status="success",
            verification_id=verification_id,
            transaction_count=len(transactions),
            overall_score=scores["overall_score"],
            consistency=scores["consistency"],
            savings_ratio=scores["savings_ratio"],
            investment_multiplier=scores["investment_multiplier"],
            cryptographic_signature=signature,
            verify_url=verify_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")