from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Patient, Triage, NurseAssessment, DoctorExamination, LabRequest, Prescription, ExternalLabResult
from datetime import datetime
import json

emergency_bp = Blueprint('emergency', __name__, url_prefix='/emergency')

@emergency_bp.route('/patients', methods=['GET'])
@login_required
def patient_list():
    # Get patients who have been registered but not yet triaged
    new_patients = db.session.query(Patient).outerjoin(Triage).filter(Triage.id == None).all()
    
    # Get patients who have been triaged
    triaged_patients = db.session.query(Patient).join(Triage).all()
    
    return render_template('emergency/patient_list.html', 
                          new_patients=new_patients, 
                          triaged_patients=triaged_patients)

@emergency_bp.route('/triage/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def triage(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Check if patient already has triage information
    existing_triage = Triage.query.filter_by(patient_id=patient_id).first()
    if existing_triage:
        flash('Patient has already been triaged', 'info')
        return redirect(url_for('emergency.nurse_assessment', patient_id=patient_id))
    
    if request.method == 'POST':
        try:
            # Convert vital signs from form into JSON
            vitals = {
                'temperature': request.form.get('temperature'),
                'heart_rate': request.form.get('heart_rate'),
                'respiratory_rate': request.form.get('respiratory_rate'),
                'blood_pressure': request.form.get('blood_pressure'),
                'oxygen_saturation': request.form.get('oxygen_saturation'),
                'pain_level': request.form.get('pain_level')
            }
            
            triage = Triage(
                patient_id=patient_id,
                category=request.form.get('triage_category'),
                reason=request.form.get('triage_reason'),
                vital_signs=vitals,
                triaged_by=current_user.id
            )
            
            db.session.add(triage)
            db.session.commit()
            
            flash('Triage information saved successfully!', 'success')
            return redirect(url_for('emergency.nurse_assessment', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving triage information: {str(e)}', 'danger')
    
    return render_template('emergency/triage.html', patient=patient)

@emergency_bp.route('/nurse-assessment/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def nurse_assessment(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    triage = Triage.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Check if patient already has a nurse assessment
    existing_assessment = NurseAssessment.query.filter_by(patient_id=patient_id).first()
    
    if request.method == 'POST':
        try:
            # Convert vital signs from form into JSON
            vitals = {
                'temperature': request.form.get('temperature'),
                'heart_rate': request.form.get('heart_rate'),
                'respiratory_rate': request.form.get('respiratory_rate'),
                'blood_pressure': request.form.get('blood_pressure'),
                'oxygen_saturation': request.form.get('oxygen_saturation'),
                'pain_level': request.form.get('pain_level'),
                'glucose': request.form.get('glucose')
            }
            
            if existing_assessment:
                # Update existing assessment
                existing_assessment.chief_complaint = request.form.get('chief_complaint')
                existing_assessment.history = request.form.get('history')
                existing_assessment.allergies = request.form.get('allergies')
                existing_assessment.medications = request.form.get('medications')
                existing_assessment.vital_signs = vitals
                existing_assessment.assessment_details = request.form.get('assessment_details')
            else:
                # Create new assessment
                assessment = NurseAssessment(
                    patient_id=patient_id,
                    chief_complaint=request.form.get('chief_complaint'),
                    history=request.form.get('history'),
                    allergies=request.form.get('allergies'),
                    medications=request.form.get('medications'),
                    vital_signs=vitals,
                    assessment_details=request.form.get('assessment_details'),
                    nurse_id=current_user.id
                )
                db.session.add(assessment)
            
            db.session.commit()
            
            flash('Nursing assessment saved successfully!', 'success')
            return redirect(url_for('emergency.doctor_examination', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving nursing assessment: {str(e)}', 'danger')
    
    return render_template('emergency/nurse_assessment.html', 
                          patient=patient, 
                          triage=triage, 
                          assessment=existing_assessment)

@emergency_bp.route('/doctor-examination/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def doctor_examination(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    triage = Triage.query.filter_by(patient_id=patient_id).first_or_404()
    nurse_assessment = NurseAssessment.query.filter_by(patient_id=patient_id).first_or_404()
    
    # Check if patient already has doctor examination
    existing_examination = DoctorExamination.query.filter_by(patient_id=patient_id).first()
    
    if request.method == 'POST':
        try:
            requires_lab = 'requires_lab_tests' in request.form
            
            if existing_examination:
                # Update existing examination
                existing_examination.subjective = request.form.get('subjective')
                existing_examination.objective = request.form.get('objective')
                existing_examination.assessment = request.form.get('assessment')
                existing_examination.plan = request.form.get('plan')
                existing_examination.doctor_name = request.form.get('doctor_name')
                existing_examination.requires_lab_tests = requires_lab
            else:
                # Create new examination
                examination = DoctorExamination(
                    patient_id=patient_id,
                    subjective=request.form.get('subjective'),
                    objective=request.form.get('objective'),
                    assessment=request.form.get('assessment'),
                    plan=request.form.get('plan'),
                    doctor_name=request.form.get('doctor_name'),
                    requires_lab_tests=requires_lab
                )
                db.session.add(examination)
            
            db.session.commit()
            
            flash('Doctor examination saved successfully!', 'success')
            
            if requires_lab:
                return redirect(url_for('emergency.lab_request', patient_id=patient_id))
            else:
                return redirect(url_for('emergency.nursing_care', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving doctor examination: {str(e)}', 'danger')
    
    return render_template('emergency/doctor_examination.html', 
                          patient=patient, 
                          triage=triage, 
                          nurse_assessment=nurse_assessment,
                          examination=existing_examination)

@emergency_bp.route('/lab-request/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def lab_request(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Get existing lab requests
    existing_requests = LabRequest.query.filter_by(patient_id=patient_id).all()
    
    # Check if there are pending external lab results for this patient
    pending_external_results = None
    if patient.medical_record_number:
        pending_external_results = ExternalLabResult.query.filter_by(
            patient_mrn=patient.medical_record_number,
            is_imported=False
        ).all()
    
    if request.method == 'POST':
        try:
            # Create new lab request
            lab_request = LabRequest(
                patient_id=patient_id,
                test_type=request.form.get('test_type'),
                test_name=request.form.get('test_name'),
                priority=request.form.get('priority'),
                clinical_info=request.form.get('clinical_info'),
                requested_by=request.form.get('requested_by')
            )
            
            db.session.add(lab_request)
            db.session.commit()
            
            # Check if we can auto-match with any pending external results
            if patient.medical_record_number and lab_request.test_type and lab_request.test_name:
                matching_external = ExternalLabResult.query.filter_by(
                    patient_mrn=patient.medical_record_number,
                    test_type=lab_request.test_type,
                    test_name=lab_request.test_name,
                    is_imported=False
                ).first()
                
                if matching_external:
                    # Auto-import the matching result
                    lab_request.result = matching_external.result
                    lab_request.is_completed = True
                    lab_request.completed_at = datetime.utcnow()
                    lab_request.result_added_by = "Auto-import"
                    lab_request.is_auto_imported = True
                    lab_request.external_system_id = matching_external.external_system_id
                    
                    # Mark the external result as imported
                    matching_external.is_imported = True
                    matching_external.lab_request_id = lab_request.id
                    
                    db.session.commit()
                    flash('Lab request created and result automatically imported from external system!', 'success')
                else:
                    flash('Lab request saved successfully!', 'success')
            else:
                flash('Lab request saved successfully!', 'success')
            
            # Redirect to the same page to allow adding more lab requests
            return redirect(url_for('emergency.lab_request', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving lab request: {str(e)}', 'danger')
    
    return render_template('emergency/lab_request.html', 
                          patient=patient, 
                          lab_requests=existing_requests,
                          pending_external_results=pending_external_results)

@emergency_bp.route('/lab-results/<int:request_id>', methods=['GET', 'POST'])
@login_required
def lab_results(request_id):
    lab_request = LabRequest.query.get_or_404(request_id)
    patient = Patient.query.get_or_404(lab_request.patient_id)
    
    if request.method == 'POST':
        try:
            lab_request.result = request.form.get('result')
            lab_request.result_added_by = request.form.get('result_added_by')
            lab_request.is_completed = True
            lab_request.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Lab results saved successfully!', 'success')
            
            # Check if all lab requests are completed
            incomplete_requests = LabRequest.query.filter_by(
                patient_id=patient.id, 
                is_completed=False
            ).count()
            
            if incomplete_requests == 0:
                return redirect(url_for('emergency.nursing_care', patient_id=patient.id))
            else:
                return redirect(url_for('emergency.lab_request', patient_id=patient.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving lab results: {str(e)}', 'danger')
    
    return render_template('emergency/lab_results.html', lab_request=lab_request, patient=patient)

@emergency_bp.route('/nursing-care/<int:patient_id>', methods=['GET'])
@login_required
def nursing_care(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    triage = Triage.query.filter_by(patient_id=patient_id).first_or_404()
    nurse_assessment = NurseAssessment.query.filter_by(patient_id=patient_id).first_or_404()
    doctor_examination = DoctorExamination.query.filter_by(patient_id=patient_id).first_or_404()
    lab_requests = LabRequest.query.filter_by(patient_id=patient_id).all()
    
    return render_template('emergency/nursing_care.html', 
                          patient=patient, 
                          triage=triage,
                          nurse_assessment=nurse_assessment,
                          doctor_examination=doctor_examination,
                          lab_requests=lab_requests)

@emergency_bp.route('/pharmacy/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def pharmacy(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    # Get existing prescriptions
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()
    
    if request.method == 'POST':
        try:
            # Create new prescription
            prescription = Prescription(
                patient_id=patient_id,
                medication_name=request.form.get('medication_name'),
                dosage=request.form.get('dosage'),
                route=request.form.get('route'),
                frequency=request.form.get('frequency'),
                duration=request.form.get('duration'),
                special_instructions=request.form.get('special_instructions'),
                prescribed_by=request.form.get('prescribed_by')
            )
            
            db.session.add(prescription)
            db.session.commit()
            
            flash('Prescription saved successfully!', 'success')
            return redirect(url_for('emergency.pharmacy', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving prescription: {str(e)}', 'danger')
    
    return render_template('emergency/pharmacy.html', patient=patient, prescriptions=prescriptions)

@emergency_bp.route('/dispense-medication/<int:prescription_id>', methods=['POST'])
@login_required
def dispense_medication(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    
    try:
        prescription.is_dispensed = True
        prescription.dispensed_at = datetime.utcnow()
        prescription.dispensed_by = request.form.get('dispensed_by')
        
        db.session.commit()
        
        flash('Medication marked as dispensed!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error dispensing medication: {str(e)}', 'danger')
    
    return redirect(url_for('emergency.pharmacy', patient_id=prescription.patient_id))
