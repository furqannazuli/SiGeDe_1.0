from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('admin.patient_registration'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.patient_registration'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('admin.patient_registration'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

# This route is for development purposes only - create a default nurse account
@auth_bp.route('/setup', methods=['GET'])
def setup():
    # Check if any users exist
    if User.query.count() > 0:
        flash('Setup has already been completed', 'info')
        return redirect(url_for('auth.login'))
    
    # Create a default nurse account
    default_nurse = User(
        username='nurse1',
        email='nurse1@sigede.org',
        full_name='Test Nurse',
        role='nurse'
    )
    default_nurse.set_password('password123')
    
    try:
        db.session.add(default_nurse)
        db.session.commit()
        flash('Default nurse account created. Username: nurse1, Password: password123', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating default account: {str(e)}', 'danger')
    
    return redirect(url_for('auth.login'))
