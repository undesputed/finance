from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Installment
from app.database import create_mysql_connection
from typing import List, Optional
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Installments ---

@router.post("/", response_model=int)
def create_installment(inst: Installment, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO installments (account_id, total_amount, installment_amount, start_date, end_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (inst.account_id, inst.total_amount, inst.installment_amount, inst.start_date, inst.end_date, inst.description)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[Installment])
def get_installments(
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
        query = "SELECT i.* FROM installments i JOIN accounts a ON i.account_id = a.id WHERE a.user_id = %s"
        params = [user["id"]]
        if account_id:
            query += " AND i.account_id = %s"
            params.append(account_id)
        if start_date:
            query += " AND i.start_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND i.end_date <= %s"
            params.append(end_date)
        if search:
            query += " AND (i.description LIKE %s)"
            params.append(f"%{search}%")
        query += " ORDER BY i.start_date DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [Installment(**row) for row in rows]

@router.get("/{inst_id}", response_model=Installment)
def get_installment(inst_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT i.* FROM installments i
            JOIN accounts a ON i.account_id = a.id
            WHERE i.id=%s AND a.user_id=%s
        """, (inst_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Installment not found")
        return Installment(**row)

@router.put("/{inst_id}", response_model=bool)
def update_installment(inst_id: int, inst: Installment, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT i.id FROM installments i JOIN accounts a ON i.account_id = a.id WHERE i.id=%s AND a.user_id=%s", (inst_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Installment not found or not authorized")
        cursor.execute(
            "UPDATE installments SET account_id=%s, total_amount=%s, installment_amount=%s, start_date=%s, end_date=%s, description=%s WHERE id=%s",
            (inst.account_id, inst.total_amount, inst.installment_amount, inst.start_date, inst.end_date, inst.description, inst_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{inst_id}", response_model=bool)
def delete_installment(inst_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT i.id FROM installments i JOIN accounts a ON i.account_id = a.id WHERE i.id=%s AND a.user_id=%s", (inst_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Installment not found or not authorized")
        cursor.execute("DELETE FROM installments WHERE id=%s", (inst_id,))
        conn.commit()
        return cursor.rowcount > 0
