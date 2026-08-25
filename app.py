import time
import random
import uuid
import datetime
import os
import re
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response, g
from database import (
    init_db, get_db, get_user_by_phone, get_user_by_id, 
    get_user_card, get_user_address, get_user_transactions, get_user_payments
)

app = Flask(__name__)
# Keep the demo safe to run locally and make the production secret configurable
# before it is deployed. Never use this application to collect live financial data
# without the required security and regulatory controls.
app.secret_key = os.environ.get('EXPRESS_SECRET_KEY', 'local-demo-only-change-me')
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # Statement uploads: 8 MB
DEMO_MODE = os.environ.get('EXPRESS_DEMO_MODE', 'true').lower() == 'true'

# --- Decorators & Middleware ---

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = request.cookies.get('express_session')
        if not session_token:
            return redirect(url_for('login'))
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE session_token = ?', (session_token,)).fetchone()
        if not user:
            return redirect(url_for('login'))
        
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

# --- Page Routes ---

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/waitlist')
def waitlist():
    return render_template('waitlist.html')

@app.route('/logout')
def logout():
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('express_session')
    return response

@app.route('/home')
@login_required
def home():
    user = dict(g.user)
    card = get_user_card(user['id'])
    card_data = dict(card) if card else None
    if card_data:
        card_data['last4'] = (card_data.get('card_number') or '7163')[-4:]
        card_data['card_type'] = (card_data.get('card_type') or 'premium').lower()
        card_data['color'] = (card_data.get('color') or 'gold').lower()
        card_data['spent'] = max(0, (card_data.get('credit_limit') or 0) - (card_data.get('available_limit') or 0))
        card_data['utilisation'] = round((card_data['spent'] / card_data['credit_limit']) * 100) if card_data['credit_limit'] else 0
        card_data['available_percent'] = 100 - card_data['utilisation']
        card_data['min_due'] = round(card_data['spent'] * 0.05)
    return render_template('index.html', user=user, has_card=(card is not None), card=card_data)

@app.route('/apply')
@login_required
def apply():
    return render_template('apply.html', user=dict(g.user))

@app.route('/dashboard')
@login_required
def dashboard():
    user = dict(g.user)
    card = get_user_card(user['id'])
    if not card:
        return redirect(url_for('apply'))
    card_data = dict(card)
    card_data['last4'] = (card_data.get('card_number') or '7163')[-4:]
    card_data['card_type'] = (card_data.get('card_type') or 'premium').lower()
    card_data['color'] = (card_data.get('color') or 'gold').lower()
    card_data['spent'] = max(0, (card_data.get('credit_limit') or 0) - (card_data.get('available_limit') or 0))
    card_data['utilisation'] = round((card_data['spent'] / card_data['credit_limit']) * 100) if card_data['credit_limit'] else 0
    card_data['available_percent'] = 100 - card_data['utilisation']
    card_data['min_due'] = round(card_data['spent'] * 0.05)
    return render_template(
        'dashboard.html', user=user, card=card_data,
        transactions=get_user_transactions(user['id']), payments=get_user_payments(user['id']),
        address=get_user_address(user['id'])
    )

