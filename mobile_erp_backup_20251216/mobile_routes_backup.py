# Mobile ERP Routes Backup - Removed from app.py on Dec 16, 2025

# Mobile login tokens table creation (from init_db function)
mobile_login_tokens_table = '''
    # Mobile login tokens (for one-time link login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mobile_login_tokens (
            token TEXT PRIMARY KEY,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            used INTEGER DEFAULT 0
        )
    """)
'''

# Mobile Routes to be removed from app.py
mobile_routes = '''
@app.route('/mobile-login-test')
def mobile_login_test():
    return render_template('mobile_login_test.html')

@app.route('/mobile-simple-old')
def mobile_simple_old():
    return render_template('mobile_simple_test.html')

@app.route('/mobile-instant')
def mobile_instant():
    return render_template('mobile_instant.html')

@app.route('/mobile-debug')
def mobile_debug():
    return render_template('mobile_debug.html')

@app.route('/mobile-simple')
def mobile_simple_new():
    return render_template('mobile_simple_working.html')

@app.route('/test-mobile')
def test_mobile():
    return send_from_directory('.', 'test_mobile_simple.html')

@app.route('/mobile-diagnostic')
def mobile_diagnostic():
    return render_template('mobile_diagnostic_simple.html')

@app.route('/mobile-test')
def mobile_test_connection():
    return render_template('mobile_test_connection.html')

@app.route('/mobile-fresh')
def mobile_fresh_version():
    return render_template('mobile_fresh.html')

@app.route('/mobile-test-page')
def mobile_test_page():
    return render_template('mobile_test_simple.html')

@app.route('/mobile')
def mobile_app():
    return render_template('mobile_simple_working.html')

@app.route('/mobile-v1')
def mobile_app_v1():
    return render_template('mobile_erp_working.html')

@app.route('/mobile-old')
def mobile_app_old():
    return render_template('mobile_erp_working.html')

@app.route('/mobile-working')
def mobile_working():
    return render_template('mobile_erp_working.html')

@app.route('/mobile-fixed')
def mobile_app_fixed():
    return render_template('mobile_erp_working.html')

@app.route('/mobile-pwa')
def mobile_pwa():
    from flask import make_response
    response = make_response(render_template('mobile_erp_working.html'))
    # Add cache-busting headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/mobile/reports')
def mobile_reports():
    """Mobile Reports & Analytics"""
    return render_template('mobile_reports.html')
'''

# Mobile API Routes to be removed
mobile_api_routes = '''
@app.route('/api/mobile/request-link', methods=['POST'])
def api_mobile_request_link():
    """Request a one-time mobile login link to be sent to a phone number."""
    data = request.json or {}
    phone = data.get('phone')
    if not phone:
        return jsonify({'message': 'Missing phone number'}), 400

    # Generate token and expiry (10 minutes)
    token = uuid.uuid4().hex
    expires_at = (datetime.now() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db_connection()
    conn.execute('INSERT INTO mobile_login_tokens (token, phone, expires_at) VALUES (?, ?, ?)',
                 (token, phone, expires_at))
    conn.commit()
    conn.close()

    # Build deep link
    link = request.host_url.rstrip('/') + f"/mobile-simple?token={token}"

    # Try to send via WhatsApp if available
    sent_via = None
    try:
        if whatsapp_service:
            msg = f"Open your BizPulse Mobile: {link} (valid 10 minutes)"
            res = whatsapp_service.send_from_developer_number(phone, msg)
            sent_via = 'whatsapp' if res.get('success') else None
    except Exception:
        sent_via = None

    return jsonify({'message': 'Link created', 'token': token, 'link': link, 'sent_via': sent_via})

@app.route('/api/auth/mobile-token-login', methods=['POST'])
def api_auth_mobile_token_login():
    """Exchange a mobile login token for a session (used by mobile app)."""
    data = request.json or {}
    token = data.get('token')
    if not token:
        return jsonify({'message': 'Missing token'}), 400

    conn = get_db_connection()
    row = conn.execute('SELECT token, phone, expires_at, used FROM mobile_login_tokens WHERE token = ?', (token,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'message': 'Invalid token'}), 400

    if row['used']:
        conn.close()
        return jsonify({'message': 'Token already used'}), 400

    expires = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expires:
        conn.close()
        return jsonify({'message': 'Token expired'}), 400

    phone = row['phone']

    # Try to find client by phone (phone column is `phone_number` or `whatsapp_number`)
    client = conn.execute('SELECT id, company_name, contact_email FROM clients WHERE phone_number = ? OR whatsapp_number = ? LIMIT 1', (phone, phone)).fetchone()

    # Mark token used
    conn.execute('UPDATE mobile_login_tokens SET used = 1 WHERE token = ?', (token,))
    conn.commit()

    # Create session similar to unified-login
    if client:
        session['user_id'] = client['id']
        session['user_type'] = 'client'
        session['user_name'] = client['company_name']
        session['is_super_admin'] = False
        conn.close()
        return jsonify({'message': 'Login successful', 'token': 'client-jwt-token', 'user': {'id': client['id'], 'name': client['company_name'], 'email': client['contact_email'], 'type': 'client'}})

    # Fallback: create a temporary guest session
    session['user_id'] = f'guest-{uuid.uuid4().hex[:8]}'
    session['user_type'] = 'guest'
    session['user_name'] = f'Guest ({phone})'
    session['is_super_admin'] = False
    conn.close()
    return jsonify({'message': 'Login successful (guest)', 'token': 'guest-token', 'user': {'id': session['user_id'], 'name': session['user_name'], 'type': 'guest'}})

@app.route('/api/mobile/confirm-link', methods=['POST'])
def api_mobile_confirm_link():
    """Confirm a previously-created mobile link for the currently-authenticated session."""
    if 'user_id' not in session:
        return jsonify({'message': 'Not authenticated'}), 401
    
    data = request.json or {}
    token = data.get('token')
    if not token:
        return jsonify({'message': 'Missing token'}), 400

    conn = get_db_connection()
    row = conn.execute('SELECT token, phone, expires_at, used FROM mobile_login_tokens WHERE token = ?', (token,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'message': 'Invalid token'}), 400

    if row['used']:
        conn.close()
        return jsonify({'message': 'Token already used'}), 400

    expires = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S')
    if datetime.now() > expires:
        conn.close()
        return jsonify({'message': 'Token expired'}), 400

    # Mark token used and record who confirmed it
    conn.execute('UPDATE mobile_login_tokens SET used = 1 WHERE token = ?', (token,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Link confirmed'})
'''

# CORS configuration for mobile (from app.py line 14-16)
mobile_cors_config = '''
# Enable CORS for all domains and methods (for mobile app)
CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"])
'''

# Mobile access print statement (from line 7077)
mobile_access_print = '''
    print("[MOBILE ACCESS]:")
    print(f"   Mobile App: http://{local_ip}:5000/mobile-simple")
    print(f"   Login: bizpulse.erp@gmail.com / demo123")
'''