from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Income
from app.database import create_mysql_connection
from typing import List, Optional
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Income ---

@router.post("/", response_model=int)
def create_income(income: Income, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO income (account_id, amount, date, source) VALUES (%s, %s, %s, %s)",
            (income.account_id, income.amount, income.date, income.source)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[Income])
def get_incomes(
    user=Depends(get_current_user),
    account_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = "SELECT i.* FROM income i JOIN accounts a ON i.account_id = a.id WHERE a.user_id = %s"
        params = [user["id"]]
        if account_id:
            query += " AND i.account_id = %s"
            params.append(account_id)
        if start_date:
            query += " AND i.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND i.date <= %s"
            params.append(end_date)
        if source:
            query += " AND i.source = %s"
            params.append(source)
        if search:
            query += " AND (i.source LIKE %s)"
            params.append(f"%{search}%")
        query += " ORDER BY i.date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [Income(**row) for row in rows]

@router.get("/{income_id}", response_model=Income)
def get_income(income_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT i.* FROM income i
            JOIN accounts a ON i.account_id = a.id
            WHERE i.id=%s AND a.user_id=%s
        """, (income_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Income not found")
        return Income(**row)

@router.put("/{income_id}", response_model=bool)
def update_income(income_id: int, income: Income, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT i.id FROM income i JOIN accounts a ON i.account_id = a.id WHERE i.id=%s AND a.user_id=%s", (income_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Income not found or not authorized")
        cursor.execute(
            "UPDATE income SET account_id=%s, amount=%s, date=%s, source=%s WHERE id=%s",
            (income.account_id, income.amount, income.date, income.source, income_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{income_id}", response_model=bool)
def delete_income(income_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT i.id FROM income i JOIN accounts a ON i.account_id = a.id WHERE i.id=%s AND a.user_id=%s", (income_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Income not found or not authorized")
        cursor.execute("DELETE FROM income WHERE id=%s", (income_id,))
        conn.commit()
        return cursor.rowcount > 0
