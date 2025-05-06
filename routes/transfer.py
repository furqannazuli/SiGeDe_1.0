from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Patient, Triage, NurseAssessment, DoctorExamination, LabRequest, Prescription, Disposition
from datetime import datetime

transfer_bp = Blueprint('transfer', __name__, url_prefix='/transfer')

@transfer_bp.route('/disposition/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def disposition(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if all required assessments are completed
    doctor_exam = DoctorExamination.query.filter_by(patient_id=patient_id).first()
    if not doctor_exam:
        flash('Doctor examination must be completed before disposition', 'warning')
        return redirect(url_for('emergency.doctor_examination', patient_id=patient_id))
    
    # Get existing disposition if it exists
    existing_disposition = Disposition.query.filter_by(patient_id=patient_id).first()
    
    if request.method == 'POST':
        disposition_type = request.form.get('disposition_type')
        
        try:
            if existing_disposition:
                # Update existing disposition
                existing_disposition.disposition_type = disposition_type
                existing_disposition.authorized_by = request.form.get('authorized_by')
                existing_disposition.notes = request.form.get('notes')
            else:
                # Create new disposition
                disposition = Disposition(
                    patient_id=patient_id,
                    disposition_type=disposition_type,
                    authorized_by=request.form.get('authorized_by'),
                    notes=request.form.get('notes')
                )
                db.session.add(disposition)
            
            db.session.commit()
            
            # Redirect based on disposition type
            if disposition_type == 'discharge':
                return redirect(url_for('transfer.discharge_planning', patient_id=patient_id))
            elif disposition_type == 'outpatient':
                return redirect(url_for('transfer.outpatient_referral', patient_id=patient_id))
            elif disposition_type == 'inpatient':
                return redirect(url_for('transfer.inpatient_transfer', patient_id=patient_id))
            elif disposition_type == 'deceased':
                return redirect(url_for('transfer.mortality', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving disposition: {str(e)}', 'danger')
    
    return render_template('transfer/disposition.html', 
                          patient=patient,
                          disposition=existing_disposition)

@transfer_bp.route('/discharge-planning/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def discharge_planning(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    disposition = Disposition.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Verify it's a discharge disposition
    if disposition.disposition_type != 'discharge':
        flash('This patient is not marked for discharge', 'warning')
        return redirect(url_for('transfer.disposition', patient_id=patient_id))
    
    if request.method == 'POST':
        try:
            disposition.discharge_instructions = request.form.get('discharge_instructions')
            disposition.follow_up_plan = request.form.get('follow_up_plan')
            disposition.is_completed = True
            disposition.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Discharge planning completed successfully!', 'success')
            return redirect(url_for('emergency.patient_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving discharge planning: {str(e)}', 'danger')
    
    return render_template('transfer/discharge_planning.html', 
                          patient=patient,
                          disposition=disposition)

@transfer_bp.route('/outpatient-referral/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def outpatient_referral(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    disposition = Disposition.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Verify it's an outpatient disposition
    if disposition.disposition_type != 'outpatient':
        flash('This patient is not marked for outpatient referral', 'warning')
        return redirect(url_for('transfer.disposition', patient_id=patient_id))
    
    if request.method == 'POST':
        try:
            disposition.clinic_referred_to = request.form.get('clinic_referred_to')
            appointment_date = request.form.get('appointment_date')
            
            if appointment_date:
                disposition.appointment_date = datetime.strptime(appointment_date, '%Y-%m-%dT%H:%M')
            
            disposition.is_completed = True
            disposition.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Outpatient referral completed successfully!', 'success')
            return redirect(url_for('emergency.patient_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving outpatient referral: {str(e)}', 'danger')
    
    return render_template('transfer/outpatient_referral.html', 
                          patient=patient,
                          disposition=disposition)

@transfer_bp.route('/inpatient-transfer/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def inpatient_transfer(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    disposition = Disposition.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Verify it's an inpatient disposition
    if disposition.disposition_type != 'inpatient':
        flash('This patient is not marked for inpatient transfer', 'warning')
        return redirect(url_for('transfer.disposition', patient_id=patient_id))
    
    if request.method == 'POST':
        try:
            disposition.destination_ward = request.form.get('destination_ward')
            disposition.bed_number = request.form.get('bed_number')
            bed_available = request.form.get('is_bed_available') == 'yes'
            disposition.is_bed_available = bed_available
            
            if not bed_available:
                disposition.waiting_list_position = request.form.get('waiting_list_position')
            
            disposition.is_completed = bed_available  # Only complete if bed is available
            
            if bed_available:
                disposition.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            if bed_available:
                flash('Patient transfer to inpatient completed successfully!', 'success')
                return redirect(url_for('emergency.patient_list'))
            else:
                flash('Patient added to waiting list for inpatient bed', 'info')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving inpatient transfer: {str(e)}', 'danger')
    
    return render_template('transfer/inpatient_transfer.html', 
                          patient=patient,
                          disposition=disposition)

@transfer_bp.route('/mortality/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def mortality(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    disposition = Disposition.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Verify it's a mortality disposition
    if disposition.disposition_type != 'deceased':
        flash('This patient is not marked as deceased', 'warning')
        return redirect(url_for('transfer.disposition', patient_id=patient_id))
    
    if request.method == 'POST':
        try:
            death_datetime = request.form.get('time_of_death')
            if death_datetime:
                disposition.time_of_death = datetime.strptime(death_datetime, '%Y-%m-%dT%H:%M')
                
            disposition.cause_of_death = request.form.get('cause_of_death')
            disposition.is_completed = True
            disposition.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Mortality documentation completed successfully', 'success')
            return redirect(url_for('emergency.patient_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving mortality documentation: {str(e)}', 'danger')
    
    return render_template('transfer/mortality.html', 
                          patient=patient,
                          disposition=disposition)
