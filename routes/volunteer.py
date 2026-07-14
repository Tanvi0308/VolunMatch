from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from db import get_db_connection
from recommender import get_project_recommendations

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or session.get('is_admin'):
            flash('Please log in as a volunteer.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@volunteer_bp.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    # Get recommendations from ML engine
    recommended_projects = get_project_recommendations(user_id, top_n=5)
    
    return render_template('dashboard.html', projects=recommended_projects)

@volunteer_bp.route('/apply/<int:project_id>', methods=['POST'])
@login_required
def apply(project_id):
    user_id = session['user_id']
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Check if already applied
        cursor.execute("SELECT id FROM applications WHERE volunteer_id=? AND project_id=?", (user_id, project_id))
        if cursor.fetchone():
            flash('You have already applied to this project.', 'info')
        else:
            cursor.execute(
                "INSERT INTO applications (volunteer_id, project_id, status) VALUES (?, ?, 'pending')",
                (user_id, project_id)
            )
            conn.commit()
            flash('Application submitted successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error applying to project.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('volunteer.dashboard'))

@volunteer_bp.route('/my_applications')
@login_required
def my_applications():
    user_id = session['user_id']
    
    conn = get_db_connection()
    applications = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.status, a.applied_at, p.title, p.description
            FROM applications a
            JOIN projects p ON a.project_id = p.id
            WHERE a.volunteer_id = ?
            ORDER BY a.applied_at DESC
        """, (user_id,))
        applications = cursor.fetchall()
        
        from datetime import datetime
        for app in applications:
            if app.get('applied_at') and isinstance(app['applied_at'], str):
                try:
                    app['applied_at'] = datetime.strptime(app['applied_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        app['applied_at'] = datetime.strptime(app['applied_at'], '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                        pass
    finally:
        conn.close()
        
    return render_template('my_applications.html', applications=applications)
