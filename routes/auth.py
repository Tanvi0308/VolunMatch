from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
# from recommender import retrain_model # We will call this after registration

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        skills = request.form.getlist('skills') # List of skill IDs
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Check if email exists
            cursor.execute("SELECT id FROM volunteers WHERE email = ?", (email,))
            if cursor.fetchone():
                flash('Email already registered.', 'danger')
                return redirect(url_for('auth.register'))
                
            # Insert volunteer
            password_hash = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO volunteers (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            volunteer_id = cursor.lastrowid
            
            # one more comment here 
            # Insert skills
            for skill_id in skills:
                cursor.execute(
                    "INSERT INTO volunteer_skills (volunteer_id, skill_id) VALUES (?, ?)",
                    (volunteer_id, skill_id)
                )
            conn.commit()
            
            # TODO: Trigger ML retrain here
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            conn.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
        finally:
            conn.close()
            
    # GET request: fetch skills for form
    conn = get_db_connection()
    skills = []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills ORDER BY name")
        skills = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('register.html', skills=skills)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM volunteers WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['is_admin'] = user['is_admin']
                
                if user['is_admin']:
                    return redirect(url_for('admin.dashboard'))
                else:
                    return redirect(url_for('volunteer.dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
        finally:
            conn.close()
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
