# main.py
from fastapi import FastAPI
from dotenv import load_dotenv
import os
import api
import web

load_dotenv()

# Fail fast check
if not os.getenv("SECRET_KEY"):
    raise ValueError("FATAL ERROR: SECRET_KEY is missing. Check your .env file.")

app = FastAPI(title="CreditPassport Trust Engine")

# Register our clean architecture routes!
app.include_router(api.router, prefix="/api")
app.include_router(web.router)