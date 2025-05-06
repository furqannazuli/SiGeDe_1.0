from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta
from models import Patient, Triage, NurseAssessment, DoctorExamination, User
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with ER statistics"""
    
    # Get current date for filters
    today = datetime.now().date()
    
    # --- PATIENTS PER HOUR ---
    # Get patient count per hour for the current day
    patients_per_hour = db.session.query(
        func.date_part('hour', Patient.created_at).label('hour'),
        func.count(Patient.id).label('count')
    ).filter(
        func.cast(Patient.created_at, Date) == today
    ).group_by(
        func.date_part('hour', Patient.created_at)
    ).order_by(
        func.date_part('hour', Patient.created_at)
    ).all()
    
    # Format for chart
    hours_labels = [int(record.hour) for record in patients_per_hour]
    hours_data = [record.count for record in patients_per_hour]
    
    # Fill in missing hours with zeros
    all_hours = list(range(24))
    patients_per_hour_complete = [0] * 24
    for i, hour in enumerate(all_hours):
        if hour in hours_labels:
            idx = hours_labels.index(hour)
            patients_per_hour_complete[i] = hours_data[idx]
    
    # --- PATIENTS PER MONTH ---
    # Get patient count per month for the current year
    current_year = today.year
    patients_per_month = db.session.query(
        func.date_part('month', Patient.created_at).label('month'),
        func.count(Patient.id).label('count')
    ).filter(
        func.date_part('year', Patient.created_at) == current_year
    ).group_by(
        func.date_part('month', Patient.created_at)
    ).order_by(
        func.date_part('month', Patient.created_at)
    ).all()
    
    # Format for chart
    month_labels = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    month_data = [0] * 12
    for record in patients_per_month:
        month_idx = int(record.month) - 1  # Months are 1-indexed in SQL
        month_data[month_idx] = record.count
    
    # --- TRIAGE CATEGORIES ---
    # Get counts per triage category
    triage_counts = db.session.query(
        Triage.category,
        func.count(Triage.id).label('count')
    ).group_by(
        Triage.category
    ).all()
    
    # Format for chart
    triage_labels = []
    triage_data = []
    triage_colors = {
        'red': '#dc3545',
        'yellow': '#ffc107',
        'green': '#28a745',
        'black': '#343a40'
    }
    triage_colors_list = []
    
    for record in triage_counts:
        triage_labels.append(record.category.capitalize())
        triage_data.append(record.count)
        triage_colors_list.append(triage_colors.get(record.category, '#6c757d'))
    
    # --- ON-CALL STAFF ---
    # In a real implementation, this would come from a schedule database
    # For demo purposes, we'll use the existing users
    nurses = User.query.filter_by(role='nurse').all()
    
    # --- DOCTOR DETAILS ---
    # Get doctors who have examined patients
    doctors = db.session.query(
        DoctorExamination.doctor_name,
        func.count(DoctorExamination.id).label('patient_count')
    ).group_by(
        DoctorExamination.doctor_name
    ).order_by(
        func.count(DoctorExamination.id).desc()
    ).limit(10).all()
    
    # Calculate total patients
    total_patients_today = sum(patients_per_hour_complete)
    
    return render_template('dashboard/index.html',
                          hours_labels=list(range(24)),
                          hours_data=patients_per_hour_complete,
                          month_labels=month_labels,
                          month_data=month_data,
                          triage_labels=triage_labels,
                          triage_data=triage_data,
                          triage_colors=triage_colors_list,
                          nurses=nurses,
                          doctors=doctors,
                          today=today,
                          total_patients_today=total_patients_today)