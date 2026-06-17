# web.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import jwt
import os
from db import get_db_connection

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

@router.get("/check/{verification_id}", response_class=HTMLResponse)
async def verify_passport(verification_id: str):
    # Open the vault and search for the ID
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT jwt_signature FROM verified_passports WHERE verification_id = %s", 
        (verification_id,)
    )
    result = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    # If the database returns nothing, the ID is fake or doesn't exist
    if not result:
        return """
        <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: red;">Error: Document Not Found</h1>
            <p>This Credit Passport ID does not exist or has been deleted.</p>
        </body></html>
        """
        
    # If we found it, pull the token out of the SQL result tuple
    token = result[0]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verified Credit Passport</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 flex items-center justify-center min-h-screen p-4">
            <div class="max-w-md w-full bg-white rounded-2xl shadow-xl p-8 border border-gray-200">
                <div class="text-center mb-8">
                    <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-green-100 mb-4 border-4 border-green-50">
                        <svg class="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">Verified Passport</h1>
                    <p class="text-gray-500 mt-2 font-mono bg-gray-50 py-1 px-3 rounded-lg inline-block text-sm border border-gray-200">ID: {payload['verification_id']}</p>
                </div>
                
                <div class="space-y-4">
                    <div class="flex justify-between items-center py-3 border-b border-gray-100">
                        <span class="text-gray-600 font-medium">Overall Trust Score</span>
                        <span class="text-2xl font-bold text-teal-600">{payload['overall_score']}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-100">
                        <span class="text-gray-600">Consistency</span>
                        <span class="font-semibold text-gray-900">{payload['consistency']}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-100">
                        <span class="text-gray-600">Savings Ratio</span>
                        <span class="font-semibold text-gray-900">{payload['savings_ratio']}</span>
                    </div>
                    <div class="flex justify-between items-center py-3 border-b border-gray-100">
                        <span class="text-gray-600">Investment Multiplier</span>
                        <span class="font-semibold text-gray-900">{payload['investment_multiplier']}</span>
                    </div>
                    <div class="flex justify-between items-center py-3">
                        <span class="text-gray-600">Transactions Analyzed</span>
                        <span class="font-semibold text-gray-900">{payload['transaction_count']}</span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
        
    except jwt.ExpiredSignatureError:
        return "<html><body><h1 style='color:red;'>Error: Document Expired</h1></body></html>"
    except jwt.InvalidTokenError:
        return "<html><body><h1 style='color:red;'>Error: Invalid Signature</h1></body></html>"
