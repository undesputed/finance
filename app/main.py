from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import accounts, credit_cards, income, transactions, monthly_payments, installments, notifications, login
from app.database import initialize_schema

app = FastAPI(
    title="Finance Notification System API",
    description="A robust API for managing accounts, credit cards, transactions, budgets, notifications, and more. Includes JWT authentication and is ready for web/mobile integration.",
    version="1.0.0",
    contact={
        "name": "Finance App Team",
        "email": "support@yourdomain.com"
    }
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize schema at startup (optional, can be commented out after first run)
@app.on_event("startup")
def on_startup():
    initialize_schema()

# API versioning
app.include_router(accounts.router, prefix="/v1/accounts", tags=["Accounts"])
app.include_router(credit_cards.router, prefix="/v1/credit-cards", tags=["Credit Cards"])
app.include_router(income.router, prefix="/v1/income", tags=["Income"])
app.include_router(transactions.router, prefix="/v1/transactions", tags=["Transactions"])
app.include_router(monthly_payments.router, prefix="/v1/monthly-payments", tags=["Monthly Payments"])
app.include_router(installments.router, prefix="/v1/installments", tags=["Installments"])
app.include_router(notifications.router, prefix="/v1/notifications", tags=["Notifications"])
app.include_router(login.router, prefix="/v1/login", tags=["Login"])