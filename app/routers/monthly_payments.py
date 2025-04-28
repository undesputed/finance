from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import MonthlyPayment
from app.database import create_mysql_connection
from typing import List, Optional
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Monthly Payments ---

@router.post("/", response_model=int)
def create_monthly_payment(mp: MonthlyPayment, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO monthly_payments (account_id, amount, due_date, description) VALUES (%s, %s, %s, %s)",
            (mp.account_id, mp.amount, mp.due_date, mp.description)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[MonthlyPayment])
def get_monthly_payments(
    user=Depends(get_current_user),
    account_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = "SELECT mp.* FROM monthly_payments mp JOIN accounts a ON mp.account_id = a.id WHERE a.user_id = %s"
        params = [user["id"]]
        if account_id:
            query += " AND mp.account_id = %s"
            params.append(account_id)
        if start_date:
            query += " AND mp.due_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND mp.due_date <= %s"
            params.append(end_date)
        if search:
            query += " AND (mp.description LIKE %s)"
            params.append(f"%{search}%")
        query += " ORDER BY mp.due_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [MonthlyPayment(**row) for row in rows]

@router.get("/{mp_id}", response_model=MonthlyPayment)
def get_monthly_payment(mp_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT mp.* FROM monthly_payments mp
            JOIN accounts a ON mp.account_id = a.id
            WHERE mp.id=%s AND a.user_id=%s
        """, (mp_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Monthly payment not found")
        return MonthlyPayment(**row)

@router.put("/{mp_id}", response_model=bool)
def update_monthly_payment(mp_id: int, mp: MonthlyPayment, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT mp.id FROM monthly_payments mp JOIN accounts a ON mp.account_id = a.id WHERE mp.id=%s AND a.user_id=%s", (mp_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Monthly payment not found or not authorized")
        cursor.execute(
            "UPDATE monthly_payments SET account_id=%s, amount=%s, due_date=%s, description=%s WHERE id=%s",
            (mp.account_id, mp.amount, mp.due_date, mp.description, mp_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{mp_id}", response_model=bool)
def delete_monthly_payment(mp_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT mp.id FROM monthly_payments mp JOIN accounts a ON mp.account_id = a.id WHERE mp.id=%s AND a.user_id=%s", (mp_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Monthly payment not found or not authorized")
        cursor.execute("DELETE FROM monthly_payments WHERE id=%s", (mp_id,))
        conn.commit()
        return cursor.rowcount > 0
