#!/usr/bin/env python3
"""
SPEED MOI - Web Application
Fast contribution (moi) recording and bill printing for traditional functions.

To run:
    python app.py
Opens at http://127.0.0.1:5000
"""

import os
import secrets
from datetime import date
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
import database

# Initialize Flask application
app = Flask(__name__)

# Manage session secret key (persisted in secret.key on first run)
SECRET_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret.key')
if os.path.exists(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE, 'r', encoding='utf-8') as f:
        app.secret_key = f.read().strip()
else:
    generated_key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, 'w', encoding='utf-8') as f:
        f.write(generated_key)
    app.secret_key = generated_key

# Ensure database tables exist on start
database.init_db()

def ensure_session_authenticated():
    """Automatically authenticates the session so users enter the app without login barriers."""
    if 'user_id' not in session:
        admin_user = database.get_user_by_username('admin')
        if not admin_user:
            database.create_user('admin', generate_password_hash('admin123'))
            admin_user = database.get_user_by_username('admin')
        session['user_id'] = admin_user['id']
        session['username'] = admin_user['username']

def login_required(f):
    """Decorator to ensure session is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ensure_session_authenticated()
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    """Injects current function details into all templates."""
    current_func = None
    if 'function_id' in session:
        current_func = database.get_function(session['function_id'])
    return dict(current_function=current_func)

# -----------------------------------------------------------------------------
# DIRECT ACCESS ROUTES (NO LOGIN SCREEN BARRIER)
# -----------------------------------------------------------------------------

@app.route('/')
def index():
    """Root route: bypasses login and jumps directly into the application."""
    ensure_session_authenticated()
    if 'function_id' in session and session['function_id']:
        return redirect(url_for('add_contribution'))

    # If any function exists in database, make the most recent one active
    all_funcs = database.get_all_functions()
    if all_funcs:
        session['function_id'] = all_funcs[0]['id']
        return redirect(url_for('add_contribution'))

    return redirect(url_for('function_setup'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Bypasses login and directs straight to function setup or contributions."""
    ensure_session_authenticated()
    if 'function_id' in session and session['function_id']:
        return redirect(url_for('add_contribution'))

    all_funcs = database.get_all_functions()
    if all_funcs:
        session['function_id'] = all_funcs[0]['id']
        return redirect(url_for('add_contribution'))

    return redirect(url_for('function_setup'))

@app.route('/create-admin', methods=['POST'])
def create_admin():
    """Bypass to setup."""
    ensure_session_authenticated()
    return redirect(url_for('function_setup'))

@app.route('/logout')
def logout():
    """Resets to main screen without locking the user out."""
    session.pop('function_id', None)
    return redirect(url_for('function_setup'))

# -----------------------------------------------------------------------------
# FUNCTION SETUP & SELECTION ROUTES
# -----------------------------------------------------------------------------

@app.route('/function-setup')
@login_required
def function_setup():
    """Renders the Function Setup page."""
    today_str = date.today().isoformat()
    return render_template('function_setup.html', default_date=today_str)

@app.route('/start-function', methods=['POST'])
@login_required
def start_function():
    """
    Saves a newly created function, stores its ID in the session,
    and opens the Add Contribution page (not the dashboard).
    """
    function_name = request.form.get('function_name', '').strip()
    coordinator_name = request.form.get('coordinator_name', '').strip()
    function_date = request.form.get('function_date', '').strip()
    host_details = request.form.get('host_details', '').strip()
    venue = request.form.get('venue', '').strip()
    contact_number = request.form.get('contact_number', '').strip()
    clerk_name = request.form.get('clerk_name', '').strip()

    if not function_name or not coordinator_name or not function_date:
        flash("Please fill in all required function details.", "error")
        return redirect(url_for('function_setup'))

    func_id = database.create_function(
        function_name=function_name,
        coordinator_name=coordinator_name,
        function_date=function_date,
        host_details=host_details,
        venue=venue,
        contact_number=contact_number,
        clerk_name=clerk_name
    )
    session['function_id'] = func_id
    flash(f"Function '{function_name}' started successfully!", "success")
    return redirect(url_for('add_contribution'))

@app.route('/functions')
@login_required
def previous_functions():
    """Lists all previous and current functions."""
    all_funcs = database.get_all_functions()
    return render_template('previous_functions.html', functions=all_funcs)

@app.route('/open-function/<int:function_id>')
@login_required
def open_function(function_id):
    """Sets a previously created function as the active function in session."""
    func = database.get_function(function_id)
    if not func:
        flash("Function not found.", "error")
        return redirect(url_for('previous_functions'))

    session['function_id'] = func['id']
    flash(f"Active function switched to: {func['function_name']}", "success")
    return redirect(url_for('add_contribution'))

# -----------------------------------------------------------------------------
# HELPER FORMATTING FUNCTIONS
# -----------------------------------------------------------------------------

def format_indian_currency(amount):
    """Formats a number into Indian currency style, e.g. 2000 -> ₹2,000, 150000 -> ₹1,50,000"""
    try:
        val = int(amount)
        s = str(abs(val))
    except (ValueError, TypeError):
        return f"₹{amount}"

    if len(s) <= 3:
        formatted = s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        parts = []
        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.insert(0, remaining)
        formatted = ",".join(parts) + "," + last_three

    sign = "-" if val < 0 else ""
    return f"{sign}₹{formatted}"

