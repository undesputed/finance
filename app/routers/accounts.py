from fastapi import APIRouter, HTTPException, Depends, Query
from app.models import Account
from app.database import create_mysql_connection
from typing import List, Optional
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Accounts ---

@router.post("/", response_model=int)
def create_account(account: Account, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO accounts (name, type, balance, currency, user_id) VALUES (%s, %s, %s, %s, %s)",
            (account.name, account.type, account.balance, account.currency, user["id"])
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[Account])
def get_accounts(
    user=Depends(get_current_user),
    type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = "SELECT * FROM accounts WHERE user_id = %s"
        params = [user["id"]]
        if type:
            query += " AND type = %s"
            params.append(type)
        if search:
            query += " AND (name LIKE %s OR type LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [Account(**row) for row in rows]

@router.get("/{account_id}", response_model=Account)
def get_account(account_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM accounts WHERE id=%s AND user_id=%s", (account_id, user["id"]))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Account not found")
        return Account(**row)

@router.put("/{account_id}", response_model=bool)
def update_account(account_id: int, account: Account, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM accounts WHERE id=%s AND user_id=%s", (account_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Account not found or not authorized")
        cursor.execute(
            "UPDATE accounts SET name=%s, type=%s, balance=%s, currency=%s WHERE id=%s",
            (account.name, account.type, account.balance, account.currency, account_id)
        )
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{account_id}", response_model=bool)
def delete_account(account_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM accounts WHERE id=%s AND user_id=%s", (account_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Account not found or not authorized")
        cursor.execute("DELETE FROM accounts WHERE id=%s", (account_id,))
        conn.commit()
        return cursor.rowcount > 0

@router.post("/{account_id}/manage-credit-cards-balance", response_model=dict)
def manage_credit_cards_balance(account_id: int, user=Depends(get_current_user)):
    """
    Calculate and update all credit cards' balances for the given account based on income (money in) and transactions (money out).
    Returns updated balances for each credit card.
    """
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        # Ensure ownership
        cursor.execute("SELECT id FROM accounts WHERE id=%s AND user_id=%s", (account_id, user["id"]))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Account not found or not authorized")
        # Calculate money in (sum of income)
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total_in FROM income WHERE account_id=%s", (account_id,))
        total_in = cursor.fetchone()["total_in"]
        # Calculate money out (sum of transactions)
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total_out FROM transactions WHERE account_id=%s", (account_id,))
        total_out = cursor.fetchone()["total_out"]
        # Net balance
        net_change = float(total_in) - float(total_out)
        # Get all credit cards for this account
        cursor.execute("SELECT id, balance FROM credit_cards WHERE account_id=%s", (account_id,))
        cards = cursor.fetchall()
        updated_balances = {}
        for card in cards:
            new_balance = float(card["balance"]) + net_change
            cursor.execute("UPDATE credit_cards SET balance=%s WHERE id=%s", (new_balance, card["id"]))
            updated_balances[card["id"]] = new_balance
        conn.commit()
        return {"updated_balances": updated_balances, "money_in": total_in, "money_out": total_out}
