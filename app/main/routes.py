from flask import render_template, redirect, url_for, session, send_from_directory
from app.main import bp
from app.models import User

@bp.route('/')
def index():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif user:
            return redirect(url_for('employee.dashboard'))
    return redirect(url_for('auth.login'))

# PWA Routes
@bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@bp.route('/sw.js')
def service_worker():
    return send_from_directory('static', 'sw.js')

@bp.route('/offline')
def offline():
    return render_template('offline.html')