def format_bill_id(bill_number):
    """Formats an integer bill counter to SM-0001 format."""
    try:
        return f"SM-{int(bill_number):04d}"
    except (ValueError, TypeError):
        return f"SM-{bill_number}"

app.jinja_env.filters['indian_currency'] = format_indian_currency
app.jinja_env.filters['bill_id'] = format_bill_id

# -----------------------------------------------------------------------------
# DASHBOARD & CONTRIBUTION ROUTES
# -----------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page showing active function summary."""
    curr_func = None
    total_contributors = 0
    total_amount = 0

    if 'function_id' in session:
        curr_func = database.get_function(session['function_id'])
        if curr_func:
            # Query totals for this function
            conn = database.get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
                FROM contributions WHERE function_id = ?
            """, (curr_func['id'],))
            row = cursor.fetchone()
            if row:
                total_contributors = row['count']
                total_amount = row['total']
            conn.close()

    return render_template(
        'dashboard.html',
        current_function=curr_func,
        total_contributors=total_contributors,
        total_amount=total_amount
    )

@app.route('/add-contribution')
@login_required
def add_contribution():
    """
    Add Contribution page.
    Ensures an active function is selected before recording.
    """
    if 'function_id' not in session:
        flash("Please setup or select a function first.", "error")
        return redirect(url_for('function_setup'))

    curr_func = database.get_function(session['function_id'])
    if not curr_func:
        flash("Active function could not be found. Please select a function.", "error")
        return redirect(url_for('previous_functions'))

    # Retrieve last 5 contributions for quick reference
    recent = database.get_recent_contributions(curr_func['id'], limit=5)

    return render_template(
        'add_contribution.html',
        current_function=curr_func,
        recent_contributions=recent
    )

@app.route('/save-contribution', methods=['POST'])
@login_required
def save_contribution():
    """
    Saves a contribution, generates unique Bill ID (SM-XXXX),
    and redirects directly to the individual bill page.
    """
    if 'function_id' not in session:
        flash("No active function. Please select or create a function.", "error")
        return redirect(url_for('function_setup'))

    function_id = session['function_id']
    contributor_name = request.form.get('contributor_name', '').strip()
    native_place = request.form.get('native_place', '').strip()
    amount_str = request.form.get('amount', '').strip()
    entry_date = request.form.get('entry_date', '').strip()
    entry_time = request.form.get('entry_time', '').strip()

    # Fallback to server local date/time if browser omitted them
    from datetime import datetime
    now = datetime.now()
    if not entry_date:
        entry_date = now.strftime('%d-%m-%Y')
    if not entry_time:
        entry_time = now.strftime('%I:%M %p')

    # Basic validations
    if not contributor_name:
        flash("Contributor name is required.", "error")
        return redirect(url_for('add_contribution'))

    if not native_place:
        flash("Native place is required.", "error")
        return redirect(url_for('add_contribution'))

    try:
        amount = int(amount_str)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        flash("Please enter a valid positive contribution amount.", "error")
        return redirect(url_for('add_contribution'))

    try:
        contrib_id, bill_num = database.save_contribution(
            function_id=function_id,
            contributor_name=contributor_name,
            native_place=native_place,
            amount=amount,
            entry_date=entry_date,
            entry_time=entry_time
        )
        bill_id_str = format_bill_id(bill_num)
        flash(f"Receipt {bill_id_str} recorded successfully for {contributor_name}!", "success")
        return redirect(url_for('receipt', contribution_id=contrib_id))
    except Exception as e:
        flash(f"Failed to save contribution: {str(e)}", "error")
        return redirect(url_for('add_contribution'))

@app.route('/receipt/<int:contribution_id>')
@login_required
def receipt(contribution_id):
    """
    Renders the individual bill receipt page.
    """
    item = database.get_contribution(contribution_id)
    if not item:
        flash("Contribution record not found.", "error")
        return redirect(url_for('add_contribution'))

    bill_id = format_bill_id(item['bill_number'])
    formatted_amount = format_indian_currency(item['amount'])

    return render_template(
        'receipt.html',
        contribution=item,
        bill_id=bill_id,
        formatted_amount=formatted_amount
    )

@app.route('/print-receipt/<int:contribution_id>')
@login_required
def print_receipt(contribution_id):
    """
    Renders printable receipt view.
    """
    return redirect(url_for('receipt', contribution_id=contribution_id))

@app.route('/contributions')
@login_required
def contributions_list():
    """
    Lists all contributions for the currently active function.
    """
    if 'function_id' not in session:
        flash("Please select a function first.", "error")
        return redirect(url_for('function_setup'))

    curr_func = database.get_function(session['function_id'])
    if not curr_func:
        flash("Active function not found.", "error")
        return redirect(url_for('previous_functions'))

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM contributions 
        WHERE function_id = ? 
        ORDER BY bill_number ASC
    """, (curr_func['id'],))
    all_items = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
        FROM contributions WHERE function_id = ?
    """, (curr_func['id'],))
    stats = cursor.fetchone()
    total_count = stats['count'] if stats else 0
    total_amount = stats['total'] if stats else 0
    conn.close()

    return render_template(
        'contributions.html',
        current_function=curr_func,
        contributions=all_items,
        total_contributors=total_count,
        formatted_total_amount=format_indian_currency(total_amount)
    )


# -----------------------------------------------------------------------------
# MAIN ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    # Default port is 5000 as specified; supports PORT env var if configured
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting SPEED MOI server on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
