from fastapi import APIRouter, HTTPException, Depends
from app.models import Notification
from app.database import create_mysql_connection
from typing import List
from datetime import datetime, timedelta
from app.auth import get_current_user

router = APIRouter()

# --- CRUD Logic & Endpoints for Notifications ---

@router.post("/", response_model=int)
def create_notification(notification: Notification, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO notifications (monthly_payment_id, message, notified_at, is_read) VALUES (%s, %s, %s, %s)",
            (notification.monthly_payment_id, notification.message, notification.notified_at or datetime.now(), notification.is_read)
        )
        conn.commit()
        return cursor.lastrowid

@router.get("/", response_model=List[Notification])
def get_notifications(user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM notifications")
        rows = cursor.fetchall()
        return [Notification(**row) for row in rows]

@router.get("/due/", response_model=List[Notification])
def get_due_notifications(days: int = 3, user=Depends(get_current_user)):
    """
    Get notifications for monthly payments due today or within the next X days (default: 3).
    """
    conn = create_mysql_connection()
    with conn.cursor(dictionary=True) as cursor:
        query = '''
            SELECT n.* FROM notifications n
            JOIN monthly_payments mp ON n.monthly_payment_id = mp.id
            WHERE mp.due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
        '''
        cursor.execute(query, (days,))
        rows = cursor.fetchall()
        return [Notification(**row) for row in rows]

@router.put("/{notification_id}", response_model=bool)
def mark_notification_as_read(notification_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE notifications SET is_read=TRUE WHERE id=%s", (notification_id,))
        conn.commit()
        return cursor.rowcount > 0

@router.delete("/{notification_id}", response_model=bool)
def delete_notification(notification_id: int, user=Depends(get_current_user)):
    conn = create_mysql_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM notifications WHERE id=%s", (notification_id,))
        conn.commit()
        return cursor.rowcount > 0
