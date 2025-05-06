from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Patient, LabRequest, ExternalLabResult
from datetime import datetime
import logging

laboratory_bp = Blueprint('laboratory', __name__)

@laboratory_bp.route('/external-lab-api/results', methods=['POST'])
def receive_external_results():
    """API endpoint to receive results from external laboratory or radiology systems"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['external_id', 'patient_mrn', 'test_type', 'test_name', 'result']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if result already exists to avoid duplicates
        existing_result = ExternalLabResult.query.filter_by(
            external_system_id=data['external_id']
        ).first()
        
        if existing_result:
            return jsonify({"error": "Result with this external ID already exists"}), 409
        
        # Create new external lab result
        new_result = ExternalLabResult(
            external_system_id=data['external_id'],
            patient_mrn=data['patient_mrn'],
            test_type=data['test_type'],
            test_name=data['test_name'],
            result=data['result'],
            result_date=datetime.strptime(data.get('result_date', datetime.now().isoformat()), '%Y-%m-%dT%H:%M:%S.%f') if 'result_date' in data else datetime.now()
        )
        
        db.session.add(new_result)
        db.session.commit()
        
        # Try to match with a pending lab request
        process_external_result(new_result.id)
        
        return jsonify({"message": "Lab result received successfully", "id": new_result.id}), 201
    
    except Exception as e:
        logging.error(f"Error processing external lab result: {str(e)}")
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@laboratory_bp.route('/laboratory/pending-results')
@login_required
def pending_results():
    """Admin view for pending external results that haven't been matched to lab requests"""
    pending_results = ExternalLabResult.query.filter_by(is_imported=False).all()
    return render_template('laboratory/pending_results.html', pending_results=pending_results)

@laboratory_bp.route('/laboratory/manual-import/<int:result_id>', methods=['POST'])
@login_required
def manual_import(result_id):
    """Manually import an external lab result to a specific lab request"""
    lab_request_id = request.form.get('lab_request_id')
    if not lab_request_id:
        flash('Lab request ID is required', 'danger')
        return redirect(url_for('laboratory.pending_results'))
    
    try:
        external_result = ExternalLabResult.query.get_or_404(result_id)
        lab_request = LabRequest.query.get_or_404(lab_request_id)
        
        # Update the lab request with the external result
        lab_request.result = external_result.result
        lab_request.is_completed = True
        lab_request.completed_at = datetime.now()
        lab_request.result_added_by = f"Auto-import (manual match by {current_user.username})"
        lab_request.is_auto_imported = True
        lab_request.external_system_id = external_result.external_system_id
        
        # Mark the external result as imported
        external_result.is_imported = True
        external_result.lab_request_id = lab_request.id
        
        db.session.commit()
        flash('Lab result successfully imported', 'success')
        
    except Exception as e:
        logging.error(f"Error manually importing result: {str(e)}")
        db.session.rollback()
        flash(f'Error importing result: {str(e)}', 'danger')
        
    return redirect(url_for('laboratory.pending_results'))

def process_external_result(result_id):
    """Process a newly received external lab result and try to match it with a pending lab request"""
    try:
        external_result = ExternalLabResult.query.get(result_id)
        if not external_result:
            logging.error(f"External result with ID {result_id} not found")
            return False
        
        # Find the patient by MRN
        patient = Patient.query.filter_by(medical_record_number=external_result.patient_mrn).first()
        if not patient:
            logging.warning(f"Patient with MRN {external_result.patient_mrn} not found for external result")
            return False
        
        # Find matching lab requests
        matching_requests = LabRequest.query.filter_by(
            patient_id=patient.id,
            test_type=external_result.test_type,
            test_name=external_result.test_name,
            is_completed=False
        ).all()
        
        if not matching_requests:
            logging.info(f"No matching lab requests found for external result {result_id}")
            return False
        
        # Get the oldest matching request
        matched_request = sorted(matching_requests, key=lambda x: x.requested_at)[0]
        
        # Update the lab request with the external result
        matched_request.result = external_result.result
        matched_request.is_completed = True
        matched_request.completed_at = datetime.now()
        matched_request.result_added_by = "Auto-import"
        matched_request.is_auto_imported = True
        matched_request.external_system_id = external_result.external_system_id
        
        # Mark the external result as imported
        external_result.is_imported = True
        external_result.lab_request_id = matched_request.id
        
        db.session.commit()
        logging.info(f"Successfully imported external result {result_id} to lab request {matched_request.id}")
        return True
        
    except Exception as e:
        logging.error(f"Error processing external result {result_id}: {str(e)}")
        db.session.rollback()
        return False