from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Patient
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/patient-registration', methods=['GET', 'POST'])
@login_required
def patient_registration():
    if request.method == 'POST':
        arrival_mode = request.form.get('arrival_mode')
        
        try:
            # Common patient data for both arrival modes
            patient = Patient(
                first_name=request.form.get('first_name'),
                last_name=request.form.get('last_name'),
                date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date(),
                gender=request.form.get('gender'),
                address=request.form.get('address'),
                phone_number=request.form.get('phone_number'),
                arrival_mode=arrival_mode,
                emergency_contact_name=request.form.get('emergency_contact_name'),
                emergency_contact_phone=request.form.get('emergency_contact_phone')
            )
            
            # Data specific to arrival mode
            if arrival_mode == 'ambulance':
                patient.medical_record_number = request.form.get('medical_record_number')
                patient.referral_source = request.form.get('referral_source')
            
            db.session.add(patient)
            db.session.commit()
            
            flash('Patient registered successfully!', 'success')
            return redirect(url_for('admin.insurance_verification', patient_id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering patient: {str(e)}', 'danger')
    
    return render_template('admin/patient_registration.html')

@admin_bp.route('/insurance-verification/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def insurance_verification(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        try:
            patient.insurance_type = request.form.get('insurance_type')
            patient.insurance_number = request.form.get('insurance_number')
            
            db.session.commit()
            flash('Insurance information saved successfully!', 'success')
            return redirect(url_for('admin.print_id_band', patient_id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving insurance information: {str(e)}', 'danger')
    
    return render_template('admin/insurance_verification.html', patient=patient)

@admin_bp.route('/print-id-band/<int:patient_id>', methods=['GET'])
@login_required
def print_id_band(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('admin/print_id_band.html', patient=patient)

@admin_bp.route('/generate-mrn', methods=['POST'])
@login_required
def generate_mrn():
    # In a real system, this would follow hospital's MRN generation rules
    # For this demo, we'll create a timestamp-based MRN
    timestamp = datetime.now().strftime('%Y%m%d%H%M')
    mrn = f"MRN-{timestamp}"
    return jsonify({'mrn': mrn})
