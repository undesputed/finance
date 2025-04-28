from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import CreditCard
from app.database import create_mysql_connection
from typing import List, Optional
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Credit Cards ---

@router.post("/", response_model=int)
def create_credit_card(card: CreditCard, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO credit_cards (account_id, card_number, limit_amount, balance, due_date) VALUES (%s, %s, %s, %s, %s)",
            (card.account_id, card.card_number, card.limit_amount, card.balance, card.due_date)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[CreditCard])
def get_credit_cards(
    user=Depends(get_current_user),
    account_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None
):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = "SELECT c.* FROM credit_cards c JOIN accounts a ON c.account_id = a.id WHERE a.user_id = %s"
        params = [user["id"]]
        if account_id:
            query += " AND c.account_id = %s"
            params.append(account_id)
        if search:
            query += " AND (c.card_number LIKE %s)"
            params.append(f"%{search}%")
        query += " ORDER BY c.id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [CreditCard(**row) for row in rows]

@router.get("/{card_id}", response_model=CreditCard)
def get_credit_card(card_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT c.* FROM credit_cards c
            JOIN accounts a ON c.account_id = a.id
            WHERE c.id=%s AND a.user_id=%s
        """, (card_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Credit card not found")
        return CreditCard(**row)

@router.put("/{card_id}", response_model=bool)
def update_credit_card(card_id: int, card: CreditCard, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT c.id FROM credit_cards c JOIN accounts a ON c.account_id = a.id WHERE c.id=%s AND a.user_id=%s", (card_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Credit card not found or not authorized")
        cursor.execute(
            "UPDATE credit_cards SET account_id=%s, card_number=%s, limit_amount=%s, balance=%s, due_date=%s WHERE id=%s",
            (card.account_id, card.card_number, card.limit_amount, card.balance, card.due_date, card_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{card_id}", response_model=bool)
def delete_credit_card(card_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT c.id FROM credit_cards c JOIN accounts a ON c.account_id = a.id WHERE c.id=%s AND a.user_id=%s", (card_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Credit card not found or not authorized")
        cursor.execute("DELETE FROM credit_cards WHERE id=%s", (card_id,))
        conn.commit()
        return cursor.rowcount > 0
