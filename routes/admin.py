from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from db import get_db_connection
from recommender import get_volunteer_recommendations

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    stats = {}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM volunteers WHERE is_admin=0")
        stats['total_volunteers'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM projects")
        stats['total_projects'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM applications")
        stats['total_applications'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM skills")
        stats['total_skills'] = cursor.fetchone()['count']
        
        # Fetch all projects for the recommendation dropdown
        cursor.execute("SELECT id, title FROM projects ORDER BY title")
        projects = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('admin.html', stats=stats, projects=projects)

@admin_bp.route('/applications')
@admin_required
def applications():
    conn = get_db_connection()
    apps = []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.status, a.applied_at, v.name as volunteer_name, p.title as project_title
            FROM applications a
            JOIN volunteers v ON a.volunteer_id = v.id
            JOIN projects p ON a.project_id = p.id
            ORDER BY a.applied_at DESC
        """)
        apps = cursor.fetchall()
        
        from datetime import datetime
        for app in apps:
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
        
    return render_template('admin_applications.html', applications=apps)

@admin_bp.route('/applications/<int:app_id>/<action>', methods=['POST'])
@admin_required
def update_application(app_id, action):
    if action not in ['approve', 'reject']:
        return "Invalid action", 400
        
    status = 'approved' if action == 'approve' else 'rejected'
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET status=? WHERE id=?", (status, app_id))
        conn.commit()
        flash(f'Application {status} successfully.', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error updating application.', 'danger')
    finally:
        conn.close()
        
    return redirect(url_for('admin.applications'))

@admin_bp.route('/project_recommendations/<int:project_id>')
@admin_required
def project_recommendations(project_id):
    # Get top volunteers for a specific project
    top_volunteers = get_volunteer_recommendations(project_id, top_n=5)
    return render_template('admin_recommendations.html', volunteers=top_volunteers, project_id=project_id)
