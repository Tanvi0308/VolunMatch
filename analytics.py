from db import get_db_connection

def get_dashboard_stats():
    """
    Analyzes DB data using pure SQL and Python to generate stats for Chart.js
    (No Pandas required)
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Skill gap analysis: most needed vs available
        # Get all skills
        cursor.execute("SELECT id, name FROM skills")
        skills = {row['id']: {'name': row['name'], 'available': 0, 'required': 0} for row in cursor.fetchall()}
        
        # Get available counts
        cursor.execute("SELECT skill_id, COUNT(*) as count FROM volunteer_skills GROUP BY skill_id")
        for row in cursor.fetchall():
            if row['skill_id'] in skills:
                skills[row['skill_id']]['available'] = row['count']
                
        # Get required counts
        cursor.execute("SELECT skill_id, COUNT(*) as count FROM project_skills GROUP BY skill_id")
        for row in cursor.fetchall():
            if row['skill_id'] in skills:
                skills[row['skill_id']]['required'] = row['count']
                
        # Convert to list and sort by required (descending) to get top 5
        skills_list = list(skills.values())
        skills_list.sort(key=lambda x: x['required'], reverse=True)
        top_required = skills_list[:5]
        
        # 2. Application Status Distribution
        cursor.execute("SELECT status, COUNT(*) as count FROM applications GROUP BY status")
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        return {
            'skill_gap': {
                'labels': [s['name'] for s in top_required],
                'available': [s['available'] for s in top_required],
                'required': [s['required'] for s in top_required]
            },
            'application_status': {
                'labels': list(status_counts.keys()),
                'data': list(status_counts.values())
            }
        }
        
    except Exception as e:
        print(f"Analytics Error: {e}")
        return {'error': str(e)}
    finally:
        conn.close()
