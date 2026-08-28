import sqlite3
from flask import g
import os

# Use /tmp on Vercel or read-only serverless filesystems
if os.environ.get('VERCEL') or not os.access(os.path.dirname(os.path.abspath(__file__)), os.W_OK):
    DATABASE = '/tmp/express.db'
else:
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'express.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        if not os.path.exists(DATABASE):
            init_db()
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        
        # users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                phone TEXT UNIQUE,
                name TEXT,
                dob TEXT,
                age INTEGER,
                aadhaar_verified BOOLEAN DEFAULT 0,
                pan_verified BOOLEAN DEFAULT 0,
                aadhaar_number TEXT,
                pan_number TEXT,
                income_type TEXT,
                monthly_income INTEGER,
                otp TEXT,
                otp_expires REAL,
                session_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Lightweight migrations for databases created by earlier versions.
        existing_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)")}
        if 'statement_name' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN statement_name TEXT')
        if 'terms_accepted_at' not in existing_columns:
            cursor.execute('ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMP')
        
        # cards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                card_type TEXT,
                color TEXT,
                status TEXT DEFAULT 'processing',
                credit_limit INTEGER DEFAULT 25000,
                available_limit INTEGER DEFAULT 25000,
                order_date TEXT,
                delivery_date TEXT,
                card_number TEXT,
                on_time_payments INTEGER DEFAULT 0,
                limit_increases INTEGER DEFAULT 0
            )
        ''')
        
        # transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                merchant TEXT,
                category TEXT,
                date TEXT,
                is_emi BOOLEAN DEFAULT 0,
                emi_months INTEGER,
                emi_rate REAL,
                emi_paid INTEGER DEFAULT 0
            )
        ''')
        
        # payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                amount REAL,
                due_date TEXT,
                paid_date TEXT,
                on_time BOOLEAN
            )
        ''')
        
        # addresses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS addresses (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                line1 TEXT,
                line2 TEXT,
                apartment TEXT,
                pincode TEXT,
                city TEXT,
                state TEXT,
                country TEXT DEFAULT 'India'
            )
        ''')
        
        # Ensure default demo user exists
        user_count = cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        if user_count == 0:
            cursor.execute('''
                INSERT INTO users (phone, name, dob, age, session_token, aadhaar_verified, pan_verified)
                VALUES ('9876543210', 'Express Member', '1998-05-15', 28, 'demo-session-token-express', 0, 0)
            ''')

        db.commit()

def get_user_by_phone(phone):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()

def get_user_by_id(user_id):
    db = get_db()
    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

def get_user_card(user_id):
    db = get_db()
    return db.execute('SELECT * FROM cards WHERE user_id = ?', (user_id,)).fetchone()

def get_user_address(user_id):
    db = get_db()
    return db.execute('SELECT * FROM addresses WHERE user_id = ?', (user_id,)).fetchone()

def get_user_transactions(user_id):
    db = get_db()
    txns = db.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    if not txns:
        # Seed realistic transaction history for this user
        sample_txns = [
            (user_id, 840.0, 'Starbucks Reserve Mumbai', 'Dining', 'Today, 2:15 PM', 0, None, None, 0),
            (user_id, 4650.0, 'Taj Mahal Palace Fine Dining', 'Dining', 'Yesterday, 8:40 PM', 0, None, None, 0),
            (user_id, 24999.0, 'Apple Store BKC', 'Electronics', 'Aug 24, 2026', 1, 6, 0.99, 2),
            (user_id, 12450.0, 'Vistara Airlines Flight', 'Travel', 'Aug 18, 2026', 0, None, None, 0),
            (user_id, 3200.0, 'Marriott Executive Lounge', 'Hospitality', 'Aug 12, 2026', 0, None, None, 0),
            (user_id, 2890.0, 'Amazon India Retail', 'Shopping', 'Aug 08, 2026', 0, None, None, 0),
            (user_id, 4200.0, 'Shell Fuel Station BKC', 'Fuel', 'Aug 02, 2026', 0, None, None, 0),
            (user_id, 1850.0, 'Zomato Gold Delivery', 'Dining', 'Jul 28, 2026', 0, None, None, 0),
            (user_id, 18500.0, 'The Oberoi Mumbai Weekend Stay', 'Travel', 'Jul 22, 2026', 1, 12, 0.99, 4)
        ]
        db.executemany('''
            INSERT INTO transactions (user_id, amount, merchant, category, date, is_emi, emi_months, emi_rate, emi_paid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_txns)
        db.commit()
        txns = db.execute('SELECT * FROM transactions WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    return txns

def get_user_payments(user_id):
    db = get_db()
    payments = db.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    if not payments:
        sample_payments = [
            (user_id, 4410.0, 'Sep 01, 2026', None, 1),
            (user_id, 1695.0, 'Sep 01, 2026', None, 1),
            (user_id, 1499.0, 'Aug 28, 2026', 'Aug 28, 2026', 1)
        ]
        db.executemany('''
            INSERT INTO payments (user_id, amount, due_date, paid_date, on_time)
            VALUES (?, ?, ?, ?, ?)
        ''', sample_payments)
        db.commit()
        payments = db.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY id DESC', (user_id,)).fetchall()
    return payments
