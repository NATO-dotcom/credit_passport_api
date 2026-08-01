# 🏦 CreditPassport Trust Engine API

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=flat&logo=JSON%20web%20tokens)

> A backend engine that analyzes financial transactions to generate, cryptographically sign, and serve verifiable "Credit Passports" (trust scores).

## 📖 Overview

The **CreditPassport Trust Engine** is a FastAPI-based backend application designed to ingest financial transaction histories and calculate a robust "Trust Score" (Credit Passport). This score evaluates a user's financial consistency, savings behavior, and investment patterns.

Once calculated, the API cryptographically signs the score using JSON Web Tokens (JWT), stores it securely in a PostgreSQL database (e.g., Neon), and provides a public verification web page.

## ✨ Key Features

- **Transaction Analysis Algorithm**: Automatically calculates actionable financial metrics:
  - **Savings Ratio**: Percentage of saved capital compared to total inflows.
  - **Consistency**: Analyzes the regularity of inflows using statistical variance.
  - **Investment Multiplier**: Identifies investment-related outflows (e.g., M-Shwari, Unit Trusts, Insurance).
- **Cryptographic Signatures**: Secures the computed score using JWTs to prevent tampering.
- **Verifiable Web Passports**: Provides a publicly accessible HTML endpoint built with Tailwind CSS to view and verify the validity of a Credit Passport.
- **Database Integration**: Persists generated JWT signatures in a PostgreSQL database for verification lookups.

## 📁 Project Structure

```text
credit_passport_api/
├── .env                # Environment variables (not tracked in git)
├── .gitignore          # Git ignore file
├── main.py             # FastAPI application entry point
├── api.py              # REST API routes for processing transactions
├── web.py              # Web routes for serving HTML verification pages
├── db.py               # PostgreSQL database connection logic
└── requirements.txt    # Python dependencies
```

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database (e.g., Neon serverless Postgres)

### 2. Installation
Clone the repository and install the dependencies:

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add the following keys:

```env
SECRET_KEY="your-super-secret-jwt-signing-key"
ALGORITHM="HS256"
DATABASE_URL="postgres://user:password@hostname.neon.tech/dbname"
```
*Note: The application will fail to start if `SECRET_KEY` or `DATABASE_URL` are missing.*

### 4. Database Setup
Ensure you have a PostgreSQL table named `verified_passports` created in your database:

```sql
CREATE TABLE verified_passports (
    verification_id VARCHAR(50) PRIMARY KEY,
    jwt_signature TEXT NOT NULL
);
```

### 5. Running the API
Start the FastAPI server locally using Uvicorn:

```bash
uvicorn main:app --reload
```
*The API will be available at `http://127.0.0.1:8000`.*

---

## 📡 API Reference

### 1. Generate & Sign Transactions
Analyzes a list of transactions, computes the trust score, saves the JWT to the DB, and returns a verified passport.

```http
POST /api/v1/sign-transactions
```

**Request Body (JSON):**
```json
[
  {
    "id": "tx-001",
    "date": "2023-10-01T12:00:00Z",
    "description": "Salary Deposit",
    "amount": 5000.0,
    "is_inflow": true
  },
  {
    "id": "tx-002",
    "date": "2023-10-05T12:00:00Z",
    "description": "Transfer to M-Shwari",
    "amount": 500.0,
    "is_inflow": false
  }
]
```

**Response (JSON):**
```json
{
  "status": "success",
  "verification_id": "CP-A1B2C3D4",
  "transaction_count": 2,
  "overall_score": 75.5,
  "consistency": 100.0,
  "savings_ratio": 90.0,
  "investment_multiplier": 11.1,
  "cryptographic_signature": "eyJhbGciOiJIUzI1NiIsInR...",
  "verify_url": "https://credit-passport-api-1.onrender.com/check/CP-A1B2C3D4"
}
```

### 2. Verify Passport (Web Interface)
Retrieves the stored JWT from the database, decodes it, and serves a beautifully styled Tailwind HTML page displaying the verified passport.

```http
GET /check/{verification_id}
```

## 📜 Interactive API Docs
FastAPI automatically generates interactive documentation. Once the server is running, visit:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