# --- API Routes ---

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json(silent=True) or {}
    phone = re.sub(r'\D', '', data.get('phone', ''))
    if len(phone) != 10:
        return jsonify({'success': False, 'message': 'Phone number required'})
    
    otp = '123456'  # Fixed demo OTP
    expiry = time.time() + 300 # 5 mins
    
    db = get_db()
    user = get_user_by_phone(phone)
    
    if user:
        db.execute('UPDATE users SET otp = ?, otp_expires = ? WHERE phone = ?', (otp, expiry, phone))
    else:
        db.execute('INSERT INTO users (phone, otp, otp_expires) VALUES (?, ?, ?)', (phone, otp, expiry))
    db.commit()
    
    print(f"OTP for {phone}: {otp}")
    response = {'success': True, 'message': 'OTP sent'}
    if DEMO_MODE:
        response['demo_otp'] = otp
    return jsonify(response)

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json(silent=True) or {}
    phone = re.sub(r'\D', '', data.get('phone', ''))
    otp = str(data.get('otp', ''))
    
    user = get_user_by_phone(phone)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    if user['otp'] != otp or time.time() > user['otp_expires']:
        return jsonify({'success': False, 'message': 'Invalid or expired OTP'})
    
    session_token = str(uuid.uuid4())
    db = get_db()
    db.execute('UPDATE users SET session_token = ?, otp = NULL, otp_expires = NULL WHERE phone = ?', 
               (session_token, phone))
    db.commit()
    
    card = get_user_card(user['id'])
    
    resp = make_response(jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'phone': user['phone'],
            'name': user['name'],
            'age': user['age'],
            'terms_accepted': bool(user['terms_accepted_at']),
            'has_card': (card is not None)
        }
    }))
    resp.set_cookie(
        'express_session', session_token, httponly=True, samesite='Lax',
        secure=os.environ.get('FLASK_ENV') == 'production', max_age=60 * 60 * 24 * 30
    )
    return resp

