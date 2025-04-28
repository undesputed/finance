from app.database import create_mysql_connection
from app.models import Account, CreditCard, Income, Transaction, MonthlyPayment, Installment
from typing import List, Optional

# --- ACCOUNTS CRUD ---
def create_account(account: Account) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO accounts (name, type, balance) VALUES (%s, %s, %s)",
            (account.name, account.type, account.balance)
        )
        conn.commit()
        return cursor.lastrowid

def get_account(account_id: int) -> Optional[Account]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM accounts WHERE id=%s", (account_id,))
        row = cursor.fetchone()
        return Account(**row) if row else None

def get_accounts() -> List[Account]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM accounts")
        rows = cursor.fetchall()
        return [Account(**row) for row in rows]

def update_account(account_id: int, account: Account) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE accounts SET name=%s, type=%s, balance=%s WHERE id=%s",
            (account.name, account.type, account.balance, account_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_account(account_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM accounts WHERE id=%s", (account_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- CREDIT CARDS CRUD ---
def create_credit_card(card: CreditCard) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO credit_cards (account_id, card_number, limit_amount, balance, due_date) VALUES (%s, %s, %s, %s, %s)",
            (card.account_id, card.card_number, card.limit_amount, card.balance, card.due_date)
        )
        conn.commit()
        return cursor.lastrowid

def get_credit_card(card_id: int) -> Optional[CreditCard]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM credit_cards WHERE id=%s", (card_id,))
        row = cursor.fetchone()
        return CreditCard(**row) if row else None

def get_credit_cards() -> List[CreditCard]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM credit_cards")
        rows = cursor.fetchall()
        return [CreditCard(**row) for row in rows]

def update_credit_card(card_id: int, card: CreditCard) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE credit_cards SET account_id=%s, card_number=%s, limit_amount=%s, balance=%s, due_date=%s WHERE id=%s",
            (card.account_id, card.card_number, card.limit_amount, card.balance, card.due_date, card_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_credit_card(card_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM credit_cards WHERE id=%s", (card_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- INCOME CRUD ---
def create_income(income: Income) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO income (account_id, amount, date, source) VALUES (%s, %s, %s, %s)",
            (income.account_id, income.amount, income.date, income.source)
        )
        conn.commit()
        return cursor.lastrowid

def get_income(income_id: int) -> Optional[Income]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM income WHERE id=%s", (income_id,))
        row = cursor.fetchone()
        return Income(**row) if row else None

def get_incomes() -> List[Income]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM income")
        rows = cursor.fetchall()
        return [Income(**row) for row in rows]

def update_income(income_id: int, income: Income) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE income SET account_id=%s, amount=%s, date=%s, source=%s WHERE id=%s",
            (income.account_id, income.amount, income.date, income.source, income_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_income(income_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM income WHERE id=%s", (income_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- TRANSACTIONS CRUD ---
def create_transaction(tx: Transaction) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO transactions (account_id, amount, date, description, category) VALUES (%s, %s, %s, %s, %s)",
            (tx.account_id, tx.amount, tx.date, tx.description, tx.category)
        )
        conn.commit()
        return cursor.lastrowid

def get_transaction(tx_id: int) -> Optional[Transaction]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM transactions WHERE id=%s", (tx_id,))
        row = cursor.fetchone()
        return Transaction(**row) if row else None

def get_transactions() -> List[Transaction]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        return [Transaction(**row) for row in rows]

def update_transaction(tx_id: int, tx: Transaction) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE transactions SET account_id=%s, amount=%s, date=%s, description=%s, category=%s WHERE id=%s",
            (tx.account_id, tx.amount, tx.date, tx.description, tx.category, tx_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_transaction(tx_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM transactions WHERE id=%s", (tx_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- MONTHLY PAYMENTS CRUD ---
def create_monthly_payment(mp: MonthlyPayment) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO monthly_payments (account_id, amount, due_date, description) VALUES (%s, %s, %s, %s)",
            (mp.account_id, mp.amount, mp.due_date, mp.description)
        )
        conn.commit()
        return cursor.lastrowid

def get_monthly_payment(mp_id: int) -> Optional[MonthlyPayment]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM monthly_payments WHERE id=%s", (mp_id,))
        row = cursor.fetchone()
        return MonthlyPayment(**row) if row else None

def get_monthly_payments() -> List[MonthlyPayment]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM monthly_payments")
        rows = cursor.fetchall()
        return [MonthlyPayment(**row) for row in rows]

def update_monthly_payment(mp_id: int, mp: MonthlyPayment) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE monthly_payments SET account_id=%s, amount=%s, due_date=%s, description=%s WHERE id=%s",
            (mp.account_id, mp.amount, mp.due_date, mp.description, mp_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_monthly_payment(mp_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM monthly_payments WHERE id=%s", (mp_id,))
        conn.commit()
        return cursor.rowcount > 0

# --- INSTALLMENTS CRUD ---
def create_installment(inst: Installment) -> int:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO installments (account_id, total_amount, installment_amount, start_date, end_date, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (inst.account_id, inst.total_amount, inst.installment_amount, inst.start_date, inst.end_date, inst.description)
        )
        conn.commit()
        return cursor.lastrowid

def get_installment(inst_id: int) -> Optional[Installment]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM installments WHERE id=%s", (inst_id,))
        row = cursor.fetchone()
        return Installment(**row) if row else None

def get_installments() -> List[Installment]:
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM installments")
        rows = cursor.fetchall()
        return [Installment(**row) for row in rows]

def update_installment(inst_id: int, inst: Installment) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE installments SET account_id=%s, total_amount=%s, installment_amount=%s, start_date=%s, end_date=%s, description=%s WHERE id=%s",
            (inst.account_id, inst.total_amount, inst.installment_amount, inst.start_date, inst.end_date, inst.description, inst_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_installment(inst_id: int) -> bool:
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM installments WHERE id=%s", (inst_id,))
        conn.commit()
        return cursor.rowcount > 0
