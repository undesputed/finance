# Finance Notification System

A FastAPI-based backend for managing accounts, credit cards, transactions, income, monthly payments, and notifications, with JWT authentication. Supports both web and mobile clients.

---

## Features
- User registration and login (JWT authentication)
- CRUD for accounts, credit cards, transactions, income, monthly payments, installments
- Notification system for monthly payments
- All endpoints (except login/register) require authentication
- MySQL database support

---

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd finance/server
```

### 2. Create & Activate a Virtual Environment (Optional but Recommended)
```
python -m venv env
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Edit the `.env` file with your MySQL credentials and JWT settings:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=your_database_name
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 5. Ensure MySQL is Running and Database Exists
- Start your MySQL server.
- Create the database if it does not exist:
```
mysql -u your_mysql_user -p
CREATE DATABASE your_database_name;
```

### 6. Run the FastAPI Server
```
uvicorn app.main:app --reload
```
- The API will be available at: [http://localhost:8000](http://localhost:8000)
- Interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Usage (API)
- Register a user: `POST /login/register`
- Login to get JWT: `POST /login/token`
- Use JWT as `Authorization: Bearer <token>` header for all other endpoints

---

## Notes
- All sensitive values are managed in `.env` (do **not** commit this file to public repositories)
- Passwords are securely hashed
- Suitable for both web and mobile apps

---

## License
MIT (or specify your license)
