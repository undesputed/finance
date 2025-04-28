from pydantic import BaseModel
from typing import Optional, List

class Account(BaseModel):
    id: Optional[int]
    name: str
    type: Optional[str]
    balance: Optional[float] = 0.0
    currency: Optional[str] = 'USD'

class CreditCard(BaseModel):
    id: Optional[int]
    account_id: Optional[int]
    card_number: Optional[str]
    limit_amount: Optional[float]
    balance: Optional[float] = 0.0
    due_date: Optional[str]

class Income(BaseModel):
    id: Optional[int]
    account_id: Optional[int]
    amount: float
    date: str
    source: Optional[str]

class Transaction(BaseModel):
    id: Optional[int]
    account_id: int
    amount: float
    date: str
    description: Optional[str]
    category: Optional[str]
    currency: Optional[str] = 'USD'

class MonthlyPayment(BaseModel):
    id: Optional[int]
    account_id: Optional[int]
    amount: float
    due_date: Optional[str]
    description: Optional[str]

class Installment(BaseModel):
    id: Optional[int]
    account_id: Optional[int]
    total_amount: float
    installment_amount: float
    start_date: Optional[str]
    end_date: Optional[str]
    description: Optional[str]

class Notification(BaseModel):
    id: Optional[int]
    monthly_payment_id: int
    message: str
    notified_at: Optional[str]
    is_read: Optional[bool] = False

class User(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password_hash: Optional[str]
    created_at: Optional[str]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Budget(BaseModel):
    id: Optional[int]
    user_id: int
    account_id: Optional[int]
    category: Optional[str]
    amount: float
    period: str = 'monthly'
    currency: str = 'USD'
    created_at: Optional[str]

class Attachment(BaseModel):
    id: Optional[int]
    user_id: int
    transaction_id: int
    file_name: str
    file_path: str
    uploaded_at: Optional[str]