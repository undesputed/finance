from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Transaction
from app.database import create_mysql_connection
from typing import List, Optional, Dict, Any
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Transactions ---

@router.post("/", response_model=int)
def create_transaction(tx: Transaction, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO transactions (account_id, amount, date, description, category, currency) VALUES (%s, %s, %s, %s, %s, %s)",
            (tx.account_id, tx.amount, tx.date, tx.description, tx.category, tx.currency)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[Transaction])
def get_transactions(
    user=Depends(get_current_user),
    account_id: Optional[int] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = "SELECT t.* FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE a.user_id = %s"
        params = [user["id"]]
        if account_id:
            query += " AND t.account_id = %s"
            params.append(account_id)
        if category:
            query += " AND t.category = %s"
            params.append(category)
        if start_date:
            query += " AND t.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t.date <= %s"
            params.append(end_date)
        if search:
            query += " AND (t.description LIKE %s OR t.category LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY t.date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [Transaction(**row) for row in rows]

@router.get("/{tx_id}", response_model=Transaction)
def get_transaction(tx_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT t.* FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE t.id=%s AND a.user_id=%s
        """, (tx_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return Transaction(**row)

@router.put("/{tx_id}", response_model=bool)
def update_transaction(tx_id: int, tx: Transaction, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        # Ensure ownership
        cursor.execute("SELECT t.id FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE t.id=%s AND a.user_id=%s", (tx_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Transaction not found or not authorized")
        cursor.execute(
            "UPDATE transactions SET account_id=%s, amount=%s, date=%s, description=%s, category=%s, currency=%s WHERE id=%s",
            (tx.account_id, tx.amount, tx.date, tx.description, tx.category, tx.currency, tx_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{tx_id}", response_model=bool)
def delete_transaction(tx_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        # Ensure ownership
        cursor.execute("SELECT t.id FROM transactions t JOIN accounts a ON t.account_id = a.id WHERE t.id=%s AND a.user_id=%s", (tx_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Transaction not found or not authorized")
        cursor.execute("DELETE FROM transactions WHERE id=%s", (tx_id,))
        conn.commit()
        return cursor.rowcount > 0

@router.get("/summary", response_model=List[Dict[str, Any]])
def get_transactions_summary(user=Depends(get_current_user), start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Returns a list of {date, amount} for expenses (negative transactions) grouped by date for the current user.
    """
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = """
            SELECT t.date, SUM(t.amount) as amount
            FROM transactions t
            JOIN accounts a ON t.account_id = a.id
            WHERE a.user_id = %s
        """
        params = [user["id"]]
        if start_date:
            query += " AND t.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND t.date <= %s"
            params.append(end_date)
        query += " GROUP BY t.date ORDER BY t.date ASC"
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        # Ensure amounts are floats
        for row in rows:
            row["amount"] = float(row["amount"])
        return rows