@app.route('/api/check-age', methods=['POST'])
@login_required
def check_age():
    data = request.get_json(silent=True) or {}
    dob = data.get('dob') # YYYY-MM-DD
    
    # Calculate age
    try:
        dob_date = datetime.datetime.strptime(dob, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return jsonify({'success': False, 'message': 'Enter a valid date of birth'}), 400
    if dob_date > datetime.date.today():
        return jsonify({'success': False, 'message': 'Date of birth cannot be in the future'}), 400
    today = datetime.date.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    
    db = get_db()
    db.execute('UPDATE users SET dob = ?, age = ? WHERE id = ?', (dob, age, g.user['id']))
    db.commit()
    
    return jsonify({'success': True, 'age': age, 'eligible': age >= 21})

@app.route('/api/accept-terms', methods=['POST'])
@login_required
def accept_terms():
    db = get_db()
    db.execute('UPDATE users SET terms_accepted_at = CURRENT_TIMESTAMP WHERE id = ?', (g.user['id'],))
    db.commit()
    return jsonify({'success': True, 'redirect': '/home'})

@app.route('/api/verify-aadhaar', methods=['POST'])
@login_required
def verify_aadhaar():
    data = request.get_json(silent=True) or {}
    aadhaar = re.sub(r'\D', '', str(data.get('aadhaar_number', '')))
    if not aadhaar or len(str(aadhaar)) != 12:
        return jsonify({'success': False, 'message': 'Invalid Aadhaar format'})

    time.sleep(0.8) # Deliberate demo processing state
    
    db = get_db()
    # Store only a masked reference in the demo database. A real issuer must
    # use a regulated KYC provider and must not rely on this sample endpoint.
    db.execute("""UPDATE users
                  SET aadhaar_verified = 1, aadhaar_number = ?,
                      name = COALESCE(NULLIF(name, ''), 'Express Member')
                  WHERE id = ?""", (f'XXXXXXXX{aadhaar[-4:]}', g.user['id']))
    db.commit()
    return jsonify({'success': True, 'name': 'Express Member'})

@app.route('/api/verify-pan', methods=['POST'])
@login_required
def verify_pan():
    data = request.get_json(silent=True) or {}
    pan = str(data.get('pan_number', '')).upper().strip()
    if not re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', pan):
        return jsonify({'success': False, 'message': 'Invalid PAN format'})
        
    time.sleep(1.5)
    
    db = get_db()
    db.execute("UPDATE users SET pan_verified = 1, pan_number = ? WHERE id = ?", (f'{pan[:5]}XXXX{pan[-1]}', g.user['id']))
    db.commit()
    
    return jsonify({'success': True})

@app.route('/api/upload-statements', methods=['POST'])
@login_required
def upload_statements():
    data = request.form if request.form else (request.get_json(silent=True) or {})
    statement = request.files.get('statement')
    if statement:
        filename = statement.filename or ''
        extension = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if extension not in {'pdf', 'xls', 'xlsx', 'csv'}:
            return jsonify({'success': False, 'message': 'Upload a PDF, XLS, XLSX or CSV file'}), 400
    elif not data.get('statement_name'):
        return jsonify({'success': False, 'message': 'Please attach a recent statement'}), 400
    income_type = data.get('income_type')
    income_value = re.sub(r'[^0-9]', '', str(data.get('monthly_income', '')))
    if income_type not in {'salaried', 'business'} or not income_value or int(income_value) <= 0:
        return jsonify({'success': False, 'message': 'Select an income type and enter a valid monthly income'}), 400

    db = get_db()
    db.execute("UPDATE users SET income_type = ?, monthly_income = ?, statement_name = ? WHERE id = ?", 
               (income_type, int(income_value),
                statement.filename if statement else data.get('statement_name'), g.user['id']))
    db.commit()
    return jsonify({'success': True, 'approved': True})

@app.route('/api/select-card', methods=['POST'])
@login_required
def select_card():
    data = request.get_json(silent=True) or {}
    card_type = data.get('card_type')
    color = data.get('color')
    allowed_colours = {
        'premium': {'gold', 'rosegold', 'black'},
        'ultra': {'ultra', 'ultrablue'}
    }
    if card_type not in allowed_colours or color not in allowed_colours[card_type]:
        return jsonify({'success': False, 'message': 'Choose a valid card and finish'}), 400
    
    order_date = datetime.date.today().isoformat()
    delivery_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
    card_number = f"xxxx xxxx xxxx {random.randint(1000,9999)}"
    credit_limit = 250000 if card_type == 'premium' else 100000
    
    db = get_db()
    existing = get_user_card(g.user['id'])
    if existing:
        db.execute('''UPDATE cards SET card_type = ?, color = ?, status = 'processing',
                      credit_limit = ?, available_limit = ?, order_date = ?, delivery_date = ?, card_number = ?
                      WHERE id = ?''', (card_type, color, credit_limit, credit_limit, order_date, delivery_date, card_number, existing['id']))
    else:
        db.execute('''
            INSERT INTO cards (user_id, card_type, color, status, credit_limit, available_limit, order_date, delivery_date, card_number, on_time_payments)
            VALUES (?, ?, ?, 'processing', ?, ?, ?, ?, ?, 0)
        ''', (g.user['id'], card_type, color, credit_limit, credit_limit, order_date, delivery_date, card_number))
    
    db.commit()
    
    return jsonify({'success': True, 'card': {'type': card_type, 'color': color}})

@app.route('/api/process-payment', methods=['POST'])
@login_required
def process_payment():
    data = request.get_json(silent=True) or {}
    if data.get('method') not in {'upi', 'netbanking', 'debit_card'}:
        return jsonify({'success': False, 'message': 'Choose a payment method'}), 400
    tx_id = f"TXN{random.randint(10000000, 99999999)}"
    return jsonify({'success': True, 'transaction_id': tx_id})

@app.route('/api/save-address', methods=['POST'])
@login_required
def save_address():
    data = request.get_json(silent=True) or {}
    required_fields = ('line1', 'pincode', 'city', 'state')
    if any(not str(data.get(field, '')).strip() for field in required_fields):
        return jsonify({'success': False, 'message': 'Complete your delivery address'}), 400
    if not re.fullmatch(r'\d{6}', str(data.get('pincode', ''))):
        return jsonify({'success': False, 'message': 'Enter a valid six-digit pincode'}), 400
    db = get_db()
    card = get_user_card(g.user['id'])
    if not card:
        return jsonify({'success': False, 'message': 'Choose a card before adding an address'}), 400
    db.execute('''
        INSERT INTO addresses (user_id, line1, line2, apartment, pincode, city, state)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (g.user['id'], data.get('line1'), data.get('line2'), data.get('apartment'), 
          data.get('pincode'), data.get('city'), data.get('state')))
    
    # Update card status
    db.execute("UPDATE cards SET status = 'shipped' WHERE user_id = ?", (g.user['id'],))
    db.commit()
    
    card = get_user_card(g.user['id'])
    return jsonify({'success': True, 'delivery_date': card['delivery_date']})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'mode': 'demo' if DEMO_MODE else 'production'})

@app.route('/api/user-profile', methods=['GET'])
@login_required
def user_profile():
    user = dict(g.user)
    card = get_user_card(user['id'])
    address = get_user_address(user['id'])
    txs = get_user_transactions(user['id'])
    
    return jsonify({
        'user': user,
        'card': dict(card) if card else None,
        'address': dict(address) if address else None,
        'transactions': [dict(t) for t in txs] if txs else []
    })

@app.route('/api/request-limit-increase', methods=['POST'])
@login_required
def request_limit_increase():
    db = get_db()
    card = get_user_card(g.user['id'])
    if not card:
        return jsonify({'success': False, 'message': 'No card found'})
        
    if card['on_time_payments'] >= 3:
        new_limit = int(card['credit_limit'] * 1.10)
        new_available = card['available_limit'] + (new_limit - card['credit_limit'])
        db.execute('UPDATE cards SET credit_limit = ?, available_limit = ?, limit_increases = limit_increases + 1 WHERE id = ?', 
                   (new_limit, new_available, card['id']))
        db.commit()
        return jsonify({'success': True, 'new_limit': new_limit})
    return jsonify({'success': False, 'message': 'Not eligible yet'})

@app.route('/api/convert-to-emi', methods=['POST'])
@login_required
def convert_to_emi():
    data = request.json
    tx_id = data.get('transaction_id')
    months = data.get('months')
    
    rates = {3: 1.5, 6: 0.99, 12: 1.25}
    rate = rates.get(months, 0.99)
    
    db = get_db()
    db.execute('UPDATE transactions SET is_emi = 1, emi_months = ?, emi_rate = ? WHERE id = ? AND user_id = ?',
               (months, rate, tx_id, g.user['id']))
    db.commit()
    
    return jsonify({'success': True, 'emi_details': {'months': months, 'rate': rate}})

@app.route('/api/freeze-card', methods=['POST'])
@login_required
def freeze_card():
    data = request.get_json(silent=True) or {}
    freeze = data.get('frozen', True)
    new_status = 'frozen' if freeze else 'active'
    db = get_db()
    db.execute('UPDATE cards SET status = ? WHERE user_id = ?', (new_status, g.user['id']))
    db.commit()
    return jsonify({'success': True, 'status': new_status, 'frozen': freeze})

@app.route('/api/block-card', methods=['POST'])
@login_required
def block_card():
    data = request.get_json(silent=True) or {}
    reason = data.get('reason', 'User requested permanent block')
    db = get_db()
    db.execute("UPDATE cards SET status = 'blocked' WHERE user_id = ?", (g.user['id'],))
    db.commit()
    return jsonify({'success': True, 'status': 'blocked', 'message': 'Card blocked successfully. Replacement order initiated.'})

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    data = request.json
    db = get_db()
    db.execute('UPDATE users SET name = ? WHERE id = ?', (data.get('name'), g.user['id']))
    db.commit()
    return jsonify({'success': True})

@app.route('/api/pincode/<pincode>', methods=['GET'])
def get_pincode_info(pincode):
    # Simulated mapping
    if pincode.startswith('11'):
        return jsonify({'city': 'New Delhi', 'state': 'Delhi'})
    elif pincode.startswith('56'):
        return jsonify({'city': 'Bengaluru', 'state': 'Karnataka'})
    else:
        return jsonify({'city': 'Mumbai', 'state': 'Maharashtra'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
